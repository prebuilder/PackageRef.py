PackageRef.py [![Unlicensed work](https://raw.githubusercontent.com/unlicense/unlicense.org/master/static/favicon.png)](https://unlicense.org/)
=============
![GitLab Build Status](https://gitlab.com/KOLANICH/PackageRef.py/badges/master/pipeline.svg)
![GitLab Coverage](https://gitlab.com/KOLANICH/PackageRef.py/badges/master/coverage.svg)
[![Coveralls Coverage](https://img.shields.io/coveralls/prebuilder/PackageRef.py.svg)](https://coveralls.io/r/prebuilder/PackageRef.py)
[![GitHub Actions](https://github.com/prebuilder/PackageRef.py/workflows/CI/badge.svg)](https://github.com/prebuilder/PackageRef.py/actions/)
[![Libraries.io Status](https://img.shields.io/librariesio/github/prebuilder/PackageRef.py.svg)](https://libraries.io/github/prebuilder/PackageRef.py)

Just represents a reference to a package in a unified way.

Let's call a "string name" a name visible in a package manager, like `sqlite3:amd64`.

* `BasePackageRef` - just a `name` + `arch`itecture. Also stores the object describing how to handle "incompatible" part of version in `versionPostfix`. There is a practice to include some parts of versions into package name to allow simultaneous installation of incompatible versions. You just set the count of these components. In subclasses it is allowed to add a version. But usually you know this count before you know the version, because whether this package uses that trick or not is a matter of convention.

* `PackageRef` - `BasePackageRef` + `group`. Group is the way to name packages. For example in Debian `deb` packages for `python3` begin from `python3-` prefix. Different distros have different conventions. So we store the name and group separately and can transform a "string name" into a `PackageRef` automatically. Doing this is the goal of other packages. This one is only about storing package refs.
* `VersionedPackageRef` - adds a version to a package. When transformed into a "string name", `versionPostfix` will append this count of version components to the end of name. To get `sqlite3` just use `VersionedPackageRef("sqlite", version=AnyVer("3.29.0"), versionPostfix=1)`;

All the stuff is hashable (can be used as a key in `dict`) and clonable (`ref.clone()` returns a clone). It is mutable, but hashable, so just use with care.


All the stuff is upgradeable. You can upgrade `BasePackageRef` to `VersionedPackageRef` using `ref.clone(cls=VersionedPackageRef, version=AnyVer(pkgDepSpc.version))`.

All the stuff is downgradeable. You can downgrade `VersionedPackageRef` to `BasePackageRef` using `ref.clone(cls=BasePackageRef)`.

You can downgrade to the immediate base class using `ref.downgrade`.


Requirements
------------
* [`Python >=3.4`](https://www.python.org/downloads/). [`Python 2` is dead, stop raping its corpse.](https://python3statement.org/) Use `2to3` with manual postprocessing to migrate incompatible code to `3`. It shouldn't take so much time. For unit-testing you need Python 3.6+ or PyPy3 because their `dict` is ordered and deterministic. Python 3 is also semi-dead, 3.7 is the last minor release in 3.
