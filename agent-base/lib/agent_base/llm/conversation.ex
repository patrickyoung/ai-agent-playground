defmodule AgentBase.LLM.Conversation do
  @moduledoc """
  A GenServer that manages a stateful conversation with an LLM.

  This module provides a clean abstraction for managing multi-turn conversations
  with language models, maintaining message history and configuration.

  ## Usage

      # Start a conversation
      {:ok, pid} = Conversation.start_link(
        model: "anthropic/claude-3.5-sonnet",
        system_prompt: "You are a helpful assistant."
      )

      # Send messages
      {:ok, response} = Conversation.chat(pid, "What is 2+2?")

      # Stream responses
      Conversation.chat_stream(pid, "Tell me a story", fn chunk ->
        IO.write(chunk)
      end)

      # Get conversation history
      history = Conversation.get_history(pid)

      # Clear history
      Conversation.clear_history(pid)
  """

  use GenServer
  require Logger

  alias AgentBase.LLM.OpenRouter

  @type message :: %{role: String.t(), content: String.t()}
  @type conversation_opts :: [
          {:model, String.t()}
          | {:system_prompt, String.t()}
          | {:temperature, float()}
          | {:max_tokens, pos_integer()}
        ]

  # Client API

  @doc """
  Starts a new conversation GenServer.

  ## Options

    * `:model` - (required) The model to use
    * `:system_prompt` - Optional system prompt
    * `:temperature` - Sampling temperature (default: 0.7)
    * `:max_tokens` - Maximum tokens per response
    * `:name` - Optional registered name for the GenServer

  ## Examples

      {:ok, pid} = Conversation.start_link(
        model: "anthropic/claude-3.5-sonnet",
        system_prompt: "You are a helpful coding assistant."
      )
  """
  @spec start_link(conversation_opts()) :: GenServer.on_start()
  def start_link(opts) do
    {gen_opts, conv_opts} = Keyword.split(opts, [:name])
    GenServer.start_link(__MODULE__, conv_opts, gen_opts)
  end

  @doc """
  Sends a message and gets a non-streaming response.

  ## Examples

      {:ok, response} = Conversation.chat(pid, "Hello!")
  """
  @spec chat(GenServer.server(), String.t()) :: {:ok, String.t()} | {:error, term()}
  def chat(server, user_message) do
    GenServer.call(server, {:chat, user_message}, :infinity)
  end

  @doc """
  Sends a message and streams the response via a callback.

  The callback receives content chunks as they arrive.

  ## Examples

      Conversation.chat_stream(pid, "Tell me a story", fn chunk ->
        IO.write(chunk)
      end)
  """
  @spec chat_stream(GenServer.server(), String.t(), (String.t() -> any())) ::
          :ok | {:error, term()}
  def chat_stream(server, user_message, callback) when is_function(callback, 1) do
    GenServer.call(server, {:chat_stream, user_message, callback}, :infinity)
  end

  @doc """
  Gets the current conversation history.

  ## Examples

      history = Conversation.get_history(pid)
  """
  @spec get_history(GenServer.server()) :: [message()]
  def get_history(server) do
    GenServer.call(server, :get_history)
  end

  @doc """
  Clears the conversation history.

  ## Examples

      Conversation.clear_history(pid)
  """
  @spec clear_history(GenServer.server()) :: :ok
  def clear_history(server) do
    GenServer.call(server, :clear_history)
  end

  @doc """
  Updates the conversation configuration.

  ## Examples

      Conversation.update_config(pid, temperature: 0.9)
  """
  @spec update_config(GenServer.server(), keyword()) :: :ok
  def update_config(server, opts) do
    GenServer.call(server, {:update_config, opts})
  end

  # Server callbacks

  @impl true
  def init(opts) do
    model = Keyword.fetch!(opts, :model)
    system_prompt = Keyword.get(opts, :system_prompt)
    temperature = Keyword.get(opts, :temperature, 0.7)
    max_tokens = Keyword.get(opts, :max_tokens)

    messages =
      if system_prompt do
        [%{role: "system", content: system_prompt}]
      else
        []
      end

    state = %{
      model: model,
      messages: messages,
      temperature: temperature,
      max_tokens: max_tokens
    }

    {:ok, state}
  end

  @impl true
  def handle_call({:chat, user_message}, _from, state) do
    messages = state.messages ++ [%{role: "user", content: user_message}]

    opts = build_request_opts(state, messages)

    case OpenRouter.chat_completion(opts) do
      {:ok, response} ->
        assistant_message = extract_message_content(response)

        new_state = %{
          state
          | messages: messages ++ [%{role: "assistant", content: assistant_message}]
        }

        {:reply, {:ok, assistant_message}, new_state}

      {:error, _reason} = error ->
        {:reply, error, state}
    end
  end

  @impl true
  def handle_call({:chat_stream, user_message, callback}, _from, state) do
    messages = state.messages ++ [%{role: "user", content: user_message}]
    opts = build_request_opts(state, messages)

    # Accumulate the response
    accumulated = %{content: ""}

    stream_callback = fn chunk ->
      case get_in(chunk, ["choices", Access.at(0), "delta", "content"]) do
        nil -> :ok
        content -> callback.(content)
      end

      # Track the content
      case get_in(chunk, ["choices", Access.at(0), "delta", "content"]) do
        nil ->
          accumulated

        content ->
          Map.update!(accumulated, :content, &(&1 <> content))
      end
    end

    case OpenRouter.chat_completion_stream(opts, stream_callback) do
      :ok ->
        # Add the assistant's response to history
        assistant_content = accumulated.content

        new_state = %{
          state
          | messages: messages ++ [%{role: "assistant", content: assistant_content}]
        }

        {:reply, :ok, new_state}

      {:error, _reason} = error ->
        {:reply, error, state}
    end
  end

  @impl true
  def handle_call(:get_history, _from, state) do
    {:reply, state.messages, state}
  end

  @impl true
  def handle_call(:clear_history, _from, state) do
    # Keep system message if present
    system_messages = Enum.filter(state.messages, &(&1.role == "system"))
    {:reply, :ok, %{state | messages: system_messages}}
  end

  @impl true
  def handle_call({:update_config, opts}, _from, state) do
    new_state = Enum.reduce(opts, state, fn {key, value}, acc ->
      Map.put(acc, key, value)
    end)

    {:reply, :ok, new_state}
  end

  # Private functions

  defp build_request_opts(state, messages) do
    [
      model: state.model,
      messages: messages,
      temperature: state.temperature
    ]
    |> maybe_put(:max_tokens, state.max_tokens)
  end

  defp maybe_put(opts, _key, nil), do: opts
  defp maybe_put(opts, key, value), do: Keyword.put(opts, key, value)

  defp extract_message_content(%{"choices" => [%{"message" => %{"content" => content}} | _]}) do
    content
  end

  defp extract_message_content(_), do: ""
end
