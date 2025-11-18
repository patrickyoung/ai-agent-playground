import Config

# Runtime configuration (loaded during application start)
# This is the modern way to handle runtime configuration in Elixir

if config_env() == :prod do
  # OpenRouter API configuration from environment variables
  openrouter_api_key =
    System.get_env("OPENROUTER_API_KEY") ||
      raise """
      Environment variable OPENROUTER_API_KEY is missing.
      Set it with your OpenRouter API key to use LLM features.
      """

  config :agent_base, :openrouter,
    api_key: openrouter_api_key,
    base_url: System.get_env("OPENROUTER_BASE_URL") || "https://openrouter.ai/api/v1",
    http_referer: System.get_env("OPENROUTER_HTTP_REFERER") || "https://github.com/agent-base",
    app_title: System.get_env("OPENROUTER_APP_TITLE") || "AgentBase"
end
