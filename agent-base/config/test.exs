import Config

# Test configuration
config :agent_base,
  log_level: :warning

# OpenRouter test configuration (use fake API key for tests)
config :agent_base, :openrouter,
  api_key: "test-api-key",
  base_url: "http://localhost:4000/api/v1",
  http_referer: "https://github.com/agent-base",
  app_title: "AgentBase Test"

# Print only warnings and errors during test
config :logger, level: :warning
