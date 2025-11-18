defmodule AgentBase.LLM.ConversationTest do
  use ExUnit.Case, async: true

  alias AgentBase.LLM.Conversation

  doctest Conversation

  describe "start_link/1" do
    test "starts a conversation with required model" do
      assert {:ok, pid} =
               Conversation.start_link(
                 model: "anthropic/claude-3.5-sonnet"
               )

      assert Process.alive?(pid)
      Process.exit(pid, :normal)
    end

    test "starts with system prompt" do
      {:ok, pid} =
        Conversation.start_link(
          model: "anthropic/claude-3.5-sonnet",
          system_prompt: "You are a helpful assistant."
        )

      history = Conversation.get_history(pid)
      assert [%{role: "system", content: "You are a helpful assistant."}] = history

      Process.exit(pid, :normal)
    end

    test "starts without system prompt" do
      {:ok, pid} =
        Conversation.start_link(
          model: "anthropic/claude-3.5-sonnet"
        )

      history = Conversation.get_history(pid)
      assert [] = history

      Process.exit(pid, :normal)
    end
  end

  describe "get_history/1" do
    test "returns conversation history" do
      {:ok, pid} =
        Conversation.start_link(
          model: "anthropic/claude-3.5-sonnet",
          system_prompt: "Test system"
        )

      history = Conversation.get_history(pid)
      assert length(history) == 1
      assert hd(history).role == "system"

      Process.exit(pid, :normal)
    end
  end

  describe "clear_history/1" do
    test "clears history but keeps system message" do
      {:ok, pid} =
        Conversation.start_link(
          model: "anthropic/claude-3.5-sonnet",
          system_prompt: "Test system"
        )

      # Add a message manually to state for testing
      # In real usage, this would come from chat/2
      :ok = Conversation.clear_history(pid)

      history = Conversation.get_history(pid)
      # Should only have system message
      assert length(history) == 1
      assert hd(history).role == "system"

      Process.exit(pid, :normal)
    end

    test "clears history when no system message" do
      {:ok, pid} = Conversation.start_link(model: "anthropic/claude-3.5-sonnet")

      :ok = Conversation.clear_history(pid)

      history = Conversation.get_history(pid)
      assert [] = history

      Process.exit(pid, :normal)
    end
  end

  describe "update_config/2" do
    test "updates configuration" do
      {:ok, pid} = Conversation.start_link(model: "anthropic/claude-3.5-sonnet")

      :ok = Conversation.update_config(pid, temperature: 0.9)

      # We can't directly inspect the state, but we can verify the call succeeds
      assert Process.alive?(pid)

      Process.exit(pid, :normal)
    end
  end
end
