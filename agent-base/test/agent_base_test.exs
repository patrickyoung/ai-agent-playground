defmodule AgentBaseTest do
  use ExUnit.Case
  doctest AgentBase

  describe "version/0" do
    test "returns the version string" do
      assert is_binary(AgentBase.version())
      assert AgentBase.version() == "0.1.0"
    end
  end
end
