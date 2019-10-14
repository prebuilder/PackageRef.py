__all__ = ("PackageRef", "PackageRef", "VersionedPackageRef")
import typing
import inspect


class IncompatibleVersionPostfix:
	__slots__ = ()

	def __call__(self, ver: "BasePackageRef"):
		raise NotImplementedError


class IncompatibleVersionPostfixDot(IncompatibleVersionPostfix):
	__slots__ = ("count",)

	def __init__(self, count: int) -> None:
		self.count = count

	def __call__(self, ver: "BasePackageRef") -> str:
		return ".".join(map(str, ver[: self.count]))


class IncompatibleVersionPostfixFormat(IncompatibleVersionPostfix):
	__slots__ = ("format",)

	def __init__(self, format: str) -> None:
		self.format = format

	def __call__(self, ver: "BasePackageRef") -> str:
		return self.format.format(*ver)


versionsPostfixesTypesMapping = {
	int: IncompatibleVersionPostfixDot,
	str: IncompatibleVersionPostfixFormat
}

BasePackageRefT = typing.Type["BasePackageRef"]


class BasePackageRef:
	__slots__ = ("name", "arch", "versionPostfix")

	def __init__(self, name: str, arch: str = "amd64", versionPostfix: typing.Union[str, int, callable, IncompatibleVersionPostfix] = None) -> None:
		self.name = name
		self.arch = arch

		argType = type(versionPostfix)
		if argType in versionsPostfixesTypesMapping:
			versionPostfix = versionsPostfixesTypesMapping[argType](versionPostfix)
		self.versionPostfix = versionPostfix

	_reprOrder = ("name", "arch")

	def _metadataInnerReprStr(self):
		return ", ".join(vn + "=" + repr(getattr(self, vn)) for vn in self.__class__._reprOrder)

	def asTuple(self) -> typing.Tuple[str, str]:
		return (self.name, self.arch)

	def recreatorFull(self, cls: BasePackageRefT) -> typing.Mapping[str, typing.Any]:
		s = inspect.signature(cls.__init__)
		dic = {}
		pIter = iter(s.parameters.values())
		selfArg = next(pIter)
		assert selfArg.name == "self"

		for p in pIter:
			n = p.name
			dic[n] = getattr(self, n)
		return dic

	def downgrade(self) -> "BasePackageRef":
		mro = self.__class__.mro()
		cls = mro[1]
		assert issubclass(cls, __class__), "Cannot downgrade lower than " + __class__.__name__ + " :" + repr(mro)
		return self.clone(cls=cls)

	def clone(self, cls: typing.Optional[BasePackageRefT] = None, **kwargs) -> "BasePackageRef":
		if cls is None:
			cls = self.__class__

		if issubclass(cls, self.__class__):  # upgrade or clone
			k = self.recreatorFull(self.__class__)
		elif issubclass(self.__class__, cls):  # downgrade or clone
			k = self.recreatorFull(cls)
		else:
			raise ValueError("Only upgrades, downgrades and clones are allowed")

		k.update(kwargs)
		res = cls(**k)
		return res

	def __hash__(self) -> int:
		return hash(self.asTuple())

	def __eq__(self, other: "BasePackageRef") -> bool:
		return isinstance(other, __class__) and self.asTuple() == other.asTuple()

	def __repr__(self) -> str:
		return self.__class__.__name__ + "(" + self._metadataInnerReprStr() + ",...)"

	def toPath(self):
		return "_".join(str(el) for el in self.asTuple()).replace("/", "_").replace("\\", "_")

	def toName(self) -> str:
		return self.name

	def __str__(self) -> str:
		return self.toName() + (":" + self.arch if self.arch is not None else "")


class PackageRef(BasePackageRef):
	"""A reference to a package. Used to identify a package in a system installed package manager. It is an incomplete class without version"""

	__slots__ = ("group",)

	def __init__(self, name: str, arch: str = "amd64", group: typing.Optional[str] = None, versionPostfix: int = 0) -> None:
		super().__init__(name=name, arch=arch, versionPostfix=versionPostfix)
		self.group = group

	_reprOrder = ("name", "group", "arch")

	def asTuple(self) -> typing.Tuple[str, str, str]:
		return (self.name, self.arch, self.group)

	def __str__(self) -> str:
		return (str(self.group) + "@" if self.group is not None else "") + super().__str__()


try:
	from AnyVer import AnyVer, _AnyVer

	class VersionedPackageRef(PackageRef):
		"""A reference to a package. Used to identify a package in a system installed package manager. Also used to identify a package globally"""

		__slots__ = ("_version",)

		def __init__(self, name: str, arch: str = "amd64", group: typing.Optional[str] = None, version: typing.Optional[typing.Union[str, _AnyVer]] = None, versionPostfix: int = 0) -> None:
			super().__init__(name, arch=arch, group=group, versionPostfix=versionPostfix)
			assert version is not None
			if isinstance(version, str):
				version = AnyVer(version)
			self.version = version

		@property
		def version(self):
			return self._version

		@version.setter
		def version(self, version: typing.Optional[typing.Union[str, _AnyVer]]):
			if version is not None:
				version = AnyVer(version)

			self._version = version

		def asTuple(self) -> typing.Tuple[str, str, str, _AnyVer]:
			return super().asTuple() + (self.version,)

		_reprOrder = PackageRef._reprOrder + ("version",)

		def toName(self) -> str:
			return super().toName() + (self.versionPostfix(self.version) if self.versionPostfix else "")

		def __str__(self) -> str:
			return super().__str__() + " " + str(self.version)


except ImportError:
	warnings.warn("`AnyVer` is not present, so " + VersionedPackageRef.__name__ + " is not available")
