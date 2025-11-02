"""
Helper pour extraire les informations du User-Agent
Version V1 simple basée sur user_agent_parser ou analyse simple
"""
import re
from typing import Optional


def extract_device_info(user_agent: Optional[str]) -> str:
    """
    Extrait une version simplifiée du device depuis le User-Agent.
    Format retourné: "Browser/OS" (ex: "Chrome/Windows", "Safari/iOS")

    V1: Parsing simple basé sur des patterns regex
    TODO V2: Utiliser une lib comme user-agents ou httpagentparser pour parsing plus sophistiqué
    """
    if not user_agent:
        return "Unknown/Unknown"

    browser = extract_browser(user_agent)
    os = extract_os(user_agent)

    return f"{browser}/{os}"


def extract_browser(user_agent: str) -> str:
    """Extrait le nom du navigateur depuis le User-Agent"""
    # Ordre important : vérifier Edge/Chrome/Safari dans cet ordre
    if "Edg/" in user_agent or "Edge/" in user_agent:
        return "Edge"
    elif "Chrome/" in user_agent:
        return "Chrome"
    elif "Safari/" in user_agent and "Chrome/" not in user_agent:
        return "Safari"
    elif "Firefox/" in user_agent:
        return "Firefox"
    elif "Opera/" in user_agent or "OPR/" in user_agent:
        return "Opera"
    else:
        return "Unknown"


def extract_os(user_agent: str) -> str:
    """Extrait le système d'exploitation depuis le User-Agent"""
    if "Windows" in user_agent:
        return "Windows"
    elif "Mac OS X" in user_agent or "Macintosh" in user_agent:
        return "macOS"
    elif "iPhone" in user_agent or "iPad" in user_agent:
        return "iOS"
    elif "Android" in user_agent:
        return "Android"
    elif "Linux" in user_agent:
        return "Linux"
    else:
        return "Unknown"
