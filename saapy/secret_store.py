from cryptography.fernet import Fernet, MultiFernet
import yaml
from datetime import datetime, timezone


class SecretStore:
    def __init__(self, *master_keys, encrypted_store: dict = None):
        if not len(master_keys):
            raise ValueError('at least one master key must be passed')
        self.crypt = MultiFernet([Fernet(key) for key in master_keys])
        if not encrypted_store:
            self.encrypted_store = dict()
        else:
            self.encrypted_store = encrypted_store

    @staticmethod
    def generate_master_key():
        return Fernet.generate_key()

    @staticmethod
    def add_master_key(key_yaml_path):
        master_key = SecretStore.generate_master_key()
        try:
            master_keys = SecretStore._load_keys(key_yaml_path)
        except OSError:
            master_keys = []
        master_keys = [master_key] + master_keys
        SecretStore._save_as_yaml(key_yaml_path, 'keys', master_keys)
        return master_keys

    @staticmethod
    def _load_keys(key_yaml_path):
        with open(key_yaml_path, 'r') as key_file:
            master_keys = yaml.load(key_file)['keys']
            return master_keys

    @classmethod
    def load_from_yaml(cls, key_yaml_path, store_yaml_path=None, encrypted=True):
        master_keys = SecretStore._load_keys(key_yaml_path)
        secret_store = cls(*master_keys)
        if store_yaml_path:
            secret_store.load_as_yaml(store_yaml_path, encrypted=encrypted)
        return secret_store

    def encrypt_copy(self, plain_store, *path):
        for key in plain_store:
            value = plain_store[key]
            if isinstance(value, bytes) or isinstance(value, str):
                self.set_secret(value, *path, key)
            else:
                self.encrypt_copy(value, *(list(path) + [key]))

    def set_secret(self, secret, *path):
        if not len(path):
            raise ValueError('path to secret must not be empty')
        if not (isinstance(secret, bytes) or isinstance(secret, str)):
            raise ValueError(
                'secret must be bytes or str, but {0} is passed'.format(
                    type(secret)))
        if isinstance(secret, str):
            secret = secret.encode('utf-8')
        encrypted_secret = self.crypt.encrypt(secret)
        store = self.encrypted_store
        for key in path[:-1]:
            store = store.setdefault(key, dict())
        store[path[-1]] = encrypted_secret

    def get_secret(self, *path):
        encrypted_secret = self.get_encrypted_secret(*path)
        return self.crypt.decrypt(encrypted_secret)

    def delete_secret(self, *path):
        if not len(path):
            raise ValueError('path to secret must not be empty')
        store = self.encrypted_store
        for key in path[:-1]:
            store = store[key]
        del store[path[-1]]

    def get_encrypted_secret(self, *path):
        if not len(path):
            raise ValueError('path to secret must not be empty')
        store = self.encrypted_store
        for key in path[:-1]:
            store = store[key]
        encrypted_secret = store[path[-1]]
        return encrypted_secret

    def load_as_yaml(self, yaml_path, encrypted=True):
        with open(yaml_path, 'r') as secret_file:
            secret_storage = yaml.load(secret_file)
            if encrypted:
                self.encrypted_store = secret_storage['encrypted_store']
            else:
                self.encrypt_copy(secret_storage['encrypted_store'])

    def save_as_yaml(self, yaml_path):
        SecretStore._save_as_yaml(yaml_path, 'encrypted_store', self.encrypted_store)

    def print_as_yaml(self):
        print(yaml.dump(self.encrypted_store, default_flow_style=False))

    @staticmethod
    def _wrap_payload(payload_key, payload):
        now = datetime.now()
        timestamp = now.replace(tzinfo=timezone.utc).timestamp()
        wrapper = {
            'meta': {
                'method': 'fernet',
                'timestamp': timestamp,
                'timezone': 'utc'
            },
            payload_key: payload
        }
        return wrapper

    @staticmethod
    def _save_as_yaml(yaml_path, payload_key, payload):
        content = SecretStore._wrap_payload(payload_key, payload)
        with open(yaml_path, 'w') as yaml_file:
            yaml.dump(content, yaml_file, default_flow_style=False)
