# Validating Max Body Size
This example shows a way to validate the maximum body size using
`request.stream`, and how to post a file to a BlackSheep server using the HTML5
`fetch` API.

## Current limitations

At the time of this writing, blacksheep does not support configuring a maximum body size
globally, nor configuring a maximum body size for specific request handlers that would
validate the request body size also when trying to read the whole request content as
JSON, text, form data.

The following methods:

```python
    text = await request.text()
    data = await request.json()
    data = await request.form()
```

all cause the whole request body to be read.

## Running the example

- create a Python virtual environment
- install dependencies
- run the dev server `python main.py`
- navigate to [http://localhost:44555](http://localhost:44555)
- use the HTML page to select a file and upload it: only files smaller than
  ~1.5 MB are accepted by the server, and written to an `out` folder under
  `CWD`
