# MuseAi-FED-NET

MuseAi-FED-NET is the operator and sharing policy for FedNet. The Android connection is only the upstream pipe. It is not the product, and a working pipe must never imply that guest sharing is enabled.

## Three jobs

**Start** brings the upstream connection up and proves real internet reachability. **Watchdog** observes the connection and performs bounded recovery. **Share** is separate: it keeps the gateway closed unless the operator explicitly configures a listen port, exact guest identities, forwarding rules, and bandwidth limits.

## Share safety contract

The Share job is implemented by `desktop/fed_net.py` and configured in `fed-net/gateway.json`. The initial configuration is closed: listen port `0`, empty allowlist, empty forwarding rules, and zero bandwidth. `GatewayPolicy` requires every control to be explicit before it reports `OPEN-CONFIGURED`. It performs exact-match guest admission and exact forwarding-rule lookup. `GuestRateLimiter` provides the per-guest token-bucket enforcement primitive.

This policy layer does not open sockets or change Windows firewall rules. A platform enforcement engine must call it before doing either. That separation prevents a phone connection or a dashboard demo from accidentally opening a gateway.

## Live-test boundary

Live proof still requires the Windows PC, connected Android phone, administrator access, and the required virtual adapter. The sandbox can run policy tests but cannot live-test the connection or guest forwarding.
