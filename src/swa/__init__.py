"""Scientific Writing Agent (swa).

Guideline-driven tooling for scientific writing and manuscript revision.

Layers:
    swa.rules       -- parse the versioned guideline catalogue (guidelines/*.md)
    swa.manuscript  -- load and structure manuscripts (LaTeX / Markdown)
    swa.checks      -- deterministic (LLM-free) rule checks
    swa.report      -- render findings into review reports
    swa.mcp_server  -- MCP server exposing all of the above to any MCP client
    swa.agent       -- LangGraph agent orchestrating the full review pipeline
"""

__version__ = "0.1.0"
