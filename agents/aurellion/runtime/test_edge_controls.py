import unittest
from origin_policy import ExactOriginPolicy, OriginDenied
from rate_limiter import RedisSlidingWindowRateLimiter, RateLimitConfigurationError

class FakeRedis:
    def __init__(self):
        self.calls = []
    def eval(self, script, numkeys, key, window_ms, limit, request_id):
        self.calls.append((script, numkeys, key, window_ms, limit, request_id))
        return [1, 1]

class OriginPolicyTests(unittest.TestCase):
    def test_exact_https_origin_is_allowed(self):
        policy = ExactOriginPolicy({"https://staging.scrollverse.co"})
        self.assertEqual(policy.require("https://staging.scrollverse.co"), "https://staging.scrollverse.co")

    def test_wildcard_or_unapproved_origin_is_denied(self):
        with self.assertRaises(ValueError):
            ExactOriginPolicy({"https://*.scrollverse.co"})
        policy = ExactOriginPolicy({"https://staging.scrollverse.co"})
        with self.assertRaises(OriginDenied):
            policy.require("https://attacker.example")

class RateLimiterTests(unittest.TestCase):
    def test_uses_atomic_shared_redis_script_and_hashed_subject(self):
        client = FakeRedis()
        limiter = RedisSlidingWindowRateLimiter(
            client, redis_url="rediss://redis.example.test:6379",
            pepper="p" * 40, namespace="visitor",
        )
        decision = limiter.check("visitor-ip-address", limit=20, window_seconds=60)
        self.assertTrue(decision.allowed)
        self.assertEqual(client.calls[0][3], 60000)
        self.assertNotIn("visitor-ip-address", client.calls[0][2])

    def test_plaintext_redis_is_rejected(self):
        with self.assertRaises(RateLimitConfigurationError):
            RedisSlidingWindowRateLimiter(FakeRedis(), redis_url="redis://localhost:6379", pepper="p" * 40)

if __name__ == "__main__":
    unittest.main()
