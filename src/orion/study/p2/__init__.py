"""ORION-P2 open-world discovery study harness (issue #99).

Package boundary rule: nothing here may read `DiscoveryTask.protected_gold`
except `gold`. Systems under test receive a `PublicView` and a host-owned
`DiscoverySession`; they never receive the task, the world or the gold.

This package is deliberately system-free. The world is frozen before any
system is configured against it, so no system can be tuned to the gold.
"""
