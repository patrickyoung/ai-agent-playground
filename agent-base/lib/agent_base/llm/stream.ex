defmodule AgentBase.LLM.Stream do
  @moduledoc """
  Provides a Stream-based interface for LLM streaming responses.

  This module allows you to work with LLM streaming responses using Elixir's
  powerful Stream abstraction, enabling composition and lazy evaluation.

  ## Examples

      # Create a stream from OpenRouter
      stream = Stream.from_openrouter(
        model: "anthropic/claude-3.5-sonnet",
        messages: [%{role: "user", content: "Count to 5"}]
      )

      # Process the stream
      stream
      |> Stream.extract_content()
      |> Enum.each(&IO.write/1)

      # Or collect all chunks
      chunks = Enum.to_list(stream)

      # Map over the stream
      stream
      |> Stream.map(fn chunk -> get_in(chunk, ["choices", Access.at(0), "delta", "content"]) end)
      |> Stream.reject(&is_nil/1)
      |> Enum.join()
  """

  alias AgentBase.LLM.OpenRouter

  @doc """
  Creates a Stream from an OpenRouter streaming request.

  This function initiates a streaming request to OpenRouter and returns a Stream
  that yields each chunk as it arrives.

  ## Options

  Same as `OpenRouter.chat_completion/1` but `:stream` is automatically set to `true`.

  ## Returns

  A `Stream.t()` that yields decoded JSON chunks.

  ## Examples

      Stream.from_openrouter(
        model: "anthropic/claude-3.5-sonnet",
        messages: [%{role: "user", content: "Hello!"}]
      )
      |> Enum.to_list()
  """
  @spec from_openrouter(keyword()) :: Enumerable.t()
  def from_openrouter(opts) do
    Stream.resource(
      fn -> start_stream(opts) end,
      fn state -> next_chunk(state) end,
      fn state -> stop_stream(state) end
    )
  end

  @doc """
  Extracts content from streaming chunks.

  This is a convenience function that filters and extracts the content field
  from delta updates in streaming responses.

  ## Examples

      stream
      |> Stream.extract_content()
      |> Enum.join()
  """
  @spec extract_content(Enumerable.t()) :: Enumerable.t()
  def extract_content(stream) do
    stream
    |> Stream.map(fn chunk ->
      get_in(chunk, ["choices", Access.at(0), "delta", "content"])
    end)
    |> Stream.reject(&is_nil/1)
  end

  @doc """
  Collects the full response from a stream.

  ## Examples

      Stream.from_openrouter(opts)
      |> Stream.collect_response()
  """
  @spec collect_response(Enumerable.t()) :: String.t()
  def collect_response(stream) do
    stream
    |> extract_content()
    |> Enum.join()
  end

  # Private functions

  defp start_stream(opts) do
    parent = self()
    ref = make_ref()

    # Spawn a task to handle the streaming request
    task =
      Task.async(fn ->
        OpenRouter.chat_completion_stream(opts, fn chunk ->
          send(parent, {ref, :chunk, chunk})
        end)

        send(parent, {ref, :done})
      end)

    %{task: task, ref: ref, buffer: :queue.new()}
  end

  defp next_chunk(%{ref: ref, buffer: buffer} = state) do
    case :queue.out(buffer) do
      {{:value, chunk}, new_buffer} ->
        {[chunk], %{state | buffer: new_buffer}}

      {:empty, _buffer} ->
        receive do
          {^ref, :chunk, chunk} ->
            {[chunk], state}

          {^ref, :done} ->
            {:halt, state}
        after
          30_000 ->
            {:halt, state}
        end
    end
  end

  defp stop_stream(%{task: task}) do
    # Ensure the task is shut down properly
    Task.shutdown(task, :brutal_kill)
  end
end
