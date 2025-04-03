import sys
from pathlib import Path

FILE = Path(__file__).resolve()
# Project Root
ROOT = FILE.parent.parent
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))
