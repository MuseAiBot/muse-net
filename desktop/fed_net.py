"""FED-NET sharing policy.

This module owns the Share job. It deliberately has no socket, firewall, or
Windows side effects: a separate enforcement engine must call these checks
before admitting or forwarding any guest traffic.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import json
import time
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ForwardRule:
    name: str
    protocol: str
    listen_port: int
    target_host: str
    target_port: int

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "ForwardRule":
        return cls(
            name=str(raw.get("name", "")),
            protocol=str(raw.get("protocol", "")).lower(),
            listen_port=int(raw.get("listen_port", 0)),
            target_host=str(raw.get("target_host", "")),
            target_port=int(raw.get("target_port", 0)),
        )

    def valid(self) -> bool:
        return (
            bool(self.name)
            and self.protocol in {"tcp", "udp"}
            and 1 <= self.listen_port <= 65535
            and bool(self.target_host)
            and 1 <= self.target_port <= 65535
        )


@dataclass
class GatewayPolicy:
    bind_address: str = "127.0.0.1"
    bind_port: int = 0
    allowlist: set[str] = field(default_factory=set)
    forwarding: list[ForwardRule] = field(default_factory=list)
    per_guest_kbps: int = 0
    burst_kb: int = 0
    logging_enabled: bool = True
    log_file: str = "fed-net.log"

    @classmethod
    def load(cls, path: str | Path) -> "GatewayPolicy":
        with Path(path).open("r", encoding="utf-8") as handle:
            raw = json.load(handle)
        bandwidth = raw.get("bandwidth", {})
        logging_config = raw.get("logging", {})
        return cls(
            bind_address=str(raw.get("bind_address", "127.0.0.1")),
            bind_port=int(raw.get("bind_port", 0)),
            allowlist={str(item) for item in raw.get("allowlist", [])},
            forwarding=[ForwardRule.from_dict(item) for item in raw.get("forwarding", [])],
            per_guest_kbps=int(bandwidth.get("per_guest_kbps", 0)),
            burst_kb=int(bandwidth.get("burst_kb", 0)),
            logging_enabled=bool(logging_config.get("enabled", True)),
            log_file=str(logging_config.get("file", "fed-net.log")),
        )

    @property
    def share_enabled(self) -> bool:
        """Return true only when every required sharing control is explicit."""
        return (
            self.bind_port > 0
            and bool(self.allowlist)
            and bool(self.forwarding)
            and self.per_guest_kbps > 0
            and all(rule.valid() for rule in self.forwarding)
        )

    def status(self) -> str:
        return "OPEN-CONFIGURED" if self.share_enabled else "CLOSED-BY-DEFAULT"

    def admit_guest(self, identity: str) -> bool:
        """Exact-match admission; an identity absent from the list is denied."""
        return self.share_enabled and identity in self.allowlist

    def forwarding_rule(self, protocol: str, listen_port: int) -> ForwardRule | None:
        protocol = protocol.lower()
        for rule in self.forwarding:
            if rule.protocol == protocol and rule.listen_port == listen_port and rule.valid():
                return rule
        return None

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not 0 <= self.bind_port <= 65535:
            errors.append("bind_port must be between 0 and 65535")
        if self.per_guest_kbps < 0 or self.burst_kb < 0:
            errors.append("bandwidth values cannot be negative")
        for rule in self.forwarding:
            if not rule.valid():
                errors.append(f"invalid forwarding rule: {rule.name or '<unnamed>'}")
        return errors


class GuestRateLimiter:
    """Small token bucket used by an enforcement engine for one guest."""

    def __init__(self, kilobits_per_second: int, burst_kilobytes: int = 0) -> None:
        if kilobits_per_second <= 0:
            raise ValueError("kilobits_per_second must be positive")
        self.rate_bytes = kilobits_per_second * 1000 / 8
        self.capacity = max(self.rate_bytes, burst_kilobytes * 1024)
        self.tokens = self.capacity
        self.updated = time.monotonic()

    def allow(self, byte_count: int) -> bool:
        if byte_count < 0:
            raise ValueError("byte_count cannot be negative")
        now = time.monotonic()
        self.tokens = min(self.capacity, self.tokens + (now - self.updated) * self.rate_bytes)
        self.updated = now
        if byte_count > self.tokens:
            return False
        self.tokens -= byte_count
        return True
