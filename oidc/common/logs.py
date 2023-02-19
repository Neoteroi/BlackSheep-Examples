import logging

from blacksheep.baseapp import get_logger
from blacksheep.server.authentication.oidc import get_logger as get_oidc_logger

logging.basicConfig(level=logging.DEBUG, format="%(message)s")

for logger in {get_logger(), get_oidc_logger()}:
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
