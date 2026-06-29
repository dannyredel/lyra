"""Snapshot serving layer.

Static-replay first (D-01): ``serving/export.py`` produces the JSON snapshots the frontend reads
(`frontend/public/data/`). A live FastAPI adapter over the same snapshots is a Phase-2 option.
"""
