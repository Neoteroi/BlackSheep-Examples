"""
Example: Using BlackSheep with a2wsgi

This example demonstrates how to use BlackSheep (an ASGI framework) with
a2wsgi to run on WSGI servers like Gunicorn with sync workers, uWSGI, or
mod_wsgi.

Installation:
    pip install blacksheep a2wsgi gunicorn

Usage:
    # Run with Gunicorn (WSGI server)
    gunicorn server:wsgi_app -w 4

    # Or with uWSGI
    uwsgi --http :8000 --wsgi-file server.py --callable wsgi_app
"""
from pathlib import Path
from blacksheep import Application, json, html
from a2wsgi import ASGIMiddleware


# Create BlackSheep application
app = Application(show_error_details=True)


# Configure static file serving
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.serve_files(static_path)


@app.router.get("/")
async def home():
    return html("""
        <html>
            <head>
                <title>BlackSheep + a2wsgi</title>
            </head>
            <body>
                <h1>BlackSheep with a2wsgi</h1>
                <p>This BlackSheep application is running through a2wsgi!</p>
                <ul>
                    <li><a href="/api/info">API Info</a></li>
                    <li><a href="/api/health">Health Check</a></li>
                </ul>
            </body>
        </html>
    """)


@app.router.get("/api/info")
async def api_info():
    """API endpoint returning JSON."""
    return json({
        "framework": "BlackSheep",
        "adapter": "a2wsgi",
        "description": "ASGI to WSGI bridge",
        "features": [
            "Static file serving with Content-Length",
            "Full BlackSheep functionality",
            "Compatible with WSGI servers"
        ]
    })


@app.router.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return json({"status": "healthy", "message": "All systems operational"})


@app.router.post("/api/echo")
async def echo(data: dict):
    """Echo back the received JSON data."""
    return json({"received": data, "echo": True})


# Wrap the ASGI app with a2wsgi to create a WSGI app
# This is the WSGI callable that WSGI servers expect
wsgi_app = ASGIMiddleware(app)
