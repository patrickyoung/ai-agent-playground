import Config

# Test configuration
config :agent_base,
  log_level: :warning

# Print only warnings and errors during test
config :logger, level: :warning
