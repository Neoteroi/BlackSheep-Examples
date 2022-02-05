# Chat app example

This folder contains a simple chat application built using WebSocket and VueJS.
You can use it as a starting point to build your own real-time application using
WebSocket.

Bear in mind, though, that this is merely an example. In the real world, you would
probably like to use a message queue like Redis to broadcast messages to the clients 
and some persistent storage like PostgreSQL or MongoDB to store your messages, users, etc.

## Getting started

1. Create a Python virtual environment
2. Activate the virtual environment
3. Install dependencies in `requirements.txt`
4. Run the application using `uvicorn --reload server:app`
5. Navigate to `http://localhost:8000` in your browser and try sending
some messages. You can open it in multiple tabs to simulate
multiple clients connected.

```bash
# create a Python virtual environment
python -m venv venv

# activate
source venv/bin/activate  # (Linux)

venv\Scripts\activate  # (Windows)

# install dependencies
pip install -r requirements.txt

# run app
uvicorn --reload server:app
```