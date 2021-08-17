"""This module is where the application is configured.

To run with uvicorn cli, with hot reload:
    $ uvicorn server:app --reload --log-level info
"""
from app.configuration import load_configuration
from app.program import configure_application
from app.services import configure_services

app = configure_application(*configure_services(load_configuration()))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=44777, log_level="debug")
