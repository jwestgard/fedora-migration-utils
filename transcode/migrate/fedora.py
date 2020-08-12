import os

class FedoraObject:
    """Parent class for all digital collections objects; it provides a registry
        to ensure uniqueness of PIDs across the collection as well as lookup via
        PID"""

    _registry = {}

    @classmethod
    def from_registry(cls, **kwargs):
        """Returns the object with the supplied pid or creates and registers a 
            new object if none exists with the supplied pid"""
        pid = kwargs['pid']
        if pid not in cls._registry:
            cls._registry[pid] = cls(**kwargs)
        return cls._registry[pid]

    def __init__(self, pid):
        self.pid = pid
        self.pathsafe_pid = self.pid.replace(":", "_")

    def __lt__(self, other):
        return int(self.pid[4:]) < int(other.pid[4:]) 

    def __repr__(self):
        return f"<{self.type} object PID={self.pid}>"


class Umdm(FedoraObject):
    """Class representing an item-level digital collections object;
        described by University of Maryland Descriptive Metadata (UMDM)"""

    def __init__(self, pid, collection):
        super().__init__(pid)
        self.type = "UMDM"
        self.collection = collection
        self.parts = set()

    def add_part(self, umam):
        self.parts.add(umam)

    def tree_view(self):
        print(self)
        for n, part in enumerate(sorted(self.parts), 1):
            print(f"  ({n}) {part.identifier}")
            for asset in sorted(part.assets):
                print(f"      - {asset.filename} ({asset.role:>6}): {asset.md5}")

    def is_well_formed(self):
        return all([part.has_unambiguous_representation_set() for part in self.parts])


class Umam(FedoraObject):
    """Class representing one part of an item-level object;
        described by University of Maryland Administrative Metadata (UMAM)"""

    def __init__(self, pid, identifier):
        super().__init__(pid)
        self.type = "UMAM"
        self.identifier = identifier
        self.assets = set()

    def add_asset(self, file):
        self.assets.add(file)

    def has_unambiguous_representation_set(self):
        for role in ["master", "access"]:
            all_role_versions = [asset for asset in self.assets if asset.role == role]
            if len(set([asset.md5 for asset in all_role_versions])) > 1:
                return False
        return True

    def has_access_version(self):
        return any([asset.role == "access" for asset in self.assets])

    def has_master_version(self):
        return any([asset.role == "master" for asset in self.assets])


class DigitalAsset:
    """Class representing a single digital asset (file) under management"""

    master_formats = ['mov', 'wav']
    access_formats = ['mp4', 'mp3']

    def __init__(self, filename, bytes=None, path=None, md5=None, ext=None):
        self.filename = filename
        self.basename, self.ext = os.path.splitext(self.filename)
        self.bytes = bytes
        self.md5 = md5
        self.ext = ext
        self.path = path
        if self.ext in DigitalAsset.master_formats:
            self.role = "master"
        elif self.ext in DigitalAsset.access_formats:
            self.role = "access"
        else:
            self.role = "other"

    def __lt__(self, other):
        return self.filename < other.filename
