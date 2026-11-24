"""The storage device base classes.

``storage.py`` defines StorageDevice and its subclasses. The ``storage`` package shadows that file (``import
setupimagebbs.storage`` is the package), so this module loads ``storage.py`` by its path and exposes the base classes to
the package's own device modules (cbm.py, ltk.py).
"""

import importlib.util
import pathlib
import sys

_PATH = pathlib.Path(__file__).resolve().parent.parent / "storage.py"
_NAME = "setupimagebbs._storage_model"

if _NAME in sys.modules:
    _model = sys.modules[_NAME]
else:
    _spec = importlib.util.spec_from_file_location(_NAME, _PATH)
    _model = importlib.util.module_from_spec(_spec)
    sys.modules[_NAME] = _model
    _spec.loader.exec_module(_model)

StorageDevice = _model.StorageDevice
