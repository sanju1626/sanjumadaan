"""
NetArchitect IPv4 Bitwise Address Utility
Pure bitwise integer arithmetic (<<, >>, &, |, ~) for IPv4 manipulation.
No standard ipaddress module is used here (reserved strictly for test oracles).
"""

from engine.errors import InvalidParameterError

def ip_to_int(ip_str: str) -> int:
    """Convert dotted-decimal IPv4 string to 32-bit unsigned integer using bitwise shifts."""
    if not isinstance(ip_str, str):
        raise InvalidParameterError(f"IP address must be a string, got {type(ip_str).__name__}")
    parts = ip_str.strip().split(".")
    if len(parts) != 4:
        raise InvalidParameterError(f"Invalid IPv4 format '{ip_str}': exactly 4 octets required")
    val = 0
    for i, p in enumerate(parts):
        if not p.isdigit():
            raise InvalidParameterError(f"Invalid IPv4 octet '{p}' in '{ip_str}': must be numeric")
        num = int(p)
        if num < 0 or num > 255:
            raise InvalidParameterError(f"IPv4 octet '{num}' out of range [0, 255] in '{ip_str}'")
        val = (val << 8) | (num & 0xFF)
    return val & 0xFFFFFFFF


def int_to_ip(ip_int: int) -> str:
    """Convert 32-bit unsigned integer to dotted-decimal IPv4 string using bitwise extraction."""
    ip_int = ip_int & 0xFFFFFFFF
    return f"{(ip_int >> 24) & 0xFF}.{(ip_int >> 16) & 0xFF}.{(ip_int >> 8) & 0xFF}.{ip_int & 0xFF}"


def prefix_to_mask_int(prefix: int) -> int:
    """
    Calculate 32-bit subnet mask integer from prefix length.
    Uses bitwise shift and 32-bit mask: (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF.
    """
    if not isinstance(prefix, int) or prefix < 0 or prefix > 32:
        raise InvalidParameterError(f"Prefix length must be an integer between 0 and 32, got {prefix}")
    if prefix == 0:
        return 0
    return (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF


def prefix_to_wildcard_int(prefix: int) -> int:
    """
    Calculate 32-bit wildcard mask integer from prefix length.
    Bitwise: ~mask & 0xFFFFFFFF.
    """
    mask = prefix_to_mask_int(prefix)
    return (~mask) & 0xFFFFFFFF


def prefix_to_mask_str(prefix: int) -> str:
    """Return dotted-decimal subnet mask string for a prefix."""
    return int_to_ip(prefix_to_mask_int(prefix))


def prefix_to_wildcard_str(prefix: int) -> str:
    """Return dotted-decimal wildcard mask string for a prefix."""
    return int_to_ip(prefix_to_wildcard_int(prefix))


def parse_cidr(cidr_str: str) -> tuple[int, int, str]:
    """
    Parse a CIDR string (e.g. '10.10.0.0/16').
    Returns (network_ip_int, prefix, original_str).
    Validates:
      - Valid format and 4 octets [0-255]
      - Prefix in valid range (1-30 for root subnets)
      - Host bits must be zero for network root: (ip_int & wildcard) == 0.
    """
    if not isinstance(cidr_str, str) or "/" not in cidr_str:
        raise InvalidParameterError(f"CIDR format must be IP/prefix (e.g. '10.10.0.0/16'), got '{cidr_str}'")
    ip_part, prefix_part = cidr_str.strip().split("/", 1)
    ip_int = ip_to_int(ip_part)
    if not prefix_part.isdigit():
        raise InvalidParameterError(f"Invalid prefix length '{prefix_part}' in CIDR '{cidr_str}'")
    prefix = int(prefix_part)
    if prefix < 1 or prefix > 30:
        raise InvalidParameterError(f"Root prefix /{prefix} out of range: must be between /1 and /30")

    mask_int = prefix_to_mask_int(prefix)
    wildcard_int = prefix_to_wildcard_int(prefix)
    if (ip_int & wildcard_int) != 0:
        suggested = int_to_ip(ip_int & mask_int)
        raise InvalidParameterError(
            f"Host bits are set in root CIDR '{cidr_str}'. "
            f"Network base address must have host bits cleared (did you mean {suggested}/{prefix}?)"
        )
    return ip_int, prefix, cidr_str.strip()


def mask_int_to_prefix(mask_int: int) -> int:
    """
    Convert 32-bit mask integer to prefix length (0-32).
    Verifies that the mask is contiguous (no 1s after first 0).
    """
    mask_int = mask_int & 0xFFFFFFFF
    # Check contiguity: (~mask_int + 1) must be a power of 2
    inv = (~mask_int) & 0xFFFFFFFF
    if ((inv + 1) & inv) != 0 and mask_int != 0xFFFFFFFF:
        raise InvalidParameterError(f"Non-contiguous subnet mask: {int_to_ip(mask_int)}")
    # Count set bits
    prefix = bin(mask_int).count("1")
    return prefix
