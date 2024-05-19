import modal

from .utils import to_fake

mount = modal.Mount.from_local_python_packages("common")


__all__ = ["to_fake", "to_real", "mount"]
