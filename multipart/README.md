# MultiPart Form Data

This folder contains examples illustrating `multipart/form-data` with BlackSheep>=`4.6.0`.

## How to verify memory consumption

One way to verify that multipart file uploads and server-side parsing are
memory-efficient:

```bash
# Terminal 1 - Run server
python server.py

# Terminal 2 - Monitor memory continuously
watch -n 0.5 'ps aux | grep "python.*server.py" | grep -v grep | awk "{print \$6/1024 \" MB\"}"'

# Terminal 3 - Upload file
python test_client.py
```
