import Config

# Runtime configuration (loaded during application start)
# This is the modern way to handle runtime configuration in Elixir

if config_env() == :prod do
  # Example: Load configuration from environment variables
  # config :agent_base, :some_setting, System.get_env("SOME_SETTING")
end
