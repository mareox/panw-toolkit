"""
Utility functions for Panorama Cloud API
"""


def build_panorama_base_url(panorama_region: str) -> str:
    """
    Build Panorama Cloud API base URL with smart region detection.

    Supports two formats:
    1. Short identifier (e.g., "paas-5")
       → Constructs: https://paas-5.prod.panorama.paloaltonetworks.com

    2. Full domain (e.g., "paas-1.prod.sg.panorama.paloaltonetworks.com")
       → Uses as-is: https://paas-1.prod.sg.panorama.paloaltonetworks.com

    Args:
        panorama_region: Either short identifier or full domain

    Returns:
        Full base URL for Panorama Cloud API

    Examples:
        >>> build_panorama_base_url("paas-5")
        'https://paas-5.prod.panorama.paloaltonetworks.com'

        >>> build_panorama_base_url("paas-1.prod.sg.panorama.paloaltonetworks.com")
        'https://paas-1.prod.sg.panorama.paloaltonetworks.com'
    """
    if not panorama_region:
        raise ValueError("panorama_region cannot be empty")

    # Smart detection: if contains a dot, it's a full domain
    if '.' in panorama_region:
        # Full domain provided (e.g., "paas-1.prod.sg.panorama.paloaltonetworks.com")
        return f"https://{panorama_region}"
    else:
        # Short identifier provided (e.g., "paas-5")
        # Construct standard domain pattern
        return f"https://{panorama_region}.prod.panorama.paloaltonetworks.com"
