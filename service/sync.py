"""Compatibility shim: service.sync re-exports the implementation from `crypto.sync`.
This keeps older imports working while we move the implementation into `crypto`.
"""
from crypto.sync import SyncStore

__all__ = ["SyncStore"]

