# Example showing an HTTP Proxy implemented with BlackSheep

This example shows an HTTP Proxy implementation, proxying requests for another
`blacksheep` back-end.

Run the frst BlackSheep application:

```bash
python blacksheep_app/server.py
```

Run the BlackSheep proxy application:

```bash
python blacksheep_proxy/server.py
```

Open `example-2.html` in a browser and use its forms to test uploading to the
server directly, and to the BlackSheep proxy. The result should be the same.

## Note
The example proxy in `blacksheep_proxy` handles memory in the proper way:

- it reads input streams as chunks (never whole in memory)
- it reads response streams from the back-end in chunks (never whole in memory)
