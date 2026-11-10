"""Import shim for ANGELA v8.1.2.

The v8.1.2 sources ship as flat modules in this directory, but parts of the code
import them as ``modules.<name>`` (for example ``from modules import meta_cognition``
or ``from modules.simulation_core import SimulationCore``). This package makes
both spellings resolve to the same flat module object.

Resolution is lazy, so modules that import each other do not deadlock when the
package is first imported.
"""
from __future__ import annotations

import importlib
import importlib.abc
import importlib.util
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent.parent
FLAT_MODULES = frozenset(
    path.stem for path in _HERE.glob("*.py") if path.stem not in {"__init__", "angela", "index"}
)


class _AliasFinder(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    prefix = __name__ + "."

    def find_spec(self, fullname, path, target=None):
        if fullname.startswith(self.prefix) and fullname[len(self.prefix):] in FLAT_MODULES:
            return importlib.util.spec_from_loader(fullname, self)
        return None

    def create_module(self, spec):
        return importlib.import_module(spec.name[len(self.prefix):])

    def exec_module(self, module):
        return None


if not any(isinstance(finder, _AliasFinder) for finder in sys.meta_path):
    sys.meta_path.insert(0, _AliasFinder())


def __getattr__(name: str):
    if name in FLAT_MODULES:
        return importlib.import_module(name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
