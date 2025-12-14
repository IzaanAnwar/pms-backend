from cuid2 import Cuid


_CUID_GENERATOR = Cuid(length=24)


def generate_cuid() -> str:
    return _CUID_GENERATOR.generate()
