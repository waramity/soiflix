from main.server import db
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
        # userlist = db.relationship('UserList', secondary=userlist, backref=db.backref('userlist', lazy='dynamic'))

# userlist = db.Table('userlist',
#     db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
#     db.Column('userlist_id', db.Integer, db.ForeignKey('userlist.id'))
# )
# userlist_movies = db.Table('userlist_movies',
    # db.Column('movie_id', db.Integer, db.ForeignKey('movie.id')),
    # db.Column('userlist_id', db.Integer, db.ForeignKey('userlist.id'))
# )

# userlist_series = db.Table('userlist_series',
    # db.Column('series_id', db.Integer, db.ForeignKey('series.id')),
    # db.Column('userlist_id', db.Integer, db.ForeignKey('userlist.id'))
# )

# class UserList(db.Model):
    # id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    # movies = db.relationship('Movie', secondary=userlist_movies, backref=db.backref('userlist_movies', lazy='dynamic'), order_by='Movie.name')
    # series = db.relationship('Series', secondary=userlist_series, backref=db.backref('userlist_series', lazy='dynamic'), order_by='Series.name')

movie_genres = db.Table('movie_genres',
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.id')),
    db.Column('movie_id', db.Integer, db.ForeignKey('movie.id'))
)

movie_actors = db.Table('movie_actors',
    db.Column('actor_id', db.Integer, db.ForeignKey('actor.id')),
    db.Column('movie_id', db.Integer, db.ForeignKey('movie.id'))
)

movie_directors = db.Table('movie_directors',
    db.Column('director_id', db.Integer, db.ForeignKey('director.id')),
    db.Column('movie_id', db.Integer, db.ForeignKey('movie.id'))
)

movie_studio = db.Table('movie_studio',
    db.Column('studio_id', db.Integer, db.ForeignKey('studio.id')),
    db.Column('movie_id', db.Integer, db.ForeignKey('movie.id'))
)

class Movie(db.Model):
   __tabelname__ = 'movie'
   id = db.Column(db.Integer, primary_key = True, autoincrement=False)
   title = db.Column(db.String(100), nullable=False)
   genres = db.relationship('Genre', secondary=movie_genres, backref=db.backref('movie_genres', lazy='dynamic'))
   description = db.Column(db.String(255), nullable=True)
   youtube_url = db.Column(db.String(255), nullable=False)
   actors = db.relationship('Actor', secondary=movie_actors, backref=db.backref('movie_actors', lazy='dynamic'))
   directors = db.relationship('Director', secondary=movie_directors, backref=db.backref('movie_directors', lazy='dynamic'))
   last_updated = db.Column(db.DateTime, nullable=True)
   thumbnail = db.Column(db.String(100), nullable=True)
   published_year = db.Column(db.Integer, nullable = True)
   runtime_min = db.Column(db.Integer, nullable = True)

   studio = db.relationship('Studio', secondary=movie_studio, backref=db.backref('movie_studio', lazy='dynamic'))

   def __repr__(self):
       return f"Movie('{self.id}', '{self.title}', '{self.genres}', '{self.youtube_url}', '{self.actors}', '{self.directors}'"

episode_list = db.Table('episode_list',
    db.Column('episode_id', db.Integer, db.ForeignKey('episode.id')),
    db.Column('season_id', db.Integer, db.ForeignKey('season.id'))
)

series_genres = db.Table('series_genres',
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.id')),
    db.Column('series_id', db.Integer, db.ForeignKey('series.id'))
)

season_list = db.Table('season_list',
    db.Column('season_id', db.Integer, db.ForeignKey('season.id')),
    db.Column('series_id', db.Integer, db.ForeignKey('series.id'))
)

series_actors = db.Table('series_actors',
    db.Column('actor_id', db.Integer, db.ForeignKey('actor.id')),
    db.Column('series_id', db.Integer, db.ForeignKey('series.id'))
)

series_directors = db.Table('series_directors',
    db.Column('director_id', db.Integer, db.ForeignKey('director.id')),
    db.Column('series_id', db.Integer, db.ForeignKey('series.id'))
)

series_studio = db.Table('series_studio',
    db.Column('studio_id', db.Integer, db.ForeignKey('studio.id')),
    db.Column('series_id', db.Integer, db.ForeignKey('series.id'))
)

tvshow_genres = db.Table('tvshow_genres',
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.id')),
    db.Column('tvshow_id', db.Integer, db.ForeignKey('tvshow.id'))
)

tvshow_season = db.Table('tvshow_season',
    db.Column('season_id', db.Integer, db.ForeignKey('season.id')),
    db.Column('tvshow_id', db.Integer, db.ForeignKey('tvshow.id'))
)

tvshow_actors = db.Table('tvshow_actors',
    db.Column('actor_id', db.Integer, db.ForeignKey('actor.id')),
    db.Column('tvshow_id', db.Integer, db.ForeignKey('tvshow.id'))
)

tvshow_studio = db.Table('tvshow_studio',
    db.Column('studio_id', db.Integer, db.ForeignKey('studio.id')),
    db.Column('tvshow_id', db.Integer, db.ForeignKey('tvshow.id'))
)

class Series(db.Model):
   id = db.Column(db.Integer, primary_key = True, autoincrement=False)
   title = db.Column(db.String(100), nullable=False)
   thumbnail = db.Column(db.String(100), nullable=True)
   description = db.Column(db.String(255), nullable=True)
   seasons = db.relationship('Season', secondary=season_list, backref=db.backref('season_list', lazy='dynamic'))
   genres = db.relationship('Genre', secondary=series_genres, backref=db.backref('series_genres', lazy='dynamic'))
   last_updated = db.Column(db.DateTime, nullable=True)
   actors = db.relationship('Actor', secondary=series_actors, backref=db.backref('series_actors', lazy='dynamic'))
   directors = db.relationship('Director', secondary=series_directors, backref=db.backref('series_directors', lazy='dynamic'))
   studio = db.relationship('Studio', secondary=series_studio, backref=db.backref('series_studio', lazy='dynamic'))
   state = db.Column(db.Boolean, unique=False, nullable=True)

   def __repr__(self):
        return f"Series('{self.id}', '{self.title}', '{self.seasons}', '{self.last_updated}', '{self.directors}', '{self.actors}'"

class Tvshow(db.Model):
   id = db.Column(db.Integer, primary_key = True, autoincrement=False)
   title = db.Column(db.String(100), nullable=False)
   thumbnail = db.Column(db.String(100), nullable=True)
   description = db.Column(db.String(255), nullable=True)
   seasons = db.relationship('Season', secondary=tvshow_season, backref=db.backref('tvshow_season', lazy='dynamic'))
   genres = db.relationship('Genre', secondary=tvshow_genres, backref=db.backref('tvshow_genres', lazy='dynamic'))
   last_updated = db.Column(db.DateTime, nullable=True)
   actors = db.relationship('Actor', secondary=tvshow_actors, backref=db.backref('tvshow_actors', lazy='dynamic'))
   studio = db.relationship('Studio', secondary=tvshow_studio, backref=db.backref('tvshow_studio', lazy='dynamic'))
   state = db.Column(db.Boolean, unique=False, nullable=True)

   def __repr__(self):
        return f"Tvshow('{self.id}', '{self.title}', '{self.seasons}', '{self.last_updated}', '{self.actors}'"

class Season(db.Model):
   id = db.Column(db.Integer, primary_key = True, autoincrement=False)
   season_title = db.Column(db.String(100), nullable=False)
   yt_playlist_url = db.Column(db.String(100), nullable=False)
   episodes = db.relationship('Episode', secondary=episode_list, backref=db.backref('episode_list', lazy='dynamic'))
   published_year = db.Column(db.Integer, nullable=True)

   def __repr__(self):
        return f"Season('{self.id}', '{self.published_year}', '{self.season_title}', '{self.yt_playlist_url}', '{self.episodes}'"

class Episode(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    title = db.Column(db.String(100), nullable=False)
    youtube_url = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"Episode('{self.id}', '{self.title}', '{self.youtube_url}')"

class Actor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), index=True, unique=True)

    def __repr__(self):
        return f"Actor('{self.id}', '{self.name}')"

class Studio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), index=True, unique=True)

    def __repr__(self):
        return f"Studio('{self.id}', '{self.name}')"

class Director(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), index=True, unique=True)

    def __repr__(self):
        return f"Director('{self.id}', '{self.name}')"

class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), index=True, unique=True)

    def __repr__(self):
        return f"Genre('{self.id}', '{self.name}')"

post_actors = db.Table('post_actors',
    db.Column('actor_id', db.Integer, db.ForeignKey('actor.id')),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'))
)

post_genres = db.Table('post_genres',
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.id')),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'))
)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    thumbnail = db.Column(db.String(100), nullable=True)
    actors = db.relationship('Actor', secondary=post_actors, backref=db.backref('post_actors', lazy='dynamic'))
    genres = db.relationship('Genre', secondary=post_genres, backref=db.backref('post_genres', lazy='dynamic'))
    date_posted = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"
