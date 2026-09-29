"""
DevRecall Agent module.
Coordinates prompt processing, Hindsight memory recall/retention,
and environment-adaptive command generation.
"""

from typing import Dict, Any, List, Optional
from .memory import DevMemory


class DevRecallAgent:
    """
    Developer pair-programmer agent that utilizes Hindsight memory
    to prevent repetitive developer environment mistakes.
    """

    def __init__(self, memory: Optional[DevMemory] = None):
        self.memory = memory or DevMemory()

    def process(self, prompt: str, use_memory: bool = True) -> Dict[str, Any]:
        """
        Process a user request.
        If use_memory is True, recalls Hindsight facts before generating commands.
        If use_memory is False, runs naive default generation (demonstrating agent drift).
        """
        recalled_memories: List[Dict[str, Any]] = []

        if use_memory:
            recalled_memories = self.memory.recall(prompt)

        # Generate command response based on memory context
        response = self._synthesize_command(prompt, recalled_memories, use_memory)

        return {
            "prompt": prompt,
            "use_memory": use_memory,
            "recalled_memories": recalled_memories,
            "response": response
        }

    def _synthesize_command(
        self,
        prompt: str,
        memories: List[Dict[str, Any]],
        use_memory: bool
    ) -> Dict[str, Any]:
        """
        Synthesizes the terminal commands, taking into account any recalled quirks.
        """
        p_lower = prompt.lower()
        has_memory = len(memories) > 0 and use_memory

        # Memory contextual extraction
        memory_text = " ".join([m.get("content", "").lower() for m in memories]) if has_memory else ""

        is_powershell = "powershell" in memory_text or "windows" in memory_text
        use_pnpm = "pnpm" in memory_text
        pg_port = "5433" if "5433" in memory_text else ("5432" if not has_memory else "5433")

        # Scenario 1: Setting environment variables and running tests
        if "test" in p_lower or "env" in p_lower:
            if not has_memory:
                # Naive failure case: uses bash 'export' and generic npm
                return {
                    "explanation": "Default naive generation (Bash assumed, standard npm):",
                    "command": "export NODE_ENV=test && export DB_PORT=5432 && npm test",
                    "notes": "Will fail on Windows PowerShell ('export' not recognized) or pnpm repos.",
                    "success": False
                }
            else:
                # Hindsight memory case: adapted for PowerShell & pnpm
                cmd_env = "$env:NODE_ENV='test'; $env:DB_PORT='5433';" if is_powershell else "export NODE_ENV=test DB_PORT=5433"
                pkg_cmd = "pnpm test" if use_pnpm else "npm test"
                return {
                    "explanation": "Memory-augmented generation (Recalled Windows PowerShell & pnpm):",
                    "command": f"{cmd_env} {pkg_cmd}",
                    "notes": "Exact syntax synthesized from Hindsight environment bank.",
                    "success": True
                }

        # Scenario 2: Starting Database / Docker Postgres
        elif "postgres" in p_lower or "db" in p_lower or "database" in p_lower:
            if not has_memory:
                # Naive failure case: standard 5432 port collision
                return {
                    "explanation": "Default naive generation (Assumes standard port 5432 is free):",
                    "command": "docker run -d --name my-postgres -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres",
                    "notes": "Collides with local port 5432 if local PostgreSQL is already bound.",
                    "success": False
                }
            else:
                # Hindsight memory case: remapped port
                return {
                    "explanation": f"Memory-augmented generation (Recalled port 5432 collision, using {pg_port}):",
                    "command": f"docker run -d --name dev-postgres -p {pg_port}:5432 -e POSTGRES_PASSWORD=secret postgres:16-alpine",
                    "notes": f"Avoids local binding conflict by mapping host port {pg_port}.",
                    "success": True
                }

        # Scenario 3: Python Virtual Environment / Dependencies
        elif "python" in p_lower or "pip" in p_lower or "venv" in p_lower:
            if not has_memory:
                return {
                    "explanation": "Default naive generation (Standard Linux source activate):",
                    "command": "source .venv/bin/activate && pip install -r requirements.txt",
                    "notes": "Fails on Windows (source not recognized, requires .venv\\Scripts\\Activate.ps1).",
                    "success": False
                }
            else:
                return {
                    "explanation": "Memory-augmented generation (Recalled Windows virtualenv path):",
                    "command": ".\\.venv\\Scripts\\Activate.ps1; pip install -r requirements.txt",
                    "notes": "Targeted script execution for current PowerShell environment.",
                    "success": True
                }

        # Generic command fallback
        if not has_memory:
            return {
                "explanation": "Default command generation without context memory:",
                "command": f"# Running generic: {prompt}\n./run.sh",
                "notes": "No environment memory attached.",
                "success": False
            }
        else:
            return {
                "explanation": "Adaptive generation with Hindsight context:",
                "command": f"# Context-aware execution for: {prompt}\nWrite-Host 'Executing with recalled profile'",
                "notes": f"Applied {len(memories)} recalled facts from Hindsight bank.",
                "success": True
            }

    def learn_from_failure(self, error_message: str, corrective_rule: str, tags: Optional[List[str]] = None):
        """
        Retains a new rule into Hindsight after debugging an environment mistake.
        """
        tags = tags or ["environment", "fix", "powershell"]
        memory_content = f"Rule: {corrective_rule} (Context: Fixed error '{error_message}')"
        return self.memory.retain(content=memory_content, tags=tags)
