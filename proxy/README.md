# Example showing an HTTP Proxy implemented with BlackSheep

Run the Flask application:

```bash
python flask_app/server.py
```

Run the BlackSheep application:

```bash
python blacksheep_app/server.py
```

Open the file "example.html" and use its forms to test uploading to the Flask
server directly (uploaded files should be written to the `out` folder), and
test uploading to the BlackSheep proxy. The result should be the same.

## Note
The example proxy in `blacksheep_proxy` handles memory in the proper way:

- it reads input streams as chunks (never whole in memory)
- it reads response streams from the back-end in chunks (never whole in memory)

It always sends response contents backs using `Transfer-Encoding: chunked`,
which might or might not be desirable, but ensures memory is handled
efficiently.
