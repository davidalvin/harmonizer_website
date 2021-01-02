# When running on uwsgi this is the main file which starts the app
from webapp import app

if __name__ == "__main__":
    app.run()