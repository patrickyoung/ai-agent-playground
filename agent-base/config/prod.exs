import Config

# Production configuration
config :agent_base,
  log_level: :info

# Do not print debug messages in production
config :logger, level: :info
