#!/usr/bin/env python3
import sys
from pathlib import Path
from collections import OrderedDict
import unittest

thisFile = Path(__file__).absolute()
thisDir = thisFile.parent.absolute()
repoMainDir = thisDir.parent.absolute()
sys.path.insert(0, str(repoMainDir))

dict = OrderedDict

from AnyVer import AnyVer
from PackageRef import BasePackageRef, PackageRef, VersionedPackageRef

class SimpleTests(unittest.TestCase):
	def testOperation1(self):
		v = VersionedPackageRef("sqlite", arch="amd64", version=AnyVer("3.29.0"), versionPostfix=1)
		v.versionPostfix.count = 1
		self.assertEqual(v.toName(), "sqlite3")
		v.versionPostfix.count = 2
		self.assertEqual(v.toName(), "sqlite3.29")

	def testOperation2(self):
		v = VersionedPackageRef("lib3ds", arch="amd64", version=AnyVer("1.3.0"), versionPostfix="-{0}-{1}")
		self.assertEqual(v.toName(), "lib3ds-1-3")

	def testCloningAndHashability(self):
		v1 = VersionedPackageRef("sqlite", arch="amd64", version=AnyVer("3.29.0"))
		v2 = v1.clone()
		self.assertEqual(v1, v2)
		d = {v1: 1}
		d[v2]

	vRef = VersionedPackageRef("sqlite", arch="amd64", version=AnyVer("3.29.0"))
	jRef = PackageRef("sqlite", arch="amd64")
	bRef = BasePackageRef("sqlite", arch="amd64")

	def testUpgradeClone(self):
		self.assertEqual(self.__class__.jRef.clone(cls=self.__class__.vRef.__class__, version=self.__class__.vRef.version), self.__class__.vRef)

	def testDowngradeClone(self):
		self.assertEqual(self.__class__.vRef.clone(cls=self.__class__.jRef.__class__), self.__class__.jRef)

	def testDowngrade(self):
		self.assertEqual(self.__class__.vRef.downgrade(), self.__class__.jRef)
		self.assertEqual(self.__class__.jRef.downgrade(), self.__class__.bRef)



if __name__ == "__main__":
	unittest.main()
