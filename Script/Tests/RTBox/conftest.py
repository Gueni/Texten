from __future__ import annotations

import sys
from pathlib import Path

# The RT Box tests import it as `from RT_Box import RT_Box`, so make sure
# Lib/ is on sys.path before either test module is collected.
_LIB_DIR = Path(__file__).resolve().parents[2] / "Lib"
if str(_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(_LIB_DIR))
