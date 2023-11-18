# Example of Self Hosted OAuth2 Password Provider

A simple example of a self hosted OAuth2 password provider. 
It can be used to authenticate users in own applications with password flow.

## Running the example

- create a Python virtual environment

```bash
python -m venv venv
```

- install dependencies

```bash
pip install -r requirements.txt
```

- run the dev server

```bash
python server.py
```

- look at [example.http](example.http) to find at the example requests

## Server has 4 endpoints

- `/api/register` - register a new user
- `/api/token` - get a new access token
- `/api/refresh` - refresh an access token
- `/api/revoke` - revoke an access token
- `/api/anonymous` - get a resource without authentication
- `/api/protected` - get a resource with authentication