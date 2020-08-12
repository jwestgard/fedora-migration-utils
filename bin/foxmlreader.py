#!/usr/bin/env python3

import sys
from io import StringIO, BytesIO
import lxml.etree as ET

FOXML = "{info:fedora/fedora-system:def/foxml#}"

class FedoraObject:

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return f"<FedoraObject pid={self.pid}>"

    @classmethod
    def from_foxml(cls, path):
        tree = ET.parse(path)
        root = tree.getroot()
        print(root.nsmap)
        pid = root.get('PID')
        for elem in root.find('.//{FOXML}objectProperties'):
            if elem.get('NAME') == 'info:fedora/fedora-system:def/model#contentModel':
                self.content_model = elem.get('VALUE')
        return cls(tree=tree, pid=pid)


def main():

    for path in sys.argv[1:]:
        obj = FedoraObject.from_foxml(path)
        print(obj)


if __name__ == "__main__":
    main()