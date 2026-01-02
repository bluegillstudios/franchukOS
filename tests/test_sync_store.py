import os
import tempfile
from crypto.sync import SyncStore


def test_sync_store_set_get_delete(tmp_path):
    path = tmp_path / 'store.bin'
    s = SyncStore(str(path), 'testpass')
    s.set('k', {'v': 1})
    assert s.get('k') == {'v': 1}
    s.delete('k')
    assert s.get('k') is None
