from .util import get_config
from flask import Flask, g
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_restx import Api
from flask_cors import CORS
import flask_jwt_extended as JWT
from .games_api import games_api
from .auth_api import auth_api
import os

# Import your API namespaces and models
from .games_api import games_api
from .auth_api import auth_api
from .auth_orm import base as AuthBase
from .langman_orm import Base as GamesBase
from .langman_orm import Base as UsageBase  # if you have a usage base

app = Flask(__name__)                         # Create Flask app

# Pick env from system environment variable, default to dev_postgres
# env = os.environ.get("FLASK_ENV", "dev_postgres")

# Load config using your env + config.yaml
# app.config.update(get_config(env, open("server/config.yaml")))

app.config['DB_USAGE'] = os.environ.get("DB_USAGE")
app.config['DB_GAMES'] = os.environ.get("DB_GAMES")
app.config['DB_AUTH']  = os.environ.get("DB_AUTH")
app.config['JWT_SECRET_KEY'] = os.environ.get("JWT_SECRET_KEY")

CORS(app)                                     # Cross-origin resource sharing

api = Api(app, doc=False)
api.add_namespace(games_api, path='/api/games')
api.add_namespace(auth_api, path='/api/auth')

assert ('JWT_SECRET_KEY' in app.config), 'Must set FLASK_JWT_SECRET_KEY env variable'
if 'JWT_ACCESS_TOKEN_EXPIRES' not in app.config:
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 86400   # default is 1 day

app.config['PROPAGATE_EXCEPTIONS'] = True    # avoids server error w/bad JWTs in gunicorn

jwt = JWT.JWTManager(app)  # do this after config is set


print('URL MAP', app.url_map)   # useful for debugging

# -----------------------------
# Database setup
# -----------------------------
def create_all_tables():
    """Create tables on app startup if they don't exist."""
    if app.config['DB_AUTH']:
        engine_auth = create_engine(app.config['DB_AUTH'])
        AuthBase.metadata.create_all(engine_auth)
    if app.config['DB_GAMES']:
        engine_games = create_engine(app.config['DB_GAMES'])
        GamesBase.metadata.create_all(engine_games)
    if app.config['DB_USAGE']:
        engine_usage = create_engine(app.config['DB_USAGE'])
        UsageBase.metadata.create_all(engine_usage)

create_all_tables()

@app.before_request
def init_db():
    '''Initialize db by creating the global db_session

    This runs on each request.
    '''
    db_auth = create_engine(app.config['DB_AUTH'])
    g.auth_db = sessionmaker(db_auth)()

    db_usage = create_engine(app.config['DB_USAGE'])
    g.usage_db = sessionmaker(db_usage)()

    db_games = create_engine(app.config['DB_GAMES'])
    g.games_db = sessionmaker(db_games)()

@app.teardown_request
def close_db(exception):    
    '''Close down db connection; same one cannot be used b/w threads

    This runs after each request.
    '''
    if hasattr(g, 'auth_db'):
        g.auth_db.close()
        _ = g.pop('auth_db')

    if hasattr(g, 'usage_db'):
        g.usage_db.close()
        _ = g.pop('usage_db')

    if hasattr(g, 'games_db'):
        g.games_db.close()
        _ = g.pop('games_db')
