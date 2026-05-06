# QR Designer -- Development Guide

This guide covers setup, running, testing, code conventions, and common development tasks.

---

## Prerequisites

- Python 3.12+
- System package: `libcairo2-dev` (required by `cairosvg`, for future SVG-to-PNG conversion)

---

## Setup

```bash
git clone git@github.com:Mo-Tamim/qr_designer.git
cd qr_designer
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Running the Application

```bash
python run.py
```

This starts a uvicorn development server with hot-reload at `http://0.0.0.0:8011`.

| URL | Description |
|---|---|
| `http://localhost:8011/` | QR Designer page |
| `http://localhost:8011/layout` | Print layout page |
| `http://localhost:8011/docs` | Swagger UI (interactive API docs) |
| `http://localhost:8011/redoc` | ReDoc (alternative API docs) |

---

## Project Layout at a Glance

```
qr_designer/          # Python package
├── core/              # QR generation logic (no rendering)
├── styles/            # Pydantic config models + presets
├── renderer/          # Pillow (raster) and SVG (vector) renderers
│   └── shapes/        # Pluggable shape drawers
├── logo/              # Logo compositing engine
├── export/            # PNG/SVG/PDF byte-stream generators
├── layout/            # Print grid layout + PDF generation
└── web/               # FastAPI app, routes, static assets, templates
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed module documentation.

---

## Code Conventions

### Python

- **Type hints**: All function signatures use type annotations. Use `from __future__ import annotations` for forward references.
- **Models**: All configuration and API request/response objects are Pydantic `BaseModel` subclasses.
- **Naming**: Snake case for functions/variables, PascalCase for classes, UPPER_SNAKE for module-level constants.
- **Imports**: Absolute imports within the package (e.g., `from ..styles.config import QRStyleConfig`).
- **No comments that narrate code**. Comments should only explain non-obvious intent or constraints.

### Frontend

- Vanilla JavaScript (no framework, no build step).
- All API calls use `fetch()` with JSON payloads.
- Real-time preview is debounced at 300ms.
- Dark theme via CSS custom properties in `main.css`.

---

## Testing

### Quick Smoke Test (in-process)

```python
from fastapi.testclient import TestClient
from qr_designer.web.app import create_app

client = TestClient(create_app())

# Preview
r = client.post("/api/preview", json={"style": {"content_type": "url", "content_data": {"url": "https://example.com"}}, "preview_size": 200})
assert r.status_code == 200
assert r.json()["image"].startswith("data:image/png;base64,")

# Export PNG
r = client.post("/api/export", json={"style": {}, "format": "png"})
assert r.status_code == 200

# Grid layout
r = client.post("/api/layout/export", json={"style": {}, "grid": {"rows": 2, "cols": 2}})
assert r.status_code == 200
```

### Unit Testing Individual Modules

```python
# Matrix generation
from qr_designer.core.generator import generate_matrix
matrix = generate_matrix("https://example.com", error_correction="H")
assert len(matrix) == len(matrix[0])  # square matrix
assert all(isinstance(cell, bool) for row in matrix for cell in row)

# Classification
from qr_designer.core.matrix_analyzer import classify_matrix, ModuleType
classified = classify_matrix(matrix)
types = {t for row in classified for t in row}
assert ModuleType.FINDER_OUTER in types
assert ModuleType.DATA in types

# Rendering
from qr_designer.renderer.pillow_renderer import PillowRenderer
from qr_designer.styles.config import QRStyleConfig
renderer = PillowRenderer()
img = renderer.render(matrix, classified, QRStyleConfig(size_px=200))
assert img.size[0] > 0

# Content encoding
from qr_designer.core.encoder import encode_content
assert encode_content("wifi", ssid="Net", password="pass") == "WIFI:T:WPA;S:Net;P:pass;H:false;;"
```

---

## Common Development Tasks

### Add a new module shape

1. `qr_designer/renderer/shapes/modules.py` -- add drawer class + DRAWERS entry
2. `qr_designer/renderer/svg_renderer.py` -- add SVG case in `_draw_module_svg()`
3. `qr_designer/web/templates/designer.html` -- add `<option>` in module shape select

### Add a new content encoder

1. `qr_designer/core/encoder.py` -- add encoder class + ENCODERS entry
2. `qr_designer/web/templates/designer.html` -- add content section + select option
3. `qr_designer/web/static/js/designer.js` -- add case in `getContentData()`

### Add a style preset

1. `qr_designer/styles/presets.py` -- add factory function + PRESETS entry

### Modify the logo embedder

The logo embedder is in `qr_designer/logo/embedder.py`. Parameters are defined in `LogoConfig` (`qr_designer/styles/config.py`). The API passes all `LogoConfig` fields to `embed_logo()` in `qr_designer/web/routes/api.py:_generate_qr_image()`.

If you add new `LogoConfig` fields:
1. Add the field to `LogoConfig` in `styles/config.py`
2. Add the parameter to `embed_logo()` in `logo/embedder.py`
3. Pass the parameter in `_generate_qr_image()` in `web/routes/api.py`
4. Add UI controls in `designer.html` and read them in `designer.js`

---

## Dependencies

| Package | Version | Purpose |
|---|---|---|
| `qrcode[pil]` | >= 7.4 | QR matrix generation |
| `Pillow` | >= 10.0 | Raster image rendering |
| `fastapi` | >= 0.110 | Web framework |
| `uvicorn[standard]` | >= 0.29 | ASGI server |
| `python-multipart` | >= 0.0.9 | File upload support |
| `jinja2` | >= 3.1 | HTML template rendering |
| `reportlab` | >= 4.1 | PDF generation |
| `pydantic` | >= 2.5 | Data validation models |
| `cairosvg` | >= 2.7 | SVG-to-PNG (reserved) |
| `svgwrite` | >= 1.4 | SVG builder (reserved) |
| `openpyxl` | >= 3.1 | Excel import (reserved) |

---

## Roadmap / Future Work

- **Batch generation**: CSV/Excel import for bulk QR code creation (using `openpyxl`)
- **Template save/load**: Serialize `QRStyleConfig` to JSON files
- **WebSocket preview**: Lower-latency live preview (FastAPI has native support)
- **Dynamic QR codes**: Redirect tracking / analytics
- **Artistic patterns**: Liquid/blob styles via Perlin noise
- **Custom SVG modules**: Import SVG path data as module shapes
- **CLI tool**: Headless generation for scripting and CI/CD pipelines
- **SVG logo embedding**: Currently logos are only composited in the Pillow pipeline
