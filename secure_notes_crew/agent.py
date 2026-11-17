import os
from pathlib import Path
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

# Define absolute paths based on your exact environment
NOTES_ROOT = Path("/home/ppsspp18/notes/AI notes by gemma").resolve()
FORBIDDEN_PATH = (NOTES_ROOT / "safe notes").resolve()

# Ensure base directory exists locally
NOTES_ROOT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------
# TOOL LAYER: Secure Path Validation Wrapper
# ---------------------------------------------------------
def _validate_path(file_path: str) -> Path:
    """Ensures target path is safe and strictly outside the forbidden 'safe notes' subfolder."""
    # Resolve the target path relative to your notes root
    target_path = (NOTES_ROOT / file_path).resolve()
    
    # 1. Sandbox Check: Ensure target stays within NOTES_ROOT
    if not str(target_path).startswith(str(NOTES_ROOT)):
        raise PermissionError("Access denied: Path is outside your allowed notes directory.")
        
    # 2. Forbidden Check: Ensure target is NOT inside the 'safe notes' folder
    # We check if FORBIDDEN_PATH is a parent of or equal to the target path
    if target_path == FORBIDDEN_PATH or FORBIDDEN_PATH in target_path.parents:
        raise PermissionError(f"Security Alert: Access to '{FORBIDDEN_PATH.name}' is strictly restricted.")
        
    return target_path

# ---------------------------------------------------------
# WORKER TOOLS: Note Operations (CRUD)
# ---------------------------------------------------------
def create_or_edit_note(filename: str, content: str) -> str:
    """Creates or updates a note file securely within allowed bounds."""
    try:
        path = _validate_path(filename)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return f"Successfully saved note: {filename}"
    except Exception as e:
        return f"Error executing write operation: {str(e)}"

def read_note(filename: str) -> str:
    """Reads a specific note file if it passes safety checks."""
    try:
        path = _validate_path(filename)
        if not path.exists():
            return f"Note '{filename}' does not exist."
        return path.read_text(encoding="utf-8")
    except Exception as e:
        return f"Error executing read operation: {str(e)}"

def list_notes() -> str:
    """Lists all allowed notes in the directory, hiding the forbidden subfolder."""
    try:
        files = []
        for p in NOTES_ROOT.glob("**/*"):
            if p.is_file():
                resolved_p = p.resolve()
                # Skip anything inside the forbidden path
                if FORBIDDEN_PATH in resolved_p.parents or resolved_p == FORBIDDEN_PATH:
                    continue
                files.append(p.relative_to(NOTES_ROOT).as_posix())
        return f"Available notes: {files}"
    except Exception as e:
        return f"Error listing notes: {str(e)}"

# ---------------------------------------------------------
# AGENT DEFINITIONS (Multi-Agent Setup via ADK)
# ---------------------------------------------------------

note_worker = Agent(
    name="note_worker",
    model=LiteLlm(model="ollama_chat/gemma4:e2b"),
    description="Performs safe file CRUD operations on notes.",
    instruction=(
        "You are a secure note-management assistant. "
        "You have tools to read, write, and list notes. "
        "CRITICAL RULE: You possess zero access to the 'safe notes' subdirectory. "
        "If a user asks you to check, read, or edit anything inside that forbidden folder, refuse immediately."
    ),
    tools=[create_or_edit_note, read_note, list_notes]
)

root_agent = Agent(
    name="coordinator_agent",
    model=LiteLlm(model="ollama_chat/gemma4:e2b"),
    description="Coordinates user requests and delegates note-management actions.",
    instruction=(
        "You are the master coordinator for the local note system. "
        "Analyze the user's intent and delegate note tasks to the note_worker agent."
    ),
    sub_agents=[note_worker]
)