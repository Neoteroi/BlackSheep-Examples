#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import uvicorn

# from tmw_server.app import app

if __name__ == "__main__":
    uvicorn.run(
        "src.app:app",
        host="127.0.0.1",
        port=8000,
        log_level="debug",
        reload=True,
    )
