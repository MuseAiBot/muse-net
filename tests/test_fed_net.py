import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "desktop"))
from fed_net import ForwardRule, GatewayPolicy, GuestRateLimiter


class FedNetPolicyTests(unittest.TestCase):
    def test_default_gateway_is_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "gateway.json"
            path.write_text(json.dumps({
                "bind_address": "127.0.0.1",
                "bind_port": 0,
                "allowlist": [],
                "forwarding": [],
                "bandwidth": {"per_guest_kbps": 0, "burst_kb": 0},
            }), encoding="utf-8")
            policy = GatewayPolicy.load(path)
        self.assertFalse(policy.share_enabled)
        self.assertEqual(policy.status(), "CLOSED-BY-DEFAULT")
        self.assertFalse(policy.admit_guest("guest-1"))

    def test_exact_allowlist_and_forwarding_rule(self):
        policy = GatewayPolicy(
            bind_port=9000,
            allowlist={"guest-1"},
            forwarding=[ForwardRule("web", "tcp", 8080, "example.internal", 80)],
            per_guest_kbps=128,
        )
        self.assertTrue(policy.share_enabled)
        self.assertTrue(policy.admit_guest("guest-1"))
        self.assertFalse(policy.admit_guest("guest-10"))
        self.assertIsNotNone(policy.forwarding_rule("TCP", 8080))
        self.assertIsNone(policy.forwarding_rule("tcp", 8081))

    def test_rate_limiter_rejects_over_budget(self):
        limiter = GuestRateLimiter(8, burst_kilobytes=1)
        self.assertTrue(limiter.allow(1024))
        self.assertFalse(limiter.allow(1))


if __name__ == "__main__":
    unittest.main()
