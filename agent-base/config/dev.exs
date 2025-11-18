import Config

# Development configuration
config :agent_base,
  log_level: :debug

# OpenRouter configuration
# Set your API key via environment variable: OPENROUTER_API_KEY
config :agent_base, :openrouter,
  api_key: {:system, "OPENROUTER_API_KEY"},
  base_url: "https://openrouter.ai/api/v1",
  http_referer: "https://github.com/agent-base",
  app_title: "AgentBase Development"

# Do not include metadata or timestamps in development logs
config :logger, :console, format: "[$level] $message\n"
