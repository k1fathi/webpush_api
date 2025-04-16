"""
User Agent Parser Module

This module provides functionality to parse User-Agent strings
and extract useful information like browser, OS, and device type.
"""

import re
from typing import Dict, Any, Optional


def parse_user_agent(user_agent_string: str) -> Dict[str, Any]:
    """
    Parse a User-Agent string and extract browser, OS, and device information.
    
    Args:
        user_agent_string: The User-Agent string from the browser
        
    Returns:
        Dictionary containing parsed information
    """
    if not user_agent_string:
        return {
            "browser_name": "Unknown",
            "browser_version": None,
            "os_name": "Unknown",
            "os_version": None,
            "device_type": "Unknown",
            "is_mobile": False
        }
    
    # Initialize result
    result = {
        "browser_name": "Unknown",
        "browser_version": None,
        "os_name": "Unknown",
        "os_version": None,
        "device_type": "desktop",
        "is_mobile": False
    }
    
    # Convert to lowercase for easier matching
    ua_lower = user_agent_string.lower()
    
    # Check for mobile devices
    if any(mobile_keyword in ua_lower for mobile_keyword in ["mobile", "android", "iphone", "ipad", "ipod"]):
        result["is_mobile"] = True
        
        # Determine device type
        if any(tablet_keyword in ua_lower for tablet_keyword in ["ipad", "tablet"]):
            result["device_type"] = "tablet"
        else:
            result["device_type"] = "mobile"
    
    # Browser detection
    # Chrome
    chrome_match = re.search(r"chrome/(\d+(\.\d+)?)", ua_lower)
    # Edge
    edge_match = re.search(r"edg[e]?/(\d+(\.\d+)?)", ua_lower)
    # Firefox
    firefox_match = re.search(r"firefox/(\d+(\.\d+)?)", ua_lower)
    # Safari
    safari_match = re.search(r"version/(\d+(\.\d+)?).+safari", ua_lower)
    # Opera
    opera_match = re.search(r"opr/(\d+(\.\d+)?)", ua_lower)
    
    if edge_match:
        result["browser_name"] = "Edge"
        result["browser_version"] = edge_match.group(1)
    elif opera_match:
        result["browser_name"] = "Opera"
        result["browser_version"] = opera_match.group(1)
    elif chrome_match and "chrome" in ua_lower and not "chromium" in ua_lower:
        result["browser_name"] = "Chrome"
        result["browser_version"] = chrome_match.group(1)
    elif firefox_match:
        result["browser_name"] = "Firefox"
        result["browser_version"] = firefox_match.group(1)
    elif safari_match and "safari" in ua_lower:
        result["browser_name"] = "Safari"
        result["browser_version"] = safari_match.group(1)
    elif "msie" in ua_lower or "trident" in ua_lower:
        result["browser_name"] = "Internet Explorer"
        ie_match = re.search(r"msie (\d+(\.\d+)?)", ua_lower) or re.search(r"rv:(\d+(\.\d+)?)", ua_lower)
        if ie_match:
            result["browser_version"] = ie_match.group(1)
    
    # OS detection
    if "windows" in ua_lower:
        result["os_name"] = "Windows"
        win_version_match = re.search(r"windows nt (\d+\.?\d*)", ua_lower)
        if win_version_match:
            nt_version = win_version_match.group(1)
            version_map = {
                "10.0": "10",
                "6.3": "8.1",
                "6.2": "8",
                "6.1": "7",
                "6.0": "Vista",
                "5.2": "XP",
                "5.1": "XP",
                "5.0": "2000"
            }
            result["os_version"] = version_map.get(nt_version, nt_version)
    elif "macintosh" in ua_lower or "mac os x" in ua_lower:
        result["os_name"] = "macOS"
        mac_version_match = re.search(r"mac os x (\d+[._]\d+([._]\d+)?)", ua_lower)
        if mac_version_match:
            result["os_version"] = mac_version_match.group(1).replace("_", ".")
    elif "android" in ua_lower:
        result["os_name"] = "Android"
        android_version_match = re.search(r"android (\d+(\.\d+)?)", ua_lower)
        if android_version_match:
            result["os_version"] = android_version_match.group(1)
    elif "ios" in ua_lower or "iphone" in ua_lower or "ipad" in ua_lower:
        result["os_name"] = "iOS"
        ios_version_match = re.search(r"os (\d+[._]\d+([._]\d+)?)", ua_lower)
        if ios_version_match:
            result["os_version"] = ios_version_match.group(1).replace("_", ".")
    elif "linux" in ua_lower:
        result["os_name"] = "Linux"
    
    return result


def get_browser_icon(browser_name: str) -> Optional[str]:
    """
    Get the icon path for a browser.
    
    Args:
        browser_name: Name of the browser
        
    Returns:
        Path to the browser icon or None
    """
    browser_name = browser_name.lower() if browser_name else ""
    
    icon_map = {
        "chrome": "/static/images/browsers/chrome.png",
        "firefox": "/static/images/browsers/firefox.png",
        "safari": "/static/images/browsers/safari.png",
        "edge": "/static/images/browsers/edge.png",
        "opera": "/static/images/browsers/opera.png",
        "internet explorer": "/static/images/browsers/ie.png"
    }
    
    return icon_map.get(browser_name)


def get_os_icon(os_name: str) -> Optional[str]:
    """
    Get the icon path for an operating system.
    
    Args:
        os_name: Name of the operating system
        
    Returns:
        Path to the OS icon or None
    """
    os_name = os_name.lower() if os_name else ""
    
    icon_map = {
        "windows": "/static/images/os/windows.png",
        "macos": "/static/images/os/macos.png",
        "android": "/static/images/os/android.png",
        "ios": "/static/images/os/ios.png",
        "linux": "/static/images/os/linux.png"
    }
    
    return icon_map.get(os_name)