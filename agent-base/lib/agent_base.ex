defmodule AgentBase do
  @moduledoc """
  AgentBase is a foundation for building Elixir-powered agents.

  This module provides the core functionality and API for agent operations.
  """

  @doc """
  Returns the version of AgentBase.
  """
  @spec version() :: String.t()
  def version do
    "0.1.0"
  end
end
