defmodule AgentBase.LLM.OpenRouter do
  @moduledoc """
  Client for interacting with the OpenRouter API.

  This module provides a clean interface to the OpenRouter API with support for
  both regular and streaming requests. It follows OpenAI's API specification.

  ## Configuration

  Configure your OpenRouter API key in your config files:

      config :agent_base, :openrouter,
        api_key: "your-api-key",
        base_url: "https://openrouter.ai/api/v1"

  Or set it at runtime via environment variables:

      config :agent_base, :openrouter,
        api_key: {:system, "OPENROUTER_API_KEY"}

  ## Examples

      # Non-streaming request
      {:ok, response} = OpenRouter.chat_completion(
        model: "anthropic/claude-3.5-sonnet",
        messages: [
          %{role: "user", content: "Hello!"}
        ]
      )

      # Streaming request
      OpenRouter.chat_completion_stream(
        [
          model: "anthropic/claude-3.5-sonnet",
          messages: [%{role: "user", content: "Hello!"}]
        ],
        fn chunk -> IO.inspect(chunk) end
      )
  """

  require Logger

  @base_url "https://openrouter.ai/api/v1"
  @chat_completions_path "/chat/completions"

  @type message :: %{
          role: String.t(),
          content: String.t(),
          optional(:name) => String.t()
        }

  @type chat_options :: [
          {:model, String.t()}
          | {:messages, [message()]}
          | {:temperature, float()}
          | {:max_tokens, pos_integer()}
          | {:top_p, float()}
          | {:frequency_penalty, float()}
          | {:presence_penalty, float()}
          | {:stop, String.t() | [String.t()]}
          | {:stream, boolean()}
        ]

  @type error :: {:error, term()}
  @type chunk_callback :: (map() -> :ok | {:error, term()})

  @doc """
  Makes a chat completion request to OpenRouter (non-streaming).

  ## Options

    * `:model` - (required) The model to use (e.g., "anthropic/claude-3.5-sonnet")
    * `:messages` - (required) List of message maps with `:role` and `:content`
    * `:temperature` - Sampling temperature (0.0 to 2.0)
    * `:max_tokens` - Maximum tokens to generate
    * `:top_p` - Nucleus sampling parameter
    * `:frequency_penalty` - Penalize frequent tokens
    * `:presence_penalty` - Penalize repeated tokens
    * `:stop` - Stop sequences (string or list of strings)

  ## Returns

    * `{:ok, response}` - Success with response map
    * `{:error, reason}` - Error with reason

  ## Examples

      {:ok, response} = OpenRouter.chat_completion(
        model: "anthropic/claude-3.5-sonnet",
        messages: [
          %{role: "system", content: "You are a helpful assistant."},
          %{role: "user", content: "What is 2+2?"}
        ],
        temperature: 0.7,
        max_tokens: 100
      )
  """
  @spec chat_completion(chat_options()) :: {:ok, map()} | error()
  def chat_completion(opts) do
    with {:ok, api_key} <- get_api_key(),
         {:ok, body} <- build_request_body(opts) do
      request(:post, @chat_completions_path, body, api_key)
    end
  end

  @doc """
  Makes a streaming chat completion request to OpenRouter.

  The callback function will be called for each chunk received from the API.
  Chunks contain partial responses with `delta` updates.

  ## Arguments

    * `opts` - Same options as `chat_completion/1`
    * `callback` - Function that receives each chunk (arity 1)

  ## Returns

    * `:ok` - Stream completed successfully
    * `{:error, reason}` - Error occurred

  ## Examples

      OpenRouter.chat_completion_stream(
        [
          model: "anthropic/claude-3.5-sonnet",
          messages: [%{role: "user", content: "Tell me a story"}]
        ],
        fn chunk ->
          case chunk do
            %{"choices" => [%{"delta" => %{"content" => content}} | _]} ->
              IO.write(content)
            _ ->
              :ok
          end
        end
      )
  """
  @spec chat_completion_stream(chat_options(), chunk_callback()) :: :ok | error()
  def chat_completion_stream(opts, callback) when is_function(callback, 1) do
    with {:ok, api_key} <- get_api_key(),
         {:ok, body} <- build_request_body(Keyword.put(opts, :stream, true)) do
      stream_request(:post, @chat_completions_path, body, api_key, callback)
    end
  end

  @doc """
  Lists available models from OpenRouter.

  ## Returns

    * `{:ok, models}` - List of available models
    * `{:error, reason}` - Error occurred
  """
  @spec list_models() :: {:ok, map()} | error()
  def list_models do
    with {:ok, api_key} <- get_api_key() do
      request(:get, "/models", nil, api_key)
    end
  end

  # Private functions

  defp request(method, path, body, api_key) do
    url = base_url() <> path

    req =
      Req.new(
        method: method,
        url: url,
        headers: build_headers(api_key),
        json: body,
        retry: :transient,
        max_retries: 3,
        receive_timeout: 60_000
      )

    case Req.request(req) do
      {:ok, %Req.Response{status: status, body: response_body}} when status in 200..299 ->
        {:ok, response_body}

      {:ok, %Req.Response{status: status, body: body}} ->
        Logger.error("OpenRouter API error: #{status} - #{inspect(body)}")
        {:error, {:http_error, status, body}}

      {:error, exception} ->
        Logger.error("OpenRouter request failed: #{inspect(exception)}")
        {:error, {:request_failed, exception}}
    end
  end

  defp stream_request(method, path, body, api_key, callback) do
    url = base_url() <> path

    req =
      Req.new(
        method: method,
        url: url,
        headers: build_headers(api_key),
        json: body,
        receive_timeout: :infinity,
        into: fn {:data, data}, {req, resp} ->
          process_stream_chunk(data, callback)
          {:cont, {req, resp}}
        end
      )

    case Req.request(req) do
      {:ok, %Req.Response{status: status}} when status in 200..299 ->
        :ok

      {:ok, %Req.Response{status: status, body: body}} ->
        Logger.error("OpenRouter streaming error: #{status} - #{inspect(body)}")
        {:error, {:http_error, status, body}}

      {:error, exception} ->
        Logger.error("OpenRouter streaming request failed: #{inspect(exception)}")
        {:error, {:request_failed, exception}}
    end
  end

  defp process_stream_chunk(data, callback) do
    # SSE format: "data: {json}\n\n"
    data
    |> String.split("\n")
    |> Enum.filter(&String.starts_with?(&1, "data: "))
    |> Enum.each(fn line ->
      case String.trim_leading(line, "data: ") do
        "[DONE]" ->
          :ok

        json_str ->
          case Jason.decode(json_str) do
            {:ok, chunk} ->
              callback.(chunk)

            {:error, _} = error ->
              Logger.warning("Failed to decode SSE chunk: #{inspect(error)}")
          end
      end
    end)
  end

  defp build_headers(api_key) do
    [
      {"authorization", "Bearer #{api_key}"},
      {"content-type", "application/json"},
      {"http-referer", get_http_referer()},
      {"x-title", get_app_title()}
    ]
  end

  defp build_request_body(opts) do
    required_keys = [:model, :messages]

    case Enum.all?(required_keys, &Keyword.has_key?(opts, &1)) do
      true ->
        body =
          opts
          |> Enum.into(%{})
          |> Map.take([
            :model,
            :messages,
            :temperature,
            :max_tokens,
            :top_p,
            :frequency_penalty,
            :presence_penalty,
            :stop,
            :stream
          ])
          |> Enum.reject(fn {_k, v} -> is_nil(v) end)
          |> Map.new()

        {:ok, body}

      false ->
        missing = required_keys -- Keyword.keys(opts)
        {:error, {:missing_required_keys, missing}}
    end
  end

  defp get_api_key do
    case Application.get_env(:agent_base, :openrouter)[:api_key] do
      nil ->
        {:error, :missing_api_key}

      {:system, env_var} ->
        case System.get_env(env_var) do
          nil -> {:error, {:missing_env_var, env_var}}
          key -> {:ok, key}
        end

      key when is_binary(key) ->
        {:ok, key}
    end
  end

  defp base_url do
    Application.get_env(:agent_base, :openrouter)[:base_url] || @base_url
  end

  defp get_http_referer do
    Application.get_env(:agent_base, :openrouter)[:http_referer] || "https://github.com/agent-base"
  end

  defp get_app_title do
    Application.get_env(:agent_base, :openrouter)[:app_title] || "AgentBase"
  end
end
