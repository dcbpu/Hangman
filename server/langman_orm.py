from sqlalchemy import create_engine, ForeignKey, Column, types, MetaData
from sqlalchemy.orm import declarative_base, relationship

import json
import datetime

from server.util import date_to_ordinal

meta = MetaData()
Base = declarative_base(metadata=meta)

class Usage(Base):
    __tablename__ = 'usages'
    usage_id    = Column(types.Integer, primary_key=True)
    language    = Column(types.Enum("en","es","fr", name='language_codes'), nullable=False)
    secret_word = Column(types.String(length=25), nullable=False)
    usage       = Column(types.String(length=500), nullable=False)
    source      = Column(types.String(length=100))

class User(Base):
    __tablename__ = 'users'
    user_id    = Column(types.String(length=38), primary_key=True)
    user_name  = Column(types.String(length=30), nullable=False)
    num_games  = Column(types.Integer, default=0)
    outcomes   = Column(types.Text, default='{}')
    by_lang    = Column(types.Text, default='{}')
    first_time = Column(types.DateTime)
    total_time = Column(types.Interval)
    avg_time   = Column(types.Interval)

    games = relationship("Game", back_populates="user")
    def _incr_json_field(self, field, key):
        '''Increment the value of self.``field``[``key``] by one where 
        ``field`` is a JSON text string. (Does not commit.)'''
        d = json.loads(getattr(self, field))
        d[key] = d.get(key, 0) + 1
        setattr(self, field, json.dumps(d))

    def _decr_json_field(self, field, key):
        '''Decrement the value of self.``field``[``key``] by one where 
        ``field`` is a JSON text string.  (Does not commit.)'''
        d = json.loads(getattr(self, field))
        d[key] = d.get(key, 0) - 1
        setattr(self, field, json.dumps(d))
        
    def _game_started(self, lang):
        '''Update the number of games ``num_games`` and both ``outcomes`` and
        ``by_lang`` counts by one. (Does not commit.)'''
        self.num_games = (self.num_games or 0) + 1
        self._incr_json_field('outcomes', 'active')
        self._incr_json_field('by_lang', lang)

    def _game_ended(self, outcome, time_delta):
        '''Update the ``total_time`` and ``avg_time`` according to a game that 
        took ``time_delta`` time. Also, update ``outcomes`` by converting one
        active game to have outcome ``outcome``. (Does not commit.)'''
        self._decr_json_field('outcomes', 'active')
        self._incr_json_field('outcomes', outcome)
        self.total_time  = time_delta + (self.total_time or datetime.timedelta(0))
        self.avg_time    = self.total_time / self.num_games

class Game(Base):
    __tablename__ = 'games'
    game_id     = Column(types.String(length=38), primary_key=True)
    player      = Column(types.String(length=38), ForeignKey("users.user_id"), nullable=False)
    usage_id    = Column(types.Integer, ForeignKey("usages.usage_id"), nullable=False)
    guessed     = Column(types.String(length=30), default='')
    reveal_word = Column(types.String(length=25), nullable=False)
    bad_guesses = Column(types.Integer)
    start_time  = Column(types.DateTime)
    end_time    = Column(types.DateTime)

    user  = relationship("User", back_populates="games")
    usage = relationship("Usage")

    def _result(self):
        '''Return the result of the game: lost, won, or active'''
        if self.bad_guesses == 6:
            return 'lost'
        elif '_' not in self.reveal_word:
            return 'won'
        else:
            return 'active'

    def _to_dict(self):
        '''Convert the game into a dictionary suitable for JSON serialization

        Special attention is paid to DateTime fields using the
        date_to_ordinals function.'''
        as_dict = { k:v for k,v in self.__dict__.items()
                    if not k.startswith('_') }
        as_dict['result'] = self._result()
        as_dict['start_time'] = date_to_ordinal(as_dict.get('start_time'))
        as_dict['end_time'] = date_to_ordinal(as_dict.get('end_time'))
        return as_dict
