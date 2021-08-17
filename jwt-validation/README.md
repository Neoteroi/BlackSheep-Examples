# JWT example

This folder contains an example showing how to use JWTs (JSON Web Tokens) for
authenticating and authorizing users.

This example illustrates how to validate JSON Web Tokens issued by Azure Active
Directory, but the same principles apply to any identity provider implementing
OAuth.

## How to try the example

1. update `settings.json` to include information that is relevant to your
   scenario, for example `issuers` and `audiences` according to your
   application
2. run the application using `uvicorn`
```bash
$ uvicorn example:app --port 44777
```

3. verify that requests to the `/api/message` route require an access token according to the configuration
