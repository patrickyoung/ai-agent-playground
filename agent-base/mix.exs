defmodule AgentBase.MixProject do
  use Mix.Project

  def project do
    [
      app: :agent_base,
      version: "0.1.0",
      elixir: "~> 1.17",
      start_permanent: Mix.env() == :prod,
      deps: deps(),
      elixirc_paths: elixirc_paths(Mix.env()),
      aliases: aliases(),
      preferred_cli_env: [
        test: :test,
        "test.watch": :test
      ]
    ]
  end

  # Run "mix help compile.app" to learn about applications.
  def application do
    [
      extra_applications: [:logger, :inets, :ssl],
      mod: {AgentBase.Application, []}
    ]
  end

  # Specifies which paths to compile per environment.
  defp elixirc_paths(:test), do: ["lib", "test/support"]
  defp elixirc_paths(_), do: ["lib"]

  # Run "mix help deps" to learn about dependencies.
  defp deps do
    [
      # HTTP client with streaming support
      {:req, "~> 0.5"},
      # JSON encoding/decoding
      {:jason, "~> 1.4"},
      # Options validation
      {:nimble_options, "~> 1.1"},

      # Development and testing
      {:ex_doc, "~> 0.34", only: :dev, runtime: false},
      {:credo, "~> 1.7", only: [:dev, :test], runtime: false},
      {:dialyxir, "~> 1.4", only: [:dev, :test], runtime: false},
      {:bypass, "~> 2.1", only: :test}
    ]
  end

  defp aliases do
    [
      setup: ["deps.get"],
      test: ["test --trace"]
    ]
  end
end
