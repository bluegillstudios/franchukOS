# Copyright 2025 the FranchukOS project authors.
# Contributed under the Apache License, Version 2.0.

# Minimal encrypted sync store (local-only MVP)
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import base64
import json
import os
from typing import Any

class SyncStore:
    """Simple file-backed encrypted store using a passphrase-derived Fernet key.

    This is an MVP local store. Later we can add push/pull to a remote server.
    """

    def __init__(self, path: str, passphrase: str, iterations: int = 390000):
        self.path = path
        self.passphrase = passphrase.encode('utf-8')
        self.iterations = iterations
        # per-store random salt persisted to <store>.salt
        self._salt_path = f"{self.path}.salt"
        self.salt = self._load_or_create_salt()
        self._fernet = self._derive_fernet(self.passphrase, iterations, self.salt)
        # ensure file exists
        if not os.path.exists(self.path):
            self._write_encrypted({})

    def _derive_fernet(self, passphrase: bytes, iterations: int, salt: bytes) -> Fernet:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=iterations,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(passphrase))
        return Fernet(key)

    def _load_or_create_salt(self) -> bytes:
        """Load the salt from disk or create and persist a new random salt (16 bytes)."""
        try:
            if os.path.exists(self._salt_path):
                with open(self._salt_path, 'rb') as f:
                    return f.read()
        except Exception:
            # If reading fails, fall through and create a new salt
            pass
        s = os.urandom(16)
        try:
            with open(self._salt_path, 'wb') as f:
                f.write(s)
        except Exception:
            # If writing salt fails, still return the generated salt (non-persistent)
            pass
        return s

    def _read_encrypted(self) -> dict:
        with open(self.path, 'rb') as f:
            token = f.read()
            if not token:
                return {}
            try:
                dec = self._fernet.decrypt(token)
                return json.loads(dec.decode('utf-8'))
            except Exception:
                return {}

    def _write_encrypted(self, data: dict):
        payload = json.dumps(data).encode('utf-8')
        token = self._fernet.encrypt(payload)
        with open(self.path, 'wb') as f:
            f.write(token)

    def get(self, key: str, default: Any=None) -> Any:
        data = self._read_encrypted()
        return data.get(key, default)

    def set(self, key: str, value: Any):
        data = self._read_encrypted()
        data[key] = value
        self._write_encrypted(data)

    def delete(self, key: str):
        data = self._read_encrypted()
        if key in data:
            del data[key]
            self._write_encrypted(data)
