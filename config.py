from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

DEFAULT_QR_SIZE = 400
DEFAULT_DPI = 300
DEFAULT_ERROR_CORRECTION = "H"
MAX_LOGO_SIZE_RATIO = 0.3
PREVIEW_SIZE = 400
EXPORT_MAX_SIZE = 4096
