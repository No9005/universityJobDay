# start app ----------------------------------------
from app import app

# gunicorn entrypoint
if __name__ == "__main__":
    app.run()