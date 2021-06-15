from blacksheep.server.openapi.v3 import OpenAPIHandler
from openapidocs.v3 import Info

docs = OpenAPIHandler(
    info=Info(title="Demo API", version="0.0.1"), anonymous_access=True
)

# include only endpoints whose path starts with "/api/"
docs.include = lambda path, _: path.startswith("/api/")
