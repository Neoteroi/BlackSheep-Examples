from blacksheep.server.authorization import auth
from blacksheep.server.controllers import Controller, get
from guardpost.authentication import User


class HomeController(Controller):
    @get("/")
    def home(self):
        return "Hello, World"

    @auth("authenticated")
    @get("/api/message")
    def example(self, user: User):
        return f"This is only for authenticated users {user.name}"
