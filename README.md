# QR Designer

A Python application for creating highly customizable QR codes and preparing them for print on sticker sheets.

## Features

- **QR Code Designer** — Full visual customization: module shapes, finder pattern styles, colors, gradients, logo embedding, background images, and QR code shape masking.
- **Print Layout Generator** — Grid-based PDF output for sticker sheet printing with precise alignment controls.
- **Multiple Export Formats** — PNG, SVG, and print-ready PDF.
- **Real-Time Preview** — Web-based UI with live preview as you adjust settings.

## Quick Start

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py
```

Open http://localhost:8011 in your browser.

## API Documentation

FastAPI auto-generates interactive API docs:

- Swagger UI: http://localhost:8011/docs
- ReDoc: http://localhost:8011/redoc

## Project Structure

```
qr_designer/
├── core/           # QR matrix generation and content encoding
├── renderer/       # Pillow (raster) and SVG (vector) rendering engines
│   └── shapes/     # Module, finder, and alignment pattern drawers
├── styles/         # Color specs, style config, presets
├── logo/           # Logo embedding logic
├── export/         # PNG / SVG / PDF export
├── layout/         # Print grid layout and PDF generation
└── web/            # FastAPI app, routes, templates, static assets
```
