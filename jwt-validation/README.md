# JWT example

This folder contains an example showing how to use JWTs (JSON Web Tokens) for
authenticating and authorizing users.

This example illustrates how to validate JSON Web Tokens issued by Azure Active
Directory, but the same principles apply to any identity provider implementing
OAuth.

To have an overview about validating JWTs using Python and configuring an
application in Azure Active Directory or Azure Active Directory B2C, read this
article: [Validating JSON web tokens (JWTs) from Azure AD, in
Python](https://robertoprevato.github.io/Validating-JWT-Bearer-tokens-from-Azure-AD-in-Python/).

## How to try the example

1. update `settings.json` to include information that is relevant to your
   scenario, for example `issuers` and `audiences` according to your
   application
2. run the application using `uvicorn`
```bash
$ uvicorn example:app --port 44777
```

3. verify that requests to the `/api/message` route require an access token according to the configuration

## Notes

Portions of this code will be packed in a dedicated library.
