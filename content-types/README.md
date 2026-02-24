# Content Types Example

This example demonstrates how to handle requests with multiple content types in
[BlackSheep](https://github.com/Neoteroi/BlackSheep) (requires **BlackSheep >= 2.6.2**).

## Overview

The `POST /foo` endpoint accepts request bodies in any of the following formats:

- `application/json`
- `application/xml`
- `text/xml`

This is achieved using a union type annotation combining `FromJSON` and `FromXML`
binders:

```python
@post("/foo")
async def create_foo(data: FromJSON[CreateFooInput] | FromXML[CreateFooInput]):
    return Foo(data.foo)
```

BlackSheep inspects the `Content-Type` header of the incoming request and
automatically deserializes the body into the appropriate type, so the handler
receives a plain `CreateFooInput` instance regardless of which format the client
used.

## Running the example

```bash
pip install blacksheep>=2.6.2 uvicorn
python server.py
```

The OpenAPI documentation is available at `http://localhost:8000/docs` once the
server is running.

## Generated OpenAPI specification

```yaml
openapi: 3.1.0
info:
    title: Example API
    version: 0.0.1
paths:
    /foo:
        get:
            responses:
                '200':
                    description: Success response
                    content:
                        application/json:
                            schema:
                                $ref: '#/components/schemas/Foo'
            operationId: get_foo
        post:
            responses: {}
            operationId: create_foo
            parameters: []
            requestBody:
                content:
                    application/json:
                        schema:
                            $ref: '#/components/schemas/CreateFooInput'
                    application/xml:
                        schema:
                            $ref: '#/components/schemas/CreateFooInput'
                    text/xml:
                        schema:
                            $ref: '#/components/schemas/CreateFooInput'
                required: true
servers: []
components:
    schemas:
        Foo:
            type: object
            required:
            - foo
            properties:
                foo:
                    type: string
                    nullable: false
        CreateFooInput:
            type: object
            required:
            - foo
            properties:
                foo:
                    type: string
                    nullable: false
tags: []
```
