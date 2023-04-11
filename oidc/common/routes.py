from textwrap import dedent

import jwt
from blacksheep.messages import Request
from blacksheep.server.application import Application
from blacksheep.server.authorization import allow_anonymous
from blacksheep.server.responses import html, pretty_json, redirect, unauthorized
from essentials.json import dumps
from guardpost.authentication import Identity


def _render_access_token(user: Identity) -> str:
    if not user.access_token:
        return ""

    # parse without validating the access token
    # (the id_token was validated upon sign-in!)
    claims = jwt.decode(user.access_token, options={"verify_signature": False})

    return dedent(
        f"""
        <h3>You also have an access token for an API</h3>
        <p>These are the claims, from your <strong>access_token</strong>:</p>
        <pre>{dumps(claims, indent=4)}</pre>
        """
    )


def register_routes(app: Application, static_home: bool = False) -> None:
    @allow_anonymous()
    @app.route("/sign-in-error")
    async def error_handler(request: Request, error: str):
        if error == "access_denied":
            # the user declined consents to the app
            return html("<h1>OK, but you won't be able to use our wonderful app.</h1>")
        return html(f"<h1>Oh, no! {error}</h1>")

    if static_home:
        # for advanced examples using JWT Bearer authentication
        app.serve_files("static")
    else:
        # for examples using Cookie based authentication
        @app.route("/")
        async def home(request: Request, user: Identity):
            host = request.get_first_header(b"Host")
            if b"localhost" not in host:
                return redirect("http://localhost:5000/")

            if user.is_authenticated():
                id_claims = dumps(user.claims, indent=4)

                return html(
                    dedent(
                        f"""
                        <!DOCTYPE html>
                        <html>
                        <head>
                        <style>
                        pre {{
                            border: 1px dotted darkred;
                            padding: 1rem;
                        }}
                        </style>
                        </head>
                        <body>
                            <h1>Welcome!</h1>
                            <p>
                            These are your claims, from your
                            <strong>id_token</strong>:</p>
                            <pre>{id_claims}</pre>
                            {_render_access_token(user)}
                        </body>
                        </html>
                    """
                    )
                )

            return html(
                dedent(
                    """
                    <!DOCTYPE html>
                    <html>
                    <head>
                    </head>
                    <body>
                        <h1>You are not authenticated!</h1>
                        <a href='/sign-in'>Sign in here.</a><br/>
                    </body>
                    </html>
                """
                )
            )

    @app.route("/auth/me")
    async def user_info(user: Identity):
        if not user.is_authenticated():
            return unauthorized("Unauthorized")
        return pretty_json(user.claims)
