"""
NetArchitect Error Hierarchy
Custom exceptions for physical media violations, address exhaustion,
optical/latency budgets, resiliency, and parameter validation.
"""

class NetArchitectError(Exception):
    """Base exception for all NetArchitect domain errors."""
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        return self.message


class PhysicalDistanceViolationError(NetArchitectError):
    """
    Raised when a physical link exceeds the transmission distance limits
    of the selected or forced media (e.g. Cat6a copper > 100m, OM4 MMF > 400m).
    """
    pass


class AddressSpaceExhaustedError(NetArchitectError):
    """
    Raised when requested subnet allocations exceed the capacity of the root prefix.
    Includes remaining capacity and requested capacity details.
    """
    def __init__(self, message: str, remaining_hosts: int = 0, requested_hosts: int = 0, details: dict | None = None):
        d = details or {}
        d.update({"remaining_hosts": remaining_hosts, "requested_hosts": requested_hosts})
        super().__init__(message, details=d)
        self.remaining_hosts = remaining_hosts
        self.requested_hosts = requested_hosts


class OpticalBudgetError(NetArchitectError):
    """
    Raised when optical span attenuation exceeds the transceiver power budget,
    resulting in a negative power margin.
    """
    def __init__(self, message: str, loss_db: float = 0.0, budget_db: float = 0.0, margin_db: float = 0.0, details: dict | None = None):
        d = details or {}
        d.update({"loss_db": loss_db, "budget_db": budget_db, "margin_db": margin_db})
        super().__init__(message, details=d)
        self.loss_db = loss_db
        self.budget_db = budget_db
        self.margin_db = margin_db


class LatencyBudgetError(NetArchitectError):
    """
    Raised when path latency exceeds the design budget (e.g. 5 ms in Metro MAN).
    """
    def __init__(self, message: str, measured_latency_us: float = 0.0, budget_latency_us: float = 0.0, details: dict | None = None):
        d = details or {}
        d.update({"measured_latency_us": measured_latency_us, "budget_latency_us": budget_latency_us})
        super().__init__(message, details=d)
        self.measured_latency_us = measured_latency_us
        self.budget_latency_us = budget_latency_us


class ResiliencyViolationError(NetArchitectError):
    """
    Raised when a network topology becomes disconnected upon single link failure (N-1 redundancy failure).
    """
    pass


class InvalidParameterError(NetArchitectError):
    """
    Raised when custom parameters fail validation (e.g. invalid CIDR, host bits set,
    disallowed VLAN IDs, negative distances, duplicate device/VLAN names).
    """
    pass
