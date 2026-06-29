"""Vega simulation engine.

The engine runs the marketplace and emits an append-only event log (see ``EVENT_LOG.md``).
It must NOT compute experiment results — that is the inference layer's job. The only output
is the event log under ``events/``.

Layer boundary: engine → event log. The engine knows nothing about metrics, inference, or
the dashboard.
"""
