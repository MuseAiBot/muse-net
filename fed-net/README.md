# FED-NET Share

FED-NET is the sharing layer owned by MuseAi-FED-NET. The gateway is **closed by default**.

- `gateway.json` must explicitly enable a listen port, allowlist entries, forwarding rules, and a nonzero per-guest bandwidth cap before sharing can open.
- Guest identities require an exact match in `allowlist`; an identity not listed is denied.
- Forwarding is deny-by-default: only an exact protocol and listen-port rule is eligible.
- `per_guest_kbps` and `burst_kb` are enforced by the policy layer; zero keeps sharing disabled.
- This directory contains policy and validation only. A platform-specific enforcement engine must call `GatewayPolicy.admit_guest()` and `forwarding_rule()` before opening sockets or applying OS forwarding rules.

The phone connection is the upstream pipe. It is not the FED-NET product and must not be treated as proof that sharing is open.
