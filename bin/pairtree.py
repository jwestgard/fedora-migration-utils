#!/usr/bin/env python3

import os
import shutil
import sys

class Foxml:

    def __init__(self, filename):
        self.filename = os.path.basename(filename)
        self.base, self.ext = os.path.splitext(self.filename)
        self.prefix = self.base[:4]
        self.serial = self.base[4:]

    @property
    def pairtree(self):
        pairtree = ''
        for d in ('0' * (6 - len(self.serial))) + self.serial[:-1]:
            pairtree = os.path.join(pairtree, d)
        return os.path.join(pairtree, self.filename)


if __name__ == "__main__":

    sroot = sys.argv[1]
    droot = sys.argv[2]

    for file in os.listdir(sroot):
        origin = os.path.join(sroot, file)
        foxml = Foxml(origin)
        dest = os.path.join(droot, foxml.pairtree)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        print(f"{origin} => {dest}")
        os.rename(origin, dest)
