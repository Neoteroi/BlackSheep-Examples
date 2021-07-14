# TestClient example

This folder contains an example showing how to test an API using the built-in
`TestClient` and `pytest`.

The preparation of this example is described in the official documentation under [testing](https://www.neoteroi.dev/blacksheep/testing/).
This demo uses SQLite, refer to Piccolo's documentation to use PostgreSQL.

## Getting started

1. Create a Python virtual environment
2. Activate the virtual environment
3. Install dependencies in `requirements.txt`
4. Run tests using `pytest`

```bash
# create a Python virtual environment
python -m venv venv

# activate
source venv/bin/activate  # (Linux)

venv\Scripts\activate  # (Windows)

# install dependencies
pip install -r requirements.txt

# run tests
pytest
```
