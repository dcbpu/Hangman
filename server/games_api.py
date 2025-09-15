import os
from flask import Flask, g
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_restx import Resource, Api, Namespace
from flask_cors import CORS
from sqlalchemy import func

import datetime
import random
import uuid

from server.util import get_config
from server.langman_orm import Usage, User, Game

from unidecode import unidecode

from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity, get_jwt
)


games_api = Namespace('games', description='Creating and playing games')

@games_api.route('')
class Games(Resource):
    pass

class OneGame(Resource):
    pass

# Create the app and configure it
app = Flask(__name__)                       # Create Flask app
#env = os.environ.get('FLASK_ENV', 'production')
#app.config.update(get_config(env, open('server/config.yaml')))
#app.config.update(get_config(app.config['ENV'], 
#app.open_resource('config.yaml')))
# Make sure you define these in Render Dashboard → Environment
app.config["DB_USAGE"] = os.environ["DB_USAGE"]
app.config["DB_GAMES"] = os.environ["DB_GAMES"]
app.config["JWT_SECRET_KEY"] = os.environ["JWT_SECRET_KEY"]

CORS(app)                                   # Cross-origin resource sharing
api = Api(app)                              # Create RESTplus api on app
api.add_namespace(games_api, path='/api/games') # Insert games namespace
# -- client expects /api/games; changed from /games to /api/games here.


@games_api.route('')
class Games(Resource):
    valid_langs = ('en', 'es', 'fr')
    @jwt_required()
    def post(self):
        '''Start a new game and return the game id

        :route: ``/`` GET

        :payload:
              * ``username`` A string containing the player's name
              * ``language`` Language to play in (e.g., 'en')

        :returns:
           A success message:
              * ``message`` Literal 'success'
              * ``game_id`` The new game's UUID
        '''
        # check input is valid
        if not (games_api.payload and
                #'username' in games_api.payload and
                'language' in games_api.payload):
            games_api.abort(400, 'New game POST requires username and language')
        lang = games_api.payload['language']
        #name = games_api.payload['username']
        #user_id = str(uuid.uuid3(uuid.NAMESPACE_URL, name))
        name = get_jwt()['name']
        user_id = get_jwt_identity()
        if lang not in self.valid_langs:
            return {'message': 'New game POST language must be from ' +
                               ', '.join(Games.valid_langs)}, 400

        # if user does not exist, create user; get user id
        user = g.games_db.query(User).filter(User.user_id == user_id).one_or_none()
        if user is None:
            user = User(
                user_id = user_id, 
                user_name = name,
                first_time = datetime.datetime.now(),
            )
            g.games_db.add(user)
            g.games_db.commit()
            user = g.games_db.query(User).filter(User.user_name == name).one()
        user._game_started(lang)
        
        # select a usage example
        usage = g.usage_db.query(Usage).filter(
            Usage.language==lang
        ).order_by(func.random()).first()
        
        # create the new game
        new_game_id = str(uuid.uuid4())
        new_game = Game(
            game_id  = new_game_id,
            player   = user.user_id,
            usage_id = usage.usage_id,
            bad_guesses = 0,
            reveal_word = '_' * len(usage.secret_word),
            start_time = datetime.datetime.now()
        )
        g.games_db.add(new_game)
        g.games_db.commit()

        #return { 'message': 'success', 'game_id':new_game_id }
        return { 'message': 'success', 
         'game_id':new_game_id,
         'access_token': create_access_token(
            identity=user_id,
            additional_claims={'access':'player',
                        'name':name,
                        'game_id':new_game_id}) }
    

@games_api.route('/<game_id>')
class OneGame(Resource):
    @jwt_required()
    def get(self, game_id):
        '''Get the game ``game_id`` information

        :route: ``/<game_id>`` GET

        :returns:
           The object for a game, including:
              * ``game_id`` The game's UUID
              * ``player`` The player's name
              * ``usage_id`` The game usage id from the Usages table
              * ``guessed`` A string of guessed letters
              * ``reveal_word`` Guessed letters in otherwise blanked word string
              * ``bad_guesses`` Number of incorrect guesses so far
              * ``start_time`` The epoch ordinal time when game began
              * ``end_time`` The epoch ordinal time when game ended
              * ``result`` Game outcome from ('lost', 'won', 'active')
              * ``usage`` The full sentence example with guess-word blanked
              * ``lang`` The language of the example, such as 'en'
              * ``source`` The book from which the usage example originated
        '''
        # check input is valid
        game = g.games_db.query(Game).filter(Game.game_id == game_id).one_or_none()
        
        # if game does not exist, produce error code
        #if game is None:
            #games_api.abort(404, 'Game with id {} does not exist'.format(game_id))
        claims = get_jwt()
        if game is None or game.player != get_jwt_identity():
            games_api.abort(404, f'Game {game_id} is unauthorized or nonexistant')
        
        # get usage record because it contains the language and usage example
        usage = g.usage_db.query(Usage).filter(Usage.usage_id == game.usage_id).one()
        
        # return game state
        game_dict = game._to_dict()
        game_dict['usage']  = usage.usage.format(word='_'*len(usage.secret_word))
        game_dict['lang']   = usage.language
        game_dict['source'] = usage.source

        game_dict['access_token'] = create_access_token(
                identity   = get_jwt_identity(), 
                additional_claims={'access':'player', 'game_id':game_id,
                             'name':get_jwt()['name']})

        return game_dict
    
    @jwt_required() 
    def put(self, game_id):
        '''Update game ``game_id`` as resulting from a guessed letter

        :route: ``/<game_id>`` PUT

        :payload:
           The guessed letter as an object:
              * ``letter`` A single guessed letter

        :returns:
           The object for a game, including:
              * ``game_id`` The game's UUID
              * ``player`` The player's name
              * ``usage_id`` The game usage id from the Usages table
              * ``guessed`` A string of guessed letters
              * ``reveal_word`` Guessed letters in otherwise blanked word string
              * ``bad_guesses`` Number of incorrect guesses so far
              * ``start_time`` The epoch ordinal time when game began
              * ``end_time`` The epoch ordinal time when game ended
              * ``result`` Game outcome from ('lost', 'won', 'active')

        This method interacts with the database to update the
        indicated game.
        '''

        additional_claims = get_jwt()
        if additional_claims.get('game_id', '') != game_id:
            games_api.abort(503, 'Unauthorized access to game {}'.format(game_id))

        # check input is valid; return error if game non-existent or inactive
        game = g.games_db.query(Game).filter(Game.game_id == game_id).one_or_none()
        if game is None:
            games_api.abort(404, 'Game with id {} does not exist'.format(game_id))
        if game._result() != 'active':
            games_api.abort(403, 'Game with id {} is over'.format(game_id))
        if ('letter' not in games_api.payload or
            not games_api.payload['letter'].isalpha() or
            len(games_api.payload['letter']) != 1):
            games_api.abort(400, 'PUT requires one alphabetic character in "letter" field')
        letter = games_api.payload['letter'].lower()
        
        # update game state according to guess
        if letter in game.guessed:             # check for repeated guess
            games_api.abort(403, 'Letter {} was already guessed'.format(letter))
        game.guessed = game.guessed + letter
        usage  = g.usage_db.query(Usage).filter(Usage.usage_id == game.usage_id).one()
        if letter in unidecode(usage.secret_word.lower()):
            game.reveal_word = ''.join([
            l if unidecode(l.lower()) in game.guessed else '_'
            for l in usage.secret_word])
        else:
            game.bad_guesses += 1
            
        # if game is over, update the user record
        outcome = game._result()
        if outcome != 'active':
            user = g.games_db.query(User).filter(User.user_id == game.player).one()
            game.end_time = datetime.datetime.now()
            user._game_ended(outcome, game.end_time - game.start_time)            

        # return the modified game state
        game_dict = game._to_dict()
        game_dict['usage']  = usage.usage.format(word='_'*len(usage.secret_word))
        game_dict['lang']   = usage.language
        game_dict['source'] = usage.source
        if outcome != 'active':
            game_dict['secret_word'] = usage.secret_word
        
        g.games_db.commit()

        return game_dict
    
    @jwt_required()
    def delete(self, game_id):
        '''Delete record for game ``game_id``

        :route: ``/<game_id>`` DELETE
        :returns:
           An acknowledgment object:
              * ``message`` Either 'One' or 'Zero' records deleted

        This method removed the game from its table
        '''
        claims = get_jwt()
        if claims.get('game_id', '') != game_id:
            games_api.abort(503, 'Unauthorized access to game {}'.format(game_id))

        game = g.games_db.query(Game).filter(Game.game_id == game_id).one_or_none()
        if game is not None:
            g.games_db.delete(game)
            g.games_db.commit()
            msg = 'One record deleted'
        else:
            msg = 'Zero records deleted'

        return {'message': msg}
    
