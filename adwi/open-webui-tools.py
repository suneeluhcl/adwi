"""
Open WebUI Tool definitions for Adwi's Safe Command API.

HOW TO USE:
1. Open http://localhost:3000
2. Go to Settings → Tools → Add Tool
3. Paste each class below as a separate Tool in Open WebUI.
   (Open WebUI reads Python classes with docstrings as tool definitions)
4. Enable the tool in a chat session.

The tools call Adwi's Safe Command API at http://host.docker.internal:5055
which runs on the Mac host (accessible from Docker containers).
"""

import urllib.request
import json

COMMAND_API = "http://host.docker.internal:5055"


class AdwiStatusTool:
    """
    name: adwi_status
    description: Check the health of Suneel's local AI stack (Ollama, Docker services, etc.)
    """

    def run(self) -> str:
        """Check if local AI services are healthy."""
        try:
            req = urllib.request.Request(f"{COMMAND_API}/status-ai")
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.load(r)
                return data.get("stdout", "Status check complete.")
        except Exception as e:
            return f"Command API unavailable: {e}"


class AdwiMaintenanceTool:
    """
    name: adwi_maintenance
    description: Run Suneel's daily AI maintenance routine (status report, notes index, knowledge sync)
    """

    def run(self) -> str:
        """Run the daily AI maintenance workflow."""
        try:
            req = urllib.request.Request(f"{COMMAND_API}/auto-ai-maintenance")
            with urllib.request.urlopen(req, timeout=300) as r:
                data = json.load(r)
                return data.get("stdout", "Maintenance complete.")[:2000]
        except Exception as e:
            return f"Command API unavailable: {e}"


class AdwiSelfHealTool:
    """
    name: adwi_self_heal
    description: Auto-repair Suneel's local AI setup if something is broken or not running
    """

    def run(self) -> str:
        """Run self-heal to fix broken services."""
        try:
            req = urllib.request.Request(f"{COMMAND_API}/adwi-self-heal")
            with urllib.request.urlopen(req, timeout=300) as r:
                data = json.load(r)
                return data.get("stdout", "Self-heal complete.")[:2000]
        except Exception as e:
            return f"Command API unavailable: {e}"


class AdwiRagIndexTool:
    """
    name: adwi_rag_index
    description: Rebuild Adwi's semantic notes index for RAG search over local knowledge
    """

    def run(self) -> str:
        """Rebuild the RAG index from local notes."""
        try:
            req = urllib.request.Request(f"{COMMAND_API}/rag-index")
            with urllib.request.urlopen(req, timeout=300) as r:
                data = json.load(r)
                return data.get("stdout", "RAG index rebuilt.")[:1000]
        except Exception as e:
            return f"Command API unavailable: {e}"


class AdwiGitStatusTool:
    """
    name: adwi_git_status
    description: Show git status for all repositories in Suneel's workspace
    """

    def run(self) -> str:
        """Check git status across all workspace repos."""
        try:
            req = urllib.request.Request(f"{COMMAND_API}/git-status-workspace")
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.load(r)
                return data.get("stdout", "Git status complete.")[:3000]
        except Exception as e:
            return f"Command API unavailable: {e}"
