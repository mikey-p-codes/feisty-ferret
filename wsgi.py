# This is the entry point for the WSGI server to run the Flask application.
from app import app
if __name__ == "__main__":
    app.run()