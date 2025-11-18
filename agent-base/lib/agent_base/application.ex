defmodule AgentBase.Application do
  @moduledoc """
  The AgentBase application.

  This is the entry point for the supervision tree.
  """

  use Application

  @impl true
  def start(_type, _args) do
    children = [
      # Add your supervised processes here
      # Example: {AgentBase.Worker, arg}
    ]

    # See https://hexdocs.pm/elixir/Supervisor.html
    # for other strategies and supported options
    opts = [strategy: :one_for_one, name: AgentBase.Supervisor]
    Supervisor.start_link(children, opts)
  end
end
