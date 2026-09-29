"""
Automated tests for DevRecall and Hindsight memory integration.
Verifies memory retention, recall relevance, and agent command synthesis.
"""

import os
import unittest
from devrecall.memory import DevMemory
from devrecall.agent import DevRecallAgent


class TestDevRecall(unittest.TestCase):
    def setUp(self):
        self.test_storage = ".devrecall/test_memory.json"
        self.memory = DevMemory(storage_file=self.test_storage)
        self.memory.clear()
        self.agent = DevRecallAgent(memory=self.memory)

    def tearDown(self):
        if os.path.exists(self.test_storage):
            os.remove(self.test_storage)

    def test_memory_retention(self):
        """Test retaining environment facts into the memory bank."""
        result = self.memory.retain(
            content="Host is Windows 11 using PowerShell 7. Use $env:KEY='val'.",
            tags=["powershell", "windows"]
        )
        self.assertIn(result["status"], ["retained", "success"])
        memories = self.memory.list_all()
        self.assertEqual(len(memories), 1)
        self.assertIn("PowerShell", memories[0]["content"])

    def test_memory_recall_relevance(self):
        """Test recalling relevant memories based on query keywords."""
        self.memory.retain("PostgreSQL port mapped to 5433", tags=["database", "postgres", "ports"])
        self.memory.retain("Use pnpm for all frontend builds", tags=["package-manager", "pnpm"])

        # Recall for database query
        db_results = self.memory.recall("How do I connect to postgres?")
        self.assertTrue(len(db_results) > 0)
        self.assertIn("5433", db_results[0]["content"])

        # Recall for package manager query
        frontend_results = self.memory.recall("Install frontend packages")
        self.assertTrue(len(frontend_results) > 0)
        self.assertIn("pnpm", frontend_results[0]["content"])

    def test_agent_before_and_after_memory(self):
        """Verify the agent changes output when memory is provided vs omitted."""
        query = "How do I set test environment variables and run our integration tests?"

        # 1. Without Memory: Naive bash/npm output
        naive_result = self.agent.process(query, use_memory=False)
        self.assertIn("export", naive_result["response"]["command"])
        self.assertIn("npm test", naive_result["response"]["command"])
        self.assertFalse(naive_result["response"]["success"])

        # 2. Retain rules into Hindsight
        self.memory.retain(
            "Host environment: Windows 11 using PowerShell 7. Always use $env:KEY='val'.",
            tags=["environment", "powershell"]
        )
        self.memory.retain(
            "Package manager: Repository exclusively uses pnpm.",
            tags=["package-manager", "pnpm"]
        )

        # 3. With Memory: Adapted PowerShell/pnpm output
        memory_result = self.agent.process(query, use_memory=True)
        self.assertIn("$env:", memory_result["response"]["command"])
        self.assertIn("pnpm test", memory_result["response"]["command"])
        self.assertTrue(memory_result["response"]["success"])

    def test_learn_from_failure(self):
        """Verify the agent can learn a corrective rule from an error trace."""
        self.agent.learn_from_failure(
            error_message="port 5432 is already allocated",
            corrective_rule="Map Docker host port to 5433 instead of 5432"
        )
        memories = self.memory.list_all()
        self.assertEqual(len(memories), 1)
        self.assertIn("5433", memories[0]["content"])


if __name__ == "__main__":
    unittest.main()
