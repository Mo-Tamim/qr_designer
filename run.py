#!/usr/bin/env python3
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "qr_designer.web.app:create_app",
        factory=True,
        host="0.0.0.0",
        port=8011,
        reload=True,
    )
