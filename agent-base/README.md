# AgentBase

An Elixir-powered agent foundation built with modern OTP practices and integrated LLM capabilities.

## Overview

AgentBase provides a solid foundation for building intelligent agents in Elixir, leveraging the power of the BEAM VM and OTP supervision trees for fault-tolerant, concurrent operations. It includes first-class support for Large Language Models via the OpenRouter API with both streaming and non-streaming interfaces.

## Features

- 🚀 Built with modern Elixir (1.17+)
- 🔄 OTP supervision tree for fault tolerance
- 🤖 **OpenRouter API integration with streaming support**
- 💬 **Stateful conversation management via GenServers**
- 🌊 **Idiomatic Stream abstractions for LLM responses**
- 📝 Comprehensive documentation and typespecs
- ✅ Full test coverage
- 🎨 Code formatting with `mix format`

## Installation

If [available in Hex](https://hex.pm/docs/publish), the package can be installed
by adding `agent_base` to your list of dependencies in `mix.exs`:

```elixir
def deps do
  [
    {:agent_base, "~> 0.1.0"}
  ]
end
```

## Development Setup

```bash
# Install dependencies
mix deps.get

# Run tests
mix test

# Format code
mix format

# Generate documentation
mix docs
```

## Configuration

Set your OpenRouter API key as an environment variable:

```bash
export OPENROUTER_API_KEY="your-api-key-here"
```

Or configure it directly in your config files:

```elixir
# config/dev.exs
config :agent_base, :openrouter,
  api_key: {:system, "OPENROUTER_API_KEY"},
  base_url: "https://openrouter.ai/api/v1",
  http_referer: "https://github.com/your-project",
  app_title: "Your App Name"
```

## Architecture

AgentBase follows idiomatic Elixir patterns:

- **Application**: OTP application with supervision tree
- **Modularity**: Clean separation of concerns
- **Fault Tolerance**: Supervised processes with restart strategies
- **Documentation**: Inline docs and typespecs for all public functions
- **LLM Integration**: Three-tier approach for different use cases:
  - `OpenRouter` - Low-level API client
  - `Stream` - Functional Stream abstraction
  - `Conversation` - Stateful GenServer for multi-turn conversations

## Usage

### Basic LLM Interaction

```elixir
alias AgentBase.LLM.OpenRouter

# Simple non-streaming request
{:ok, response} = OpenRouter.chat_completion(
  model: "anthropic/claude-3.5-sonnet",
  messages: [
    %{role: "user", content: "What is the capital of France?"}
  ]
)

# Streaming request with callback
OpenRouter.chat_completion_stream(
  [
    model: "anthropic/claude-3.5-sonnet",
    messages: [%{role: "user", content: "Tell me a story"}]
  ],
  fn chunk ->
    case get_in(chunk, ["choices", Access.at(0), "delta", "content"]) do
      nil -> :ok
      content -> IO.write(content)
    end
  end
)
```

### Using Stream Abstraction (Idiomatic Elixir)

```elixir
alias AgentBase.LLM.Stream

# Create a stream and process it
Stream.from_openrouter(
  model: "anthropic/claude-3.5-sonnet",
  messages: [%{role: "user", content: "Count to 5"}]
)
|> Stream.extract_content()
|> Enum.each(&IO.write/1)

# Or collect the full response
response =
  Stream.from_openrouter(
    model: "anthropic/claude-3.5-sonnet",
    messages: [%{role: "user", content: "Hello!"}]
  )
  |> Stream.collect_response()
```

### Stateful Conversations

```elixir
alias AgentBase.LLM.Conversation

# Start a conversation with history management
{:ok, pid} = Conversation.start_link(
  model: "anthropic/claude-3.5-sonnet",
  system_prompt: "You are a helpful assistant.",
  temperature: 0.7
)

# Chat maintains context automatically
{:ok, response1} = Conversation.chat(pid, "My name is Alice")
{:ok, response2} = Conversation.chat(pid, "What's my name?")

# Stream responses
Conversation.chat_stream(pid, "Tell me a story", fn chunk ->
  IO.write(chunk)
end)

# Access conversation history
history = Conversation.get_history(pid)

# Clear history while keeping system prompt
Conversation.clear_history(pid)
```

### Running Examples

Start an IEx session and try the built-in examples:

```elixir
iex -S mix

# Simple examples
AgentBase.Examples.LLMExample.simple_chat()
AgentBase.Examples.LLMExample.streaming_chat()
AgentBase.Examples.LLMExample.stateful_conversation()
AgentBase.Examples.LLMExample.list_available_models()
```

## Contributing

Contributions are welcome! Please follow the existing code style and ensure all tests pass.

## License

Copyright (c) 2025

This project is licensed under the MIT License.
