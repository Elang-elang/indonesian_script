# ==================== utils.py ====================
# Tidak diubah, sudah benar
class Object:
    def __init__(self, hex=False):
        self.keys = []
        self.values = []
        self.repr = []
        self.hex = True if hex else False

    def set(self, key, value):
        if self.hex:
            key = hex(id(key))
        self.keys.append(key)
        self.values.append(value)
        self.repr.append(f"{key}: {value}")

    def get(self, key, default=None):
        if key in self.keys:
            idx = self.keys.index(key)
            return self.values[idx]
        return default

    def has(self, key):
        return key in self.keys

    def delete(self, key):
        if key in self.keys:
            idx = self.keys.index(key)
            self.keys.pop(idx)
            return self.values.pop(idx)
        return None

    def items(self):
        return list(zip(self.keys, self.values))

    def __repr__(self):
        if self.items():
            return f"Object({{{', '.join(f'{k}: {v}' for k, v in self.items())}}})"
        return "Object({})"