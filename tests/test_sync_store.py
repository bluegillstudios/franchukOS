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


def test_salt_created_and_persisted(tmp_path):
    path = tmp_path / 'store.bin'
    s1 = SyncStore(str(path), 'testpass')
    salt_path = str(path) + '.salt'
    assert os.path.exists(salt_path)
    with open(salt_path, 'rb') as f:
        salt1 = f.read()
    # Re-open store and ensure salt didn't change
    s2 = SyncStore(str(path), 'testpass')
    with open(salt_path, 'rb') as f:
        salt2 = f.read()
    assert salt1 == salt2
