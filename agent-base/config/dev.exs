import Config

# Development configuration
config :agent_base,
  log_level: :debug

# Do not include metadata or timestamps in development logs
config :logger, :console, format: "[$level] $message\n"
