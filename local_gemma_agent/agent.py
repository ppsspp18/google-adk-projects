import datetime
import subprocess
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

def get_system_time() -> str:
    """Returns the current local date and time on the user's Linux Mint machine."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_system_stats() -> str:
    """Checks real-time RAM consumption and disk space on the Linux Mint laptop."""
    try:
        mem = subprocess.check_output(["free", "-h"]).decode("utf-8")
        disk = subprocess.check_output(["df", "-h", "/"]).decode("utf-8")
        return f"--- Memory Status ---\n{mem}\n--- Disk Usage (Root) ---\n{disk}"
    except Exception as e:
        return f"Error fetching system stats: {str(e)}"

def check_battery_status() -> str:
    """Reads the laptop's battery percentage and whether it is plugged in or discharging."""
    try:
        battery = subprocess.check_output(["acpi"]).decode("utf-8")
        return battery.strip()
    except Exception:
        try:
            with open("/sys/class/power_supply/BAT0/capacity", "r") as f:
                cap = f.read().strip()
            with open("/sys/class/power_supply/BAT0/status", "r") as f:
                status = f.read().strip()
            return f"Battery capacity: {cap}%, Status: {status}"
        except Exception as e:
            return f"Could not retrieve battery info: {str(e)}"

def get_running_processes() -> str:
    """Lists the top memory-hungry applications currently running on the Linux Mint machine."""
    try:
        cmd = "ps aux --sort=-%mem | head -n 6"
        result = subprocess.check_output(cmd, shell=True).decode("utf-8")
        return result
    except Exception as e:
        return f"Error fetching running processes: {str(e)}"

def get_network_status() -> str:
    """Fetches active network connection details and IP information on Linux Mint."""
    try:
        result = subprocess.check_output(["ip", "-brief", "address"]).decode("utf-8")
        return result
    except Exception as e:
        return f"Error fetching network status: {str(e)}"

def send_desktop_notification(title: str, message: str) -> str:
    """Triggers a native Linux Mint desktop pop-up notification with a given title and message."""
    try:
        subprocess.run(["notify-send", title, message], check=True)
        return f"Successfully sent notification: '{title} - {message}'"
    except Exception as e:
        return f"Failed to send notification: {str(e)}"

root_agent = Agent(
    name="gemma_local_agent",
    model=LiteLlm(model="ollama_chat/gemma4:e2b"),
    description="An advanced local assistant running on Gemma 4 via Ollama with Linux Mint hardware and system tools.",
    instruction=(
        "You are an advanced local AI assistant running on Linux Mint. "
        "You have direct access to system tools to check time, RAM/disk usage, battery status, "
        "running processes, network status, and trigger desktop notifications. "
        "Use these tools automatically whenever the user asks about their laptop's health, battery, apps, or network."
    ),
    tools=[
        get_system_time,
        get_system_stats,
        check_battery_status,
        get_running_processes,
        get_network_status,
        send_desktop_notification,
    ],
)