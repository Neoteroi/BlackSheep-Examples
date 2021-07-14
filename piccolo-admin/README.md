# Piccolo Admin example

This folder contains an example showing how to use the `mount` feature to run
a `Piccolo Admin` application in `BlackSheep`.

For more information on the `mount` feature, refer to the [documentation](https://www.neoteroi.dev/blacksheep/mounting/).

For more information on Piccolo Admin, refer to its [project in GitHub](https://github.com/piccolo-orm/piccolo_admin).

## Getting started

1. Create a Python virtual environment
2. Activate the virtual environment
3. Install dependencies in `requirements.txt`
4. Run, using the desired HTTP server (e.g. `uvicorn server:app --reload`)

```bash
# create a Python virtual environment
python -m venv venv

# activate
source venv/bin/activate  # (Linux)

venv\Scripts\activate  # (Windows)

# install dependencies
pip install -r requirements.txt

# run
uvicorn server:app --reload
```
