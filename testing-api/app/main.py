from .routes import router
from .docs import docs
from blacksheep.server.application import Application


app = Application(router=router)
docs.bind_app(app)
