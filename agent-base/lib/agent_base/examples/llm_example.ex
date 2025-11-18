defmodule AgentBase.Examples.LLMExample do
  @moduledoc """
  Example usage of AgentBase LLM integration with OpenRouter.

  These examples demonstrate how to use the various LLM features
  in AgentBase for building AI agents.

  ## Running Examples

  Make sure you have set your OPENROUTER_API_KEY environment variable:

      export OPENROUTER_API_KEY="your-key-here"

  Then start IEx:

      iex -S mix

  And run the examples:

      AgentBase.Examples.LLMExample.simple_chat()
      AgentBase.Examples.LLMExample.streaming_chat()
      AgentBase.Examples.LLMExample.stateful_conversation()
  """

  alias AgentBase.LLM.{OpenRouter, Conversation, Stream}
  require Logger

  @doc """
  Example of a simple non-streaming chat completion.
  """
  def simple_chat do
    Logger.info("Running simple chat example...")

    opts = [
      model: "anthropic/claude-3.5-sonnet",
      messages: [
        %{role: "user", content: "What is the capital of France? Answer in one word."}
      ],
      max_tokens: 10
    ]

    case OpenRouter.chat_completion(opts) do
      {:ok, response} ->
        content = get_in(response, ["choices", Access.at(0), "message", "content"])
        Logger.info("Response: #{content}")
        {:ok, content}

      {:error, reason} ->
        Logger.error("Error: #{inspect(reason)}")
        {:error, reason}
    end
  end

  @doc """
  Example of streaming chat completion with a callback.
  """
  def streaming_chat do
    Logger.info("Running streaming chat example...")

    opts = [
      model: "anthropic/claude-3.5-sonnet",
      messages: [
        %{role: "user", content: "Count from 1 to 5, one number per line."}
      ]
    ]

    OpenRouter.chat_completion_stream(opts, fn chunk ->
      case get_in(chunk, ["choices", Access.at(0), "delta", "content"]) do
        nil -> :ok
        content -> IO.write(content)
      end
    end)

    IO.puts("\n")
  end

  @doc """
  Example using the Stream abstraction for more idiomatic Elixir code.
  """
  def stream_abstraction do
    Logger.info("Running Stream abstraction example...")

    response =
      Stream.from_openrouter(
        model: "anthropic/claude-3.5-sonnet",
        messages: [
          %{role: "user", content: "Say 'Hello, Elixir!' and nothing else."}
        ]
      )
      |> Stream.collect_response()

    Logger.info("Collected response: #{response}")
    {:ok, response}
  end

  @doc """
  Example of a stateful conversation using the Conversation GenServer.
  """
  def stateful_conversation do
    Logger.info("Running stateful conversation example...")

    {:ok, pid} =
      Conversation.start_link(
        model: "anthropic/claude-3.5-sonnet",
        system_prompt: "You are a helpful math tutor. Keep responses brief.",
        temperature: 0.7
      )

    # First message
    Logger.info("Asking first question...")

    case Conversation.chat(pid, "What is 2 + 2?") do
      {:ok, response} ->
        Logger.info("Response 1: #{response}")

      {:error, reason} ->
        Logger.error("Error: #{inspect(reason)}")
    end

    # Second message (builds on history)
    Logger.info("Asking follow-up question...")

    case Conversation.chat(pid, "What about if I multiply that by 3?") do
      {:ok, response} ->
        Logger.info("Response 2: #{response}")

      {:error, reason} ->
        Logger.error("Error: #{inspect(reason)}")
    end

    # Get full history
    history = Conversation.get_history(pid)
    Logger.info("Conversation history has #{length(history)} messages")

    # Clean up
    GenServer.stop(pid)

    :ok
  end

  @doc """
  Example of streaming with a stateful conversation.
  """
  def stateful_streaming_conversation do
    Logger.info("Running stateful streaming conversation example...")

    {:ok, pid} =
      Conversation.start_link(
        model: "anthropic/claude-3.5-sonnet",
        system_prompt: "You are a creative storyteller."
      )

    Logger.info("Streaming response:")

    Conversation.chat_stream(pid, "Tell me a very short story about a robot.", fn chunk ->
      IO.write(chunk)
    end)

    IO.puts("\n")

    # Clean up
    GenServer.stop(pid)

    :ok
  end

  @doc """
  Example showing how to list available models.
  """
  def list_available_models do
    Logger.info("Fetching available models...")

    case OpenRouter.list_models() do
      {:ok, response} ->
        models = response["data"] || []
        Logger.info("Found #{length(models)} models")

        # Show first 5 models
        models
        |> Enum.take(5)
        |> Enum.each(fn model ->
          Logger.info("  - #{model["id"]}")
        end)

        {:ok, models}

      {:error, reason} ->
        Logger.error("Error: #{inspect(reason)}")
        {:error, reason}
    end
  end
end
