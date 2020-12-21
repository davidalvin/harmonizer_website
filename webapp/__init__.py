from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

if app.config["ENV"] == "development":
    print("\nRUNNING ON DEVELOPMENT...\n")
    app.config.from_object('config.DevelopmentConfig')
else:
    print("\nRUNNING ON PRODUCTION...\n")
    app.config.from_object('config.ProductionConfig')

# Limit traffic to the website as it is in alpha
limiter = Limiter(
    app,
    key_func= lambda : "1", # 1 means this applies to all users
    default_limits=["20 per day", "10 per hour", "1 per 2minutes"]
)

from webapp import routes
