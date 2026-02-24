import os
import sys
from pathlib import Path

# Ensure repo root is on sys.path for module imports like "import db".
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Provide defaults for required env vars during tests.
os.environ.setdefault("BOT_TOKEN", "test-token")
os.environ.setdefault("METRIKA_COUNTER_ID", "test-counter")
