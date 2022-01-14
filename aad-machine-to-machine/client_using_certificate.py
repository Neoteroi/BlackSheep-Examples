"""
This module shows an example of how the client credentials flow with certificate can be
used with Azure Active Directory and MSAL for Python.
For information on how to generate valid certificates, refer to the README files in this
repository.
"""
import asyncio
import logging
import os

import httpx
import msal
from dotenv import load_dotenv

# read .env file into environment variables
load_dotenv()

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("msal").setLevel(logging.INFO)

app = msal.ConfidentialClientApplication(
    os.environ["APP_CLIENT_ID"],
    authority=os.environ["AAD_AUTHORITY"],
    client_credential={
        "thumbprint": os.environ["APP_CLIENT_CERT_THUMBPRINT"],
        "private_key": open("example.pri.pem").read(),
    },
)

scope = [os.environ["APP_CLIENT_SCOPE"]]

result = app.acquire_token_silent(scope, account=None)

if not result:
    logging.info("No suitable token exists in cache. Let's get a new one from AAD.")
    result = app.acquire_token_for_client(scopes=scope)

if "access_token" in result:
    access_token = result["access_token"]
    logging.info("Access token %s", access_token)

    async def calls():
        # call the API using the access token
        async with httpx.AsyncClient(timeout=60) as client:
            for _ in range(4):
                response = await client.get(
                    "http://localhost:5000",
                    headers={"Authorization": f"Bearer {access_token}"},
                )

                if response.status_code != 200:
                    logging.error(
                        "The request to the API failed, with status %s",
                        response.status_code,
                    )
                else:
                    logging.info(
                        "The request to the API server succeeded. Response body: %s",
                        response.text,
                    )

    asyncio.run(calls())

else:
    print(result.get("error"))
    print(result.get("error_description"))
    print(result.get("correlation_id"))
