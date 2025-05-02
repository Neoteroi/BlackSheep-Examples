# Using Dependency Injector instead of Rodi

This example illustrates how to use Dependency Injector instead of Rodi.

The example supports automatic injection of dependencies in request handlers
and controllers' constructors when dependencies are type annotated.

To run the example:

```bash
uvicorn main:app
```

Make requests to "/" and "/controller-test" to test DI resolution in request
handlers defined using functions and `Controller` methods respectively.
