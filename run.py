from main.server import app, db
from main.features.auth.routes import auth
from main.features.main.routes import main
from main.models import User, Movie, Series, Genre, Season, Episode, Director, Actor, Tvshow, Studio
import datetime
from flask import Blueprint, render_template, redirect, request, session, make_response, send_file

from flask_login import LoginManager
import csv

from bs4 import BeautifulSoup
import requests
import json
import string
import random

app.register_blueprint(auth)
app.register_blueprint(main)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

#db.create_all()


@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.get(int(user_id))


@app.template_filter('convert_datetime_to_th_str')
def convert_datetime_to_th_str(datetime_obj):
    day = datetime_obj.day
    month = datetime_obj.month
    year = datetime_obj.year
    if month == 1:
        month = "มกราคม"
    elif month == 2:
        month = "กุมภาพันธ์"
    elif month == 3:
        month = "มีนาคม"
    elif month == 4:
        month = "เมษายน"
    elif month == 5:
        month = "พฤษภาคม"
    elif month == 6:
        month = "มิถุนายน"
    elif month == 7:
        month = "กรกฎาคม"
    elif month == 8:
        month = "สิงหาคม"
    elif month == 9:
        month = "กันยายน"
    elif month == 10:
        month = "ตุลาคม"
    elif month == 11:
        month = "พฤศจิกายน"
    elif month == 12:
        month = "ธันวาคม"
    th_string = str(day) + " " + str(month) + " " + str(year)
    return th_string

def check_new_content_3_day_ago(html_content, content_last_updated):
    today = datetime.datetime.now()
    d_ago = datetime.timedelta(days = 5)
    d_ago = today - d_ago

    # print(content_last_updated.microsecond)

    if content_last_updated > d_ago and content_last_updated.microsecond == 999999:
        return """
        <div class="movie__cover swiper-slide">
          	<div class="item">
              			<span class="notify-badge orange-badge">ตอนใหม่</span>
        """ + html_content + """
            </div>
            </div>
        """

    elif content_last_updated > d_ago:
        return """
        <div class="movie__cover swiper-slide">
          	<div class="item">
              			<span class="notify-badge red-badge">มาใหม่</span>
        """ + html_content + """
            </div>
            </div>
        """
    else:
        return """
        <div class="movie__cover swiper-slide">
        """ + html_content + """
            </div>
        """


def check_new_content_3_day_ago_not_swiper_template(html_content, content_last_updated):
    today = datetime.datetime.now()
    d_ago = datetime.timedelta(days = 5)
    d_ago = today - d_ago

    if content_last_updated > d_ago and content_last_updated.microsecond == 999999:
        return """
          	<div class="item">
              			<span class="notify-badge orange-badge">ตอนใหม่</span>
        """ + html_content + """
            </div>
        """
    elif content_last_updated > d_ago:
        return """
          	<div class="item">
              			<span class="notify-badge red-badge">มาใหม่</span>
        """ + html_content + """
            </div>
        """
    else:
        return html_content


def check_new_content_3_day_ago_not_swiper_template_V2(html_content, content_last_updated):
    today = datetime.datetime.now()
    d_ago = datetime.timedelta(days = 5)
    d_ago = today - d_ago

    if content_last_updated > d_ago and content_last_updated.microsecond == 999999:
        return """
              			<span class="notify-badge orange-badge">ตอนใหม่</span>
        """ + html_content + """
        """
    elif content_last_updated > d_ago:
        return """
              			<span class="notify-badge red-badge">มาใหม่</span>
        """ + html_content + """
        """
    else:
        return html_content


def id_generator(size=11, chars=string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def check_series_tvshow_continued_episode_cookies(val, content_type, content_str):

    today = datetime.datetime.now()
    d_ago = datetime.timedelta(days = 5)
    d_ago = today - d_ago
    continue_content = request.cookies.get('continue_content')
    if continue_content is not None:
        continue_content = continue_content.split(",")
        for content in continue_content[:45]:
            content = content.split("|")
            if content[0] == content_type and int(val.id) == int(content[1]):

                #----------------------------------------------------------
                # if val.last_updated > d_ago and val.last_updated.microsecond == 999999:
                #     last_season = max(val.seasons, key=lambda seasons: seasons.id)
                #     last_episode = max(last_season.episodes, key=lambda episodes: episodes.id)
                #     sorted_last_season = sorted(last_season.episodes, key=lambda episodes: episodes.id, reverse=False)
                    # if len(sorted_last_season) > 2:
                    #     second_last_episode = sorted_last_season[-2]
                    #     if second_last_episode.youtube_url == str(content[3]):
                    #         return "" + str(val.id) + "/season/" + str(last_season.id) + "/episode/" + str(last_episode.youtube_url)
                #----------------------------------------------------------
                return "" + str(content[1]) + "/season/" + str(content[2]) + "/episode/" + str(content[3])
    if val.last_updated > d_ago and val.last_updated.microsecond == 999999:
        last_season = max(val.seasons, key=lambda seasons: seasons.id)
        last_episode = max(last_season.episodes, key=lambda episodes: episodes.id)
        return "" + str(val.id) + "/season/" + str(last_season.id) + "/episode/" + str(last_episode.youtube_url)
    if content_str == "" or content_str is None:
        return "" + str(val.id)
    return content_str

def generateGenreDescription(value):
        genre_str = ""
        genre_list = value.genres[:4]
        for genre in genre_list:
            genre_str += genre.name
            if genre != genre_list[-1]:
                genre_str += ", "
        return genre_str

@app.template_filter('genre_filter')
def genre_filter(value):
    last_episode_title = ""
    content_str = ""
    if hasattr(value, 'directors') is False:

        today = datetime.datetime.now()
        d_ago = datetime.timedelta(days = 5)
        d_ago = today - d_ago

        if value.last_updated > d_ago and value.last_updated.microsecond == 999999:
            last_season = max(value.seasons, key=lambda seasons: seasons.id)
            last_episode = max(last_season.episodes, key=lambda episodes: episodes.id)
            last_episode_title = last_episode.title
            content_str = "" + str(value.id) + "/season/" + str(last_season.id) + "/episode/" + str(last_episode.youtube_url)
        content_str = check_series_tvshow_continued_episode_cookies(value, "Tvshow", content_str)
        genre_str = generateGenreDescription(value)
        html_content = """
            <div class="content-box">
                <a class="movie__link" href="/tvshow/{0}">
                  <img
                    class="semi-movie__poster lazyload"
                    data-src="/static/tvshow/thumbnail/{1}"
                    alt="{2}"
                  />
                  <h5 class="movie__header">{3}</h5>

                  <p class="genre__description-list" >{5}</p>
                  <p class="content__new-ep">{4}</p>
                </a>
            </div>
         """.format(content_str, value.thumbnail, value.title, value.title, last_episode_title, genre_str)
        return check_new_content_3_day_ago_not_swiper_template(html_content, value.last_updated)
    elif hasattr(value, 'seasons'):
        today = datetime.datetime.now()
        d_ago = datetime.timedelta(days = 5)
        d_ago = today - d_ago

        if value.last_updated > d_ago and value.last_updated.microsecond == 999999:
            last_season = max(value.seasons, key=lambda seasons: seasons.id)
            last_episode = max(last_season.episodes, key=lambda episodes: episodes.id)
            last_episode_title = last_episode.title
            content_str = "" + str(value.id) + "/season/" + str(last_season.id) + "/episode/" + str(last_episode.youtube_url)
        # else:
        content_str = check_series_tvshow_continued_episode_cookies(value, "Series", content_str)
        genre_str = generateGenreDescription(value)
        html_content = """
            <div class="content-box">
                <a class="movie__link" href="/series/{0}">
                  <img
                    class="semi-movie__poster lazyload"
                    data-src="/static/series/thumbnail/{1}"
                    alt="{2}"
                  />
                  <h5 class="movie__header">{3}</h5>
                  <p class="genre__description-list" >{5}</p>
                  <p class="content__new-ep">{4}</p>
                </a>
            </div>
         """.format(content_str, value.thumbnail, value.title, value.title, last_episode_title, genre_str)
        return check_new_content_3_day_ago_not_swiper_template(html_content, value.last_updated)
    elif value.thumbnail is not None:
        genre_str = generateGenreDescription(value)
        html_content = """
                <div class="content-box">
                    <a class="movie__link" href="/movie/{0}">
                      <img
                        class="semi-movie__poster lazyload"
                        data-src="/static/movies/thumbnail/{1}"
                        alt="{2}"
                      />
                      <h5 class="movie__header">{3}</h5>
                  <p class="genre__description-list" >{4}</p>
                    </a>
                </div>
             """.format(value.id, value.thumbnail, value.title, value.title, genre_str)
        return check_new_content_3_day_ago_not_swiper_template(html_content, value.last_updated)
    else:

        genre_str = generateGenreDescription(value)
        html_content = """
                <div class="content-box">
                    <a class="movie__link" href="/movie/{0}">
                      <img
                        class="semi-movie__poster lazyload"
                        data-src="http://img.youtube.com/vi/{1}/mqdefault.jpg"
                        alt="{2}"
                      />
                      <h5 class="movie__header">{3}</h5>
                  <p class="genre__description-list" >{4}</p>
                    </a>
                </div>
             """.format(value.id, value.youtube_url, value.title, value.title, genre_str)
        return check_new_content_3_day_ago_not_swiper_template(html_content, value.last_updated)

@app.template_filter('mobile_main_genre_filter')
def mobile_main_genre_filter(value):
    last_episode_title = ""
    content_str = ""
    if hasattr(value, 'directors') is False:

        today = datetime.datetime.now()
        d_ago = datetime.timedelta(days = 5)
        d_ago = today - d_ago

        if value.last_updated > d_ago and value.last_updated.microsecond == 999999:
            last_season = max(value.seasons, key=lambda seasons: seasons.id)
            last_episode = max(last_season.episodes, key=lambda episodes: episodes.id)
            content_str = "" + str(value.id) + "/season/" + str(last_season.id) + "/episode/" + str(last_episode.youtube_url)
        content_str = check_series_tvshow_continued_episode_cookies(value, "Tvshow", content_str)
        genre_str = generateGenreDescription(value)
        html_content = """
            <div class="mobile__content-box">
                <a class="movie__link" href="/tvshow/{0}">
                  <img
                    class="semi-movie__poster lazyload"
                    data-src="/static/tvshow/thumbnail/{1}"
                    alt="{2}"
                  />
                  <h6 class="mobile__genre-header">{3}</h5>
                </a>
            </div>
         """.format(content_str, value.thumbnail, value.title, value.title)
        return check_new_content_3_day_ago_not_swiper_template(html_content, value.last_updated)
    elif hasattr(value, 'seasons'):
        today = datetime.datetime.now()
        d_ago = datetime.timedelta(days = 5)
        d_ago = today - d_ago

        if value.last_updated > d_ago and value.last_updated.microsecond == 999999:
            last_season = max(value.seasons, key=lambda seasons: seasons.id)
            last_episode = max(last_season.episodes, key=lambda episodes: episodes.id)
            content_str = "" + str(value.id) + "/season/" + str(last_season.id) + "/episode/" + str(last_episode.youtube_url)
        content_str = check_series_tvshow_continued_episode_cookies(value, "Series", content_str)
        genre_str = generateGenreDescription(value)
        html_content = """
            <div class="mobile__content-box">
                <a class="movie__link" href="/series/{0}">
                  <img
                    class="semi-movie__poster lazyload"
                    data-src="/static/series/thumbnail/{1}"
                    alt="{2}"
                  />
                  <h6 class="mobile__genre-header">{3}</h5>
                </a>
            </div>
         """.format(content_str, value.thumbnail, value.title, value.title)
        return check_new_content_3_day_ago_not_swiper_template(html_content, value.last_updated)
    elif value.thumbnail is not None:
        genre_str = generateGenreDescription(value)
        html_content = """
                <div class="mobile__content-box">
                    <a class="movie__link" href="/movie/{0}">
                      <img
                        class="semi-movie__poster lazyload"
                        data-src="/static/movies/thumbnail/{1}"
                        alt="{2}"
                      />
                      <h6 class="mobile__genre-header">{3}</h5>
                    </a>
                </div>
             """.format(value.id, value.thumbnail, value.title, value.title)
        return check_new_content_3_day_ago_not_swiper_template(html_content, value.last_updated)
    else:

        genre_str = generateGenreDescription(value)
        html_content = """
                <div class="mobile__content-box">
                    <a class="movie__link" href="/movie/{0}">
                      <img
                        class="semi-movie__poster lazyload"
                        data-src="http://img.youtube.com/vi/{1}/mqdefault.jpg"
                        alt="{2}"
                      />
                      <h6 class="mobile__genre-header">{3}</h5>
                    </a>
                </div>
             """.format(value.id, value.youtube_url, value.title, value.title)
        return check_new_content_3_day_ago_not_swiper_template(html_content, value.last_updated)

@app.template_filter('suggest_program_filter')
def genre_filter(value):

    content_str = None
    if hasattr(value, 'directors') is False:
        content_str = check_series_tvshow_continued_episode_cookies(value, "Tvshow", content_str)
        return """
            <a class="movie__link" href="/tvshow/{0}">
              <img
                class="suggest__thumbnail lazyload"
                data-src="/static/tvshow/thumbnail/{1}"
                alt="{2}"
              />
            </a>
         """.format(content_str, value.thumbnail, value.title)
    elif hasattr(value, 'seasons'):
        content_str = check_series_tvshow_continued_episode_cookies(value, "Series", content_str)
        return """
                <a class="movie__link" href="/series/{0}">
                  <img
                    class="suggest__thumbnail lazyload"
                    data-src="/static/series/thumbnail/{1}"
                    alt="{2}"
                  />
                </a>
         """.format(content_str, value.thumbnail, value.title)

    return """
                <a class="movie__link" href="/movie/{0}">
                  <img
                    class="suggest__thumbnail lazyload"
                    data-src="/static/movies/thumbnail/{1}"
                    alt="{2}"
                  />
                </a>
         """.format(value.id, value.thumbnail, value.title)

@app.template_filter('suggest_program_carousel_filter')
def genre_filter(value):

    content_str = None
    if hasattr(value, 'directors') is False:
        content_str = check_series_tvshow_continued_episode_cookies(value, "Tvshow", content_str)
        return """
            <a class="movie__link" href="/tvshow/{0}">
              <img
                src="/static/tvshow/thumbnail/{1}"
                class="d-block w-100"
                alt="{2}"
              />
            </a>
         """.format(content_str, value.thumbnail, value.title)
    elif hasattr(value, 'seasons'):
        content_str = check_series_tvshow_continued_episode_cookies(value, "Series", content_str)
        return """
            <a class="movie__link" href="/series/{0}">
              <img
                src="/static/series/thumbnail/{1}"
                class="d-block w-100"
                alt="{2}"
              />
            </a>
         """.format(content_str, value.thumbnail, value.title)
    return """
            <a class="movie__link" href="/movie/{0}">
              <img
                src="/static/movies/thumbnail/{1}"
                class="d-block w-100"
                alt="{2}"
              />
            </a>
         """.format(value.id, value.thumbnail, value.title)

@app.template_filter('mobile_tablet_thumbnail_filter')
def mobile_tablet_thumbnail_filter(value):
    if hasattr(value, 'directors') is False:
        html_content = """
                <a class="movie__link" href="/tvshow/{0}">
                  <img
                    class="mobile-tablet__thumbnail lazyload"
                    data-src="/static/tvshow/thumbnail/{1}"
                    alt="{2}"
                  />
                  <h5 class="movie__header">{3}</h5>
                </a>
         """.format(value.id, value.thumbnail, value.title, value.title)
        return check_new_content_3_day_ago_not_swiper_template(html_content, value.last_updated)
    elif hasattr(value, 'seasons'):
        html_content = """
                <a class="movie__link" href="/series/{0}">
                  <img
                    class="mobile-tablet__thumbnail lazyload"
                    data-src="/static/series/thumbnail/{1}"
                    alt="{2}"
                  />
                  <h5 class="movie__header">{3}</h5>
                </a>
         """.format(value.id, value.thumbnail, value.title, value.title)
        return check_new_content_3_day_ago_not_swiper_template(html_content, value.last_updated)

    if value.thumbnail is not None:
        html_content = """
                    <a class="movie__link" href="/movie/{0}">
                      <img
                        class="mobile-tablet__thumbnail lazyload"
                        data-src="/static/movies/thumbnail/{1}"
                        alt="{2}"
                      />
                      <h5 class="movie__header">{3}</h5>
                    </a>
             """.format(value.id, value.thumbnail, value.title, value.title)
        return check_new_content_3_day_ago_not_swiper_template(html_content, value.last_updated)
    else:
        html_content = """
                    <a class="movie__link" href="/movie/{0}">
                      <img
                        class="mobile-tablet__thumbnail lazyload"
                        data-src="http://img.youtube.com/vi/{1}/mqdefault.jpg"
                        alt="{2}"
                      />
                      <h5 class="movie__header">{3}</h5>
                    </a>
             """.format(value.id, value.youtube_url, value.title, value.title)
        return check_new_content_3_day_ago_not_swiper_template(html_content, value.last_updated)

@app.template_filter('mobile_tablet_thumbnail_filter_V2')
def mobile_tablet_thumbnail_filter_V2(value):
    if hasattr(value, 'directors') is False:
        html_content = """
                <a class="movie__link" href="/tvshow/{0}">
                  <img
                    class="lazyload"
                    data-src="/static/tvshow/thumbnail/{1}"
                    alt="{2}"
                  />
                  <h5 class="movie__header">{3}</h5>
                </a>
         """.format(value.id, value.thumbnail, value.title, value.title)
        return check_new_content_3_day_ago_not_swiper_template_V2(html_content, value.last_updated)
    elif hasattr(value, 'seasons'):
        html_content = """
                <a class="movie__link" href="/series/{0}">
                  <img
                    class="lazyload"
                    data-src="/static/series/thumbnail/{1}"
                    alt="{2}"
                  />
                  <h5 class="movie__header">{3}</h5>
                </a>
         """.format(value.id, value.thumbnail, value.title, value.title)
        return check_new_content_3_day_ago_not_swiper_template_V2(html_content, value.last_updated)

    if value.thumbnail is not None:
        html_content = """
                    <a class="movie__link" href="/movie/{0}">
                      <img
                        class="lazyload"
                        data-src="/static/movies/thumbnail/{1}"
                        alt="{2}"
                      />
                      <h5 class="movie__header">{3}</h5>
                    </a>
             """.format(value.id, value.thumbnail, value.title, value.title)
        return check_new_content_3_day_ago_not_swiper_template_V2(html_content, value.last_updated)
    else:
        html_content = """
                    <a class="movie__link" href="/movie/{0}">
                      <img
                        class="lazyload"
                        data-src="http://img.youtube.com/vi/{1}/mqdefault.jpg"
                        alt="{2}"
                      />
                      <h5 class="movie__header">{3}</h5>
                    </a>
             """.format(value.id, value.youtube_url, value.title, value.title)
        return check_new_content_3_day_ago_not_swiper_template_V2(html_content, value.last_updated)

@app.template_filter('tablet_thumbnail_filter_new_release')
def tablet_thumbnail_filter_new_release(value):

    content_str = None
    if hasattr(value, 'directors') is False and value.last_updated.microsecond == 999999 or hasattr(value, 'seasons') and value.last_updated.microsecond == 999999:
        last_season = max(value.seasons, key=lambda seasons: seasons.id)
        last_episode = max(last_season.episodes, key=lambda episodes: episodes.id)
        last_episode_title = last_episode.title
        content_url = "" + str(value.id) + "/season/" + str(last_season.id) + "/episode/" + str(last_episode.youtube_url)
    else:
        content_url = "" + str(value.id)
        last_episode_title = ""

    if hasattr(value, 'directors') is False:
        content_url = check_series_tvshow_continued_episode_cookies(value, "Tvshow", content_str)
    elif hasattr(value, 'seasons'):
        content_url = check_series_tvshow_continued_episode_cookies(value, "Series", content_str)

    if hasattr(value, 'directors') is False:
        genre_str = generateGenreDescription(value)
        html_content = """
                <a class="movie__link" href="/tvshow/{0}">
                  <img
                    class="mobile-tablet__thumbnail lazyload"
                    data-src="/static/tvshow/thumbnail/{1}"
                    alt="{2}"
                  />
                  <h5 class="movie__header">{3}</h5>
                  <p class="genre__description-list" >{5}</p>
                  <p class="content__new-ep">{4}</p>
                </a>
         """.format(content_url, value.thumbnail, value.title, value.title, last_episode_title, genre_str)
        return check_new_content_3_day_ago_not_swiper_template(html_content, value.last_updated)
    elif hasattr(value, 'seasons'):
        genre_str = generateGenreDescription(value)
        html_content = """
                <a class="movie__link" href="/series/{0}">
                  <img
                    class="mobile-tablet__thumbnail lazyload"
                    data-src="/static/series/thumbnail/{1}"
                    alt="{2}"
                  />
                  <h5 class="movie__header">{3}</h5>
                  <p class="genre__description-list" >{5}</p>
                  <p class="content__new-ep">{4}</p>
                </a>
         """.format(content_url, value.thumbnail, value.title, value.title, last_episode_title, genre_str)
        return check_new_content_3_day_ago_not_swiper_template(html_content, value.last_updated)

    if value.thumbnail is not None:
        genre_str = generateGenreDescription(value)
        html_content = """
                    <a class="movie__link" href="/movie/{0}">
                      <img
                        class="mobile-tablet__thumbnail lazyload"
                        data-src="/static/movies/thumbnail/{1}"
                        alt="{2}"
                      />
                      <h5 class="movie__header">{3}</h5>
                  <p class="genre__description-list" >{4}</p>
                    </a>
             """.format(value.id, value.thumbnail, value.title, value.title, genre_str)
        return check_new_content_3_day_ago_not_swiper_template(html_content, value.last_updated)
    else:
        genre_str = generateGenreDescription(value)
        html_content = """
                    <a class="movie__link" href="/movie/{0}">
                      <img
                        class="mobile-tablet__thumbnail lazyload"
                        data-src="http://img.youtube.com/vi/{1}/mqdefault.jpg"
                        alt="{2}"
                      />
                      <h5 class="movie__header">{3}</h5>
                  <p class="genre__description-list" >{4}</p>
                    </a>
             """.format(value.id, value.youtube_url, value.title, value.title, genre_str)
        return check_new_content_3_day_ago_not_swiper_template(html_content, value.last_updated)


@app.template_filter('mobile_tablet_thumbnail_filter_new_release')
def mobile_tablet_thumbnail_filter_new_release(value):

    content_str = None
    if hasattr(value, 'directors') is False and value.last_updated.microsecond == 999999 or hasattr(value, 'seasons') and value.last_updated.microsecond == 999999:
        last_season = max(value.seasons, key=lambda seasons: seasons.id)
        last_episode = max(last_season.episodes, key=lambda episodes: episodes.id)
        last_episode_title = last_episode.title
        content_url = "" + str(value.id) + "/season/" + str(last_season.id) + "/episode/" + str(last_episode.youtube_url)
    else:
        content_url = "" + str(value.id)
        last_episode_title = ""

    if hasattr(value, 'directors') is False:
        content_url = check_series_tvshow_continued_episode_cookies(value, "Tvshow", content_str)
    elif hasattr(value, 'seasons'):
        content_url = check_series_tvshow_continued_episode_cookies(value, "Series", content_str)

    if hasattr(value, 'directors') is False:
        genre_str = generateGenreDescription(value)
        html_content = """

                <a class="movie__link" href="/tvshow/{0}">
                  <img
                    class="mobile-tablet__thumbnail lazyload"
                    data-src="/static/tvshow/thumbnail/{1}"
                    alt="{2}"
                  />
                  <h5 class="movie__header">{3}</h5>
                  <p class="genre__description-list" >{5}</p>
                  <p class="content__new-ep">{4}</p>
                </a>
         """.format(content_url, value.thumbnail, value.title, value.title, last_episode_title, genre_str)
        return check_new_content_3_day_ago_not_swiper_template_V2(html_content, value.last_updated)
    elif hasattr(value, 'seasons'):
        genre_str = generateGenreDescription(value)
        html_content = """

                <a class="movie__link" href="/series/{0}">
                  <img
                    class="mobile-tablet__thumbnail lazyload"
                    data-src="/static/series/thumbnail/{1}"
                    alt="{2}"
                  />
                  <h5 class="movie__header">{3}</h5>
                  <p class="genre__description-list" >{5}</p>
                  <p class="content__new-ep">{4}</p>
                </a>
         """.format(content_url, value.thumbnail, value.title, value.title, last_episode_title, genre_str)
        return check_new_content_3_day_ago_not_swiper_template_V2(html_content, value.last_updated)

    elif value.thumbnail is not None:
        genre_str = generateGenreDescription(value)
        html_content = """

                    <a class="movie__link" href="/movie/{0}">
                      <img
                        class="mobile-tablet__thumbnail lazyload"
                        data-src="/static/movies/thumbnail/{1}"
                        alt="{2}"
                      />
                      <h5 class="movie__header">{3}</h5>
                  <p class="genre__description-list" >{4}</p>
                    </a>
             """.format(value.id, value.thumbnail, value.title, value.title, genre_str)
        return check_new_content_3_day_ago_not_swiper_template_V2(html_content, value.last_updated)
    else:
        genre_str = generateGenreDescription(value)
        html_content = """

                    <a class="movie__link" href="/movie/{0}">
                      <img
                        class="mobile-tablet__thumbnail lazyload"
                        data-src="http://img.youtube.com/vi/{1}/mqdefault.jpg"
                        alt="{2}"
                      />
                      <h5 class="movie__header">{3}</h5>
                  <p class="genre__description-list" >{4}</p>
                    </a>
             """.format(value.id, value.youtube_url, value.title, value.title, genre_str)
        return check_new_content_3_day_ago_not_swiper_template_V2(html_content, value.last_updated)

@app.template_filter('mobile_tablet_thumbnail_filter_new_release_V2')
def mobile_tablet_thumbnail_filter_new_release_V2(value):

    content_str = None

    if hasattr(value, 'directors') is False and value.last_updated.microsecond == 999999 or hasattr(value, 'seasons') and value.last_updated.microsecond == 999999:
        last_season = max(value.seasons, key=lambda seasons: seasons.id)
        last_episode = max(last_season.episodes, key=lambda episodes: episodes.id)
        last_episode_title = last_episode.title
        content_url = "" + str(value.id) + "/season/" + str(last_season.id) + "/episode/" + str(last_episode.youtube_url)
    else:
        content_url = "" + str(value.id)
        last_episode_title = ""

    if hasattr(value, 'directors') is False:
        content_url = check_series_tvshow_continued_episode_cookies(value, "Tvshow", content_str)
    elif hasattr(value, 'seasons'):
        content_url = check_series_tvshow_continued_episode_cookies(value, "Series", content_str)

    if hasattr(value, 'directors') is False:
        genre_str = generateGenreDescription(value)
        html_content = """
                <a class="movie__link" href="/tvshow/{0}">
                  <img
                    class="lazyload"
                    data-src="/static/tvshow/thumbnail/{1}"
                    alt="{2}"
                  />
                  <h6 class="movie__header">{3}</h5>

                  <p class="genre__description-list" >{5}</p>
                  <p class="content__new-ep">{4}</p>
                </a>
         """.format(content_url, value.thumbnail, value.title, value.title, last_episode_title, genre_str)
        return check_new_content_3_day_ago_not_swiper_template_V2(html_content, value.last_updated)
    elif hasattr(value, 'seasons'):
        genre_str = generateGenreDescription(value)
        html_content = """
                <a class="movie__link" href="/series/{0}">
                  <img
                    class="lazyload"
                    data-src="/static/series/thumbnail/{1}"
                    alt="{2}"
                  />
                  <h6 class="movie__header">{3}</h5>
                  <p class="genre__description-list" >{5}</p>
                  <p class="content__new-ep">{4}</p>
                </a>
         """.format(content_url, value.thumbnail, value.title, value.title, last_episode_title, genre_str)
        return check_new_content_3_day_ago_not_swiper_template_V2(html_content, value.last_updated)

    elif value.thumbnail is not None:
        genre_str = generateGenreDescription(value)
        html_content = """
                    <a class="movie__link" href="/movie/{0}">
                      <img
                        class="lazyload"
                        data-src="/static/movies/thumbnail/{1}"
                        alt="{2}"
                      />
                      <h6 class="movie__header">{3}</h5>
                  <p class="genre__description-list" >{4}</p>
                    </a>
             """.format(value.id, value.thumbnail, value.title, value.title, genre_str)
        return check_new_content_3_day_ago_not_swiper_template_V2(html_content, value.last_updated)
    else:
        genre_str = generateGenreDescription(value)
        html_content = """
                    <a class="movie__link" href="/movie/{0}">
                      <img
                        class="lazyload"
                        data-src="http://img.youtube.com/vi/{1}/mqdefault.jpg"
                        alt="{2}"
                      />
                      <h6 class="movie__header">{3}</h5>
                  <p class="genre__description-list" >{4}</p>
                    </a>
             """.format(value.id, value.youtube_url, value.title, value.title, genre_str)
        return check_new_content_3_day_ago_not_swiper_template_V2(html_content, value.last_updated)


@app.template_filter('continue_content_thumbnail_filter')
def continue_content_thumbnail_filter(content_json):
    if content_json['type'] == "Tvshow":
        html_content = """
            <div class="content-box">
                <a class="movie__link" href="/tvshow/{0}/season/{1}/episode/{2}">
                  <img
                    class="mobile-tablet__thumbnail lazyload"
                    data-src="/static/tvshow/thumbnail/{3}"
                    alt="{4}"
                  />
                  <h5 class="movie__header">{5}</h5>
                </a>
            </div>
         """.format(content_json['id'], content_json["season"], content_json["episode"], content_json['thumbnail'], content_json['title'], content_json['title'])
        return check_new_content_3_day_ago_not_swiper_template(html_content, content_json['last_updated'])
    # Series content
    elif content_json['type'] == "Series":
        html_content = """
            <div class="content-box">
                <a class="movie__link" href="/series/{0}/season/{1}/episode/{2}">
                  <img
                    class="mobile-tablet__thumbnail lazyload"
                    data-src="/static/series/thumbnail/{3}"
                    alt="{4}"
                  />
                  <h5 class="movie__header">{5}</h5>
                </a>
            </div>
         """.format(content_json['id'], content_json["season"], content_json["episode"], content_json['thumbnail'], content_json['title'], content_json['title'])
        return check_new_content_3_day_ago_not_swiper_template(html_content, content_json['last_updated'])
    # Movie content with image from static folder
    elif content_json['type'] == "Movie" and content_json['thumbnail'] is not None:
        html_content = """
            <div class="content-box">
                    <a class="movie__link" href="/movie/{0}">
                      <img
                        class="mobile-tablet__thumbnail lazyload"
                        data-src="/static/movies/thumbnail/{1}"
                        alt="{2}"
                      />
                      <h5 class="movie__header">{3}</h5>
                    </a>
            </div>
         """.format(content_json['id'], content_json['thumbnail'], content_json['title'], content_json['title'])
        return check_new_content_3_day_ago_not_swiper_template(html_content, content_json['last_updated'])
    # Movie content with youtube image
    else:
        html_content = """
            <div class="content-box">
                    <a class="movie__link" href="/movie/{0}">
                      <img
                        class="mobile-tablet__thumbnail lazyload"
                        data-src="http://img.youtube.com/vi/{1}/mqdefault.jpg"
                        alt="{2}"
                      />
                      <h5 class="movie__header">{3}</h5>
                    </a>
            </div>
         """.format(content_json['id'], content_json['youtube_url'], content_json['title'], content_json['title'])
        return check_new_content_3_day_ago_not_swiper_template(html_content, content_json['last_updated'])

@app.template_filter('mobile_continue_content_thumbnail_filter')
def mobile_continue_content_thumbnail_filter(content_json):
    if content_json['type'] == "Tvshow":
        html_content = """
                <a class="movie__link" href="/tvshow/{0}/season/{1}/episode/{2}">
                  <img
                    class="mobile-tablet__thumbnail lazyload"
                    data-src="/static/tvshow/thumbnail/{3}"
                    alt="{4}"
                  />
                  <h6 class="mobile__genre-header">{5}</h6>
                </a>
         """.format(content_json['id'], content_json["season"], content_json["episode"], content_json['thumbnail'], content_json['title'], content_json['title'])
        return check_new_content_3_day_ago_not_swiper_template(html_content, content_json['last_updated'])
    # Series content
    elif content_json['type'] == "Series":
        html_content = """
                <a class="movie__link" href="/series/{0}/season/{1}/episode/{2}">
                  <img
                    class="mobile-tablet__thumbnail lazyload"
                    data-src="/static/series/thumbnail/{3}"
                    alt="{4}"
                  />
                  <h6 class="mobile__genre-header">{5}</h6>
                </a>
         """.format(content_json['id'], content_json["season"], content_json["episode"], content_json['thumbnail'], content_json['title'], content_json['title'])
        return check_new_content_3_day_ago_not_swiper_template(html_content, content_json['last_updated'])
    # Movie content with image from static folder
    elif content_json['type'] == "Movie" and content_json['thumbnail'] is not None:
        html_content = """
                    <a class="movie__link" href="/movie/{0}">
                      <img
                        class="mobile-tablet__thumbnail lazyload"
                        data-src="/static/movies/thumbnail/{1}"
                        alt="{2}"
                      />
                      <h6 class="mobile__genre-header">{3}</h6>
                    </a>
         """.format(content_json['id'], content_json['thumbnail'], content_json['title'], content_json['title'])
        return check_new_content_3_day_ago_not_swiper_template(html_content, content_json['last_updated'])
    # Movie content with youtube image
    else:
        html_content = """
                    <a class="movie__link" href="/movie/{0}">
                      <img
                        class="mobile-tablet__thumbnail lazyload"
                        data-src="http://img.youtube.com/vi/{1}/mqdefault.jpg"
                        alt="{2}"
                      />
                      <h6 class="mobile__genre-header">{3}</h6>
                    </a>
         """.format(content_json['id'], content_json['youtube_url'], content_json['title'], content_json['title'])
        return check_new_content_3_day_ago_not_swiper_template(html_content, content_json['last_updated'])

@app.template_filter('continue_content_mobile_tablet_thumbnail_filter_V2')
def continue_content_mobile_tablet_thumbnail_filter_V2(content_json):
    # TVshow Content
    if content_json['type'] == "Tvshow":
        html_content = """
                <a class="movie__link" href="/tvshow/{0}/season/{1}/episode/{2}">
                  <img
                    class="lazyload"
                    data-src="/static/tvshow/thumbnail/{3}"
                    alt="{4}"
                  />
                  <h5 class="movie__header">{5}</h5>
                </a>
         """.format(content_json['id'], content_json["season"], content_json["episode"], content_json['thumbnail'], content_json['title'], content_json['title'])
        return check_new_content_3_day_ago_not_swiper_template_V2(html_content, content_json['last_updated'])
    # Series content
    elif content_json['type'] == "Series":
        html_content = """
                <a class="movie__link" href="/series/{0}/season/{1}/episode/{2}">
                  <img
                    class="lazyload"
                    data-src="/static/series/thumbnail/{3}"
                    alt="{4}"
                  />
                  <h5 class="movie__header">{5}</h5>
                </a>
         """.format(content_json['id'], content_json["season"], content_json["episode"], content_json['thumbnail'], content_json['title'], content_json['title'])
        return check_new_content_3_day_ago_not_swiper_template_V2(html_content, content_json['last_updated'])
    # Movie content with image from static folder
    elif content_json['type'] == "Movie" and content_json['thumbnail'] is not None:
        html_content = """
                    <a class="movie__link" href="/movie/{0}">
                      <img
                        class="lazyload"
                        data-src="/static/movies/thumbnail/{1}"
                        alt="{2}"
                      />
                      <h5 class="movie__header">{3}</h5>
                    </a>
         """.format(content_json['id'], content_json['thumbnail'], content_json['title'], content_json['title'])
        return check_new_content_3_day_ago_not_swiper_template_V2(html_content, content_json['last_updated'])
    # Movie content with youtube image
    else:
        html_content = """
                    <a class="movie__link" href="/movie/{0}">
                      <img
                        class="lazyload"
                        data-src="http://img.youtube.com/vi/{1}/mqdefault.jpg"
                        alt="{2}"
                      />
                      <h5 class="movie__header">{3}</h5>
                    </a>
         """.format(content_json['id'], content_json['youtube_url'], content_json['title'], content_json['title'])
        return check_new_content_3_day_ago_not_swiper_template_V2(html_content, content_json['last_updated'])

@app.template_filter('swiper_template')
def swiper_template(vdosets, title, genre, css_className):

    if css_className == "trending_content" and title == "รายการยอดนิยมล่าสุด":
        header_html = """
                  <div class="row" style="margin: 40px 0;">
                    <div class="col-8 col-md-10 col-lg-11" style="margin-top: 5px;">
                      <h2 class="topic__header">{0}</h2>
                    </div>

                    <div class="col-4 col-md-2 col-lg-1 text-right" style="color: #58667e;">
                      <a
                        href="/genre/80"
                        style="text-decoration: none; color: black;"
                      >
                        <button
                          type="button"
                          class="btn btn-secondary"
                          style="font-size: 14px;"
                        >
                          ดูทั้งหมด
                        </button>
                      </a>
                    </div>
                  </div>""".format(title, genre)

    elif css_className == "new-release":

        if title == "หนังใหม่และล่าสุด":
            header_html = """
                      <div class="row" style="margin: 40px 0;">
                        <div class="col-8 col-md-10 col-lg-11" style="margin-top: 5px;">
                          <h2 class="topic__header">{0}</h2>
                        </div>

                        <div class="col-4 col-md-2 col-lg-1 text-right" style="color: #58667e;">
                          <a
                            href="/movie/genres/{1}"
                            style="text-decoration: none; color: black;"
                          >
                            <button
                              type="button"
                              class="btn btn-secondary"
                              style="font-size: 14px;"
                            >
                              ดูทั้งหมด
                            </button>
                          </a>
                        </div>
                      </div>""".format(title, genre)
        elif title == "ซีรี่ส์ใหม่และตอนล่าสุด":
            header_html = """
                      <div class="row" style="margin: 40px 0;">
                        <div class="col-8 col-md-10 col-lg-11" style="margin-top: 5px;">
                          <h2 class="topic__header">{0}</h2>
                        </div>

                        <div class="col-4 col-md-2 col-lg-1 text-right" style="color: #58667e;">
                          <a
                            href="/series/genres/{1}"
                            style="text-decoration: none; color: black;"
                          >
                            <button
                              type="button"
                              class="btn btn-secondary"
                              style="font-size: 14px;"
                            >
                              ดูทั้งหมด
                            </button>
                          </a>
                        </div>
                      </div>""".format(title, genre)
        elif title == "รายการทีวีใหม่และล่าสุด":
            header_html = """
                      <div class="row" style="margin: 40px 0;">
                        <div class="col-8 col-md-10 col-lg-11" style="margin-top: 5px;">
                          <h2 class="topic__header">{0}</h2>
                        </div>

                        <div class="col-4 col-md-2 col-lg-1 text-right" style="color: #58667e;">
                          <a
                            href="/tvshow/genres/{1}/page/1"
                            style="text-decoration: none; color: black;"
                          >
                            <button
                              type="button"
                              class="btn btn-secondary"
                              style="font-size: 14px;"
                            >
                              ดูทั้งหมด
                            </button>
                          </a>
                        </div>
                      </div>""".format(title, genre)
        else:
            header_html = """
                      <div class="row" style="margin: 40px 0;">
                        <div class="col-8 col-md-10 col-lg-11" style="margin-top: 5px;">
                          <h2 class="topic__header">{0}</h2>
                        </div>

                        <div class="col-4 col-md-2 col-lg-1 text-right" style="color: #58667e;">
                          <a
                            href="/genre/{1}"
                            style="text-decoration: none; color: black;"
                          >
                            <button
                              type="button"
                              class="btn btn-secondary"
                              style="font-size: 14px;"
                            >
                              ดูทั้งหมด
                            </button>
                          </a>
                        </div>
                      </div>""".format(title, genre)

    elif hasattr(vdosets[0], 'directors') is False:
        if css_className == "trending_content":
            genre = Genre.query.filter(Genre.name.contains("ยอดนิยม")).first().id
        elif genre != "tvshow":
            genre = Genre.query.filter(Genre.name == genre).first().id
        header_html = """
                  <div class="row" style="margin: 40px 0;">
                    <div class="col-8 col-md-10 col-lg-11" style="margin-top: 5px;">
                      <h2 class="topic__header">{0}</h2>
                    </div>

                    <div class="col-4 col-md-2 col-lg-1 text-right" style="color: #58667e;">
                      <a
                        href="/tvshow/genres/{1}/page/1"
                        style="text-decoration: none; color: black;"
                      >
                        <button
                          type="button"
                          class="btn btn-secondary"
                          style="font-size: 14px;"
                        >
                          ดูทั้งหมด
                        </button>
                      </a>
                    </div>
                  </div>""".format(title, genre)
    elif hasattr(vdosets[0], 'seasons'):
        if css_className == "trending_content":
            genre = Genre.query.filter(Genre.name.contains("ยอดนิยม")).first().id
        elif genre != "series":
            genre = Genre.query.filter(Genre.name == genre).first().id
        header_html = """
                  <div class="row" style="margin: 40px 0;">
                    <div class="col-8 col-md-10 col-lg-11" style="margin-top: 5px;">
                      <h2 class="topic__header">{0}</h2>
                    </div>

                    <div class="col-4 col-md-2 col-lg-1 text-right" style="color: #58667e;">
                      <a
                        href="/series/genres/{1}/page/1"
                        style="text-decoration: none; color: black;"
                      >
                        <button
                          type="button"
                          class="btn btn-secondary"
                          style="font-size: 14px;"
                        >
                          ดูทั้งหมด
                        </button>
                      </a>
                    </div>
                  </div>""".format(title, genre)
    else:
        if css_className == "trending_content":
            genre = Genre.query.filter(Genre.name.contains("ยอดนิยม")).first().id
        elif genre != "movie":
            genre = Genre.query.filter(Genre.name == genre).first().id
        header_html = """
                  <div class="row" style="margin: 40px 0;">
                    <div class="col-8 col-md-10 col-lg-11" style="margin-top: 5px;">
                      <h2 class="topic__header">{0}</h2>
                    </div>

                    <div class="col-4 col-md-2 col-lg-1 text-right" style="color: #58667e;">
                      <a
                        href="/movie/genres/{1}/page/1"
                        style="text-decoration: none; color: black;"
                      >
                        <button
                          type="button"
                          class="btn btn-secondary"
                          style="font-size: 14px;"
                        >
                          ดูทั้งหมด
                        </button>
                      </a>
                    </div>
                  </div>""".format(title, genre)

    slide_element_html = ""

    for vdo in vdosets:
        html_content = ""

        content_str = None
        if hasattr(vdo, 'directors') is False:
            content_str = check_series_tvshow_continued_episode_cookies(vdo, "Tvshow", content_str)
            genre_str = generateGenreDescription(vdo)
            html_content = """
                    <a class="movie__link" href="/tvshow/{0}">
                      <img
                        class="semi-movie__poster"
                        src="/static/tvshow/thumbnail/{1}"
                        alt="{2}"
                      />
                      <h5 class="movie__header">{3}</h5>
                  <p class="genre__description-swiper-list" >{4}</p>
                    </a>
            """.format(content_str, vdo.thumbnail, vdo.title, vdo.title, genre_str)
        elif hasattr(vdo, 'seasons'):
            content_str = check_series_tvshow_continued_episode_cookies(vdo, "Series", content_str)
            genre_str = generateGenreDescription(vdo)
            html_content = """
                    <a class="movie__link" href="/series/{0}">
                      <img
                        class="semi-movie__poster"
                        src="/static/series/thumbnail/{1}"
                        alt="{2}"
                      />
                      <h5 class="movie__header">{3}</h5>
                  <p class="genre__description-swiper-list" >{4}</p>
                    </a>
            """.format(content_str, vdo.thumbnail, vdo.title, vdo.title, genre_str)
        elif vdo.thumbnail is not None:

            genre_str = generateGenreDescription(vdo)
            html_content = """
                    <a class="movie__link" href="/movie/{0}">
                      <img
                        class="semi-movie__poster"
                        src="/static/movies/thumbnail/{1}"
                        alt="{2}"
                      />
                      <h5 class="movie__header">{3}</h5>
                  <p class="genre__description-swiper-list" >{4}</p>
                    </a>
            """.format(vdo.id, vdo.thumbnail, vdo.title, vdo.title, genre_str)
        else:
            genre_str = generateGenreDescription(vdo)
            html_content = """
                    <a class="movie__link" href="/movie/{0}">
                      <img
                        class="semi-movie__poster"
                        src="http://img.youtube.com/vi/{1}/mqdefault.jpg"
                        alt="{2}"
                      />
                      <h5 class="movie__header">{3}</h5>

                  <p class="genre__description-swiper-list" >{4}</p>
                    </a>
            """.format(vdo.id, vdo.youtube_url, vdo.title, vdo.title, genre_str)

        # if vdo.last_updated > d_ago:
        #     slide_element_html += """
        #
        #     </div>
        #     </div>
        #     """
        # else:
        #     slide_element_html += """
        #     </div>
        #     """
        slide_element_html += check_new_content_3_day_ago(html_content, vdo.last_updated)

    swiper_className = "swiper-" + css_className
    swiper_button_prev_className = "swiper-button-prev-" + css_className
    slider_open_tag_html = """
          <div class="swiper {0}">
            <div class="swiper-button-prev {1}"></div>
            <!-- Additional required wrapper -->
            <div class="swiper-wrapper">
              <!-- Slides -->
    """.format(swiper_className, swiper_button_prev_className)

    swiper_pagination_className = "swiper-pagination-" + css_className
    swiper_button_next_className = "swiper-button-next-" + css_className
    slider_close_tag_html = """
            </div>
            <!-- If we need pagination -->
            <!--<div class="swiper-pagination {0}"></div>-->

            <!-- If we need navigation buttons -->

            <!-- If we need scrollbar -->
            <div class="swiper-scrollbar"></div>
            <div class="swiper-button-next {1}"></div>
          </div>
    """.format(swiper_pagination_className, swiper_button_next_className)

    slider_js = """
          <script>
            var swiper = new Swiper(".{0}", {{
                  slidesPerView: 2,
                  slidesPerGroup: 2,
                  spaceBetween: 5,
                              lazy: true,
                                  preloadImages: false,
    watchOverflow: true,
                          shortSwipes: false,
              breakpoints: {{
                // when window width is >= 320px
                880: {{

                  slidesPerView: 5,
                  slidesPerGroup: 5,
                }},
              }},
              pagination: {{
                el: ".{1}",
                clickable: false,
              }},
              navigation: {{
                nextEl: ".{2}",
                prevEl: ".{3}",
              }},
            }});
          </script>
    """.format(swiper_className, swiper_pagination_className, swiper_button_next_className, swiper_button_prev_className )

    return header_html + slider_open_tag_html + slide_element_html + slider_close_tag_html + slider_js

@app.template_filter('swiper_template_new_release')
def swiper_template_new_release(vdosets, title, genre, css_className):

    if css_className == "new-release":

        if title == "หนังใหม่และล่าสุด":
            header_html = """
                      <div class="row" style="margin: 40px 0;">
                        <div class="col-8 col-md-10 col-lg-11" style="margin-top: 5px;">
                          <h2 class="topic__header">{0}</h2>
                        </div>

                        <div class="col-4 col-md-2 col-lg-1 text-right" style="color: #58667e;">
                          <a
                            href="/movie/genres/{1}"
                            style="text-decoration: none; color: black;"
                          >
                            <button
                              type="button"
                              class="btn btn-secondary"
                              style="font-size: 14px;"
                            >
                              ดูทั้งหมด
                            </button>
                          </a>
                        </div>
                      </div>""".format(title, genre)
        elif title == "ซีรี่ส์ใหม่และตอนล่าสุด":
            header_html = """
                      <div class="row" style="margin: 40px 0;">
                        <div class="col-8 col-md-10 col-lg-11" style="margin-top: 5px;">
                          <h2 class="topic__header">{0}</h2>
                        </div>

                        <div class="col-4 col-md-2 col-lg-1 text-right" style="color: #58667e;">
                          <a
                            href="/series/genres/{1}"
                            style="text-decoration: none; color: black;"
                          >
                            <button
                              type="button"
                              class="btn btn-secondary"
                              style="font-size: 14px;"
                            >
                              ดูทั้งหมด
                            </button>
                          </a>
                        </div>
                      </div>""".format(title, genre)
        elif title == "รายการทีวีใหม่และตอนล่าสุด":
            header_html = """
                      <div class="row" style="margin: 40px 0;">
                        <div class="col-8 col-md-10 col-lg-11" style="margin-top: 5px;">
                          <h2 class="topic__header">{0}</h2>
                        </div>

                        <div class="col-4 col-md-2 col-lg-1 text-right" style="color: #58667e;">
                          <a
                            href="/tvshow/genres/{1}"
                            style="text-decoration: none; color: black;"
                          >
                            <button
                              type="button"
                              class="btn btn-secondary"
                              style="font-size: 14px;"
                            >
                              ดูทั้งหมด
                            </button>
                          </a>
                        </div>
                      </div>""".format(title, genre)
        else:
            header_html = """
                      <div class="row" style="margin: 40px 0;">
                        <div class="col-8 col-md-10 col-lg-11" style="margin-top: 5px;">
                          <h2 class="topic__header">{0}</h2>
                        </div>

                        <div class="col-4 col-md-2 col-lg-1 text-right" style="color: #58667e;">
                          <a
                            href="/genre/{1}"
                            style="text-decoration: none; color: black;"
                          >
                            <button
                              type="button"
                              class="btn btn-secondary"
                              style="font-size: 14px;"
                            >
                              ดูทั้งหมด
                            </button>
                          </a>
                        </div>
                      </div>""".format(title, genre)
    elif css_className == "new-content-release" or css_className == "new-ep-release":
            header_html = """
                      <div class="row" style="margin: 40px 0;">
                        <div class="col-8 col-md-10 col-lg-11" style="margin-top: 5px;">
                          <h2 class="topic__header">{0}</h2>
                        </div>

                        <div class="col-4 col-md-2 col-lg-1 text-right" style="color: #58667e;">
                          <a
                            href="/genre/{1}"
                            style="text-decoration: none; color: black;"
                          >
                            <button
                              type="button"
                              class="btn btn-secondary"
                              style="font-size: 14px;"
                            >
                              ดูทั้งหมด
                            </button>
                          </a>
                        </div>
                      </div>""".format(title, genre)


    elif hasattr(vdosets[0], 'directors') is False:
        header_html = """
                  <div class="row" style="margin: 40px 0;">
                    <div class="col-8 col-md-10 col-lg-11" style="margin-top: 5px;">
                      <h2 class="topic__header">{0}</h2>
                    </div>

                    <div class="col-4 col-md-2 col-lg-1 text-right" style="color: #58667e;">
                      <a
                        href="/tvshow/genres/{1}"
                        style="text-decoration: none; color: black;"
                      >
                        <button
                          type="button"
                          class="btn btn-secondary"
                          style="font-size: 14px;"
                        >
                          ดูทั้งหมด
                        </button>
                      </a>
                    </div>
                  </div>""".format(title, genre)
    elif hasattr(vdosets[0], 'seasons'):
        header_html = """
                  <div class="row" style="margin: 40px 0;">
                    <div class="col-8 col-md-10 col-lg-11" style="margin-top: 5px;">
                      <h2 class="topic__header">{0}</h2>
                    </div>

                    <div class="col-4 col-md-2 col-lg-1 text-right" style="color: #58667e;">
                      <a
                        href="/series/genres/{1}"
                        style="text-decoration: none; color: black;"
                      >
                        <button
                          type="button"
                          class="btn btn-secondary"
                          style="font-size: 14px;"
                        >
                          ดูทั้งหมด
                        </button>
                      </a>
                    </div>
                  </div>""".format(title, genre)
    else:
        header_html = """
                  <div class="row" style="margin: 40px 0;">
                    <div class="col-8 col-md-10 col-lg-11" style="margin-top: 5px;">
                      <h2 class="topic__header">{0}</h2>
                    </div>

                    <div class="col-4 col-md-2 col-lg-1 text-right" style="color: #58667e;">
                      <a
                        href="/movie/genres/{1}"
                        style="text-decoration: none; color: black;"
                      >
                        <button
                          type="button"
                          class="btn btn-secondary"
                          style="font-size: 14px;"
                        >
                          ดูทั้งหมด
                        </button>
                      </a>
                    </div>
                  </div>""".format(title, genre)

    slide_element_html = ""

    # today = datetime.datetime.now()
    # d_ago = datetime.timedelta(days = 3)
    # d_ago = today - d_ago
    for vdo in vdosets:
        html_content = ""
        last_episode_title = ""

        content_str = None
        if hasattr(vdo, 'directors') is False and vdo.last_updated.microsecond == 999999 or hasattr(vdo, 'seasons') and vdo.last_updated.microsecond == 999999:
            last_season = max(vdo.seasons, key=lambda seasons: seasons.id)
            last_episode = max(last_season.episodes, key=lambda episodes: episodes.id)
            last_episode_title = last_episode.title
            content_url = "" + str(vdo.id) + "/season/" + str(last_season.id) + "/episode/" + str(last_episode.youtube_url)
        # else:
        if hasattr(vdo, 'directors') is False:
            content_url = check_series_tvshow_continued_episode_cookies(vdo, "Tvshow", content_str)
        elif hasattr(vdo, 'seasons'):
            content_url = check_series_tvshow_continued_episode_cookies(vdo, "Series", content_str)
        if hasattr(vdo, 'directors') is False:
            genre_str = generateGenreDescription(vdo)
            html_content = """
                    <a class="movie__link" href="/tvshow/{0}">
                      <img
                        class="semi-movie__poster"
                        src="/static/tvshow/thumbnail/{1}"
                        alt="{2}"
                      />
                      <h5 class="movie__header">{3}</h5>

                  <p class="genre__description-swiper-list" >{5}</p>
                      <p style="font-size: 0.90em; margin-right: 2em">{4}</p>

                    </a>
            """.format(content_url, vdo.thumbnail, vdo.title, vdo.title, last_episode_title, genre_str)
        elif hasattr(vdo, 'seasons'):
            genre_str = generateGenreDescription(vdo)
            html_content = """
                    <a class="movie__link" href="/series/{0}">
                      <img
                        class="semi-movie__poster"
                        src="/static/series/thumbnail/{1}"
                        alt="{2}"
                      />
                      <h5 class="movie__header">{3}</h5>

                  <p class="genre__description-swiper-list" >{5}</p>
                      <p style="font-size: 0.90em; margin-right: 2em">{4}</p>
                    </a>
            """.format(content_url, vdo.thumbnail, vdo.title, vdo.title, last_episode_title, genre_str)

        elif vdo.thumbnail is not None:
            genre_str = generateGenreDescription(vdo)
            html_content = """
                    <a class="movie__link" href="/movie/{0}">
                      <img
                        class="semi-movie__poster"
                        src="/static/movies/thumbnail/{1}"
                        alt="{2}"
                      />
                      <h5 class="movie__header">{3}</h5>
                  <p class="genre__description-swiper-list" >{4}</p>
                    </a>
            """.format(vdo.id, vdo.thumbnail, vdo.title, vdo.title, genre_str)
        else:
            html_content = """
                    <a class="movie__link" href="/movie/{0}">
                      <img
                        class="semi-movie__poster"
                        src="http://img.youtube.com/vi/{1}/mqdefault.jpg"
                        alt="{2}"
                      />
                      <h5 class="movie__header">{3}</h5>
                  <p class="genre__description-swiper-list" >{4}</p>
                    </a>
            """.format(vdo.id, vdo.youtube_url, vdo.title, vdo.title, genre_str)

        slide_element_html += check_new_content_3_day_ago(html_content, vdo.last_updated)

    swiper_className = "swiper-" + css_className
    swiper_button_prev_className = "swiper-button-prev-" + css_className
    slider_open_tag_html = """
          <div class="swiper {0}">
            <div class="swiper-button-prev {1}"></div>
            <!-- Additional required wrapper -->
            <div class="swiper-wrapper">
              <!-- Slides -->
    """.format(swiper_className, swiper_button_prev_className)

    swiper_pagination_className = "swiper-pagination-" + css_className
    swiper_button_next_className = "swiper-button-next-" + css_className
    slider_close_tag_html = """
            </div>
            <!-- If we need pagination -->
            <!--<div class="swiper-pagination {0}"></div>-->

            <!-- If we need navigation buttons -->

            <!-- If we need scrollbar -->
            <div class="swiper-scrollbar"></div>
            <div class="swiper-button-next {1}"></div>
          </div>
    """.format(swiper_pagination_className, swiper_button_next_className)

    slider_js = """
          <script>
            var swiper = new Swiper(".{0}", {{
                  slidesPerView: 2,
                  slidesPerGroup: 2,
                  spaceBetween: 5,
                              lazy: true,
                                  preloadImages: false,
    watchOverflow: true,
                          shortSwipes: false,
              breakpoints: {{
                // when window width is >= 320px
                880: {{

                  slidesPerView: 5,
                  slidesPerGroup: 5,
                }},
              }},
              pagination: {{
                el: ".{1}",
                clickable: false,
              }},
              navigation: {{
                nextEl: ".{2}",
                prevEl: ".{3}",
              }},
            }});
          </script>
    """.format(swiper_className, swiper_pagination_className, swiper_button_next_className, swiper_button_prev_className )

    return header_html + slider_open_tag_html + slide_element_html + slider_close_tag_html + slider_js

@app.template_filter('swiper_template_speicific_episode_link')
def swiper_template_speicific_episode_link(contents, title, genre, css_className):

    if contents[0]["type"] == "Tvshow":
        header_html = """
                  <div class="row" style="margin-bottom: 40px;">
                    <div class="col-8 col-md-10 col-lg-11" style="margin-top: 5px;">
                      <h2 class="topic__header">{0}</h2>
                    </div>

                    <div class="col-4 col-md-2 col-lg-1 text-right" style="color: #58667e;">
                      <a
                        href="/genre/{1}/page/1"
                        style="text-decoration: none; color: black;"
                      >
                        <button
                          type="button"
                          class="btn btn-secondary"
                          style="font-size: 14px;"
                        >
                          ดูทั้งหมด
                        </button>
                      </a>
                    </div>
                  </div>""".format(title, genre)
    elif contents[0]["type"] == "Series":
        header_html = """
                  <div class="row" style="margin-bottom: 40px;">
                    <div class="col-8 col-md-10 col-lg-11" style="margin-top: 5px;">
                      <h2 class="topic__header">{0}</h2>
                    </div>

                    <div class="col-4 col-md-2 col-lg-1 text-right" style="color: #58667e;">
                      <a
                        href="/genre/{1}/page/1"
                        style="text-decoration: none; color: black;"
                      >
                        <button
                          type="button"
                          class="btn btn-secondary"
                          style="font-size: 14px;"
                        >
                          ดูทั้งหมด
                        </button>
                      </a>
                    </div>
                  </div>""".format(title, genre)
    else:
        header_html = """
                  <div class="row" style="margin-bottom: 40px;">
                    <div class="col-8 col-md-10 col-lg-11" style="margin-top: 5px;">
                      <h2 class="topic__header">{0}</h2>
                    </div>

                    <div class="col-4 col-md-2 col-lg-1 text-right" style="color: #58667e;">
                      <a
                        href="/genre/{1}/page/1"
                        style="text-decoration: none; color: black;"
                      >
                        <button
                          type="button"
                          class="btn btn-secondary"
                          style="font-size: 14px;"
                        >
                          ดูทั้งหมด
                        </button>
                      </a>
                    </div>
                  </div>""".format(title, genre)

    # today = datetime.datetime.now()
    # d_ago = datetime.timedelta(days = 3)
    # d_ago = today - d_ago

    slide_element_html = ""
    for content in contents:
        # if content["last_updated"] > d_ago:
        #     slide_element_html += """
        #
        #     <div class="movie__cover swiper-slide">
        #
        #       	<div class="item">
        #           			<span class="notify-badge">มาใหม่</span>
        #     """
        # else:
        #     slide_element_html += """
        #     <div class="movie__cover swiper-slide">
        #     """
        html_content = ""
        if content["type"] == "Tvshow":
            html_content = """
                    <a class="movie__link" href="/tvshow/{0}/season/{1}/episode/{2}">
                      <img
                        class="semi-movie__poster"
                        src="/static/tvshow/thumbnail/{3}"
                        alt="{4}"
                      />
                      <h5 class="movie__header">{5}</h5>
                    </a>
            """.format(content["id"], content["season"], content["episode"], content["thumbnail"], content["title"], content["title"])
        elif content["type"] == "Series":
            html_content = """
                    <a class="movie__link" href="/series/{0}/season/{1}/episode/{2}">
                      <img
                        class="semi-movie__poster"
                        src="/static/series/thumbnail/{3}"
                        alt="{4}"
                      />
                      <h5 class="movie__header">{5}</h5>
                    </a>
            """.format(content["id"], content["season"], content["episode"], content["thumbnail"], content["title"], content["title"])
        elif content["thumbnail"] is None:
            html_content = """
                    <a class="movie__link" href="/movie/{0}">
                      <img
                        class="semi-movie__poster"
                        src="http://img.youtube.com/vi/{1}/mqdefault.jpg"
                        alt="{2}"
                      />
                      <h5 class="movie__header">{3}</h5>
                    </a>
            """.format(content["id"], content["youtube_url"], content["title"], content["title"])
        else:
            html_content = """
                    <a class="movie__link" href="/movie/{0}">
                      <img
                        class="semi-movie__poster"
                        src="/static/movies/thumbnail/{1}"
                        alt="{2}"
                      />
                      <h5 class="movie__header">{3}</h5>
                    </a>
            """.format(content["id"], content["thumbnail"], content["title"], content["title"])

        # if content["last_updated"] > d_ago:
        #     slide_element_html += """
        #
        #     </div>
        #     </div>
        #     """
        # else:
        #     slide_element_html += """
        #     </div>
        #     """
        slide_element_html += check_new_content_3_day_ago(html_content, content["last_updated"])

    swiper_className = "swiper-" + css_className
    swiper_button_prev_className = "swiper-button-prev-" + css_className
    slider_open_tag_html = """
          <div class="swiper {0}">
            <div class="swiper-button-prev {1}"></div>
            <!-- Additional required wrapper -->
            <div class="swiper-wrapper">
              <!-- Slides -->
    """.format(swiper_className, swiper_button_prev_className)

    swiper_pagination_className = "swiper-pagination-" + css_className
    swiper_button_next_className = "swiper-button-next-" + css_className
    slider_close_tag_html = """
            </div>
            <!-- If we need pagination -->
            <!--<div class="swiper-pagination {0}"></div>-->

            <!-- If we need navigation buttons -->

            <!-- If we need scrollbar -->
            <div class="swiper-scrollbar"></div>
            <div class="swiper-button-next {1}"></div>
          </div>
    """.format(swiper_pagination_className, swiper_button_next_className)

    slider_js = """
          <script>
            var swiper = new Swiper(".{0}", {{
                  slidesPerView: 2,
                  slidesPerGroup: 2,
                  spaceBetween: 5,
                              lazy: true,
                                  preloadImages: false,
    watchOverflow: true,
                          shortSwipes: false,
              breakpoints: {{
                // when window width is >= 320px
                880: {{

                  slidesPerView: 5,
                  slidesPerGroup: 5,
                }},
              }},
              pagination: {{
                el: ".{1}",
                clickable: false,
              }},
              navigation: {{
                nextEl: ".{2}",
                prevEl: ".{3}",
              }},
            }});
          </script>
    """.format(swiper_className, swiper_pagination_className, swiper_button_next_className, swiper_button_prev_className )

    return header_html + slider_open_tag_html + slide_element_html + slider_close_tag_html + slider_js

def initialMovie(studios):
    with open('./main/movie_data.csv', mode='r', encoding="utf8") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        i = 0
        for row in csv_reader:
            movie_check = Movie.query.filter_by(youtube_url=row["youtube_url"]).first()
            print(row)
            if movie_check is None:
                print(movie_check)
                genres = row["genres"].split(",")
                genre_list = []
                for genre in genres:
                    genre = genre.strip()
                    genre_check = Genre.query.filter_by(name=genre).first()
                    if genre_check is None:
                        genre_data = Genre(name=genre)
                        db.session.add(genre_data)
                        genre_list.append(genre_data)
                    else:
                        genre_list.append(genre_check)

                actors = row["actors"].split(",")
                actor_list = []
                for actor in actors:
                    actor = actor.strip()
                    actor_check = Actor.query.filter_by(name=actor).first()
                    if actor_check is None:
                        actor_data = Actor(name=actor)
                        db.session.add(actor_data)
                        actor_list.append(actor_data)
                    else:
                        actor_list.append(actor_check)

                directors = row["director"].split(",")
                director_list = []
                for director in directors:
                    director = director.strip()
                    director_check = Director.query.filter_by(name=director).first()
                    if director_check is None:
                        director_data = Director(name=director)
                        db.session.add(director_data)
                        director_list.append(director_data)
                    else:
                        director_list.append(director_check)

                studio_list = []
                for studio in studios:
                    studio_check = Studio.query.filter_by(name=studio).first()
                    if studio_check is None:
                        studio_data = Studio(name=studio)
                        db.session.add(studio_data)
                        studio_list.append(studio_data)
                    else:
                        studio_list.append(studio_check)


                movie_data = Movie(title=row["title"], last_updated=datetime.datetime.now(), description=row["description"], youtube_url=row["youtube_url"], genres=genre_list, actors=actor_list, directors=director_list, published_year=row['published_year'], studio=studio_list)
                db.session.add(movie_data)
                db.session.commit()


def initialMovieV2(movie_json):

    print("Do u want to add " + movie_json['title'] + " to Movie database [y/n]: ")
    ans = input()
    if ans == 'n':
        return

    movie_check = Movie.query.filter_by(youtube_url=movie_json["youtube_url"]).first()
    if movie_check is None:
        genre_list = []
        for genre in movie_json["genres"]:
            genre = genre.strip()
            genre_check = Genre.query.filter_by(name=genre).first()
            if genre_check is None:
                genre_data = Genre(name=genre)
                db.session.add(genre_data)
                genre_list.append(genre_data)
            else:
                genre_list.append(genre_check)

        actor_list = []
        for actor in movie_json["actors"]:
            actor = actor.strip()
            actor_check = Actor.query.filter_by(name=actor).first()
            if actor_check is None:
                actor_data = Actor(name=actor)
                db.session.add(actor_data)
                actor_list.append(actor_data)
            else:
                actor_list.append(actor_check)

        director_list = []
        for director in movie_json["directors"]:
            director = director.strip()
            director_check = Director.query.filter_by(name=director).first()
            if director_check is None:
                director_data = Director(name=director)
                db.session.add(director_data)
                director_list.append(director_data)
            else:
                director_list.append(director_check)

        studio_list = []
        for studio in movie_json["studio"]:
            studio_check = Studio.query.filter_by(name=studio).first()
            if studio_check is None:
                studio_data = Studio(name=studio)
                db.session.add(studio_data)
                studio_list.append(studio_data)
            else:
                studio_list.append(studio_check)


        movie_data = Movie(title=movie_json["title"], last_updated=datetime.datetime.now(), description=movie_json["description"], youtube_url=movie_json["youtube_url"], genres=genre_list, actors=actor_list, directors=director_list, studio=studio_list, published_year=movie_json["published_year"], thumbnail=movie_json["thumbnail"], runtime_min=movie_json["runtime_min"])
        db.session.add(movie_data)
        db.session.commit()

def initialSeries(series_json):
    season_list = []
    genre_list = []
    director_list = []
    actor_list = []
    studio_list = []

    print("Do u want to add " + series_json['title'] + " to Series database [y/n]: ")
    ans = input()
    if ans == 'n':
        return

    series_check = Series.query.filter_by(title=series_json["title"]).first()
    if series_check is None:
        for genre in series_json["genres"]:
            genre = genre.strip()
            genre_check = Genre.query.filter_by(name=genre).first()
            if genre_check is None:
                genre_data = Genre(name=genre)
                db.session.add(genre_data)
                genre_list.append(genre_data)
            else:
                genre_list.append(genre_check)

        for director in series_json["directors"]:
            director = director.strip()
            director_check = Director.query.filter_by(name=director).first()
            if director_check is None:
                director_data = Director(name=director)
                db.session.add(director_data)
                director_list.append(director_data)
            else:
                director_list.append(director_check)

        for actor in series_json["actors"]:
            actor = actor.strip()
            actor_check = Actor.query.filter_by(name=actor).first()
            if actor_check is None:
                actor_data = Actor(name=actor)
                db.session.add(actor_data)
                actor_list.append(actor_data)
            else:
                actor_list.append(actor_check)


        for studio in series_json["studio"]:
            studio = studio.strip()
            studio_check = Studio.query.filter_by(name=studio).first()
            if studio_check is None:
                studio_data = Studio(name=studio)
                db.session.add(studio_data)
                studio_list.append(studio_data)
            else:
                studio_list.append(studio_check)

        for season in series_json["seasons"]:
            season_check = Season.query.filter_by(yt_playlist_url=season['yt_playlist_url']).first()
            if season_check is None:
                r = requests.get(season["yt_playlist_url"])
                soup = BeautifulSoup(r.content, 'html.parser')
                items = soup.findAll('script')
                ytJson = ""
                episode_list = []
                for item in items:
                    result = str(item).find(series_json["keyword"])
                    if result != -1:
                        ytJson = item.text[:-1]
                        ytJson = ytJson.replace("var ytInitialData = ", "")
                        ytJson = json.loads(ytJson)
                        ytJson = ytJson["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][0]["tabRenderer"]["content"]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"][0]["playlistVideoListRenderer"]["contents"]
                        if series_json['reverse_loop']:
                            for ytContent in reversed(ytJson[:100]):
                                episode_check = Episode.query.filter_by(youtube_url=ytContent["playlistVideoRenderer"]["videoId"]).first()
                                if episode_check is None:
                                    episode_data = Episode(title=ytContent["playlistVideoRenderer"]["title"]["runs"][0]["text"], youtube_url=ytContent["playlistVideoRenderer"]["videoId"])
                                    db.session.add(episode_data)
                                    episode_list.append(episode_data)

                                else:
                                    episode_list.append(episode_check)
                        else:
                            for ytContent in ytJson[:100]:
                                episode_check = Episode.query.filter_by(youtube_url=ytContent["playlistVideoRenderer"]["videoId"]).first()
                                if episode_check is None:
                                    episode_data = Episode(title=ytContent["playlistVideoRenderer"]["title"]["runs"][0]["text"], youtube_url=ytContent["playlistVideoRenderer"]["videoId"])
                                    db.session.add(episode_data)
                                    episode_list.append(episode_data)

                                else:
                                    episode_list.append(episode_check)

                new_season_id = ""
                # while True:
                #   new_season_id = id_generator()
                #   season_id_check = Season.query.filter_by(id=new_season_id).first()
                #   if season_id_check is None:
                #       print("U can use this id!: " + new_season_id)
                #       break
                #   else:
                #       print("Generate new id......")
                #
                #===============================================
                if season_list != []:
                    previous_season = max(season_list, key=lambda seasons: seasons.id)
                else:
                    previous_season = None
                randomIdCheck = True

                new_season_id = ""
                while randomIdCheck == True:
                  if previous_season is None:
                      new_season_id = id_generator()
                      season_id_check = Season.query.filter_by(id=new_season_id).first()
                      if season_id_check is None:
                          print("U can use this id!: " + str(new_season_id))
                          randomIdCheck = False
                      else:
                          print("Generate new id......")
                  else:
                      random_num = random.randint(0, 1000000)
                      print("Random ID = " + str(random_num))
                      print("Last season id: " + str(previous_season.id))
                      new_season_id = int(random_num) + int(previous_season.id)
                      print("New id = " + str(new_season_id))
                      season_id_check = Season.query.filter_by(id=new_season_id).first()
                      if season_id_check is None:
                          print("U can use this id!: " + str(new_season_id))
                          randomIdCheck = False
                      else:
                          print("Generate new id......")
                #=============================================
                season_data = Season(id=int(new_season_id), season_title=season["season_title"], yt_playlist_url=season['yt_playlist_url'], episodes=episode_list, published_year=season['published_year'])
                db.session.add(season_data)
                season_list.append(season_data)


        series_data = Series(title=series_json["title"], description=series_json["description"], genres=genre_list, seasons=season_list, last_updated=datetime.datetime.now(), directors=director_list, actors=actor_list, thumbnail=series_json["thumbnail"], studio=studio_list, state=series_json["state"])
        db.session.add(series_data)
        db.session.commit()


# tvshow_json = {
#     "title": "GGcooking | RUBSARB Production",
#     "keyword": "GGcooking",
#     "thumbnail": "GGcooking.jpg",
#     "description": 'รายการทำอาหารที จอร์จจี้ จะทำอาหารไปพร้อมกับพูดคุยกับแขกรับเชิญแบบสัพเพเหระทั้งเรื่องวิธีการลดน้ำหนักในวิธีที่ถูกต้อง หรือ หนังสนุกๆในไตรมาสนี้',
#     "genres": ["รายการไทย", "RUBSARB", "อาหาร"],
#     "actors": ["ปรีดิ์โรจน์ เกษมสันต์"],
#     "seasons": [{"season_title": "ปี 2014",
#     "yt_playlist_url": "https://www.youtube.com/playlist?list=PLs12_b9cOtEglqBmcggzcoumRRzjGFjgO",
#     "published_year": "2557"
#     },
#     {"season_title": "ปี 2015",
#     "yt_playlist_url": "https://www.youtube.com/playlist?list=PLs12_b9cOtEiF5UhUsou3cVXSpA-5w59M",
#     "published_year": "2558"
#     },
#     ],
# }




def initialTvshow(tvshow_json):
    season_list = []
    genre_list = []
    actor_list = []
    studio_list = []
    # previous_season = None

    print("Do u want to add " + tvshow_json['title'] + " to Tvshow database [y/n]: ")
    ans = input()
    if ans == 'n':
        return

    tvshow_check = Tvshow.query.filter_by(title=tvshow_json["title"]).first()
    if tvshow_check is None:
        for genre in tvshow_json["genres"]:
            genre = genre.strip()
            genre_check = Genre.query.filter_by(name=genre).first()
            if genre_check is None:
                genre_data = Genre(name=genre)
                db.session.add(genre_data)
                genre_list.append(genre_data)
            else:
                genre_list.append(genre_check)

        for actor in tvshow_json["actors"]:
            actor = actor.strip()
            actor_check = Actor.query.filter_by(name=actor).first()
            if actor_check is None:
                actor_data = Actor(name=actor)
                db.session.add(actor_data)
                actor_list.append(actor_data)
            else:
                actor_list.append(actor_check)

        for studio in tvshow_json["studio"]:
            studio = studio.strip()
            studio_check = Studio.query.filter_by(name=studio).first()
            if studio_check is None:
                studio_data = Studio(name=studio)
                db.session.add(studio_data)
                studio_list.append(studio_data)
            else:
                studio_list.append(studio_check)


        for season in tvshow_json["seasons"]:
            season_check = Season.query.filter_by(yt_playlist_url=season['yt_playlist_url']).first()
            print(season_check)
            if season_check is None:
                r = requests.get(season["yt_playlist_url"])
                soup = BeautifulSoup(r.content, 'html.parser')
                items = soup.findAll('script')
                ytJson = ""
                episode_list = []
                for item in items:
                    for keyword in tvshow_json["keywords"]:
                        result = str(item).find(keyword)
                        print(result)
                        if result != -1:
                            ytJson = item.text[:-1]
                            print(ytJson)
                            ytJson = ytJson.replace("var ytInitialData = ", "")
                            print(ytJson)
                            ytJson = json.loads(ytJson)
                            ytJson = ytJson["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][0]["tabRenderer"]["content"]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"][0]["playlistVideoListRenderer"]["contents"]
                            if tvshow_json['reverse_loop']:
                                for ytContent in reversed(ytJson[:100]):
                                    episode_check = Episode.query.filter_by(youtube_url=ytContent["playlistVideoRenderer"]["videoId"]).first()
                                    if episode_check is None:
                                        episode_data = Episode(title=ytContent["playlistVideoRenderer"]["title"]["runs"][0]["text"], youtube_url=ytContent["playlistVideoRenderer"]["videoId"])
                                        db.session.add(episode_data)
                                        episode_list.append(episode_data)
                                    else:
                                        episode_list.append(episode_check)
                            else:
                                for ytContent in ytJson[:100]:
                                    episode_check = Episode.query.filter_by(youtube_url=ytContent["playlistVideoRenderer"]["videoId"]).first()
                                    if episode_check is None:
                                        episode_data = Episode(title=ytContent["playlistVideoRenderer"]["title"]["runs"][0]["text"], youtube_url=ytContent["playlistVideoRenderer"]["videoId"])
                                        db.session.add(episode_data)
                                        episode_list.append(episode_data)
                                    else:
                                        episode_list.append(episode_check)

                # while True:
                #   new_season_id = id_generator()
                #   season_id_check = Season.query.filter_by(id=new_season_id).first()
                #   if season_id_check is None:
                #       print("U can use this id!: " + new_season_id)
                #       break
                #   else:
                #       print("Generate new id......")
                #===============================================
                if season_list != []:
                    previous_season = max(season_list, key=lambda seasons: seasons.id)
                else:
                    previous_season = None
                randomIdCheck = True

                new_season_id = ""
                while randomIdCheck == True:
                  if previous_season is None:
                      new_season_id = id_generator()
                      season_id_check = Season.query.filter_by(id=new_season_id).first()
                      if season_id_check is None:
                          print("U can use this id!: " + str(new_season_id))
                          randomIdCheck = False
                      else:
                          print("Generate new id......")
                  else:
                      random_num = random.randint(0, 1000000)
                      print("Random ID = " + str(random_num))
                      print("Last season id: " + str(previous_season.id))
                      new_season_id = int(random_num) + int(previous_season.id)
                      print("New id = " + str(new_season_id))
                      season_id_check = Season.query.filter_by(id=new_season_id).first()
                      if season_id_check is None:
                          print("U can use this id!: " + str(new_season_id))
                          randomIdCheck = False
                      else:
                          print("Generate new id......")
                #=============================================
                season_data = Season(id=int(new_season_id),season_title=season["season_title"], yt_playlist_url=season['yt_playlist_url'], episodes=episode_list, published_year=season['published_year'])
                db.session.add(season_data)
                season_list.append(season_data)

        tvshow_data = Tvshow(title=tvshow_json["title"], description=tvshow_json["description"], genres=genre_list, seasons=season_list, last_updated=datetime.datetime.now(), actors=actor_list, thumbnail=tvshow_json["thumbnail"], studio=studio_list, state=tvshow_json["state"])
        print(tvshow_data)
        db.session.add(tvshow_data)
        db.session.commit()


def addGenre(table_name, row_id, added_genre):
    check = table_name.query.filter_by(id=row_id).first()
    print("Add genre " + added_genre + " to " + check.title + " [y/n]: ")
    ans = input()
    if ans == "n":
        return
    genre_list = []

    genre_list.extend(check.genres)

    genre_check = Genre.query.filter_by(name=added_genre).first()
    if genre_check is None:
       genre_data = Genre(name=added_genre)
       db.session.add(genre_data)
       genre_list.append(genre_data)
    else:
       genre_list.append(genre_check)

    check.genres = genre_list
    db.session.commit()

#kuy = Movie.query.filter_by(youtube_url="HWJaZn13F1").first()
#kuy.youtube_url = "HWJaZn13F1s"
#Movie.query.filter_by(id=152).delete()
#Season.query.delete()
#Series.query.delete()
#Episode.query.delete()
#genre_check = Genre.query.filter_by(name="ซีรี่ยส์ไทย").first()
#print(genre_check)
#genre_check.name = "ซีรี่ส์ไทย"
#Series.query.filter_by(id=26).delete()
#db.session.commit()
#genre_check = Genre.query.filter_by(name="รายกายไทย").delete()

# tvshow_check = Tvshow.query.filter_by(id=2).first()
# genre_list = []
#
# genre_list.extend(tvshow_check.genres)
#
# genre_check = Genre.query.filter_by(name="รายการไทย").first()
# if genre_check is None:
#    genre_data = Genre(name="รายการไทย")
#    db.session.add(genre_data)
#    genre_list.append(genre_data)
# else:
#    genre_list.append(genre_check)
#
# tvshow_check.genres = genre_list

def deleteGenre(table_name, row_id, deleted_genre):
    check = table_name.query.filter_by(id=row_id).first()
    print("Do u want to delete genre " + deleted_genre + " from " + check.title + " [y/n]: ")
    ans = input()
    if ans == "n":
        return
    genre_list = []
    for genre in check.genres:
        if genre.name != deleted_genre:
            genre_list.append(genre)
    check.genres = genre_list
    db.session.commit()

# เพิ่ม episode ใน SF playlist ด้วย YT playlist
def addYTPlaylistToSFPlaylist(table_name, row_id, yt_playlist_url, keyword, season_id, reverse_loop):
    check = table_name.query.filter_by(id=row_id).first()
    print("Add YT playlist to SF playlist in season " + Season.query.filter_by(id=season_id).first().season_title + " of " + check.title + " with this yt playlist " + yt_playlist_url + " [y/n]: ")
    ans = input()
    if ans == 'n':
        return
    r = requests.get(yt_playlist_url)
    soup = BeautifulSoup(r.content, 'html.parser')
    items = soup.findAll('script')
    ytJson = ""
    episode_list = []
    curr_season = None
    for season in check.seasons:
        if season.id == season_id:
            curr_season = season
    episode_list.extend(curr_season.episodes)
    print(len(episode_list))
    for item in items:
        result = str(item).find(keyword)
        if result != -1:
            ytJson = item.text[:-1]
            ytJson = ytJson.replace("var ytInitialData = ", "")
            ytJson = json.loads(ytJson)
            ytJson = ytJson["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][0]["tabRenderer"]["content"]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"][0]["playlistVideoListRenderer"]["contents"]

            if reverse_loop:
                # ytJson = ytJson
                for ytContent in reversed(ytJson[:100]):
                    episode_check = Episode.query.filter_by(youtube_url=ytContent["playlistVideoRenderer"]["videoId"]).first()
                    if episode_check is None:
                        episode_data = Episode(title=ytContent["playlistVideoRenderer"]["title"]["runs"][0]["text"], youtube_url=ytContent["playlistVideoRenderer"]["videoId"])
                        db.session.add(episode_data)
                        episode_list.append(episode_data)
                    else:
                        episode_list.append(episode_check)
            else:
                for ytContent in ytJson[:100]:
                    episode_check = Episode.query.filter_by(youtube_url=ytContent["playlistVideoRenderer"]["videoId"]).first()
                    if episode_check is None:
                        episode_data = Episode(title=ytContent["playlistVideoRenderer"]["title"]["runs"][0]["text"], youtube_url=ytContent["playlistVideoRenderer"]["videoId"])
                        db.session.add(episode_data)
                        episode_list.append(episode_data)
                    else:
                        episode_list.append(episode_check)


    curr_season.episodes = episode_list
    db.session.commit()

# แทนที่ SF playlist ด้วย Yt playlist ทั้งหมด
def replaceYTPlaylistToSFPlaylist(table_name, row_id, yt_playlist_url, keyword, season_id, reverse_loop):
    check = table_name.query.filter_by(id=row_id).first()
    print("Replace sf playlist in season " + Season.query.filter_by(id=season_id).first().season_title + " with this yt playlist " + yt_playlist_url + " [y/n]: ")
    ans = input()
    if ans == 'n':
        return
    r = requests.get(yt_playlist_url)
    soup = BeautifulSoup(r.content, 'html.parser')
    items = soup.findAll('script')
    ytJson = ""
    episode_list = []
    for item in items:
        result = str(item).find(keyword)
        if result != -1:
            ytJson = item.text[:-1]
            ytJson = ytJson.replace("var ytInitialData = ", "")
            ytJson = json.loads(ytJson)
            ytJson = ytJson["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][0]["tabRenderer"]["content"]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"][0]["playlistVideoListRenderer"]["contents"]

            if reverse_loop:
                for ytContent in reversed(ytJson[:100]):
                    episode_check = Episode.query.filter_by(youtube_url=ytContent["playlistVideoRenderer"]["videoId"]).first()
                    if episode_check is None:
                        episode_data = Episode(title=ytContent["playlistVideoRenderer"]["title"]["runs"][0]["text"], youtube_url=ytContent["playlistVideoRenderer"]["videoId"])
                        db.session.add(episode_data)
                        episode_list.append(episode_data)
                    else:
                        Episode.query.filter_by(youtube_url=ytContent["playlistVideoRenderer"]["videoId"]).delete()
                        db.session.commit()
                        episode_data = Episode(title=ytContent["playlistVideoRenderer"]["title"]["runs"][0]["text"], youtube_url=ytContent["playlistVideoRenderer"]["videoId"])
                        db.session.add(episode_data)
                        episode_list.append(episode_data)
            else:
                for ytContent in ytJson[:100]:
                    episode_check = Episode.query.filter_by(youtube_url=ytContent["playlistVideoRenderer"]["videoId"]).first()
                    if episode_check is None:
                        episode_data = Episode(title=ytContent["playlistVideoRenderer"]["title"]["runs"][0]["text"], youtube_url=ytContent["playlistVideoRenderer"]["videoId"])
                        db.session.add(episode_data)
                        episode_list.append(episode_data)
                    else:
                        Episode.query.filter_by(youtube_url=ytContent["playlistVideoRenderer"]["videoId"]).delete()
                        db.session.commit()
                        episode_data = Episode(title=ytContent["playlistVideoRenderer"]["title"]["runs"][0]["text"], youtube_url=ytContent["playlistVideoRenderer"]["videoId"])
                        db.session.add(episode_data)
                        episode_list.append(episode_data)
    for season in check.seasons:
        if season.id == season_id:
            season.episodes = episode_list
    db.session.commit()

# แทนที่ SF playlist ด้วย Yt playlist ทั้งหมด
def replaceYTPlaylistToSFPlaylistWithUpdateLastUpdated(table_name, row_id, yt_playlist_url, keyword, season_id, reverse_loop):
    check = table_name.query.filter_by(id=row_id).first()
    print("Replace sf playlist in season " + Season.query.filter_by(id=season_id).first().season_title + " with this yt playlist " + yt_playlist_url + " [y/n]: ")
    ans = input()
    if ans == 'n':
        return
    r = requests.get(yt_playlist_url)
    soup = BeautifulSoup(r.content, 'html.parser')
    items = soup.findAll('script')
    ytJson = ""
    episode_list = []
    for item in items:
        result = str(item).find(keyword)
        if result != -1:
            ytJson = item.text[:-1]
            ytJson = ytJson.replace("var ytInitialData = ", "")
            ytJson = json.loads(ytJson)
            ytJson = ytJson["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][0]["tabRenderer"]["content"]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"][0]["playlistVideoListRenderer"]["contents"]

            if reverse_loop:
                for ytContent in reversed(ytJson[:100]):
                    episode_check = Episode.query.filter_by(youtube_url=ytContent["playlistVideoRenderer"]["videoId"]).first()
                    if episode_check is None:
                        episode_data = Episode(title=ytContent["playlistVideoRenderer"]["title"]["runs"][0]["text"], youtube_url=ytContent["playlistVideoRenderer"]["videoId"])
                        db.session.add(episode_data)
                        episode_list.append(episode_data)
                    else:
                        Episode.query.filter_by(youtube_url=ytContent["playlistVideoRenderer"]["videoId"]).delete()
                        db.session.commit()
                        episode_data = Episode(title=ytContent["playlistVideoRenderer"]["title"]["runs"][0]["text"], youtube_url=ytContent["playlistVideoRenderer"]["videoId"])
                        db.session.add(episode_data)
                        episode_list.append(episode_data)
            else:
                for ytContent in ytJson[:100]:
                    episode_check = Episode.query.filter_by(youtube_url=ytContent["playlistVideoRenderer"]["videoId"]).first()
                    if episode_check is None:
                        episode_data = Episode(title=ytContent["playlistVideoRenderer"]["title"]["runs"][0]["text"], youtube_url=ytContent["playlistVideoRenderer"]["videoId"])
                        db.session.add(episode_data)
                        episode_list.append(episode_data)
                    else:
                        Episode.query.filter_by(youtube_url=ytContent["playlistVideoRenderer"]["videoId"]).delete()
                        db.session.commit()
                        episode_data = Episode(title=ytContent["playlistVideoRenderer"]["title"]["runs"][0]["text"], youtube_url=ytContent["playlistVideoRenderer"]["videoId"])
                        db.session.add(episode_data)
                        episode_list.append(episode_data)
    for season in check.seasons:
        if season.id == season_id:
            season.episodes = episode_list
    check.last_updated = datetime.datetime.now().replace(microsecond=999999)
    db.session.commit()

def addNewEpisodeWithUpdateLastUpdated(table_name, row_id, yt_url, ep_title, season_id):
    check = table_name.query.filter_by(id=row_id).first()
    print("Add New EP to " + Season.query.filter_by(id=season_id).first().season_title + " with " + str(ep_title) + " [y/n]: ")
    ans = input()
    if ans == 'n':
        return
    episode_list = []

    for season in check.seasons:
        if season.id == season_id:
            episode_list.extend(season.episodes)
            check.last_updated = datetime.datetime.now().replace(microsecond=999999)
    episode_check = Episode.query.filter_by(youtube_url=yt_url).first()
    if episode_check is None:
        episode_data = Episode(title=ep_title, youtube_url=yt_url)
        db.session.add(episode_data)
        episode_list.append(episode_data)
    else:
        episode_list.append(episode_check)
    for season in check.seasons:
        if season.id == season_id:
            season.episodes = episode_list
    db.session.commit()


def insertEP(table_name, row_id, yt_url, ep_title, season_id, ep_num):
    check = table_name.query.filter_by(id=row_id).first()
    print("Add New EP to " + Season.query.filter_by(id=season_id).first().season_title + " with " + str(ep_title) + " [y/n]: ")
    ans = input()
    if ans == 'n':
        return
    episode_list = []

    for season in check.seasons:
        if season.id == season_id:
            episode_list.extend(season.episodes)

    episode_list = sorted(episode_list, key=lambda episodes: episodes.id)
    # print(episode_list)
    episode_check = Episode.query.filter_by(youtube_url=yt_url).first()
    if episode_check is None:
        episode_data = Episode(title=ep_title, youtube_url=yt_url)
        db.session.add(episode_data)
        # episode_list.add(ep_num+1, episode_data)
    # else:
        # episode_list.insert(ep_num+1, episode_check)
        db.session.commit()

    new_episode_list = []
    new_episode_list.extend(episode_list[:ep_num-1])
    print(new_episode_list)
    for ep in episode_list[ep_num-1:]:
        print(ep)
        tmp_ep_title = ep.title
        tmp_ep_yt_url = ep.youtube_url
        Episode.query.filter_by(youtube_url=tmp_ep_yt_url).delete()
        db.session.commit()
        episode_data = Episode(title=tmp_ep_title, youtube_url=tmp_ep_yt_url)
        db.session.add(episode_data)
        db.session.commit()
        new_episode_list.append(episode_data)

    episode_check = Episode.query.filter_by(youtube_url=yt_url).first()
    new_episode_list.append(episode_check)
    # #
    for season in check.seasons:
        if season.id == season_id:
            season.episodes = new_episode_list
    db.session.commit()

def deleteVdoFromEpisodes(table_name, row_id, season_num, episode_youtube_url):
    check = table_name.query.filter_by(id=row_id).first()
    print("Do u want to delte episode " + episode_youtube_url + " from season " + str(season_num) + " in " + check.title)
    ans = input()
    if ans == "n":
        return
    for episode in check.seasons[season_num-1].episodes:
        if episode.youtube_url == episode_youtube_url:
            Episode.query.filter_by(youtube_url=episode_youtube_url).delete()
            db.session.commit()

def changePublishedYearInSeason(table_name, row_id, season_num, changed_published_year):
    check = table_name.query.filter_by(id=row_id).first()
    check.seasons[season_num-1].published_year = changed_published_year
    db.session.commit()

def addNewSeason(table_name, row_id, keyword, season_title, yt_playlist_url, published_year, reverse_loop):
    check = table_name.query.filter_by(id=row_id).first()

    print("Want to add new season [" + season_title + "] in " + check.title + " [y/n]: ")
    ans = input()
    if ans == 'n':
        return
    season_list = []
    for season in check.seasons:
        if season.episodes is not None:
            season_list.append(season)

    r = requests.get(yt_playlist_url)
    soup = BeautifulSoup(r.content, 'html.parser')
    items = soup.findAll('script')
    ytJson = ""
    episode_list = []
    for item in items:
        result = str(item).find(keyword)
        if result != -1:
            ytJson = item.text[:-1]
            ytJson = ytJson.replace("var ytInitialData = ", "")
            ytJson = json.loads(ytJson)
            ytJson = ytJson["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][0]["tabRenderer"]["content"]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"][0]["playlistVideoListRenderer"]["contents"]
            if reverse_loop:
                for ytContent in reversed(ytJson[:100]):
                    if 'playlistVideoRenderer' in ytContent:
                        episode_check = Episode.query.filter_by(youtube_url=ytContent["playlistVideoRenderer"]["videoId"]).first()
                        if episode_check is None:
                            episode_data = Episode(title=ytContent["playlistVideoRenderer"]["title"]["runs"][0]["text"], youtube_url=ytContent["playlistVideoRenderer"]["videoId"])
                            db.session.add(episode_data)
                            episode_list.append(episode_data)
                        else:
                            episode_list.append(episode_check)
            else:
                for ytContent in ytJson[:100]:
                    if 'playlistVideoRenderer' in ytContent:
                        episode_check = Episode.query.filter_by(youtube_url=ytContent["playlistVideoRenderer"]["videoId"]).first()
                        if episode_check is None:
                            episode_data = Episode(title=ytContent["playlistVideoRenderer"]["title"]["runs"][0]["text"], youtube_url=ytContent["playlistVideoRenderer"]["videoId"])
                            db.session.add(episode_data)
                            episode_list.append(episode_data)
                        else:
                            episode_list.append(episode_check)


    previous_season = None
    if season_list != []:
        previous_season = max(season_list, key=lambda seasons: seasons.id)
    else:
        previous_season = None
    randomIdCheck = True

    while randomIdCheck == True:
      if previous_season is None:
          new_season_id = id_generator()
          print("Last season id: " + str(previous_season.id))
          # while int(new_season_id) < int(previous_season.id):
          #     print("New season id less than previous season id: " + str(new_season_id))
          #     new_season_id = id_generator()
          season_id_check = Season.query.filter_by(id=new_season_id).first()
          if season_id_check is None:
              print("U can use this id!: " + str(new_season_id))
              randomIdCheck = False
          else:
              print("Generate new id......")
      else:
          random_num = random.randint(0, 1000000)
          print("Random ID = " + str(random_num))
          print("Last season id: " + str(previous_season.id))
          new_season_id = int(random_num) + int(previous_season.id)
          print("New id = " + str(new_season_id))
          season_id_check = Season.query.filter_by(id=new_season_id).first()
          if season_id_check is None:
              print("U can use this id!: " + str(new_season_id))
              randomIdCheck = False
          else:
              print("Generate new id......")
    season_data = Season(id=int(new_season_id),season_title=season_title, yt_playlist_url=yt_playlist_url, episodes=episode_list, published_year=published_year)
    db.session.add(season_data)
    season_list.append(season_data)
    check.seasons = season_list
    check.last_updated = datetime.datetime.now().replace(microsecond=999999)
    db.session.commit()

season_json = {
    "keyword": "GGcooking",
    "yt_playlist_url": "https://www.youtube.com/playlist?list=PLFOJd2imZnwyBVPEhEj93GfqLcRsPb70_",
    "reverse_loop": True, # สำหรับ epที่จัดเรียงกลับกันใน youtube playlist # True คือ อ่าน yt playlist จากล่างขึ้นบน # False บนลงล่าง # Default คือ False
"season_title": "ปี 2017",
"published_year": "2560",
"starting_index": 70,
"ending_index": 57

}

def addSeasonWithIndex(table_name, row_id, season_json):
    check = table_name.query.filter_by(id=row_id).first()
    episode_list = []

    r = requests.get(season_json['yt_playlist_url'])
    soup = BeautifulSoup(r.content, 'html.parser')
    items = soup.findAll('script')
    ytJson = None

    for item in items:
        result = str(item).find(season_json['keyword'])
        if result != -1:
            ytJson = item.text[:-1]
            ytJson = ytJson.replace("var ytInitialData = ", "")
            ytJson = json.loads(ytJson)
            ytJson = ytJson["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][0]["tabRenderer"]["content"]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"][0]["playlistVideoListRenderer"]["contents"]
            if season_json['reverse_loop']:
                for ytContent in reversed(ytJson[season_json['ending_index']-1:season_json['starting_index']]):
                    if 'playlistVideoRenderer' in ytContent:
                        episode_data = Episode(title=ytContent["playlistVideoRenderer"]["title"]["runs"][0]["text"], youtube_url=ytContent["playlistVideoRenderer"]["videoId"])
                        db.session.add(episode_data)
                        episode_list.append(episode_data)
            else:
                for ytContent in ytJson[season_json['starting_index']-1:season_json['ending_index']]:
                    if 'playlistVideoRenderer' in ytContent:
                        episode_data = Episode(title=ytContent["playlistVideoRenderer"]["title"]["runs"][0]["text"], youtube_url=ytContent["playlistVideoRenderer"]["videoId"])
                        db.session.add(episode_data)
                        episode_list.append(episode_data)
    season_data = Season(season_title=season_json['season_title'], yt_playlist_url=season_json['yt_playlist_url'], episodes=episode_list, published_year=season_json['published_year'])
    db.session.add(season_data)
    check.seasons.append(season_data)
    db.session.commit()


def addNewCast(table_name, row_id, actor_name):
    check = table_name.query.filter_by(id=row_id).first()
    print("Do u want to add " + actor_name + " in " + check.title + " [y/n]: ")
    ans = input()
    if ans == "n":
        return
    actor_list = []
    actor_list.extend(check.actors)
    actor_check = Actor.query.filter_by(name=actor_name).first()
    if actor_check is None:
        actor_data = Actor(name=actor_name)
        db.session.add(actor_data)
        actor_list.append(actor_data)
        db.session.commit()
    else:
        actor_list.append(actor_check)
    check.actors = actor_list
    db.session.commit()

def addNewDirector(table_name, row_id, director_name):
    check = table_name.query.filter_by(id=row_id).first()
    print("Do u want to add " + director_name + " in " + check.title + " [y/n]: ")
    ans = input()
    if ans == "n":
        return
    director_list = []
    director_list.extend(check.directors)
    director_check = Director.query.filter_by(name=director_name).first()
    if director_check is None:
        director_data = Director(name=director_name)
        db.session.add(director_data)
        director_list.append(director_data)
        db.session.commit()
    else:
        director_list.append(director_check)
    check.directors = director_list
    db.session.commit()

def changeThumbnail(table_name, row_id, new_thumnail):
    check = table_name.query.filter_by(id=row_id).first()
    print("Do u want to change thumbnail in " + check.title + " from " + str(check.thumbnail) + " to " + new_thumnail + " [y/n]: ")
    ans = input()
    if ans == "n":
        return
    check.thumbnail = new_thumnail
    db.session.commit()

def changeDescription(table_name, row_id, new_description):
    check = table_name.query.filter_by(id=row_id).first()
    print("Do u want to change description in " + check.title + " [y/n]: ")
    ans = input()
    if ans == "n":
        return
    check.description = new_description
    db.session.commit()

def changeRuntime(table_name, row_id, runtime_min):
    check = table_name.query.filter_by(id=row_id).first()
    print("Do u want to change runtime in " + check.title + " from " + str(check.runtime_min) + " to " + str(runtime_min) + " [y/n]: ")
    ans = input()
    if ans == "n":
        return
    check.runtime_min = runtime_min
    db.session.commit()

def changeState(table_name, row_id, state):
    check = table_name.query.filter_by(id=row_id).first()
    print('Do u want to change state ' + check.title + " from " + str(check.state) + " to " + str(state) + " [y/n]: ")
    ans = input()
    if ans == "n":
        return
    check.state = state
    db.session.commit()

def changePublishedYearMovie(row_id, published_year):
    check = Movie.query.filter_by(id=row_id).first()
    print(check)
    print('Do u want to change published year ' + check.title + " from " + str(check.published_year) + " to " + str(published_year) + " [y/n]: ")
    ans = input()
    if ans == "n":
        return
    check.published_year = published_year
    db.session.commit()


def changeStudio(table_name, row_id, studio_name_list):
    check = table_name.query.filter_by(id=row_id).first()
    print('Do u want to change studio in ' + check.title + " from " + str(check.studio) + " to " + str(studio_name_list) + " [y/n]: ")
    ans = input()
    if ans == "n":
        return
    studio_list = []
    for studio in studio_name_list:
        studio_check = Studio.query.filter_by(name=studio).first()
        if studio_check is None:
            studio_data = Studio(name=studio)
            db.session.add(studio_data)
            studio_list.append(studio_data)
        else:
            studio_list.append(studio_check)
    check.studio = studio_list
    db.session.commit()

def deleteAll(table, row_id, table_name):
    check = table.query.filter_by(id=row_id).first()
    print('Do u want to delete ' + check.title + " [y/n]: ")
    ans = input()
    if ans == "n":
        return
    print("Deleting.... " + check.title)
    print(f"{table_name=} ")
    if table_name == "Series" or table_name == "Tvshow":
        for season in check.seasons:
            for ep in season.episodes:
                Episode.query.filter_by(id=ep.id).delete()
            Season.query.filter_by(id=season.id).delete()
    table.query.filter_by(id=row_id).delete()
    db.session.commit()


def deleteCast(table_name, row_id, deleted_cast):
    actor_list = []
    check = table_name.query.filter_by(id=row_id).first()
    for actor in check.actors:
        if actor.name == deleted_cast:
            continue
        actor_list.append(actor)
    check.actors = actor_list
    db.session.commit()

def deleteDirector(table_name, row_id, deleted_director):
    director_list = []
    check = table_name.query.filter_by(id=row_id).first()
    for director in check.directors:
        if director.name == deleted_director:
            continue
        director_list.append(director)
    check.directors = director_list
    db.session.commit()

def deleteForever(table_name, row_id):
    check = table_name.query.filter_by(id=row_id).first()
    print("Do u want to delete " + check.name + " [y/n]:")
    ans = input()
    if ans == "n":
        return
    table_name.query.filter_by(id=row_id).delete()
    db.session.commit()

def deleteEpisodeFromYTURL(yt_url):
    check = Episode.query.filter_by(youtube_url=yt_url).first()
    print("Do u want to delete " + check.title + " [y/n]:")
    ans = input()
    if ans == "n":
        return
    Episode.query.filter_by(youtube_url=yt_url).delete()
    db.session.commit()
# def deleteActor(actor_name):
#     print("Do u want to delte actor " + actor_name + " [y/n]: ")
#     ans = input()
#     if ans == "n":
#         return
#     Actor.query.filter_by(name=actor_name).delete()
#     db.session.commit()

def deleteSeason(season_id):
    check = Season.query.filter_by(id=season_id).first()

    print("Do u want to delete season" + str(season_id) + " [y/n]: ")
    ans = input()
    if ans == "n":
        return
    # curr_season = None
    # for season in check.seasons:
    #     if season.id == season_id:
    #         curr_season = season
    # for ep in curr_season.episodes:
    #     Episode.query.filter_by(id=ep.id).delete(synchronize_session=False)
    Season.query.filter_by(id=season_id).delete()
    db.session.commit()

def removeSeason(table_name, row_id, season_id):
    check = table_name.query.filter_by(id=row_id).first()

    print("Do u want to remove season" + str(season_id) + " from " + str(check.title) + " [y/n]: ")
    ans = input()
    if ans == "n":
        return
    required_season = []
    for season in check.seasons:
        if season.id != season_id:
            required_season.append(season)

    check.seasons = required_season
    db.session.commit()

def changeSeasonName(row_id, new_title):
    check = Season.query.filter_by(id=row_id).first()

    print("Do u want to change season name  from " + str(check.season_title) + " to " + str(new_title) + " [y/n]: ")
    ans = input()
    if ans == "n":
        return
    check.season_title = new_title
    db.session.commit()

def changeStudioName(curr_studio_name, new_studio_name):
    check = Studio.query.filter_by(name=curr_studio_name).first()

    print("Do u want to change studio name  from " + str(check.name) + " to " + str(new_studio_name) + " [y/n]: ")
    ans = input()
    if ans == "n":
        return
    check.name = new_studio_name
    db.session.commit()


print("=====================================================")


# movie_json = {
#     "title": "",
#     "youtube_url": "",
#     "description": "",
#     "genres": [""],
#     "directors": [""],
#     "actors": [""],
#     "published_year": "",
#     "studio": [""],
#     "runtime_min": 0
# }

movie_json = {
    "title": "Gaikotsu Kishi-sama, Tadaima Isekai e Odekakechuu บันทึกการเดินทางต่างโลกของท่านอัศวินกระดูก - ฉบับมัดรวมทุกตอน",
    "youtube_url": "2-RE8YbuXrI",
    "description": "บันทึกการเดินทางต่างโลกของท่านอัศวินกระดูก เมื่อ “อาร์ค” ลืมตาตื่นขึ้นมาอีกที เขาก็อยู่ในต่างมิติด้วยร่างกายของตัวละครที่เขาเคยใช้ในเกม MMORPG เสียแล้ว ซึ่งร่างนั้นคือ “อัศวินกระดูก” ที่ภายในสวมใส่เกราะ และเป็นกระดูกทั่วร่างนั่นเอง ถ้ามีใครรู้เรื่องนี้ มีหวังถูกเข้าใจผิดว่าเป็นมอนเตอร์จนถูกไล่ล่าแน่นอน!? อาร์คจึงได้ตัดสินใจที่จะใช้ชีวิตในฐานะทหารรับจ้าง ทว่าเขาก็ไม่ใช่ผู้ชายที่จะมองข้ามเรื่องเลวร้ายที่เกิดขึ้นตรงหน้าไปได้หน้าตายเฉย! เรื่องราวแฟนตาซีการ “กอบกู้โลก” ต่างมิติ โดยไม่รู้ตัวของอัศวินโครงกระดูก กำลังจะเปิดม่านแล้ว!!",
    "genres": ["อนิเมะญี่ปุ่น", "แอ็คชั่น", "แฟนตาซี", "ซับไทย", "การ์ตูน"],
    "directors": ["Katsumi Ono"],
    "actors": ["Miyu Tomita", "Kousuke Toriumi", "Daiki Hamano", "Tomoaki Maeno", "Akira Ishida", "Fairouz Ai", "Minoru Shiraishi", "Kengo Kawanishi", "Nene Hieda", "Rumi Okubo"],
    "published_year": "2565",
    "studio": ["Muse Thailand"],
    "runtime_min": 284
}


movie_json = {
    "title": "แสงสุดท้ายของอีเหี่ยน (Last Night of Ehean)",
    "youtube_url": "XWw-qgTiAq8",
    "description": "เรื่องราวของเด็กบ้านนานามว่า เหี่ยน (นรีรัตน์ สีหราชนิเวศน์) เธอมีความใสซื่อ ตรงไปตรงมา รักบ้านเกิดที่สุด แต่ชอบเสี่ยงดวงเพียงเพื่อหวังช่วยแม่ปลดหนี้ จึงหนีมาเมืองกรุงตามหาพ่อ สุดท้ายไม่มีเงินกลับบ้าน เหี่ยน ได้งานทำด้วยการฝากจากกะเทยคนหนึ่ง เรื่องราวความสนุกจึงเกิดขึ้น และสุดท้ายก็ไปจบที่บ้านโคกตาล จ.ศรีสะเกษ ครบทุกรส มีแง่คิด มุมมองที่เป็นบวก สอดแทรกเนื้อหาสาระเชิงท่องเที่ยวได้อย่างลงตัว",
    "genres": ["หนังไทย", "คอมเมดี้", "โรแมนติก"],
    "directors": ["นรินธ์น แก้วสีเงิน"],
    "actors": ["พศิน เรืองวุฒิ", "นรีรัตน์ สีหราชนิเวศน์", "กัญญ์ชัญญ์ เธียรวิชญ์", "สมพงษ์ คุนาประถม", "รุ้งลาวัณย์ โทนะหงษา", "ชุมพร เทพพิทักษ์"],
    "published_year": "2558",
    "studio": ["Right Comedy"],
    "runtime_min": 1
}

movie_json = {
    "title": "ทิมมวยไทย หัวใจติดเพลง",
    "youtube_url": "sXCqksKT0Lk",
    "description": "ทิม ลูกชายเจ้าของค่ายมวย ซึ่งพ่อของเขาตั้งใจที่จะฝึกซ้อมเขาให้เป็นนักมวยระดับฝีมือ เพื่อไปต่อยกับลูกชายของคู่อริ โดยมีค่ายมวยเป็นเดิมพัน แต่ทิมมีความใฝ่ฝันอยากจะเป็นนักร้อง จึงหนีพ่อของเขาเพื่อไปตามหาฝัน จนทำให้เขาได้พบรักกับจินตหรา สาวผู้รักในเสียงเพลง แต่สุดท้ายพ่อของเขาก็ตามหาเขาจนเจอและขอร้องให้เขากลับไปต่อยมวยเพื่อรักษาค่ายมวยไว้ เขาจึงต้องตัดสินใจเลือกระหว่างความฝันและความกตัญญู.....",
    "genres": ["หนังไทย", "แอ็คชั่น", "คอมเมดี้"],
    "directors": [],
    "actors": ["เกริกไกร อันสนธิ์", "พรรณวรินทร์ ศรีสวัสดิ์", "โกวิท วัฒนกุล", "อำพล รัตน์วงศ์"],
    "published_year": "2547",
    "studio": ["Right Comedy"],
    "runtime_min": 91
}

movie_json = {
    "title": "รัก หมัด สั่ง (Hooked On Love)",
    "youtube_url": "N9qu8HYbG3A",
    "description": "เรื่องราวของความรักที่ต้องใช้หมัดมวยมาเป็นตัวตัดสิน จะเกิดอะไรขึ้นเมื่อครูหนุ่มรูปหล่อพ่อรวยจากเมืองกรุง เดินทางมารับสอนหนังสืออยู่ที่ตำบลท่าทอง จ. สุพรรณบุรีและบังเอิญมาเจอรักแรกพบ ตกหลุมรักสาวงามประจำตำบลเข้าอย่างจัง เลยต้องถอดชุดครูมาใส่นวมสวมมงคลขึ้นชก เพื่อพิสูจน์รักแท้ เรื่องราวความรักในครั้งนี้จะเป็นอย่างไร จะราบรื่นหรือมีอุปสรรคหรือไม่ต้องติดตาม!",
    "genres": ["หนังไทย", "คอมเมดี้", "โรแมนติก"],
    "directors": ["ราชวัตร ฐิติวรดากูล"],
    "actors": ["ฐปนัท สัตยานุรักษ์", "อิงฟ้า เกตุคำ", "สิทธิพันธ์ กลมเกลี้ยง", "สิรยา วานิชชา", "ปุณฐิภาภัคร์ สุวรรณราช", "ณรัฐ พัฒนาพงศ์ชัย", "เกรียงไกร สินสนอง", "นุศรา ประวันณา"],
    "published_year": "2559",
    "studio": ["Right Comedy"],
    "runtime_min": 99
}

movie_json = {
    "title": "คู่อันตราย",
    "youtube_url": "JwXQuvraiOo",
    "description": "เรื่องราวของกลุ่มก่อการร้าย โดยมีกำพลเป็นผู้นำและมีนายตำรวจชั้นผู้ใหญ่เข้าร่วมด้วย กลุ่มก่อการร้ายได้ใช้คนเข้าเล่นเกมที่ตัวเองสร้างขึ้นโดยให้นักฆ่าเป็นผู้ล่าและฆ่าตำรวจนายหนึ่งจนตาย ตำรวจนายนี้ชื่อ ชาญ อยู่ในหน่วยจู่โจม ซึ่งเขาเป็นพี่ชายของริน เธอกับเมธาได้เข้ามาสืบคดีพี่ชายตัวเองจึงได้รู้เรื่องราวทุกอย่าง ทั้งคู่จึงได้เข้าทำลายกลุ่มของกำพลและทำลายเกมชั่วของพวกมันจนสำเร็จ",
    "genres": ["หนังไทย", "แอ็คชั่น"],
    "directors": ["เอกชัย เอื้อครองธรรม"],
    "actors": ["กนิษฐรินทร์ พัชรภักดีโชติ", "พชรมน แสนเสนาะ", "ปราโมทย์ สุขสถิต"],
    "published_year": "2545",
    "studio": ["Right Comedy"],
    "runtime_min": 84
}

movie_json = {
    "title": "ต้มยำเก้ง 2",
    "youtube_url": "Js7zwSkyHtM",
    "description": "ลุงแพะ หนุ่มใหญ่ ชึ่งได้สูตรกาทำต้มยำเก้งรสเด็ดมาจากบรรพบ­ุรุษ ซึ่งขายดีเป็นอยางมาก ในขณะที่ภัคตาคารใหญ่ของ เฮียเฉิน ซึ่งเน้นต้มยำเหมือนกัน กลับไม่มีลูกค้าเลย ก็เลยจะมาขอซื้อสูตร แต่ลุงแพะก็ไม่ยอมขายให้ จึงทำให้เฮียเฉินโกรธถึงขนาดต้องไปลักพาตั­วมา เพื่อจะบีบบังคับให้มอบสูตรเด็ดมาให้ จึงทำให้เกิดเรื่องราว วุ่นวาย มากมาย เดือดร้อนถึง ชู ลูกชายคนเดียวของลุงแพะ ต้องกลับมาช่วยพ่อ ส่วนเรื่องที่จะสืบสานการทำต้มยำของตระกูล­ต่อไปได้หรือไม่",
    "genres": ["หนังไทย", "ยอดนิยม", "คอมเมดี้"],
    "directors": [],
    "actors": ["ศรสุทธา กลั่นมาลี", "ชูเกียรติ เอี่ยมสุข", "เอนก อินทะจันทร์", "มูซา อะมิดู จอห์นสัน", "ฉัตรรัตน์ วัฒน์จินดาศิริ", "จุมพจน์ ศรีจามร"],
    "published_year": "2564",
    "studio": ["Right Comedy"],
    "runtime_min": 85
}

movie_json = {
    "title": "หอแห๋วแหก (Hor Haew Haek)",
    "youtube_url": "8T3SdZLd81k",
    "description": "เมื่อเหล่าสาวประเภทสองจะต้องมาปฎิบิติการกู้หอที่กำลังจะเจ๊ง จากผีเฮี้ยน ภารกิจไล่ผีสุดเริ่ดเพื่อช่วยเหลือของสาวๆจึงบังเกิด",
    "genres": ["หนังไทย", "ยอดนิยม", "คอมเมดี้"],
    "directors": [],
    "actors": ["ผดุง ทรงแสง", "เอนก อินทะจันทร์", "ชัชชัย จำเนียรกุล"],
    "published_year": "2563",
    "studio": ["Right Comedy"],
    "runtime_min": 78
}

movie_json = {
    "title": "องค์แบก 2 (Ong Bak 2)",
    "youtube_url": "sLteVG8Gcso",
    "description": "สืบสานตำนานความฮาจากภาคแรก การกลับมาอีกครั้งขององค์ที่ต้องมาเผชิญเหตุการณ์ที่ไม่คาดฝันจากหมวดโทนี่ที่กลับมาแก้แค้น โดยส่งเอมมี่มาหลอกให้เซ็นต์มอบสมบัติให้ไป จนทำให้เสี่ยขาวเครียดจนถึงกับเป็นอัมพฤกต์ องค์จะแก้สถานการณ์กลับมาได้ไหม เสี่ยจะกลับมาหายเป็นปกติไหม รับประกันความฮาเหมือนเดิม",
    "genres": ["หนังไทย", "ยอดนิยม", "คอมเมดี้"],
    "directors": [],
    "actors": ["ชูเกียรติ เอี่ยมสุข", "มูซา อะมิดู จอห์นสัน", "เอนก อินทะจันทร์", "อมลวรรณ ศิริกิตติรัตน์", "สุธน เวชกามา"],
    "published_year": "2563",
    "studio": ["Right Comedy"],
    "runtime_min": 90
}

movie_json = {
    "title": "8E88 แฟนลั้ลลา",
    "youtube_url": "i4A8UZDb0uU",
    "description": "คุนจะแต่งงานกับบุษบา วันที่จะไปรับชุดแต่งงาน คุนถูกจับข้อหาเป็นฆาตกรฆ่านักการเมือง จากเจ้าบ่าว คุน เลยกลายเป็น นช.คุน แทนเจ้าพ่อดมกับลูกแจ๊ส ผู้มีอิทธิพลนอกคุกตามราวี นช.คุน เพราะคิดว่า นช.คุน เก็บคลิปเอาไว้ ถึงขนาดสั่งย้าย นช.คุน ให้ไปอยู่แดน 8E88 (แดนประหาร) เพื่อต้องการกดดันให้ นช.คุน ส่งคลิปคืน แต่ นช.คุน ไม่รู้เรื่อง สองพ่อลูกจึงขู่ฆ่าบุษบา ส้มลูกนักการเมืองที่ถูก นช.คุนฆ่า ต้องการคลิปเพื่อเปิดโปงคนร้ายตัวจริง จึงให้ บอส เพื่อนชายคนสนิทเข้าไปในคุก เพื่อไปตีสนิทกับ นช.คุน เพราะคิดว่า นช.คุน ต้องรู้เรื่องคลิป ปฏิบัติการแหกคุกเพื่อหาคลิปจึงได้เริ่มต้นขึ้น",
    "genres": ["หนังไทย", "ยอดนิยม", "คอมเมดี้", "อาชญากรรม"],
    "directors": ["วิโรจน์ ทองชิว", "ปานสิริ ทองชิว"],
    "actors": ["จตุรงค์ พลบูรณ์", "อัฐมา ชีวนิชพันธ์", "มารี เออเจนี เลอเลย์", "ผดุง ทรงแสง", "อุดม ทรงแสง", "จักรพันธ์ วงศ์คณิต"],
    "published_year": "2553",
    "studio": ["Right Comedy"],
    "runtime_min": 95
}

movie_json = {
    "title": "บุปผาโรตี หอนี้ผีดุ",
    "youtube_url": "JhNknuQpD_w",
    "description": "เรื่องราวความรักระหว่างกฤษ หนุ่มขายโรตีกับบุปผานักศึกษาสาวสวย ความรักของทั้งคู่เบ่งบานกำลังจะได้ที่ แต่แล้วบุปผาก็เสียชีวิตลง จากความอาลัยและห่วงหาทำให้วิญญาณของเธอยังวนเวียนหลอกหลอนชาวอพาร์ทเม้นท์ต้องกระเจิดกระเจิง",
    "genres": ["หนังไทย", "ยอดนิยม", "คอมเมดี้"],
    "directors": [],
    "actors": ["เอนก อินทะจันทร์", "ชูเกียรติ เอี่ยมสุข", "จุมพจน์ ศรีจามร", "มูซา อะมิดู จอห์นสัน"],
    "published_year": "2563",
    "studio": ["Right Comedy"],
    "runtime_min": 65
}

movie_json = {
    "title": "โหดจนเหี่ยว (Hod Jon Heaw)",
    "youtube_url": "ROZqG_y6bVE",
    "description": "เมื่อนักเลงเก่ากลับตัวกลับใจมาทำอาชีพสุจ­ริต แต่พอขายของก็โดนนักเลงกลุ่มอื่นคอยตามมาร­ังควาน นักเลงเก่าจึงต้องแสดงฝีมือเพื่อความ ถั่ววว ต้มมมม ในแบบฉบับสุดฮา",
    "genres": ["หนังไทย", "ยอดนิยม", "คอมเมดี้"],
    "directors": [],
    "actors": ["เอนก อินทะจันทร์", "ผดุง ทรงแสง", "อาคม ปรีดากุล"],
    "published_year": "2563",
    "studio": ["Right Comedy"],
    "runtime_min": 76
}

movie_json = {
    "title": "รัชดาแลนด์ (Spooky Soap Land)",
    "youtube_url": "S4fNdDZZaZk",
    "description": "เรื่องของบัวตอง หมอนวดสาวที่หายตัวไปโดยไม่ทราบสาเหตุ จากสถานบันเทิงตั้งอยู่ย่านรัชดา ต่อมาก็มีเรื่องที่สร้างหวาดกลัวให้กับแขกที่มาใช้บริการ ซึ่งจริง ๆแล้ว บัวตองมาเพื่อบอกความจริงบางอย่าง ลองติดตามดูว่ามาบอกอะไร ทั้งฮา ทั้งน่าสะพรึงกลัว",
    "genres": ["หนังไทย", "ยอดนิยม", "คอมเมดี้", "สยองขวัญ"],
    "directors": [],
    "actors": ["ธัณย์สิตา สุวัชราธนากิตติ์", "ชูเกียรติ เอี่ยมสุข", "อนัญญา เมธาจันทรกูล", "เอนก อินทะจันทร์", "วลัชณัฏฐ์ ก้องภพตารีย์", "มูซา อะมิดู จอห์นสัน"],
    "published_year": "2563",
    "studio": ["Right Comedy"],
    "runtime_min": 87
}

movie_json = {
    "title": "มือปืนดาวลูกไก่ (Chicky Killer)",
    "youtube_url": "4RLHkkeQOMw",
    "description": "เต๋าได้รับมอบหมายงานจากเสี่ยโหวงให้ไปฆ่า­ลูกไก่สายลับจากหน่วยงานของรัฐบาล แต่เหตูการณ์กลับตาลปัตร เมื่อนักฆ่าตกหลุมรักเป้าหมายของตนเอง จึงยอมหักหลังเสี่ยโหวง เพื่อจะหนีไปจากเหล่านักฆ่าคนอื่นๆ ที่ตามมาเก็บทั้งสองคน เต๋าและลูกไก่จะเป็นเช่นไร",
    "genres": ["หนังไทย", "คอมเมดี้", "อาชญากรรม", "ยอดนิยม"],
    "directors": [],
    "actors": ["ชูเกียรติ เอี่ยมสุข", "จุมพจน์ ศรีจามร", "มูซา อะมิดู จอห์นสัน", "เอนก อินทะจันทร์"],
    "published_year": "2562",
    "studio": ["Right Comedy"],
    "runtime_min": 82
}

movie_json = {
    "title": "เขาวานให้หนูเป็นสายลับ ลับ (Apparently Secret Agent)",
    "youtube_url": "p32joJlvxI8",
    "description": "เกิดคดีอาชญากรรมในกองถ่ายหนังโป๊ เดือดร้อนถึงตำรวจมาสืบสวนคดี เรื่องราววุ่นๆ ฮาๆ จึงเริ่มต้นขึ้น เดือดร้อนตั้งแต่ เด็กยกไฟ ไปถึง ผู้กำกับ และ นางเอกดาวโป๊",
    "genres": ["หนังไทย", "คอมเมดี้"],
    "directors": [],
    "actors": ["เอนก อินทะจันทร์", "จุมพจน์ ศรีจามร", "วลัชณัฏฐ์ ก้องภพตารีย์", "มูซา อะมิดู จอห์นสัน"],
    "published_year": "2563",
    "studio": ["Right Comedy"],
    "runtime_min": 76
}

movie_json = {
    "title": "ฮาชิมิ โปรเจกต์ HA-CHI-MI PROJECT",
    "youtube_url": "G8qlRN9yAlM",
    "description": "เรื่องของท่านเค้าท์แดรกคูล่า ที่กำลังจะสูญเสียพละกำลังไปเนื่องจากการไม่ยอมกินเลือดมนุษย์เนื่องจากไปรับปากกับภรรยาไว้ ทำให้ต้องพ่ายแพ้ต่อศัตรูอย่างพวกมนุษย์หมาป่า ซึ่งคิดที่จะทำโปรเจกต์เกี่ยวกับฆ่าล้างบางผีดูดเลือดเพื่อออนแอร์ทางยูทูป ท่านเค้าท์คิดที่จะหาทายาทมาสืบทอดก่อนที่จะตาย และจำได้ว่าเคยมีลูกชายคนหนึ่งแต่อยู่ที่เมืองไทย จึงได้มาหา และได้พบกับเหตุการณ์ต่าง ๆ มากมายซึ่งบอกได้คำเดียวว่า ฮา ฮา แล้วก็ฮาสวด ๆ กว่าจะจบได้",
    "genres": ["หนังไทย", "คอมเมดี้"],
    "directors": [],
    "actors": ["จุมพจน์ ศรีจามร", "ชูเกียรติ เอี่ยมสุข", "มูซา อะมิดู จอห์นสัน", "ทรรศิกา ยุติมิตร", "วลัชณัฏฐ์ ก้องภพตารีย์"],
    "published_year": "2562",
    "studio": ["Right Comedy"],
    "runtime_min": 86
}

movie_json = {
    "title": "SUGAR WAR น้ำตาลแพง",
    "youtube_url": "oaO5LvEHA7A",
    "description": "เรื่องของสองเฮียอยู่ในถ้ำเดียวกันไม่ได้ ที่เปิดร้านขายของติดกัน โดยที่ลูกชายร้านเฮียหน่อย หลงรักลูกสาวร้านบังแระ ต่อมามีเหตุการณ์น้ำตาลขาดตลาด ก็ยิ่งทำให้สองร้านต้องมาห้ำหั่นกันทั้งเรื่องธุรกิจและเรื่องความรัก",
    "genres": ["หนังไทย", "ยอดนิยม", "คอมเมดี้"],
    "directors": [],
    "actors": ["ศรสุทธา กลั่นมาลี", "จุมพจน์ ศรีจามร", "สุธน เวชกามา", "เอนก อินทะจันทร์"],
    "published_year": "2562",
    "studio": ["Right Comedy"],
    "runtime_min": 87
}

movie_json = {
    "title": "การไฟฟ้ามาหานะเธอ",
    "youtube_url": "9QEFWyW6Ttw",
    "description": "เมื่อหนุ่มเก็บค่าไฟฟ้าและเพื่อนสนิท ต้องมาเรียกเก็บค่าไฟฟ้าจากบ้านลูกสาวสวย จึงมีแผนการกลเม็ดจีบสาวที่ทำให้ สาวๆต้องใจอ่อน แต่มีคุณพ่อจอมเฮี้ยวเป็นอุปสรรคขวางความรักกับทั้งสอง ผลจะออกมาเป็นอย่างไร",
    "genres": ["หนังไทย", "โรแมนติก", "คอมเมดี้", "ยอดนิยม"],
    "directors": [],
    "actors": ["ชัชชัย จำเนียรกุล", "เอนก อินทะจันทร์", "ผดุง ทรงแสง"],
    "published_year": "2562",
    "studio": ["Right Comedy"],
    "runtime_min": 71
}

movie_json = {
    "title": "ฮา 7 ทีดี 7 หน",
    "youtube_url": "hwZ_A_BiPrQ",
    "description": "แจ๊สกับบุ๋ม เป็นเพื่อนรักกัน โดยแจ๊สนั้นอยากเป็นดารา ส่วนบุ๋มก็ใฝ่ฝันจะเป็นนักร้อง พวกเขาจึงมาหาเพื่อนชื่อ ธงธง ที่อยู่กรุงเทพ ธงธงได้พาทั้งสองมาฝากกับบริษัท ของนักแสดงตลกชื่อดัง แอนนา ถั่วต้วม ซึ่งคิดว่าจะช่วยให้ฝันของพวกเขา เป็นจริงได้ ส่วนฝันของทั้งสอง จะเป็นจริงได้ ไม่ใช่เรื่องง่าย เพราะพวกเขาต้องเจอกับอุปสรรคต่าง ๆ มากมาย ซึ่งเพื่อนทั้งสองคนนี้ จะฝ่าฝันไปได้ และทำสำเร็จหรือไม่ ด้วยวิธีการใด จะฮากันกี่ทีนั้นต้องติดตามชม",
    "genres": ["หนังไทย", "ยอดนิยม", "คอมเมดี้"],
    "directors": [],
    "actors": ["ผดุง ทรงแสง", "ชูเกียรติ เอี่ยมสุข", "เอนก อินทะจันทร์", "นที ธีระเสรีวงศ์"],
    "published_year": "2562",
    "studio": ["Right Comedy"],
    "runtime_min": 85
}

movie_json = {
    "title": "องค์แบก",
    "youtube_url": "-9ixUc2Qti4",
    "description": "องค์ ชายหนุ่มจับกัง รับจ้างแบกข้าวสารอยู่ที่โรงสีของเสี่ยขาว ซึ่งแพนเค้ก ลูกสาวของเสี่ยขาวเกิดหลงรักองค์ จึงหลอกล่อให้องค์ได้เสียเป็นสามีของเธอโดยที่เขาไม่เต็มใจ ในขณะเดียวกัน หมวดโทนี่ นายตำรวจหนุ่มหน้ามน ก็วางแผนที่จะไปสู่ขอแพนเค้ก เพื่อหวังจะได้ครอบครองโรงสีของเสี่ยขาว ทั้งหมดจึงกลายเป็นเรื่องราวที่กลับตาลปัตร จากความรักกลายเป็นความแค้นที่แสนสนุกเฮฮา",
    "genres": ["หนังไทย", "คอมเมดี้", "ยอดนิยม"],
    "directors": [],
    "actors": ["ชูเกียรติ เอี่ยมสุข", "เอนก อินทะจันทร์", "สุธน เวชกามา", "มูซา อะมิดู จอห์นสัน"],
    "published_year": "2562",
    "studio": ["Right Comedy"],
    "runtime_min": 65
}

movie_json = {
    "title": "พระหยอง อาจารย์เหน่ง นักเลงหน่อย",
    "youtube_url": "_VRuBJhoTVM",
    "description": "ที่หมู่บ้านหนึ่งที่ชาวบ้านเชื่อเรื่องงมง­าย ยิ่งมีผู้ใหญ่บ้าน ที่เป็นคนเชื่อคนง่าย ประกอบในหมู่บ้านนี้ มีอาจารย์เหน่ง ที่ตั้งตนเป็นผู้มีคาถาอาคม หลอกลวงชาวบ้านไปวัน ๆ แต่โชคยังดีที่หมู่บ้านนี้มีพระหยอง ที่มาคอยใช้หลักเหตุและผลช่วยเตือนสติชาวบ­้าน ไม่ให้งมงาย เรื่องจะจบแบบฮากันขนาดไหน ก็ต้องติดตามกันให้ได้นะโยม สาธุ",
    "genres": ["หนังไทย", "ยอดนิยม", "คอมเมดี้"],
    "directors": [],
    "actors": ["จุมพจน์ ศรีจามร", "ชูเกียรติ เอี่ยมสุข", "เอนก อินทะจันทร์", "วลัชณัฏฐ์ ก้องภพตารีย์", "หฤษพล สมจิตรนา", "มูซา อะมิดู จอห์นสัน"],
    "published_year": "2554",
    "studio": ["Right Comedy"],
    "runtime_min": 101
}

movie_json = {
    "title": "Mairimashita! Iruma-kun อิรุมะคุง ผจญในแดนปีศาจ! ภาคที่ 2 - ฉบับมัดรวมทุกตอน",
    "youtube_url": "oQbmVJFGIiE",
    "description": "สึซึกิ อิรุมะ หนุ่มนิสัยดีวัย 14 ปีที่ถูกขายให้กับปีศาจ แต่กลับกลายเป็นว่า ปีศาจต้องการได้เขาเป็นหลาน และส่งให้เขาไปเรียนต่อในโรงเรียนปีศาจที่เป็นผู้อำนวยการอยู่ อิรุมะ ต้องเรียนร่วมกับปีศาจตนอื่นในฐานะนักเรียนหน้าใหม่ ถึงจะอ่อนแอ ไม่ปฏิเสธคนที่เดือดร้อน แต่เนื่องจากหนีปัญหามาทั้งชีวิต ทำให้เขามีความสามารถการป้องกันตัว (หลบหลีก) ที่ไร้ขีดจำกัด จนยากที่จะโดนโจมตีจากคู่ต่อสู้",
    "genres": ["อนิเมะญี่ปุ่น", "เหนือธรรมชาติ", "คอมเมดี้", "ซับไทย", "แฟนตาซี", "การ์ตูน"],
    "directors": ["Makoto Moriwaki"],
    "actors": ["Daisuke Ono", "Junichi Suwabe", "Genki Okawa", "Ayaka Asai", "Ayumu Murase", "Ryohei Kimura", "Mitsuki Saiga", "Gakuto Kajiwara", "Kaede Hondo", "Haruna Asami"],
    "published_year": "2562",
    "studio": ["Muse Thailand"],
    "runtime_min": 275
}

movie_json = {
    "title": "Shinchou Yuusha ผู้กล้าสุดแกร่ง ขี้ระแวงขั้นวิกฤติ - ฉบับมัดรวมทุกตอน",
    "youtube_url": "48oTbc5Zoog",
    "description": "Kono Yuusha ga Ore Tueee Kuse ni Shinchou Sugiru OreTuee กล่าวถึง เทพธิดา ลิสต้า ได้อัญเชิญผู้กล้ามาช่วยในโลกของเธอ ริวกูอิน เซยะ ถึงเขาจะมีความสามารถที่สูง แต่กลับเป็นพวกขี้ระแวงเป็นพิเศษ เช่น สั่งชุดเกราะทีละ 3 ชุด (สำรอง 2 ชุด) หรือ ใช้พลังเต็มที่เพื่อสู้สไลม์โดยไม่ประมาท",
    "genres": ["แฟนตาซี", "อนิเมะญี่ปุ่น", "การ์ตูน", "แอ็คชั่น", "ผจญภัย", "คอมเมดี้", "ซับไทย"],
    "directors": ["มาซายูกิ ซาโคอิ"],
    "actors": ["อาคิ โทโยสาคิ", "เคนโกะ คาวานิชิ", "อาโออิ โคกะ", "ยูอูอิชิโระ อูเมฮาระ"],
    "published_year": "2563",
    "studio": ["Muse Thailand"],
    "runtime_min": 284
}

movie_json = {
    "title": "Munou na Nana แผนลับดับศัตรู - ฉบับมัดรวมทุกตอน",
    "youtube_url": "ZT47zdcyL10",
    "description": "กลุ่มนักเรียนที่มีพลังพิเศษถูกฝึกบนเกาะ เพื่อต่อสู้กับสัตว์ประหลาดซึ่งเป็นภัยคุกคามของมนุษย์ จนกระทั่ง นานะ ถูกส่งมา ภารกิจลอบสังหารพวกผู้มีพลังพิเศษ ที่กำลังจะเป็นกลายเป็นศัตรูของมนุษย์ในอนาคตเสียเอง ด้วยการฆ่าทีละคนอย่างลับๆ โดยไม่ให้ใครสังเกต แต่สถานการณ์เริ่มซับซ้อนมากขึ้น เมื่อเธอกลายเป็นผู้ต้องสงสัย ทำให้มีทั้งศัตรู และผู้ที่ต้องการใช้เธอเป็นเครื่องมือ",
    "genres": ["เหนือธรรมชาติ", "ระทึกขวัญ", "จิตวิทยา", "อนิเมะญี่ปุ่น", "การ์ตูน", "ซับไทย"],
    "directors": ["Shinji Ishihira"],
    "actors": ["Mai Nakahara", "Hiro Shimono", "Atsushi Tamaru", "Yuuichi Nakamura", "Miyu Tomita", "Kouji Yusa", "Rumi Ookubo", "Yuna Kamakura", "Aiko Ninomiya"],
    "published_year": "2563",
    "studio": ["Muse Thailand"],
    "runtime_min": 307
}

movie_json = {
    "title": "JoJo’s Bizarre Adventure โจโจ้ ล่าข้ามศตวรรษ - ฉบับมัดรวมทุกตอน",
    "youtube_url": "IumwLS7LyeY",
    "description": "เรื่องราวเกิดขึ้นราวปลายศตวรรษที่ 19 ”โจนาธาน โจสตาร์” เด็กหนุ่มผู้ถือกำเนิดในสกุลขุนนางอังกฤษที่มั่งคั่ง มีชีวิตที่หลายๆคนอิจฉา แต่แล้ววันหนึ่ง เมื่อ”จอร์จ โจสตาร์”ผู้เป็นพ่อของ “โจนาธาน” ได้พา”ดิโอ บรันโด้” เข้ามาอาศัยอยู่ในบ้านในฐานะบุตรบุญธรรมของตระกูลโจสตาร์ ซึ่ง”ดิโอ บรันโด้”ผู้นี้แหละ คือผู้ที่จะมาทำให้ชีวิตอันแสนสงบสุขของเขาก็มีอันต้องเปลี่ยนแปลงไปตลอดกาล…! และนี่คือจุดเริ่มต้นของการต่อสู้ และการผจญภัยของสุภาพบุรุษตระกูลโจสตาร์ที่ประวัติศาสตร์ต้องจารึกชื่อพวกเขาไว้",
    "genres": ["ผจญภัย", "อนิเมะญี่ปุ่น", "เหนือธรรมชาติ", "แอ็คชั่น", "การ์ตูน", "ซับไทย"],
    "directors": ["Kenichi Suzuki", "Naokatsu Tsuda"],
    "actors": ["Takuya Satou", "Takehito Koyasu", "Youji Ueda", "Atsuko Tanaka", "Tomokazu Sugita", "Kazuyuki Okitsu", "Yoku Shioya"],
    "published_year": "2555",
    "studio": ["Muse Thailand"],
    "runtime_min": 315
}

movie_json = {
    "title": "Mieruko-chan มิเอรุโกะจัง ใครว่าหนูเห็นผี - ฉบับมัดรวมทุกตอน",
    "youtube_url": "qbVyGlyYn1o",
    "description": "เรื่องราวของสาวน้อยนาม มิโกะผู้ใช้ชีวิตปกติธรรมดา.. ทว่าวันหนึ่งชีวิตของเธอก็เริ่มเปลี่ยนไป เมื่อเธอได้เริ่มมองเห็น “สิ่งผิดปกติ” ที่ไม่มีใครเห็น และถึงแม้ว่าเธอจะหวาดกลัวแค่ไหน สิ่งที่เธอเลือกจะทำก็คือใช้ชีวิตของเธอต่อไปโดยทำเป็นไม่เห็น และไม่สนใจพวกมันพร้อมๆ กับข่มความกลัวของตัวเองไว้ เพื่อให้ตัวเองและเพื่อนของเธอปลอดภัยจากสิ่งที่เธอเห็น! เรื่องราวของเด็กสาวผู้ต้องรับมือกับสิ่งเหนือธรรมชาติพร้อมกับแกล้งทำเป็นไม่เห็นพวกมันก็ได้เริ่มต้นขึ้น!",
    "genres": ["คอมเมดี้", "ซับไทย", "การ์ตูน", "สยองขวัญ", "อนิเมะญี่ปุ่น", "เหนือธรรมชาติ"],
    "directors": ["Yuki Ogawa"],
    "actors": ["Sora Amamiya", "Alexis Tipton", "Sarah Wiedenheft", "Ikuko Tani", "Kaede Hondo", "Lindsay Sheppard", "Yûichi Nakamura", "Yumiri Hanamori", "Ayane Sakura"],
    "published_year": "2563",
    "studio": ["Muse Thailand"],
    "runtime_min": 286
}

movie_json = {
    "title": "เคนอิจิ ลูกแกะพันธุ์เสือ OVA - ฉบับมัดรวมทุกตอน",
    "youtube_url": "PzTuWEAGAQY",
    "description": "เคนอิจิ ชิราฮามะ ผู้ซึ่งถึงจุดพลิกผันของชีวิตขณะเป็นนักเรียนไฮสคูลวัย 16 ปี เขาเป็นผู้ที่ไม่มีพรสวรรค์ด้านการต่อสู้ใดๆ เลย แต่อยู่มาวันหนึ่งเขาได้พบกับมิอุ นักเรียนหญิงห้องเดียวกันกับเขา และได้เห็นมิอุต่อสู้กับนักเลงที่คิดจะมาทำมิดีมิร้ายกับเธออย่างกล้าหาญ แต่ตัวเคนอิจิเองกลับไม่สามารถทำอะไรได้ นอกจากดูมิอุต่อสู้เท่านั้น ด้วยความชื่นชมในตัวของมิอุ กับทั้งเกลียดในความไม่เอาไหนของตัวเอง ทำให้เขาตัดสินใจไปเรียนศิลปะการต่อสู้ที่สำนักเรียวซัมปาคุ",
    "genres": ["โรแมนติก", "แอ็คชั่น", "ศิลปะการต่อสู้", "คอมเมดี้", "อนิเมะญี่ปุ่น", "การ์ตูน", "ซับไทย"],
    "directors": ["Hajime Kamegaki"],
    "actors": ["Jūrōta Kosugi", "Hiroya Ishimaru", "Josh Grelle", "Tomokazu Seki", "Tomoko Kawakami", "Mamiko Noto"],
    "published_year": "2557",
    "studio": ["Muse Thailand"],
    "runtime_min": 261
}

movie_json = {
    "title": "Kemono Jihen คดีประหลาดคนปีศาจ - ฉบับมัดรวมทุกตอน",
    "youtube_url": "ns7FLUwSnBs",
    "description": "พวกเขาหลบอยู่ใต้เงาของโลกตั้งแต่โบราณโดยไม่ให้ใครพบเข้า มีตัวอาศัยอยู่โดยสร้างปฏิสัมพันธ์กับมนุษย์อย่างลับ ๆ โดยถูกเรียกว่าเคโมโนะ พวกเขาทั้งหลายปรับตัวเข้ากับโลก และใช้ชีวิตปะปนอยู่ในสังคมมาตลอด แต่ทว่าในปัจจุบันเกิดมีรายงานคดีที่พวกเขาเข้าไปพัวพันกับมนุษย์เกินจำเป็นมากขึ้น",
    "genres": ["ลึกลับ", "อนิเมะญี่ปุ่น", "แอ็คชั่น", "เหนือธรรมชาติ", "การ์ตูน", "ซับไทย"],
    "directors": ["Masaya Fujimori"],
    "actors": ["Natsuki Hanae", "Junichi Suwabe", "Kabane Kusaka", "Ayumu Murase", "Yumiri Hanamori"],
    "published_year": "2564",
    "studio": ["Muse Thailand"],
    "runtime_min": 284
}

movie_json = {
    "title": "Kuma Kuma Kuma Bear คุมะ คุมะ คุมะ แบร์",
    "youtube_url": "BHMezHmP9g4",
    "description": "ยูน่าอายุสิบห้าปีชอบอยู่บ้านและเล่น VRMMO ที่เธอชื่นชอบเพื่อทำสิ่งอื่นรวมถึงการไปโรงเรียน เมื่อการอัพเดทใหม่ที่แปลกประหลาดทำให้เธอมีชุดหมีที่ไม่เหมือนใครที่มีความสามารถอย่างล้นหลาม Yuna ถูกฉีกขาด: ชุดนั้นน่ารักเกินทน แต่น่าอายเกินกว่าที่จะสวมใส่ในเกม แต่ทันใดนั้นเธอก็พบว่าตัวเองถูกพาตัวไปสู่โลกของเกมเผชิญหน้ากับสัตว์ประหลาดและเวทมนตร์ที่เป็นของจริงและชุดหมีกลายเป็นอาวุธที่ดีที่สุดที่เธอมี",
    "genres": ["คอมเมดี้", "แฟนตาซี", "ผจญภัย", "อนิเมะญี่ปุ่น", "การ์ตูน", "ซับไทย"],
    "directors": ["Hisashi Ishii", "Yuu Nobuta"],
    "actors": ["Azumi Waki", "Rina Hidaka", "Maki Kawase", "Inori Minase", "Satomi Amano", "Hina Kino1"],
    "published_year": "2563",
    "studio": ["Muse Thailand"],
    "runtime_min": 286
}

movie_json = {
    "title": "Hataraku Maou-sama! ผู้กล้าซึนซ่าส์กับจอมมารสู้ชีวิต - ฉบับมัดรวมทุกตอน",
    "youtube_url": "DKVQUiUIBqI",
    "description": "อีกเพียง ก้าวเดียวเท่านั้นจอมมารซาตานก็จะครอบครองโลกได้อยู่แล้วเชียว แต่เขากลับโดนผู้กล้าโค่นลงเสียก่อน จอมมารจึงต้องกระเสือกกระสนหนีไปยังโลกต่างมิติและมาลงเอยที่เมืองซาซาสึกะ จังหวัดโตเกียว ประเทศญี่ปุ่น",
    "genres": ["โรแมนติก", "คอมเมดี้", "เหนือธรรมชาติ", "ซับไทย", "อนิเมะญี่ปุ่น", "แฟนตาซี", "การ์ตูน"],
    "directors": ["Naoto Hosoda"],
    "actors": ["Nao Touyama", "Youko Hikasa", "Hiro Shimono", "Yuuki Ono", "Ryouta Oosaka"],
    "published_year": "2556",
    "studio": ["Muse Thailand"],
    "runtime_min": 309
}

movie_json = {
    "title": "Youkoso Jitsuryoku Shijou Shugi no Kyoushitsu e ขอต้อนรับสู่ห้องเรียนนิยม (เฉพาะ) ยอดคน - ฉบับมัดรวมทุกตอน",
    "youtube_url": "c0HJ_AxH7fw",
    "description": "โรงเรียน คิโด อิคุเซย์ มีชื่อเสียงจากนักเรียนแทบจะร้อยเปอร์เซนต์ที่สามารถหางานทำหรือเข้าเรียนต่อมหาวิทยาลัยได้ มีชื่อเสียงเรื่องการปล่อยนักเรียนได้รับอิสระหลายอย่างในระหว่างที่อยู่โรงเรียน จนเหมือนเป็นโรงเรียนในฝันที่เหล่าวัยรุ่นอยากเข้าไปเรียน แต่ในความเป็นจริง มีเพียงนักเรียนห้อง A ที่ได้รับการสิทธิพิเศษ",
    "genres": ["ชีวิตประจำวัน", "ดราม่า", "จิตวิทยา", "การ์ตูน", "อนิเมะญี่ปุ่น", "วัยรุ่น", "ซับไทย"],
    "directors": ["Seiji Kishi"],
    "actors": ["Ayana Taketatsu", "Nao Touyama", "Akari Kitou", "Yurika Kubo", "Rina Hidaka", "Mao Ichimichi", "Shouya Chiba"],
    "published_year": "2560",
    "studio": ["Muse Thailand"],
    "runtime_min": 288
}

movie_json = {
    "title": "Gakuen Babysitters นักเรียนพี่เลี้ยงเด็ก - ฉบับมัดรวมทุกตอน",
    "youtube_url": "xbVd2qxwxd4",
    "description": "ริวอิจิได้สูญเสียครอบครัวจากอุบัติเหตุเครื่องบินตก เหลือเพียงตัวเขาและน้องชายที่ชื่อ โคทาโร่ ทั้งสองได้ถูกรับเลี้ยงดูต่อจากครูใหญ่ที่ไม่เคยได้พบกันมาก่อน ซึ่งทำให้เขาได้งานพิเศษนอกเวลาเรียนเป็นพี่เลี้ยงเด็ก",
    "genres": ["คอมเมดี้", "วัยรุ่น", "ชีวิตประจำวัน", "การ์ตูน", "พากย์ญี่ปุ่น", "ซับไทย", "อนิเมะญี่ปุ่น"],
    "directors": ["Shūsei Morishita"],
    "actors": ["Yoshimasa Hosoya", "Kaede Hondo", "Daisuke Ono", "Nozomi Furuki", "Koutarou Nishiyama", "Konomi Kohara", "Yuichiro Umehara", "Atsumi Tanezaki", "Tomoaki Maeno", "Yûko Sanpei"],
    "published_year": "2561",
    "studio": ["Muse Thailand"],
    "runtime_min": 290
}

movie_json = {
    "title": "Itai no wa Iya nano de น้องโล่สายแทงก์แกร่งเกินร้อย",
    "youtube_url": "hBYfMHXo_Ao",
    "description": "น้องโล่สายแทงก์ แกร่งเกินร้อย ฮอนโจ คาเอเดะ (เมเปิ้ล) สาวน่ารักที่ถูกเพื่อน ชิโรมิเนะ ริสะ (ซารี่) ชวนมาเล่นเกมในโลกเสมือนจริง VRMMORPG แต่มือใหม่แบบเธอ ไม่อยากเจ็บตัว จึงเน้นเรื่องการป้องกันเป็นพิเศษ เน้นค่า VIT ไม่อัพค่าอื่น แต่ศัตรูทำ Damage ไม่เข้า พร้อมมีสกิลการป้องกันสมบูรณ์แบบ เธอได้ออกผจญภัย รู้จักผู้เล่นคนอื่นๆ และกลายเป็นที่รู้จักในภายหลัง",
    "genres": ["แอ็คชั่น", "ไซไฟ", "คอมเมดี้", "ผจญภัย", "อนิเมะญี่ปุ่น", "แฟนตาซี", "การ์ตูน", "ซับไทย"],
    "directors": ["Shin Oonuma"],
    "actors": ["Satomi Arai", "Rina Satou", "Kaede Hondo", "Nanaka Suwa", "Ruriko Noguchi", "Saori Hayami"],
    "published_year": "2563",
    "studio": ["Muse Thailand"],
    "runtime_min": 284
}

movie_json = {
    "title": "Kai Byoui Ramune คุณหมอประหลาด รามุเนะ",
    "youtube_url": "DnKQHen5pGU",
    "description": "ตราบใดที่ผู้คนยังมีจิตใจ ก็ย่อมมีผู้คนที่มีเรื่องเป็นกังวล ซึ่งสิ่งประหลาดก็จะเข้าไปในจิตใจ ทำให้ร่างกายเริ่มแสดงอาการประหลาด โรคที่ถูกเรียกว่าโรคประหลาดนั้น แม้จะไม่มีผู้ใดล่วงรู้ แต่มันมีตัวตนอยู่จริง ทว่ามีหมอกับลูกศิษย์ที่เผชิญหน้ากับโรคประหลาดที่ไม่อาจรักษาได้ด้วยการแพทย์ในปัจจุบันอยู่ ชื่อของเขาคือลามูเนะ เขาแต่งกายไม่เหมือนหมอเลยสักนิด และก็มักจะทำตามใจชอบอยู่เสมอ มิหนำซ้ำยังปากเสียอีกต่างหาก ทว่า ขอเพียงแค่เขาได้เผชิญหน้ากับโรคประหลาด เขาก็จะสามารถเปิดโปงความกังวลในจิตใจของคนไข้ และรักษามันได้ในชั่วพริบตาเดียว และปลายทางที่เฝ้ารอพวกเขาอยู่ก็คือ...",
    "genres": ["เหนือธรรมชาติ", "จิตวิทยา", "คอมเมดี้", "ซับไทย", "อนิเมะญี่ปุ่น", "การ์ตูน"],
    "directors": ["Hideaki Ooba"],
    "actors": ["Yuuma Uchida", "Ayumu Murase", "Takuma Nagatsuka", "Nobuhiko Okamoto", "Kana Ueda"],
    "published_year": "2564",
    "studio": ["Muse Thailand"],
    "runtime_min": 283
}

movie_json = {
    "title": "Majo no Tabitabi การเดินทางของคุณแม่มด",
    "youtube_url": "KV1zBjWLzDI",
    "description": "อิเลน่า แม่มดนักเดินทาง ที่ท่องเที่ยวไปยังดินแดนต่าง ๆ พบเจอผู้คนมากมายในฐานะนักเดินทาง ดินแดนที่ต้อนรับแต่ผู้ใช้เวทมนตร์, ชายร่างใหญ่บ้ากล้าม, เด็กหนุ่มซึ่งรอการกลับมาของคนรักในบั้นปลายชีวิต, เจ้าหญิงที่เหลืออยู่เพียงตัวคนเดียวในอาณาจักรที่ล่มสลาย และเรื่องราวของตัวแม่มดเองนับจากอดีต ต่อจากนี้สัมผัสชีวิตประจำวันอันงดงามหรือน่าขำขันของใครสักคน แม้แต่ในวันนี้แม่มดก็ยังคงถักทอเรื่องราวของการพบพานและลาจากต่อไป",
    "genres": ["แฟนตาซี", "ผจญภัย", "ซับไทย", "อนิเมะญี่ปุ่น", "การ์ตูน"],
    "directors": ["Toshiyuki Kubooka"],
    "actors": ["Miho Okasaki", "Tomoyo Kurosawa", "Konomi Kohara", "Kana Hanazawa", "Kaede Hondo"],
    "published_year": "2563",
    "studio": ["Muse Thailand"],
    "runtime_min": 286
}

movie_json = {
    "title": "Servamp เซอร์แวมพ์ - ฉบับมัดรวมทุกตอน",
    "youtube_url": "OktxswUG8tk",
    "description": "เรื่องราวของชิโรตะ มาฮิรุ เด็กหนุ่มวัย 16 ปี ผู้ยึดถือคติความเรียบง่าย และเกลียดเรื่องยุ่งยาก แต่แล้ววันหนึ่ง เขาได้เก็บแมวจรจัดสีดำมาจากข้างถนน และตั้งชื่อให้มันว่า คุโระ นับแต่วินาทีนั้น มาฮิรุก็ได้เผลอทำสัญญากับแวมไพร์ผู้รับใช้ หรือ เซอร์แวมพ์ ไปโดยไม่รู้ตัว และแล้ว มาฮิรุก็ถูกดึงเข้าไปพัวพันกับสงครามระหว่างแวมไพร์แห่งบาปทั้งเจ็ด และสึบากิ แวมไพร์ตนที่ 8 เข้าจนได้",
    "genres": ["แอ็คชั่น", "ซับไทย", "อนิเมะญี่ปุ่น", "คอมเมดี้", "การ์ตูน"],
    "directors": ["Shigeyuki Miya Hideaki"],
    "actors": ["Hiro Shimono", "Hiroshi Kamiya", "Takuma Terashima", "Yuto Suzuki", "Yuki Kaji", "Ryouhei Kimura"],
    "published_year": "2563",
    "studio": ["Muse Thailand"],
    "runtime_min": 283
}

movie_json = {
    "title": "Monster Musume no Oishasan รักษาหนูหน่อย คุณหมอมอนสเตอร์ - ฉบับมัดรวมทุกตอน",
    "youtube_url": "99S7K1t-JQY",
    "description": "นายแพทย์เกลน เปิดคลินิครักษามอนสเตอร์โดยมี เซอร์เฟ่ มอนสเตอร์จากเผ่าลาเมียเป็นผู้ช่วยอยู่ในเมือง “ลินด์เวิร์ม” …เมืองที่เผ่าอสูรและมนุษย์อาศัยอยู่ร่วมกัน ในแต่ละวันคลินิคแห่งนี้ต้อนรับเหล่ามอนสเตอร์สาวๆ เข้ามาตรวจรักษา และมีชื่อเสียงซึ่งล่ำลือกันไปอย่างกว้างขวางจากวีรกรรมแปลกๆ ของคุณหมอ ไม่ว่าจะเป็นการรักษาอาการผิดปกติให้เคนเทารอสจนถูกขอแต่งงานบ้าง การล้วงเหงือกของเมอร์เมดเพื่อรักษาด้วยมือเปล่าบ้าง หรือการช่วยตามเก็บเย็บชิ้นส่วนให้เฟลชโกเลมบ้าง… ซึ่งที่จริงแล้ว เกลนก็แค่รักษาอย่างจริงจังเท่านั้นเอง",
    "genres": ["แฟนตาซี", "อนิเมะญี่ปุ่น", "การ์ตูน", "ซับไทย"],
    "directors": ["โยชิอาคิ อิวาซาคิ"],
    "actors": ["ซาโอริ โอนิชิ", "ชูนิจิ โทคิ", "ยูคิโยะ ฟูจิ", "อาซึมิ ทาเนซาคิ", "ซายูมิ สูซึชิโระ"],
    "published_year": "2564",
    "studio": ["Muse Thailand"],
    "runtime_min": 283
}

movie_json = {
    "title": "Hyouka ปริศนาความทรงจำ - ฉบับมัดรวมทุกตอน",
    "youtube_url": "G7PkTYT_2e0",
    "description": "เรื่องราวของ โอเรกิ โฮทาโร่ เด็กหนุ่ม ม.ปลาย ผู้มีสีหน้าเหนื่อยหน่ายอยู่ตลอดเวลา เขามีความเชื่อในการอนุรักษ์พลังงานจึงไม่ทำอะไรในสิ่งที่ไม่จำเป็นต้องทำจนมาวันหนึ่งเขาได้มาเข้าชมรม Koten Bu (โคเท็นบุ) ชมรมวรรณกรรมคลาสสิก ด้วยคำแนะนำของพี่สาว ที่ชมรมแห่งนี้โอเรกิได้พบกับ จิทันดะ เอรุ สาวสวยผู้เป็นศูนย์รวมของความอยากรู้อยากเห็น, ฟุคุเบะ ซาโตชิ เด็กหนุ่มเพื่อนสนิทผู้ร่าเริงและ อิบาระ มายากะ เด็กสาวร่างเล็กเพื่อนสมัยเรียนประถมเมื่อคนเหล่านี้มารวมตัวกันเรื่องราวความสนุกสนานจึงได้เกิดขึ้นพวกเขาได้เริ่มต้นที่จะตรวจสอบเรื่องราวเหตุการณ์ที่เกิดขึ้นเมื่อ 33 ปีก่อน ซึ่งเป็นเรื่องราวลึกลับที่ถูกเก็บไว้มาอย่างยาวนานโดยอดีตสมาชิกของชมรมในสมัยก่อน โดยให้ชื่อเรื่องราวลึกลับนี้ว่า “เฮียวกะ”เรื่องราวลึกลับที่ว่าในสมัยก่อน",
    "genres": ["ชีวิตประจำวัน", "ลึกลับ", "วัยรุ่น", "อนิเมะญี่ปุ่น", "การ์ตูน", "ซับไทย"],
    "directors": ["Yasuhiro Takemoto", "Naoko Yamada", "Hiroko Utsumi"],
    "actors": ["Yuuichi Nakamura", "Ai Kayano", "Satomi Satou", "Daisuke Sakaguchi", "Yukana"],
    "published_year": "2555",
    "studio": ["Muse Thailand"],
    "runtime_min": 610
}

movie_json = {
    "title": "The God Of High School เทพเกรียน โรงเรียนมัธยม - ฉบับมัดรวมทุกตอน",
    "youtube_url": "odIm6MjQ5YE",
    "description": "เรื่องราวของ Jin Mori ชายหนุ่มวัย 17 ปี ที่เป็นนักสู้เทควันโด้ที่มีความสามารถสูงมาก ในระหว่างที่เขากำลังเดินทางท้าประลองกับคนอื่นเพื่อที่ตัวเองจะได้เป็นสุดยอดนักสู้ เขาก็ถูกเชิญให้เข้าร่วมงานต่อสู้ The God of High School ที่เป็นงานแข่งขันที่สนับสนุนโดยองค์กรลึกลับ และงานนี้ยังรวมนักสู้จากทั่วทั้งเกาหลีเพื่อหาตัวแทนไปแข่งขันระดับโลก และผู้ที่ชนะก็จะได้รับรางวัลเป็นสิ่งที่ตัวเองปรารถนา",
    "genres": ["แอ็คชั่น", "อนิเมะญี่ปุ่น", "ต่อสู้", "การ์ตูน", "ซับไทย"],
    "directors": ["Sunghoo Park"],
    "actors": ["Ayaka Ohashi", "Kentarou Kumagai", "Tatsumaru Tachibana", "Yuuya Uchida", "Tomokazu Seki"],
    "published_year": "2564",
    "studio": ["Muse Thailand"],
    "runtime_min": 305
}

movie_json = {
    "title": " การปฏิวัติของสาวน้อยหนอนหนังสือ",
    "youtube_url": "onDfpdwVFRo",
    "description": "เรย์โน สาวมหาวิทยาลัยที่รักการอ่าน หนอนหนังสือที่ฝันจะได้ทำงานด้านนี้ จนได้งานเป็นบรรณารักษ์ที่หอสมุดมหาวิทยาลัย แต่กลับมาตายเพราะเหตุแผ่นดินไหวแล้วตู้หนังสือล้มทับ เธอได้มาเกิดใหม่ในร่างเด็กสาว บนโลกที่หนังสือกลายเป็นสิ่งหายาก และมีแค่ขุนนางที่สามารถเข้าถึงได้ อีกทั้งเธอเกิดในร่างเด็กสาวลูกทหารชั้นปลายแถว ไม่มีโอกาสได้สัมผัสหนังสือที่รัก แต่ด้วยความมุ่งมั่นทำให้เธอพยายามที่จะทำตามฝันให้สำเร็จ",
    "genres": ["อนิเมะญี่ปุ่น", "ซับไทย", "แฟนตาซี", "ชีวิตประจำวัน", "การ์ตูน"],
    "directors": ["Mitsuru Hongo"],
    "actors": ["Megumi Nakajima", "Show Hayami", "Tsuyoshi Koyama", "Yuka Iguchi", "Mutsumi Tamura", "Fumiko Orikasa"],
    "published_year": "2562",
    "studio": ["Muse Thailand"],
    "runtime_min": 639
}

movie_json = {
    "title": "Kanojo Okarishimasu สะดุดรักยัยแฟนเช่า",
    "youtube_url": "RrX9xLVs_R8",
    "description": "คิโนะชิดะ คาสึยะ อายุ 20 ปี เป็นนักศึกษาไม่ได้เรื่องอาศัยอยู่ในหอพักคนเดียวในโตเกียว เขาถูกบอกเลิกจากแฟนเก่าของเขา ทำให้เขารู้สึกหดหู่กับชีวิตตัวเอง แต่แล้วก็มาเจอแอปพลิเคชัน แอปหนึ่งที่สามารถให้เช่าเพื่อนสาวได้ แต่ห้ามลวนลามหรือจับเนื้อต้องตัวเป็นอันขาด แล้วชีวิตของเขาก็ได้เปลี่ยนไป ตั้งแต่ได้พบกับสาวสวยปริศนาที่ชื่อ มิสึฮาระ จิซึรุ",
    "genres": ["คอมเมดี้", "โรแมนติก", "อนิเมะญี่ปุ่น", "วัยรุ่น", "การ์ตูน", "ซับไทย"],
    "directors": ["Kazuomi Koga"],
    "actors": ["Rie Takahashi", "Nao Touyama", "Sora Amamiya", "Shun Horie", "Aoi Yuuki"],
    "published_year": "2563",
    "studio": ["Muse Thailand"],
    "runtime_min": 295
}

movie_json = {
    "title": "Slime Taoshite 300-nen ล่าสไลม์มา 300 ปี รู้ตัวอีกทีก็เลเวล MAX ซะแล้ว - ฉบับมัดรวมทุกตอน",
    "youtube_url": "96qoSb-rQO8",
    "description": "ไอซาว่า อาซึสะ สาวโสดทาสบริษัทวัย 27 ปี เสียชีวิตลง เนื่องจากทำงานหักโหม หญิงสาวได้รับชีวิตใหม่กลายเป็นแม่มดสาวสิบเจ็ดผู้ไม่แก่ไม่ตายและใช้ชีวิตอย่าง “สโลว์ไลฟ์” ในต่างโลกเป็นเวลากว่าสามร้อยปี ตลอดเวลาที่ผ่านมาอาซึสะกำจัดสไลม์เพื่อหาเงินมาใช้จ่ายในชีวิตประจำวันจนสะสมเลเวลได้เต็ม 99 เธอจึงกลายเป็นผู้แข็งแกร่งที่สุดในโลกทั้งที่ไม่เคยออกผจญภัยโดยไม่ทันรู้ตัว… ทว่า ข่าวลือเกี่ยวกับการมีอยู่ของเธอก็ได้แพร่กระจายออกไปในหมู่นักผจญภัย ทำให้เหล่าคนที่ต้องการแสวงหาชื่อเสียงหรือแม้กระทั่งมังกร ก็โผล่มาท้าสู้จนชีวิตสโลว์ไลฟ์ของแม่มดสาวถึงกับสั่นคลอน!",
    "genres": ["แฟนตาซี", "อนิเมะญี่ปุ่น", "คอมเมดี้", "การ์ตูน", "ชีวิตประจำวัน", "ซับไทย"],
    "directors": ["Nobukage Kimura"],
    "actors": ["Minami Tanaka", "Yukari Tamura", "Manami Numakura", "Sayaka Harada", "Aoi Yûki", "Sayaka Senbongi", "Kaede Hondo", "Azumi Waki", "Riho Sugiyama"],
    "published_year": "2563",
    "studio": ["Muse Thailand"],
    "runtime_min": 284
}

movie_json = {
    "title": "CHOYOYU! เจ็ดเทพ ม.ปลาย กับการใช้ชีวิตสบายๆ ในต่างโลก! - ฉบับมัดรวมทุกตอน",
    "youtube_url": "khoYHanlryw",
    "description": "ยอดนักเรียนมัธยมปลายจากญี่ปุ่น 7 คน มีความสามารถที่เป็นเลิศหลายด้าน ทั้งการเมือง เศรษฐกิจ และอื่นๆ พวกเขาและเธอมีชื่อเสียงระดับโลก อยู่มาวันหนึ่ง ทั้งเจ็ดประสบอุบัติเหตุทางเครื่องบิน พบว่าตนอยู่ในโลกที่มีเวทมนตร์ที่ต่างจากโลกเดิม แต่กลับไม่ทำให้ทั้ง 7 คิดมาก และต้องการปฏิวัติโลกใบใหม่ด้วยทักษะของพวกเขา ดรีมทีมของผู้มีสติปัญญาอันล้ำลึกกับเทคโนโลยีที่ยอดเยี่ยมที่สุดในโลก",
    "genres": ["อนิเมะญี่ปุ่น", "แฟนตาซี", "ซับไทย", "การ์ตูน", "วัยรุ่น"],
    "directors": ["Shinsuke Yanagi"],
    "actors": ["Rina Hidaka", "Natsumi Hioka", "Junji Majima", "Shizuka Ishigami", "Yūsuke Kobayashi", "Hisako Kanemoto", "Sayaka Kaneko"],
    "published_year": "2562",
    "studio": ["Muse Thailand"],
    "runtime_min": 284
}

movie_json = {
    "title": "Kanojo mo Kanojo จะคนไหนก็แฟนสาว - ฉบับมัดรวมทุกตอน",
    "youtube_url": "2ZCYspwU4Ng",
    "description": "ตัวเอกของเรื่อง นาโอยะนักเรียนชั้นมัธยมปลายปีที่ 1 ได้สารภาพรักกับซากิที่เขาชอบมาโดยตลอด และได้เป็นแฟนกันในที่สุด เรียกได้ว่าอยู่ ณ จุดสุดยอดของการมีความสุข ทว่านางิสะ สาวงามอีกคนก็ได้เข้าไปคุยกับนาโอยะ อยู่ดีๆ เธอก็สารภาพรักกับนาโอยะและบอกว่าอยากให้มาคบกับตัวเอง นาโอยะที่หวั่นไหวเพราะความเป็นคนดีเกินไปของนางิสะ จึงได้ทำการตัดสินใจอย่างหนึ่ง...!",
    "genres": ["โรแมนติก", "อนิเมะญี่ปุ่น", "คอมเมดี้", "วัยรุ่น", "การ์ตูน", "ซับไทย"],
    "directors": ["Satoshi Kuwahara"],
    "actors": ["Rie Takahashi", "Ayana Taketatsu", "Azumi Waki", "Ayane Sakura", "Junya Enoki"],
    "published_year": "2564",
    "studio": ["Muse Thailand"],
    "runtime_min": 292
}

movie_json = {
    "title": "Tokyo Revengers โตเกียว รีเวนเจอร์ส - ฉบับมัดรวมทุกตอน",
    "youtube_url": "E1NeH44gj5E",
    "description": "ฮานะกาคิ ทาเคมิจิ คนที่ทำงานพิเศษที่แย่ที่สุดในชีวิต เขาได้ทราบว่า ทาจิบานะ ฮินาตะ แฟนคนเดียวในชีวิตที่เคยคบกันตอนอยู่ชั้นมัธยมต้นตายเพราะความขัดแย้งขององค์กรอาชญากรรมนามว่าโตเกียวมันจิไค วันรุ่งขึ้นหลังจากทราบข่าว ทาเคมิจิยืนอยู่บนชานชาลาของสถานี ใครบางคนผลักเขาจนตกลงไปในรางรถไฟจากชานชาลาของสถานี เขาเตรียมใจที่จะตาย แต่เมื่อลืมตาขึ้น เขากลับย้อนเวลากลับไปเป็นตัวเองเมื่อ 12 ปีก่อนด้วยเหตุผลบางอย่าง ช่วงมัธยมต้นที่เขาย้อนเวลากลับมาเมื่อ 12 ปีก่อนนับว่าเป็นช่วงที่ดีที่สุดของชีวิต เพื่อช่วยแฟนของเขาและเพื่อเปลี่ยนแปลงตัวเองที่เอาแต่วิ่งหนี การแก้แค้นแห่งชีวิตจึงได้เริ่มต้นขึ้น!",
    "genres": ["วัยรุ่น", "แอ็คชั่น", "อนิเมะญี่ปุ่น", "ยอดนิยม", "การ์ตูน", "พากย์ไทย"],
    "directors": ["สึโตมุ ฮานาบุสะ"],
    "actors": ["อาซึมิ วากิ", "ยูกิ ชิน", "เรียวโตะ โอซาก้า", "ยู ฮายาชิ"],
    "published_year": "2564",
    "studio": ["Muse Thailand"],
    "runtime_min": 391
}

movie_json = {
    "title": " Sekai Saikou no Ansatsusha สุดยอดมือสังหารอวตารมาต่างโลก ",
    "youtube_url": "4NS2O8mIl_8",
    "description": "นักฆ่ามือหนึ่งของโลกมาเกิดใหม่เป็นบุตรชายคนโตของตระกูลขุนนางนักฆ่า ภารกิจที่เขาได้รับมอบหมายเมื่อมายังต่างโลกมีเพียงหนึ่งเดียว สังหาร ผู้ผิดแผก (ผู้กล้า) ที่มีคำทำนายว่าจะนำมหันตภัยมาสู่มนุษย์ เพื่อปฏิบัติหน้าที่แสนสำคัญนี้ให้ลุล่วง เขาจึงออกปฏิบัติการในต่างโลกไปพร้อมกับเหล่าผู้ติดตามแสนสวย ด้วยความรู้ที่กว้างขวางและประสบการณ์โชกโชนในการลอบสังหาร ประกอบกับวิชาลับและเวทมนตร์ของตระกูลนักฆ่าที่ว่ากันว่าแกร่งที่สุดในต่างโลก เขาจึงค่อยๆเติบโตขึ้นเป็นนักฆ่าแห่งยุค— “น่าสนุก ไม่นึกเลยว่าเกิดใหม่แล้วก็ยังต้องฆ่าคนอีก” ‘นักฆ่าในตำนาน’ ผู้กลับมาเกิดใหม่จะทะยานขึ้นสู่ความสุดยอดยิ่งกว่าเก่า!",
    "genres": ["อนิเมะญี่ปุ่น", "แฟนตาซี", "การ์ตูน", "แอ็คชั่น", "ซับไทย"],
    "directors": ["Masafumi Tamura"],
    "actors": ["Toshiyuki Morikawa", "Chiaki Takahashi", "Shino Shimoji", "Yukari Tamura", "Kenji Akabane", "Reina Ueda", "Ninomiya Yui", "Yûki Takada"],
    "published_year": "2563",
    "studio": ["Muse Thailand"],
    "runtime_min": 285
}

movie_json = {
    "title": "Tatoeba Last Dungeon Mae no Mura no Shounen หนุ่มน้อยใสซื่อจากหมู่บ้านหน้าลาสท์ดันเจี้ยนมาเข้ากรุงแล้ว - ฉบับมัดรวมทุกตอน",
    "youtube_url": "JTiPzPprjLs",
    "description": "ในขณะที่ทุกคนในหมู่บ้านล้วนคัดค้าน แต่เด็กหนุ่มลอยด์ก็ไม่ทิ้งความฝันที่จะเป็นทหารและออกเดินทางไปยังเมืองหลวง แต่แม้ว่าเขาที่ถูกบอกว่าเป็นคนที่อ่อนแอที่สุดในหมู่บ้านและเหล่าชาวบ้านไม่มีใครรู้เลย ว่าหมู่บ้านของตัวเองเป็นแดนอมนุษย์หน้าดันเจี้ยนสุดท้าย!! นี่เป็นเรื่องราวความกล้าหาญของเด็กหนุ่มผู้แสดงความไร้เทียมทานออกมาโดยไม่รู้ตัว――。",
    "genres": ["อนิเมะญี่ปุ่น", "การ์ตูน", "ผจญภัย", "แฟนตาซี", "ซับไทย"],
    "directors": ["migmi"],
    "actors": ["Yumiri Hanamori", "Ai Kayano", "Haruka Tomatsu", "Katsuyuki Konishi", "M.A.O", "Madoka Asahina", "Miku Itō", "Minami Tsuda", "Naomi Shindoh"],
    "published_year": "2564",
    "studio": ["Muse Thailand"],
    "runtime_min": 284
}

movie_json = {
    "title": "Moriarty the Patriot มอริอาร์ตี้ผู้รักชาติ",
    "youtube_url": "a22qagMOtWI",
    "description": "ศตวรรษที่ 19 ท่ามกลางการปฏิวัติอุตสาหกรรม เป็นช่วงเวลาที่อังกฤษกำลังขยายอำนาจอย่างยิ่งใหญ่ ทว่าในเบื้องหลังของความก้าวหน้าทางเทคโนโลยีนั้น ก็มีระบบลำดับชั้นอันเก่าแก่ที่ทำให้ขุนนางซึ่งมีจำนวนไม่ถึง 3 เปอร์เซ็นของประชากรทั้งหมดปกครองประเทศอยู่ เหล่าขุนนางที่ยึกครองสิทธิพิเศษราวกับเป็นเรื่องปกติ และชนชั้นล่างที่ต้องหาเช้ากินค่ำ ผู้คนนั้นไม่ว่าใครต่างก็ต้องใช้ชีวิตอยู่ภายในระบอบลำดับชั้นที่ถูกกำหนดตั้งแต่ถือกำเนิดมา",
    "genres": ["ดราม่า", "ประวัติศาสตร์", "อนิเมะญี่ปุ่น", "แอ็คชั่น", "ญี่ปุ่น", "ลึกลับ", "อาชญากรรม", "การ์ตูน"],
    "directors": ["Kazuya Nomura"],
    "actors": ["Yūto Uemura", "Sōma Saitō", "Takuya Satō", "Chiaki Kobayashi", "Makoto Furukawa", "Yūki Ono"],
    "published_year": "2559",
    "studio": ["Muse Thailand"],
    "runtime_min": 568
}

movie_json = {
    "title": "Kenja no Deshi wo Nanoru Kenja ฉันเป็นศิษย์จอมปราชญ์จริงๆนะ - ฉบับมัดรวมทุกตอน",
    "youtube_url": "dZTE27SuiRw",
    "description": "ซากิโมริ คางามิ ผู้สวมบทบาทเป็นนักอัญเชิญผู้น่าเกรงขามและหนึ่งในเก้าจอมปราชญ์นาม “ดัมเบิลดัฟ” ในเกมแนว VRMMO ชื่อ “อาร์คเอิร์ธออนไลน์” เผลอหลับไประหว่างเล่นและถูกส่งไปยังโลกที่เกมกลายเป็นความจริง มิหนำซ้ำ เขายังไม่ได้อยู่ในร่างนักปราชญ์ชรา แต่เป็นร่างของสาวน้อยหน้าตาน่ารักจิ้มลิ้ม...แบบนี้ก็เสียภาพพจน์ของนักปราชญ์สุดเคร่งขรึมที่อุตส่าห์สร้างมาหมดน่ะสิ! ซากิโมริ คางามิ (ดัมเบิลดัล์ฟ) ที่คิดเช่นนั้นเลือกที่จะอ้างตัวเป็นลูกศิษย์ของจอมปราชญ์ภายใต้ชื่อ “มิร่า” แต่ทว่าการผจญภัยเกิดใหม่เป็นสาวน้อยในโลกแฟนตาซี เปิดม่านขึ้นแล้วอย่างงดงาม!",
    "genres": ["ผจญภัย", "แฟนตาซี", "อนิเมะญี่ปุ่น", "ซับไทย", "การ์ตูน"],
    "directors": ["Keitaro Motonaga"],
    "actors": ["Haruka Tomatsu", "Kanomi Izawa", "Nichika Omori", "Ayumu Murase", "Isao Sasaki", "Ari Ozawa", "Junichi Saitou", "Daisuke Hirakawa", "Hiroki Yasumoto", "Ayane Sakura"],
    "published_year": "2565",
    "studio": ["Muse Thailand"],
    "runtime_min": 284
}

movie_json = {
    "title": "Asobi Asobase ชมรมสาวรักสนุก - ฉบับมัดรวมทุกตอน",
    "youtube_url": "pLzbxkTs-20",
    "description": "โอลิเวียเด็กสาวแสนสวยผมบลอนด์ที่เกิดที่ญี่ปุ่นโตที่ญี่ปุ่นแต่พูดภาษาอังกฤษไม่ได้เลยสักนิดเดียว คาสึมิเด็กสาวผมสั้นสวมแว่นที่ปล่อยบรรยากาศจริงจังและดูมีภูมิปัญญาออกมาแต่พูดภาษาอังกฤษไม่ได้เลยสักนิดเดียว และฮานาโกะเด็กสาวผมเปียที่ถึงแม้จะร่าเริงแต่ก็ไม่อาจจะเป็นพวกชีวิตสุขสมได้ ชมรมที่เด็กนักเรียนมัธยมต้นสามคนนี้สร้างขึ้นมาก็คือชมรมศึกษานักละเล่น!? บัดนี้ JC เกิร์ลคอมเมดี้ที่เต็มเปี่ยมไปด้วยความน่ารักขั้นสุดยอดและความสนุกขั้นสุดยอดกำลังจะเริ่มขึ้นแล้ว!",
    "genres": ["ญี่ปุ่น", "วัยรุ่น", "อนิเมะญี่ปุ่น", "คอมเมดี้", "การ์ตูน", "ซับไทย"],
    "directors": ["Seiji Kishi"],
    "actors": ["Ryoko Maekawa", "Hina Kino", "Rika Nagae", "Konomi Kohara", "Honoka Inoue", "Mai Kanazawa"],
    "published_year": "2561",
    "studio": ["Muse Thailand"],
    "runtime_min": 282
}

movie_json = {
    "title": "House of Haunted อาถรรพ์บ้านนางรำ",
    "youtube_url": "J1FXt7XI74Q",
    "description": "เรือนไทยหลังเก่าของท่านเจ้าคุณ ในอดีตกาลเคยเป็นโรงเรียนสอนนาฏศิลป์ ต่อมาจึง กลายเป็นมรดกสืบทอดมาสู่ มาโนช และ จาริยา สองสามีภรรยาทายาทมหาเศรษฐีพยายาม จะปฏิรูปสถานที่แห่งนี้ให้เป็นบ้านพักตากอากาศ จึงให้ เจนภพ เพื่อนรักที่เป็นสถาปนิก หนุ่มพร้อมกับ มิ่ง และ ใจ เข้ามาช่วยดูแลปรับปรุงสถานที่ ในความรู้สึกของเจนภพที่ สัมผัสถึงความลี้ลับราวกับมีบางอย่างที่มองไม่เห็นนั้นอยู่รอบๆตัวตลอดเวลา พร้อมกับ ภาพนางรำที่ปรากฏขึ้นในความทรงจำและเสียงเครื่องดนตรีไทยยิ่งดังชัดเจนขึ้นเรื่อยๆ จน เกิดความน่าสะพรึง แรงอาถรรพ์ในเรือนไทยแห่งนี้อาจเป็นลางบอกเหตุเตือนชีวิตของผู้ที่ พยายามจะทำลายมรดกอันหวงแหนรักษา",
    "genres": ["หนังไทย", "สยองขวัญ", "ระทึกขวัญ"],
    "directors": ["มนตรี คงอิ่ม"],
    "actors": ["สุพจน์ จันทร์เจริญ", "อุบลวรรณ บุญรอด", "เมธี อมรวุฒิกุล", "ฉัตรกฤษณ์ เพิ่มพานิช"],
    "published_year": "2563",
    "studio": ["Right Comedy"],
    "runtime_min": 98
}

movie_json = {
    "title": "คนอยากเห็นผี",
    "youtube_url": "2ZSzjS1DeaU",
    "description": "เมื่อแจ๊คต้องสูญเสียแม่อันเป็นที่รักไป ก็ถึงกับเข่าอ่อนเพราะมันหมายถึงการสูญสิ้นทุกสิ่งในชีวิตไปเช่นกัน แจ๊คเชื่อว่าวิญญาณของแม่ยังคงวนเวียนอยู่ใกล้ๆ แจ๊คจึงคิดที่จะติดต่อกับแม่อีกครั้ง โดยการใช้ 6 วิธีเห็นผีแบบที่เห็นในหนังผี และรายการผีๆ เค้าทำกัน ซึ่งก็ทำกันง่ายๆ ไม่ยุ่งยาก แต่ทว่ามันไม่สามารถจะเลิกได้ง่ายๆ “เมื่อเรียกพวกเค้ามา พวกเค้าก็จะมา” ถ้าเป็นคุณ....คุณจะกล้าพอมั้ย จะใจแข็งพอมั้ย ที่จะเจอกับพวกเค้าอีกครั้ง......",
    "genres": ["หนังไทย", "สยองขวัญ", "ระทึกขวัญ"],
    "directors": [],
    "actors": ["ชินกช นุกูลกิช", "ปกรณ์เกียรติ วรายุภัสร์", "อรศิริ ขุนราชอาญา", "กนกกาญจน์ ฉันทเลิศวิทยา"],
    "published_year": "2563",
    "studio": ["Right Comedy"],
    "runtime_min": 89
}

movie_json = {
    "title": "The wicked dolls ตุ๊กตาเฮี้ยน",
    "youtube_url": "mJjUBOjTBpY",
    "description": "แพทย์หนุ่ม และสาวพยาบาลที่เป็นคู่รักกัน แต่ต่างฝ่ายต่างทำงานอยู่ในโรงพยาบาลคนละ แห่ง เมื่อทั้งคู่ได้ให้คำสาบานร่วมกันต่อหน้าตุ๊กตาสาบาน ซึ่งมีความเชื่อว่าหากเป็นคู่รัก สาบาน แต่ใครคนหนึ่งกลับผิดคำมั่นสัญญาที่ให้ไว้กับตุ๊กตาตัวนั้น เมื่ออาถรรพ์เร้นลับจาก ตุ๊กตาดุจดั่งมีภูตผีวิญญาณสิงอยู่ และก่อเหตุการณ์สุดสะพรึงติดตามไปทุกหนแห่งเหมือน เงาตามตัว มันคือฝันร้ายที่คอยหลอกหลอนชีวิตจนไม่อาจหลีกหนีมันได้ เพียงเพราะการ ผิดคำสาบานเหล่านั้นได้กลับกลายมาเป็นอาถรรพ์คำสาปที่รอการทวงคืน",
    "genres": ["หนังไทย", "สยองขวัญ", "ระทึกขวัญ"],
    "directors": ["ฉัตรชัย นาคสุริยะ"],
    "actors": ["เพ็ญเพชร เพ็ญกุล", "นราวัลย์ นิรัติศัย"],
    "published_year": "2563",
    "studio": ["Right Comedy"],
    "runtime_min": 92
}

movie_json = {
    "title": "Tenchi Souzou Design-bu แผนกออกแบบสร้างสรรค์โลก - ฉบับมัดรวมทุกตอน",
    "youtube_url": "F5CiTrncPAE",
    "description": "เมื่อแรกเริ่ม พระเจ้าได้สร้างโลกใบหนึ่งขึ้นมา พระเจ้าผู้ทรงพลานุภาพยังได้สร้างสิ่งต่าง ๆ ไม่ว่าจะเป็นแสง น้ำ และแผ่นดิน—— รวมถึงสิ่งมีชีวิตที่จะลงไปอาศัยอยู่บนโลก——",
    "genres": ["วัยรุ่น", "แฟนตาซี", "ชีวิตประจำวัน", "คอมเมดี้", "ญี่ปุ่น", "อนิเมะญี่ปุ่น", "การ์ตูน", "ซับไทย"],
    "directors": ["Souichi Masui"],
    "actors": ["Junya Enoki", "Takahiro Mizushima", "Yumi Hara", "Daisuke Kishio", "Ryouta Takeuchi"],
    "published_year": "2564",
    "studio": ["Muse Thailand"],
    "runtime_min": 309
}

movie_json = {
    "title": "Seijo no Maryoku wa Bannou Desu สตรีศักดิ์สิทธิ์อิทธิฤทธิ์สารพัดอย่าง - ฉบับมัดรวมทุกตอน",
    "youtube_url": "A4ojfvGrKEc",
    "description": "เซย์ หญิงสาววัย 20 ที่ยึดติดกับการทำงาน ระหว่างที่กลับมาที่บ้านก็เกิดแสงสว่างห่อหุ้มร่างเอาไว้ และได้ถูกอัญเชิญมาในฐานะของสตรีศักดิ์สิทธิ์อีกทั้งยังโดนอัญเชิญมาด้วยกันถึงสองคน",
    "genres": ["ญี่ปุ่น", "โรแมนติก", "ชีวิตประจำวัน", "อนิเมะญี่ปุ่น", "แฟนตาซี", "การ์ตูน", "ซับไทย"],
    "directors": ["Shouta Ibata"],
    "actors": ["Yui Ishikawa", "Takuya Eguchi", "Takahiro Sakurai", "Taku Yashiro", "Yuusuke Kobayashi"],
    "published_year": "2564",
    "studio": ["Muse Thailand"],
    "runtime_min": 287
}

movie_json = {
    "title": "Tensai Ouji no Akaji Kokka Saisei Jutsu บูรณะมันวุ่นวาย ขายชาติเลยแล้วกัน - ฉบับมัดรวมทุกตอน",
    "youtube_url": "eW7Mz0dUbMk",
    "description": "จักรวรรดินาทรา ที่สูญเสียอำนาจอิทธิพลไป กลายเป็นประเทศที่เล็กและอ่อนแอ โดยมีเจ้าชายที่ยังหนุ่มนามว่า เวย์น แบกรับประเทศแห่งนี้เอาไว้ โดยมีผู้ช่วยอย่างนินิมคอยสนับสนุน และได้เริ่มสำแดงอัจฉริยภาพออกมาอย่างงดงาม ทว่า ประเทศแห่งนี้... มันมาถึงทางตันแล้ว! ภายในไม่ได้มีทรัพย์สินมาค้ำจุน อีกทั้งยังไม่มีกองทัพมากพอจะไปแย่งชิงประเทศใคร และทรัพยากรบุคคลที่มีคุณภาพก็ได้อพยพหลบหนีไปที่ประเทศอื่น “อยากรีบขายประเทศทิ้งแล้วชิ่งจังโว้ย” คือความปรารถนาของเวย์น ผู้ที่อยากจะใช้ชีวิตหลังเกษียณอย่างอยู่สุขสบายแบบไม่สนโลก",
    "genres": ["อนิเมะญี่ปุ่น", "คอมเมดี้", "แฟนตาซี", "ซับไทย", "การ์ตูน"],
    "directors": ["Masato Tamagawa"],
    "actors": ["Rie Takahashi", "Daiki Hamano", "Kengo Kawanishi", "Ryūichi Kijima", "Mamiko Noto", "Sōma Saitō", "Rie Kugimiya", "Nao Tōyama", "Kenichirō Matsuda", "Akio Ohtsuka"],
    "published_year": "2565",
    "studio": ["Muse Thailand"],
    "runtime_min": 284
}

movie_json = {
    "title": "Death March kara Hajimaru Isekai Kyousoukyoku โศกนาฏกรรมต่างโลกเริ่มต้นจากเดธมาร์ช",
    "youtube_url": "Hlq_-aBY2Fw",
    "description": "โศกนาฏกรรมต่างโลกเริ่มต้นจากเดธมาร์ช ซุซุกิ อิจิโร่ (ซาตู) โปรแกรมเมอร์เกมออนไลน์วัย 29 ปี ตื่นขึ้นมาในโลกแฟนตาซีสไตล์ RPG เขากลายเป็นตัวละครชายในชื่อ ซาตู วัย 15 ปี ด้วยความสามารถที่สูง ทำให้เขาสามารถล้มมอนสเตอร์ขั้นสูงได้อย่างง่ายดาย กลายเป็นนักผจญภัยชั้นแนวหน้าในเวลาอันสั้น",
    "genres": ["อนิเมะญี่ปุ่น", "การ์ตูน", "ผจญภัย", "แฟนตาซี", "ซับไทย"],
    "directors": ["Shin Oonuma"],
    "actors": ["Brittany Lauda", "Kiyono Yasuno", "Margaret McDonald", "Monica Rial", "Brittney Karbowski", "Justin Briner", "Hiyori Kono", "Minami Tsuda"],
    "published_year": "2561",
    "studio": ["Muse Thailand"],
    "runtime_min": 253
}

movie_json = {
    "title": "THE HUANTED BOGIE โบกี้เฮี้ยน",
    "youtube_url": "iyN-O39cMmc",
    "description": "พิสิทธิ์ ชายหนุ่มผู้หนีการจับกุมของตำรวจมาที่สถานีรถไฟแห่งหนึ่ง จนกระทั่งเขาได้พบกับแสงเดือน สาวน้อยผู้ตกหลุมรักเขาตั้งแต่แรกพบและทั้งคู่เกิดความสัมพันธ์ที่ลึกซึ้งจนยากจะห้ามใจ พิสิทธิ์สัญญาจะพาแสงเดือนไปด้วย แต่กลับทิ้งเธอไว้ที่สถานีรถไฟ โชคร้ายที่เธอพอกับกลุ่มวัยรุ่นกลุ่มหนึ่งซึ่งฉุดเธอไปข่มขืนและฆ่าตายบนโบกี้ที่จอดอยู่โดดเดี่ยว ทำให้วิญญาณของเธอแค้นใจมากจึงรอคอยการกลับมาของพิสิทธิ์ เพื่อแก้แค้นทีเขาผิดสัญญากับเธอ",
    "genres": ["หนังไทย", "สยองขวัญ", "ระทึกขวัญ"],
    "directors": [],
    "actors": ["ฐนิชา ดิษยบุตร", "สุรชัย แสงอากาศ", "พร รุ่งเรือง", "พงศกร ชูบัว"],
    "published_year": "2549",
    "studio": ["Right Comedy"],
    "runtime_min": 86
}

movie_json = {
    "title": "SHUTTER ONE ชัตเตอร์ ภาพถ่ายวิญญาณหลอน",
    "youtube_url": "rZqrpF71I3A",
    "description": "นักแทน ชายหนุ่มผู้รักในการถ่ายภาพ เขาพยายามถ่ายภาพวิวเพื่อส่งให้กับนิตยสาร ท่องเที่ยว และเขาก็พบว่าภาพที่เขาถ่ายมีวิญญาณปรากฏอยู่ ซึ่งเป็นภาพวิญญาณปริศนา ที่มากับฟิล์มเก่าสมัย 20 ปีก่อน และตั้งแต่นั้น แทนก็เจอะเจอกับเหตุการณ์แปลก ๆ และ สยองขวัญ จนไม่เป็นอันทำอะไร เขาจึงพยายามหาทางสืบหาแหล่งที่มาของฟิล์มและ วิญญาณร้าย จนได้รู้ความจริงทั้งหมดว่าแท้จริงแล้วฟิล์มนั้นเป็นของทศ ซึ่งเป็นฆาตกร จึง ทำให้วิญญาณนั้นกลายเป็นวิญญาณที่เต็มไปด้วยความอาฆาต และรอวันกลับมาแก้แค้น โดยใช้แทนเป็นคนนำไปสู่เรื่องราวทั้งหมด...",
    "genres": ["หนังไทย", "สยองขวัญ"],
    "directors": [],
    "actors": ["สุรชัย แสงอากาศ", "นราวัลย์ นิรัติศัย", "สุเชาว์ พงษ์วิไล"],
    "published_year": "2547",
    "studio": ["Right Comedy"],
    "runtime_min": 90
}

movie_json = {
    "title": "คนเดือดฟัดระห่ำ Back to the Society",
    "youtube_url": "R3l8u55pgSg",
    "description": "เรื่องราวของจางซานเหอ เมื่อหลายปีก่อนถูกคุมขังเพราะทะเลาะวิวาท จนทำให้ภรรยาของเขาเศร้าสลดและเสียชีวิตก่อนวัยอันควรและลูกสาวต้องเติบโตในศูนย์สวัสดิการสังคม หลายปีผ่านไปเขาได้รับการปล่อยตัวจากคุกและตัดสินใจเลี้ยงลูกสาวเพียงลำพัง วันหนึ่งเขาได้เข้าช่วยพี่น้องของเขาและนำไปสู่การเสียชีวิตโดยไม่ได้ตั้งใจของหัวหน้าแก๊งถ่าหลี่ น้องชายหัวหน้าแก๊งถ่าหลี่นามฉ๋าหนงจึงได้เริ่มลงมือแก้แค้นอย่าบ้าระห่ำ จับลูกสาวจางซานเหอเป็นตัวประกัน เพื่อปกป้องลูกสาวและพี่น้องของเขาจางซานเหอจึงต้องก้าวเข้าสู่สังเวียนการต่อสู้สุดระห่ำนี้",
    "genres": ["หนังจีน", "แอ็คชั่น", "ดราม่า", "ซับไทย"],
    "directors": ["Chen Si Ming"],
    "actors": ["เฉินเสี่ยวชุน", "หลี่ช่านเซิน", "จูหย่งถัง", "เถียนลู่", "หลิวเวยโจว", "จางลี่เวย", "หน่าวเหมินเอ๋อเอ่อเต๋อหนี"],
    "published_year": "2564",
    "studio": ["YOUKU Thailand"],
    "runtime_min": 79
}

movie_json = {
    "title": "ผีตาหวานกับอาจารย์ตาโบ๋",
    "youtube_url": "rAQuKisFPtk",
    "description": "The Ghost and Master Boh ผีตาหวาน กับอาจารย์ตาโบ๋ หวาน ถูกข่มขืนจนตาย แต่วิญณาณยังโดนรบกวนอีก จึงทำให้ต้องออกมาต่อสู้ และได้พบรักกับ วิทย์ ซึ่งไม่รู้ว่าตนเป็นผี อีกมุมหนึ่งอาจารย์โบ๋กับบัว น้องสาวของอาจารย์โบ๋ ตั้งตัวเป็นร่างทรงหลอกเงินชาวบ้าน และให้หวยอย่างส่งเดช แต่ก็ทำให้คนแทงถูกหวย จนสร้างความไม่พอใจให้กับ เจ้ามือหวย จนเจ้ามือหวยต้องการเก็บอาจารย์โบ๋และหวาน เมื่อรู้ว่าอาจารย์โบ๋ซึ่งเป็นคนที่วิทย์นับถืออยู่ตกอยู่ในอันตราย จึงร่วมมือกับอาจารย์โบ๋จัดการกับหมอโหมด และชำระแค้นกับพวกเสี่ยอู๋ได้สำเร็จ",
    "genres": ["หนังไทย", "สยองขวัญ", "คอมเมดี้"],
    "directors": ["วรพจน์ โพธิเนตร"],
    "actors": ["จาตุรงค์ พลบูรณ์", "บุญญาวัลย์ พงษ์สุวรรณ", "เจริญพร อ่อนละม้าย", "อาคม ปรีดากุล", "เฉลิม ปานเกิด", "พรรษชล คุ้มแพรวพรรณ", "วีระยุทธ น่าบูรณะ", "เกริก ชิลเลอร์", "รุ้งทอง ร่วมทอง", "แสนรัก เมืองโคราช"],
    "published_year": "2551",
    "studio": ["MrMonoFilm"],
    "runtime_min": 98
}

movie_json = {
    "title": "กิ๊กก๊วนป่วนซ่าส์ 1 ปรมาจารย์แห่งรัก",
    "youtube_url": "igdChYgUaMk",
    "description": "บุรุษหนุ่มผู้เชี่ยวชาญในเรื่องผู้หญิง เดช หรือ ฉายา the gig เขาถนัดในเรื่องจีบและหักอกสาว มักจะได้รับการว่าจ้างจากบรรดาผู้ชายที่เพิ่งโดนแฟนทิ้งมาหมาดๆ ให้ตามจีบแฟนเก่าของพวกเขา และพาออกเดทในแบบที่ถือว่าเลวร้ายที่สุดในชีวิตของพวกเธอ",
    "genres": ["หนังไทย", "คอมเมดี้", "วัยรุ่น"],
    "directors": ["ธรธร สิริพันธ์วราภรณ์"],
    "actors": ["อชิตะ ธนาศาสตนันท์", "สุรีรัตน์ ศรีบ้าน", "สุทิชา ภาษีผล", "ปรมะ อิ่มอโนทัย", "นันทวัฒน์ ศักยะธนาสิทธิ์", "ธิติพันธ์ สุริยาวิชญ์", "มารุต มานะกุล"],
    "published_year": "2556",
    "studio": ["MrMonoFilm"],
    "runtime_min": 81
}

movie_json = {
    "title": "The Night โรงแรมซ่อนผวา",
    "youtube_url": "RKLZLla9qS4",
    "description": "เมื่อสองสามีภรรยาชาวอิหร่านพร้อมลูกน้อย ตัดสินใจเข้าพักในโรงแรมแห่งหนึ่ง ณ อเมริกา ค่ำคืนอันควรเงียบสงบกลับกลายเป็นฝันร้าย เมื่อบางสิ่งบางอย่างในโรงแรมนี้เริ่มคุกคามพวกเขา หากเพียงแต่ว่าความน่าสะพรึงกลัวที่แท้จริง กำลังจะเริ่มขึ้นเมื่อสิ่งชั่วร้ายในโรงแรม กะเทาะด้านมืดของสามี และภรรยาคู่นี้ให้เปิดเผยออกมา ภายในค่ำคืนชวนผวาที่ดำเนินต่อไปอย่างไม่มีวันรู้จบ จวบจนชีวิตจะหาไม่!",
    "genres": ["หนังฝรั่ง", "พากย์ไทย", "สยองขวัญ", "ลึกลับ", "ดราม่า", "ระทึกขวัญ"],
    "directors": ["คูรอช อาฮารี"],
    "actors": ["ชาฮาบ ฮอสเซนี", "นิอูชา นัวร์", "จอร์จ แม็กไกวร์", "ไมเคิล เกรแฮม", "เอเลสเตอร์ ลาแธม", "อาร์มิน อามิรี"],
    "published_year": "2563",
    "studio": ["Right Comedy"],
    "runtime_min": 109
}

movie_json = {
    "title": "บุปผาราตรี เฟส 2",
    "youtube_url": "w_GJMmLV1Es",
    "description": "พวกโจรออกค้นหาทุกซอกทุกมุมในอพาร์ทเมนต์ เหลืออยู่แต่เพียงชั้น 6 ที่เจ้าของอพาร์ทเมนต์ปิดตายไว้ห้ามไม่ให้ใครเข้า โจรทั้งสี่ไม่ฟังคำเตือน ออกค้นหาเงินในชั้น 6 จนได้พบว่าเงินซ่อนอยู่ในห้อง 609 แต่พวกเขาก็ไม่สามารถนำเงินออกจากห้องนั้นได้เพราะถูกผีเจ้าของห้องออกมาหลอกหลอน โจรทั้งสี่จึงต้องคิดหาวิธีเอาเงินออกจากห้อง 609 ให้เร็วที่สุดเท่าที่จะทำได้ แม้จะกลัวผีเพียงไรก็ตาม ขณะเดียวกัน ตำรวจก็เริ่มระแคะระคาย แกะรอยโจรทั้งสี่มาถึงอพาร์ทเมนต์แล้ว...",
    "genres": ["หนังไทย", "สยองขวัญ", "คอมเมดี้", "โรแมนติก"],
    "directors": ["ยุทธเลิศ สิปปภาค"],
    "actors": ["เฌอมาลย์ บุญยศักดิ์", "กฤษณ์ ศรีภูมิเศรษฐ์", "ชมพูนุช ปิยะภาณี", "สมชาย ศักดิกุล", "ศิริสิน ศิริพรสมาธิกุล", "อดิเรก วัฏลีลา", "พิชญ์นาฏ สาขากร", "บรรพต วีระรัฐ", "พัน รจนรังษี", "สภา ศรีสวัสดิ์", "สมใจ สุขใจ"],
    "published_year": "2548",
    "studio": ["Right Comedy"],
    "runtime_min": 102
}

movie_json = {
    "title": "บางคนแคร์ แคร์บางคน",
    "youtube_url": "A8OlMMNIATk",
    "description": "ลูกบิด สาวสมัยใหม่ที่ไม่เคยเชื่อในความรัก แม้แต่งานที่เธอทำก็คืองาน “รับจ้างบอกเลิก” โดยเธอถือคติ ว่า “การบอกรักใครซักคนที่ว่ายากแล้ว...แต่การบอกเลิกกลับยากยิ่งกว่า” วันหนึ่ง คนที่ไม่เคยศรัทธาใน ความรักอย่าง ลูกบิด กลับต้องมาเจอกับ “รักแรกพบ” เข้าอย่างจัง กันต์ ชายคนแรกที่ทำให้หัวใจเธอเต้น 150 ครั้ง/นาที แต่แล้วโชคชะตาก็เล่นตลก ให้เธอต้องแคล้วคลาดกับความรักอีกครั้ง จนกระทั่ง หวัง หนุ่มรุ่นน้องข้างห้อง ได้เข้ามาในชีวิต และวันแรกที่เจอกันมีเหตุให้ ลูกบิดเข้าใจผิดคิดว่า หวัง เป็นโจร จนทำให้ทั้งคู่กลายมาเป็นคู่ปรับกัน เมื่อเวลาผ่านไป หวัง เกิดแอปปิ๊ง ลูกบิด จึงหาทางใกล้ชิดกลับเธอ โดยการช่วยตามหาชายในฝันอย่างกันต์ แต่จากเหตุการณ์เหล่านี้ กลับทำให้ทั้งคู่เปลี่ยนจากคู่กันเป็นคู่ซี้ แล้วลูกบิดจะทำยังไงกับชายอีกคนที่แอบเข้ามาในหัวใจเธอ...เธอจะเลือก “แคร์” ใคร.",
    "genres": ["หนังไทย", "คอมเมดี้", "โรแมนติก"],
    "directors": ["กุลชาติ จิตขจรวานิช"],
    "actors": ["วิริฒิพา ภักดีประสงค์", "หวัง เลี่ยงจิง", "รัฐพงศ์ ธนะพัฒน์", "ผดุง ทรงแสง", "อาคม ปรีดากุล", "วัลลภ มณีคุ้ม", "เฉลิมพล ทิฆัมพรธีรวงศ์", "เฟี้ยวฟ้าว สุดสวิงริงโก้", "เอนก อินทะจันทร์"],
    "published_year": "255",
    "studio": ["Right Comedy"],
    "runtime_min":77
}

movie_json = {
    "title": "โอ้! มายก๊อด คุณพระช่วย",
    "youtube_url": "cfeBIZqS9Xs",
    "description": "ขิมและคำปัน สองคนพี่น้องได้เดินทางเข้ามาในเมืองมาหาห้องเช่าที่เพื่อนแน่นำ ก็มาเจออพาทเมนต์ของคูณนายถาดทอง ซึ่งเป็นคนงกเงิน ห้องพักเต็มหมดแต่คนใช้คุณนายมะนาวบอกมีอยู่ห้องหนึ่งที่ปิดตายไว้ ห้องนั้นปิดตายทำไม่ เมื่อสองคนพี่น้องเข้าไปอยู่ที่ห้องนั้นก็ต้องเจอกับ อาเตา ผีที่ตายอยู่ในห้องนั้นห้องถึงปิดตายเพราะผีดุ สองคนพี่น้องจะเจออะไรกับผี และผีต้องเจออะไรบ้างโปรดติดตามชม",
    "genres": ["หนังไทย", "คอมเมดี้"],
    "directors": [],
    "actors": ["เอนก อินทะจันทร์", "จุมพจน์ ศรีจามร", "วลัชณัฏฐ์ ก้องภพตารีย์", "ธัณย์สิตา สุวัชราธนากิตติ์", "รณกร ทรงแสง", "วนิดา แสงสุข"],
    "published_year": "2565",
    "studio": ["Right Comedy"],
    "runtime_min": 104
}

movie_json = {
    "title": "เรือนนางคอย Tormented Love House ",
    "youtube_url": "5xVK5qm2L30",
    "description": "นเรศหนุ่มรูปหล่อและเพื่อนๆได้มาพักที่บ้านทรงไทยโบราณซึ่งเป็นของเพื่อนชื่อเยาว์ภา ทั้งหมดได้มาพักที่เรือนไทยหลังนี้ และทั้งหมดยังไม่รู้ถึงชะตากรรมที่จะเกิดขึ้นกับพวกเขาทั้งหมด โดยเฉพาะนเรศ เพราะบ้านหลังนี้ลูกสาวเจ้าของบ้านดั่งเดิมซึ่งเป็นท่านขุนในสมัยก่อนได้ถูกลามโซ่ตรอมใจตาย",
    "genres": ["หนังไทย", "สยองขวัญ"],
    "directors": [],
    "actors": ["ไพฑูรย์ ส่งอุบล", "ทรรศิกา ยุติมิตร", "กัลยา นนท์สูงเนิน", "พันธุ์เทพ ธาวินิต"],
    "published_year": "2556",
    "studio": ["Right Comedy"],
    "runtime_min": 76
}

movie_json = {
    "title": "3 แพร่ง สยองขวัญ",
    "youtube_url": "3WlaAnSyQig",
    "description": "หนังสยองขวัญชื่อดังของประเทศไทย ที่ทำการมัดรวมเรื่องสยองขวัญ ขนหัวลุกสามเรื่อง ที่มีเนื้อเรื่องน่ากลัวจนไม่กล้าดูคนเดียว ทั้งการดำเนินเรื่องแบบรายการเรียลลิตี้ช็อค, เรื่องราวความสัมพันธ์ต้องห้ามของดีเจกับสาวนักศึกษาที่ฆ่าตัวตาย, และ สามีภรรยาที่เกิดปัญหาระหว่างทางกลับบ้าน",
    "genres": ["หนังไทย", "สยองขวัญ", "ระทึกขวัญ"],
    "directors": [],
    "actors": ["ทรรศชล พงษ์ภควัต", "พาวิกา รอดเจริญ", "ชินกช นุกูลกิจ", "สัณห์ธุกรณ์ พิริยะธำรงศักดิ์"],
    "published_year": "2552",
    "studio": ["Right Comedy"],
    "runtime_min": 96
}

movie_json = {
    "title": "SIX หกตายท้าตาย",
    "youtube_url": "_TV0CuU9ja0",
    "description": "เรื่องราวของเพื่อนรัก 7 คน ฝ้าย, กานต์, ภัทร, อ๋อง, นัฐ, ตรี และ ลอเซอ ซึ่งถูกขีดดวงชะตาให้เดินทางเวลา เดียวกันวันเดียวกัน และเดือนเดียวกัน ที่จะต้องมาเจอกับสิ่งลี้ลับความน่าสะพรึงกลัวที่เกิดจากอดีตชาติ ส่งผลมาจาก วิบากกรรมให้พวกเขาต้องมาพบกัน และผจญไปกับเหตุการณ์ที่ไม่คาดคิดมาก่อน ในบ้านหลัง หนึ่งที่ไม่มีใครล่วงรู้มาก่อนว่า ที่นั่นพวกเขาจะต้องพบเจอกับเหตุการณ์อะไร พร้อมกับสิ่งที่พวกเขาไม่ สามารถเรียกร้องความยุติธรรมกลับมาได้อีกครั้ง ใครจะสามารถระงับเรื่องร้ายแรงในครั้งนี้ได้ และพวกเขา จะเจอกับอะไรบ้าง เตรียมพบกับแรงอาฆาตแค้นที่ไม่สิ้นสุดไปกับพวกเขาได้เลย “ชะตากรรม วิบากกรรม และเวรกรรม” กำลังกลับมาด้วยแรงอาถรรพ์แห่งความแค้นและแรงอาฆาต",
    "genres": ["หนังไทย", "สยองขวัญ"],
    "directors": ["นุสรณ์ พนังคศิริ"],
    "actors": ["อินทิรา เจริญปุระ", "วัชรชัย สัตย์พิทักษ์", "เร แม็คโดนัล", "พิพัฒน์ อภิรักษ์ธนกร", "เกริกไกร อันสนธิ์", "ภราดร ศิรโกวิท", "ชาญ โชคกมลกิจ"],
    "published_year": "2547",
    "studio": ["Right Comedy"],
    "runtime_min": 94
}

movie_json = {
    "title": "Young Love lost วัยซ่าส์พันธุ์เกรียน",
    "youtube_url": "1IsIolEWhGA",
    "description": "หลังจบจากสถาบันการศึกษาในปี 1990 นักศึกษาหนุ่มผู้ไม่เคยรู้อะไรมากไปกว่าการทำงานเป็นช่างฟิต กับการเปลี่ยนหลอดไฟในฐานะช่างไฟฟ้าของโรงงานเคมีภัณฑ์ก็มักจะใช้เวลาว่างไปกับการเล่นเกมคอมพิวเตอร์ และบังเอิญได้พบกับสาวน้อยนักเรียนแพทย์ผู้รักเขาอย่างหมดหัวใจ แต่เขากลับต้องการให้เธอจากไปเพื่ออนาคตที่ดีกว่า",
    "genres": ["หนังจีน", "คอมเมดี้", "โรแมนติก"],
    "directors": ["Guoqiang Xiang"],
    "actors": ["Dong Zi Jian", "Li Meng", "Shang Tie Long", "Li Da Guang", "Doris Tong"],
    "published_year": "2558",
    "studio": ["Right Comedy"],
    "runtime_min": 95
}

movie_json = {
    "title": "บนบานศาลกล่าว The Pray",
    "youtube_url": "Kn8mUulMJHM",
    "description": "เป็นเรื่องราวของหน่วยงานของมูลนิธิแห่งหนึ่งที่ได้รับแจ้งเรื่องเจอศพที่โรงงานร้างแห่งหนึ่ง แต่ในระหว่างที่เจ้าหน้าที่ของมูลนิธิรอให้เจ้าหน้าที่ตำรวจมาถึงนั่นก็ได้พากันเล่าถึงประสบการณ์ของอาถรรพ์ ที่พวกตนเจอในระหว่างปฏิบัติหน้าที่เก็บศพ ๆ หนึ่งที่ถูกลือว่าตายเพราะไม่ไปแก้บนที่ขอลูกกับผีแล้วผีมาเอาคืนสู่กันฟัง ก่อนที่สุดท้ายจะพบความจริงว่าคนที่นั่งฟังเรื่องเล่าและร่วมเล่าเรื่องผีและอาถรรพ์ด้วยอีกคนหนึ่งนั่น คือ ศพ ( ผี ) ที่พวกตนเคยมาเก็บที่โรงงานร้างดังกล่าวจากก่อนหน้านี้",
    "genres": ["หนังไทย", "สยองขวัญ"],
    "directors": [],
    "actors": ["ภัชรกร คชเสนีย์", "ศรสวรรค์ แทนทรัพย์", "ดรัสพงศ์ ตรงประสิทธิ์"],
    "published_year": "2564",
    "studio": ["Right Comedy"],
    "runtime_min": 83
}

movie_json = {
    "title": "Shijou Saikyou no Daimaou, Murabito A ni Tensei suru ชีวิตใหม่ไม่ธรรมดาของราชาปีศาจขี้เหงา",
    "youtube_url": "ye_AjhUOftY",
    "description": "ชีวิตใหม่ไม่ธรรมดาของราชาปีศาจขี้เหงา ในอดีต วาร์วาทอส จอมราชาปีศาจสุดแข็งแกร่ง เป็นที่หวาดกลัวจนไม่มีใครกล้าเข้าใกล้ ตัวเขาไม่ชอบชีวิตแบบนี้ จึงตัดสินใจเกิดใหม่ด้วยตนเอง ฐานะ อาร์ด ชาวบ้านธรรมดา ได้เกิดในยุคที่เวทมนตร์เสื่อมถอย ตัวเขาที่มีพลังมากกวาคนทั่วไป ถึงมุ่งมั่นที่จะใช้ชีวิตแบบปกติ แต่ไม่ได้ง่ายอย่างที่คิด",
    "genres": ["อนิเมะญี่ปุ่น", "การ์ตูน", "ซับไทย", "แอ็คชั่น", "แฟนตาซี"],
    "directors": ["Mirai Minato"],
    "actors": ["Toshinari Fukamachi", "Ayaka Ohashi", "Hina Yomiya", "Kenta Miyake", "Kōhei Amasaki", "Mie Sonozaki", "Takehito Koyasu", "Takuma Suzuki", "Wakana Maruoka", "Yui Ogura", "Yuki Kaida"],
    "published_year": "2565",
    "studio": ["Muse Thailand"],
    "runtime_min": 284
}

movie_json = {
    "title": "แท็กซี่…ดุ",
    "youtube_url": "BYhZwRxEK4c",
    "description": "บุญมี ซื้อรถแท็กซี่มือสองจาก เฮียตง เพื่อหารายได้เลี้ยงชีพ ซึ่งได้รับหญิงสาวผู้โดยสารให้ไปส่งที่วัดแห่งหนึ่ง เมื่อมาถึงวัดแล้วเธอก็หายตัวไปในพริบตา ตั้งแต่นั้นมาเขาก็ประสบกับเหตุการณ์ลี้ลับมาตลอด ทุกคนที่เคยได้ นั่งรถคันนี้ต่างก็ขวัญผวาและยืนยันว่าพบเห็นวิญญาณสาวนั่งอยู่เบาะข้างหลังรถคันนี้ และครั้งหนึ่งที่บุญมีรอด จากการถูกโจรป้นทรัพย์ที่แฝงตัวเป็นผู้โดยสารบนรถ รวมทั้งในความฝันก็ปรากฏภาพของวิญญาณสาวที่มี หน้าตาเหมือนกับหญิงสาวผู้โดยสารที่หายตัวไปอย่างลึกลับและบ้านหลังหนึ่งที่อาจไขปมปริศนานี้ได้ พร้อม ทั้งเงื่อนงำที่ เฮียตง และ บุญหลาย ได้ปิดบังมาตลอด",
    "genres": ["หนังไทย", "สยองขวัญ"],
    "directors": [],
    "actors": ["ฌานิศ ใหญ่เสมอ", "ชุติกาญจน์ จุลละนันทน์", "กนกพร พัดพรม"],
    "published_year": "2540",
    "studio": ["Right Comedy"],
    "runtime_min": 92
}

#=============================================================================================
# series_json = {
#     "title": "",
#     "keyword": "",
#     "description": "",
#     "state": True,
#     "reverse_loop": False,
#     "studio": ["TVB"],
#     "genres": ["ซีรี่ส์ฮ่องกง", "ซีรี่ส์จีน", "พากย์ไทย", "กำลังภายใน", "ประวัติศาสตร์", "คลาสสิค", "ย้อนยุค"],
#     "directors": [],
#     "actors": [""],
#     "season_title": "ซีซั่น 1",
#     "yt_playlist_url": "",
#     "published_year": ""
# }

series_json = {
    "title": "อีเหี่ยน เดอะซีรีย์ คอนเฟิร์ม",
    "keyword": "SKT Official",
    "description": "เรื่องราวของเด็กบ้านนานามว่า เหี่ยน (นรีรัตน์ สีหราชนิเวศน์) เธอมีความใสซื่อ ตรงไปตรงมา รักบ้านเกิดที่สุด แต่ชอบเสี่ยงดวงเพียงเพื่อหวังช่วยแม่ปลดหนี้ จึงหนีมาเมืองกรุงตามหาพ่อ สุดท้ายไม่มีเงินกลับบ้าน เหี่ยน ได้งานทำด้วยการฝากจากกะเทยคนหนึ่ง เรื่องราวความสนุกจึงเกิดขึ้น และสุดท้ายก็ไปจบที่บ้านโคกตาล จ.ศรีสะเกษ ครบทุกรส มีแง่คิด มุมมองที่เป็นบวก สอดแทรกเนื้อหาสาระเชิงท่องเที่ยวได้อย่างลงตัว",
    "state": 1,
    "reverse_loop": 0,
    "studio": ["SKT Official"],
    "genres": ["ซีรี่ส์ไทย", "คอมเมดี้", "ดราม่า", "โรแมนติก"],
    "directors": ["นรินธ์น แก้วสีเงิน"],
    "actors": ["พศิน เรืองวุฒิ", "นรีรัตน์ สีหราชนิเวศน์", "กัญญ์ชัญญ์ เธียรวิชญ์", "สมพงษ์ คุนาประถม", "รุ้งลาวัณย์ โทนะหงษา", "ชุมพร เทพพิทักษ์"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url": "https://www.youtube.com/playlist?list=PLs12_b9cOtEhe5XGssy4tzREUnAc9hQ-t",
    "published_year": "2558"
}

series_json = {
    "title": "อีเหี่ยน เดอะซีรีย์ คอนเฟิร์ม",
    "keyword": "SKT Official",
    "description": "เรื่องราวของเด็กบ้านนานามว่า เหี่ยน (นรีรัตน์ สีหราชนิเวศน์) เธอมีความใสซื่อ ตรงไปตรงมา รักบ้านเกิดที่สุด แต่ชอบเสี่ยงดวงเพียงเพื่อหวังช่วยแม่ปลดหนี้ จึงหนีมาเมืองกรุงตามหาพ่อ สุดท้ายไม่มีเงินกลับบ้าน เหี่ยน ได้งานทำด้วยการฝากจากกะเทยคนหนึ่ง เรื่องราวความสนุกจึงเกิดขึ้น และสุดท้ายก็ไปจบที่บ้านโคกตาล จ.ศรีสะเกษ ครบทุกรส มีแง่คิด มุมมองที่เป็นบวก สอดแทรกเนื้อหาสาระเชิงท่องเที่ยวได้อย่างลงตัว",
    "state": 1,
    "reverse_loop": 0,
    "studio": ["SKT Official"],
    "genres": ["ซีรี่ส์ไทย", "คอมเมดี้", "ดราม่า", "โรแมนติก"],
    "directors": ["นรินธ์น แก้วสีเงิน"],
    "actors": ["พศิน เรืองวุฒิ", "นรีรัตน์ สีหราชนิเวศน์", "กัญญ์ชัญญ์ เธียรวิชญ์", "สมพงษ์ คุนาประถม", "รุ้งลาวัณย์ โทนะหงษา", "ชุมพร เทพพิทักษ์"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url": "https://www.youtube.com/playlist?list=PLs12_b9cOtEhe5XGssy4tzREUnAc9hQ-t",
    "published_year": "2558"
}

series_json = {
    "title": "Tensei shitara Slime Datta Ken เกิดใหม่ทั้งทีก็เป็นสไลม์ไปซะแล้ว",
    "keyword": "Muse Thailand",
    "description": "มิคามิ ซาโตรุ หนุ่มโสด ไม่เคยมีแฟน วัย 37 ปี ถูกแทงตายเพราะช่วยเพื่อนจากคนร้าย เขาได้เกิดใหม่ในต่างโลกด้วยร่างของสไลม์ ได้พบมังกร เวรุโดร่า ผู้ถูกผนึกมาร่วม 3 ร้อยปีและรู้ว่าเขามาจากต่างโลก ด้วยความเบื่อหน่ายในชีวิตจึงยอมเป็นเพื่อนกับสไลม์ ตั้งชื่อให้เขา “ริมุรุ” และให้เขากลืนตนเข้าไปในร่าง ด้วย2 ความสามารถ “นักล่า” ที่ทำให้เขาสามารถชิงความสามารถของผู้ถูกกลืน และ “ปราชญ์ผู้ยิ่งใหญ่” ทำให้เขาเข้าใจเรื่องราวในโลกใหม่ ส่งผลให้เขาพัฒนาเป็นสไลม์ที่น่าเกรงขามต่อเหล่ามอนสเตอร์ทั่วไป จนกลายเป็นปีศาจที่ยิ่งใหญ่ในภายหลัง",
    "state": 1,
    "reverse_loop": 0,
    "studio": ["Muse Thailand"],
    "genres": ["อนิเมะญี่ปุ่น", "ซับไทย", "การ์ตูน", "แอ็คชั่น", "ผจญภัย", "คอมเมดี้", "แฟนตาซี", "เหนือธรรมชาติ"],
    "directors": ["Yasuhito Kikuchi"],
    "actors": ["Miho Okasaki", "Takuma Terashima", "Yumiri Hanamori", "Asuna Tomari", "Houchu Ohtsuka", "Jun Fukushima", "Jun Fukuyama", "Kanehira Yamamoto", "Kazuya Nakai"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url": "https://www.youtube.com/playlist?list=PLIa05JMgYhhacplnc2ZE7eSnNcmWcCfW5",
    "published_year": "2561"
}

series_json = {
    "title": "Kenja no Deshi wo Nanoru Kenja ฉันเป็นศิษย์จอมปราชญ์จริงๆนะ - ฉบับมัดรวมทุกตอน",
    "keyword": "Muse Thailand",
    "description": "ซากิโมริ คางามิ ผู้สวมบทบาทเป็นนักอัญเชิญผู้น่าเกรงขามและหนึ่งในเก้าจอมปราชญ์นาม “ดัมเบิลดัฟ” ในเกมแนว VRMMO ชื่อ “อาร์คเอิร์ธออนไลน์” เผลอหลับไประหว่างเล่นและถูกส่งไปยังโลกที่เกมกลายเป็นความจริง มิหนำซ้ำ เขายังไม่ได้อยู่ในร่างนักปราชญ์ชรา แต่เป็นร่างของสาวน้อยหน้าตาน่ารักจิ้มลิ้ม...แบบนี้ก็เสียภาพพจน์ของนักปราชญ์สุดเคร่งขรึมที่อุตส่าห์สร้างมาหมดน่ะสิ! ซากิโมริ คางามิ (ดัมเบิลดัล์ฟ) ที่คิดเช่นนั้นเลือกที่จะอ้างตัวเป็นลูกศิษย์ของจอมปราชญ์ภายใต้ชื่อ “มิร่า” แต่ทว่าการผจญภัยเกิดใหม่เป็นสาวน้อยในโลกแฟนตาซี เปิดม่านขึ้นแล้วอย่างงดงาม!",
    "state": 1,
    "reverse_loop": 0,
    "studio": ["Muse Thailand"],
    "genres": ["ผจญภัย", "แฟนตาซี", "อนิเมะญี่ปุ่น", "ซับไทย", "การ์ตูน"],
    "directors": ["Keitaro Motonaga"],
    "actors": ["Haruka Tomatsu", "Kanomi Izawa", "Nichika Omori", "Ayumu Murase", "Isao Sasaki", "Ari Ozawa", "Junichi Saitou", "Daisuke Hirakawa", "Hiroki Yasumoto", "Ayane Sakura"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url": "https://www.youtube.com/playlist?list=PLIa05JMgYhhaUGVBXd7Drxao8o7zgIJ2i",
    "published_year": "2565",
}


series_json = {
    "title": "Assassination Classroom ห้องเรียนลอบสังหาร - ฉบับมัดรวมทุกตอน",
    "keyword": "Muse Thailand",
    "description": "ในโรงเรียนม.ต้นคุนุกิงาโอกะ เขาได้เริ่มทำงานเป็นครูประจำชั้น ม.3 ห้อง E ที่สอนนักเรียนไม่เพียงแค่วิชาทั่วไป แต่วิธีการลอบสังหารด้วย รัฐบาลญี่ปุ่นได้มีรางวัลเป็นเงิน 1 หมึ่นล้านเยน (3 พันล้านบาทโดยประมาณ) ให้สำหรับนักเรียนผู้ที่สามารถฆ่าอาจารย์ได้",
    "state": 1,
    "reverse_loop": 0,
    "studio": ["Muse Thailand"],
    "genres": ["วัยรุ่น", "คอมเมดี้", "อนิเมะญี่ปุ่น", "แอ็คชั่น", "การ์ตูน", "ซับไทย"],
    "directors": ["Seiji Kishi"],
    "actors": ["Tomokazu Sugita", "Mai Fuchigami", "Shizuka Itou", "Jun Fukuyama", "Aya Suzaki", "Nobuhiko Okamoto"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url": "https://www.youtube.com/playlist?list=PLs12_b9cOtEgX3duCirMXxwMXCNpjgB9n",
    "published_year": "2558"
}


series_json = {
    "title": "Tatoeba Last Dungeon Mae no Mura no Shounen หนุ่มน้อยใสซื่อจากหมู่บ้านหน้าลาสท์ดันเจี้ยนมาเข้ากรุงแล้ว",
    "keyword": "Muse Thailand",
    "description": "ในขณะที่ทุกคนในหมู่บ้านล้วนคัดค้าน แต่เด็กหนุ่มลอยด์ก็ไม่ทิ้งความฝันที่จะเป็นทหารและออกเดินทางไปยังเมืองหลวง แต่แม้ว่าเขาที่ถูกบอกว่าเป็นคนที่อ่อนแอที่สุดในหมู่บ้านและเหล่าชาวบ้านไม่มีใครรู้เลย ว่าหมู่บ้านของตัวเองเป็นแดนอมนุษย์หน้าดันเจี้ยนสุดท้าย!! นี่เป็นเรื่องราวความกล้าหาญของเด็กหนุ่มผู้แสดงความไร้เทียมทานออกมาโดยไม่รู้ตัว――。",
    "state": 1,
    "reverse_loop": 0,
    "studio": ["Muse Thailand"],
    "genres": ["ซับไทย", "ผจญภัย", "อนิเมะญี่ปุ่น", "แฟนตาซี", "การ์ตูน"],
    "directors": ["migmi"],
    "actors": ["Naomi Shindoh", "Minami Tsuda", "Yumiri Hanamori", "Katsuyuki Konishi", "Ai Kayano", "Madoka Asahina", "Miku Itō", "M.A.O", "Haruka Tomatsu"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url": "https://www.youtube.com/playlist?list=PLIa05JMgYhhZ9r58x4AZ0RPbK1K_hvTw9",
    "published_year": "2564"
}

series_json = {
    "title": "ขวัญใจไทยแลนด์",
    "keyword": "WorkpointOfficial",
    "description": "ก้องและแอนมีลูกชายด้วยกันหนึ่งคน ข่าวคราวความไม่ลงรอยของทั้งคู่เริ่มกระจายออกไป ว่าขาเตียงของคู่สามีซุปเปอร์ตาร์เริ่มจะสั่นคลอน เพื่อเป็นการกลบข่าวลือ ก้องกับแอนจึงถูกสั่งให้มาจัดรายการแก้ปัญหาชีวิตคู่ในทีวี แล้วก็เหมือนเป็นการแก้ปัญหาชีวิตคู่ของทั้งสองคนไปด้วย",
    "state": 1,
    "reverse_loop": 0,
    "studio": ["WorkpointOfficial"],
    "genres": ["ซีรี่ส์ไทย", "ซิตคอม", "ดราม่า", "โรแมนติก", "คอมเมดี้"],
    "directors": [],
    "actors": ["ศรราม เทพพิทักษ์", "สุวนันท์ ปุณณกันต์", "โจโจ้ ไมออกซิ", "ชมพูนุช กลิ่นจำปา", "เฉลิมพล ทิฆัมพรธีรวงศ์", "สรารัตน์ แซ่จิ๋ว", "ธิติพันธ์ สุริยาวิชญ์", "อินฑัช เตะชะเกิดกมล"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url": "https://www.youtube.com/playlist?list=PLcwQy6DvJjsyBcCHoyj6VvoNwoEVQCUEP",
    "published_year": "2560"
}

series_json = {
    "title": "จ่าเริงเซิ้งยับ",
    "keyword": "WorkpointOfficial",
    "description": "จ่าเริง อยู่ในร้านอาหารของตัวเอง แต่กลับแตกต่างจากร้านอาหารตามสั่งกว่าร้านอื่นๆ คือ เจ้าของร้านจะโชว์สเต็ปแดนซ์อยู่ตลอดเวลา เพราะความสุขของจ่าเริง คือการได้ “เต้น” นั่นเอง!! ทำให้ จ่ามิตร แม้จะเป็นเพื่อนสนิทของจ่าเริงก็ตาม แต่เพราะจ่ามิตรไม่เคยชนะจ่าเริงได้ ทุกเรื่อง ทำให้จ่ามิตรหลังจากได้คัมภีร์เสต็ปอัพแอดวานซ์มา เจ้าตัวเลยขอมาท้าประชันดวลเต้นกับจ่าเริงเสียเลย !!",
    "state": 1,
    "reverse_loop": 1,
    "studio": ["WorkpointOfficial"],
    "genres": ["ซีรี่ส์ไทย", "ซิตคอม", "โรแมนติก", "คอมเมดี้"],
    "directors": [],
    "actors": ["บุญสิตา อินทาปัจ", "สุพจน์ จันทร์เจริญ", "ธนา สุทธิกมล", "พิเชษฐ์ เอี่ยมชาวนา", "จำนงค์ ปิยะโชติ"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url": "https://www.youtube.com/playlist?list=PLcwQy6DvJjswizw633wPjYEEWbwImxvCb",
    "published_year": "2559"
}


series_json = {
    "title": "บันทึกการเดินทางต่างโลกของท่านอัศวินกระดูก Gaikotsu Kishi-sama, Tadaima Isekai e Odekakechuu",
    "keyword": "Muse Thailand",
    "description": "บันทึกการเดินทางต่างโลกของท่านอัศวินกระดูก เมื่อ “อาร์ค” ลืมตาตื่นขึ้นมาอีกที เขาก็อยู่ในต่างมิติด้วยร่างกายของตัวละครที่เขาเคยใช้ในเกม MMORPG เสียแล้ว ซึ่งร่างนั้นคือ “อัศวินกระดูก” ที่ภายในสวมใส่เกราะ และเป็นกระดูกทั่วร่างนั่นเอง ถ้ามีใครรู้เรื่องนี้ มีหวังถูกเข้าใจผิดว่าเป็นมอนเตอร์จนถูกไล่ล่าแน่นอน!? อาร์คจึงได้ตัดสินใจที่จะใช้ชีวิตในฐานะทหารรับจ้าง ทว่าเขาก็ไม่ใช่ผู้ชายที่จะมองข้ามเรื่องเลวร้ายที่เกิดขึ้นตรงหน้าไปได้หน้าตายเฉย! เรื่องราวแฟนตาซีการ “กอบกู้โลก” ต่างมิติ โดยไม่รู้ตัวของอัศวินโครงกระดูก กำลังจะเปิดม่านแล้ว!!",
    "state": 1,
    "reverse_loop": 0,
    "studio": ["Muse Thailand"],
    "genres": ["อนิเมะญี่ปุ่น", "ซับไทย", "แฟนตาซี", "แอ็คชั่น"],
    "directors": ["Katsumi Ono"],
    "actors": ["Fairouz Ai", "Nene Hieda", "Tomoaki Maeno", "Akira Ishida", "Daiki Hamano", "Kengo Kawanishi", "Kousuke Toriumi", "Minoru Shiraishi", "Miyu Tomita", "Rumi Okubo"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url": "https://www.youtube.com/playlist?list=PLIa05JMgYhhZ3LA4b4UDxY3iHVBDSOk_7",
    "published_year": "2565"
}


series_json = {
    "title": "อิรุมะคุง ผจญในแดนปีศาจ! Mairimashita! Iruma-kun",
    "keyword": "Muse Thailand",
    "description": "สึซึกิ อิรุมะ หนุ่มนิสัยดีวัย 14 ปีที่ถูกขายให้กับปีศาจ แต่กลับกลายเป็นว่า ปีศาจต้องการได้เขาเป็นหลาน และส่งให้เขาไปเรียนต่อในโรงเรียนปีศาจที่เป็นผู้อำนวยการอยู่ อิรุมะ ต้องเรียนร่วมกับปีศาจตนอื่นในฐานะนักเรียนหน้าใหม่ ถึงจะอ่อนแอ ไม่ปฏิเสธคนที่เดือดร้อน แต่เนื่องจากหนีปัญหามาทั้งชีวิต ทำให้เขามีความสามารถการป้องกันตัว (หลบหลีก) ที่ไร้ขีดจำกัด จนยากที่จะโดนโจมตีจากคู่ต่อสู้",
    "state": 1,
    "reverse_loop": 0,
    "studio": ["Muse Thailand"],
    "genres": ["อนิเมะญี่ปุ่น", "ซับไทย", "แฟนตาซี", "คอมเมดี้", "เหนือธรรมชาติ"],
    "directors": ["Makoto Moriwaki"],
    "actors": ["Ayaka Asai", "Ayumu Murase", "Ryohei Kimura", "Daisuke Ono", "Gakuto Kajiwara", "Genki Okawa", "Haruna Asami", "Junichi Suwabe", "Kaede Hondo", "Mitsuki Saiga"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url": "https://www.youtube.com/playlist?list=PLIa05JMgYhhZmcpiATdQVKKJomeI8wMdc",
    "published_year": "2562"
}

series_json = {
    "title": "ยอดกุ๊กแดนมังกร Chuuka Ichiban!",
    "keyword": "Muse Thailand",
    "description": "เหลยเอิ๋น พ่อครัวจากสมาคมอาหารใต้ดิน สมาคมที่มีความทะเยอทะยานที่จะปกครองคนด้วยอาหาร เขาเริ่มแข่งขันทำอาหารกับหลิวเหมาชิง เพื่อแย่งชิงเครื่องครัวศักดิ์สิทธิ์ คราวนี้จะต้องแล่เนื้อปลา จำเป็นต้องใช้ฝีมือการใช้มีดที่ยอดเยี่ยม และการต่อสู้กับเหลยเอิ๋นผู้เชี่ยวชาญการใช้มีดก็เริ่มต้นขึ้น!!",
    "state": 1,
    "reverse_loop": 0,
    "studio": ["Muse Thailand"],
    "genres": ["อนิเมะญี่ปุ่น", "ซับไทย", "อาหาร", "คอมเมดี้", "ดราม่า"],
    "directors": ["Masami Anno"],
    "actors": ["Mayumi Tanaka", "Satsuki Yukino", "Chika Sakamoto", "Hiroshi Yanaka", "Nobutoshi Hayashi", "Daisuke Sakaguchi", "Ryotaro Okiayu", "Rihoko Yoshida"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url": "https://www.youtube.com/playlist?list=PLIa05JMgYhhYtsTe-7IG9Cj87uLjqrSVS",
    "published_year": "2540"
}

series_json = {
    "title": "มหาวิบัติบาฮามุทคลั่ง: GENESIS | Shingeki no Bahamut GENESIS",
    "keyword": "Muse Thailand",
    "description": "เนื้อเรื่องเล่าถึงตำนานเมื่อสองพันปีก่อนที่ “บาฮามุท” ออกมาลั้ลลาจนดินแดนอาโบ๊ทมอดไหม้ พวกมนุษย์ที่ไร้ปัญญาต่อกรก็ได้แต่หนีและปล่อยให้เป็นหน้าที่ของปิศาจและทวยเทพแทน ผลจากศึกนั้นคาดว่าสามารถผนึกบาฮามุทได้ จนกระทั่งปัจจุบันมาถึง ณ ดินแดน “ไวเทียร์ป” มีแม่นางคนนึงต้องการไปที่ “เฮลเฮ็ม” ที่นั่นมันมีอะไรซ่อนอยู่กันแน่…",
    "state": 1,
    "reverse_loop": 0,
    "studio": ["Muse Thailand"],
    "genres": ["อนิเมะญี่ปุ่น", "ซับไทย", "ผจญภัย", "แฟนตาซี", "แอ็คชั่น"],
    "directors": ["Keiichi Satō"],
    "actors": ["Go Inoue", "Hiroyuki Yoshino", "Risa Shimizu", "Eri Kitamura", "Hiroaki Hirata", "Hiroshi Iwasaki", "Kenjiro Tsuda", "Masakazu Morita", "Megumi Han", "Miyuki Sawashiro", "Ryūzaburō Ōtomo"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url": "https://www.youtube.com/playlist?list=PLIa05JMgYhhbsqTwV_7rfFJmDt7S6FS8Z",
    "published_year": "2557"
}

series_json = {
    "title": "Black Bullet แบล็ค บุลเลท",
    "keyword": "Muse Thailand",
    "description": "ซาโตมิ เร็นทาโร่ หน่วยงานความมั่นคงทางพลเรือนของบริษัทเท็นโด เด็กหนุ่มผู้ชำนาญการต่อสู้ ร่วมกับคู่หู ไอฮาระ เอ็นจู หนึ่งในเด็กถูกสาปที่ภายนอกเหมือนเด็กสาววัย 10 ขวบ เคยได้รับเชื้อไวรัสแก๊สเทียทำให้ใช้พลังเหนือมนุษย์ได้ ทั้งสองได้ร่วมปกป้องประชาชนผู้บริสุทธ์จากผู้ที่กลายร่างโดยไวรัสร้าย",
    "state": 1,
    "reverse_loop": 0,
    "studio": ["Muse Thailand"],
    "genres": ["อนิเมะญี่ปุ่น", "ซับไทย", "ลึกลับ", "ไซไฟ", "แอ็คชั่น", "วัยรุ่น"],
    "directors": ["Masayuki Kojima"],
    "actors": ["Rikiya Koyama", "Rina Hidaka", "Yuuki Kaji", "Aki Toyosaki", "Ami Koshimizu", "Aoi Yūki", "Hiromichi Tezuka", "Inori Minase", "Kousuke Toriumi", "Megumi Han", "Rumi Okubo"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url": "https://www.youtube.com/playlist?list=PLIa05JMgYhha97X_VamZEpqvlJUNcdYrZ",
    "published_year": "2557"
}

series_json = {
    "title": "ล่าอสูรกาย Ushio to Tora",
    "keyword": "Muse Thailand",
    "description": "เรื่องราวของ 'อุชิโอะ อาโอซึกิ' หนุ่มมัธยมต้นที่มีชีวิตเหมือนเด็กวัยรุ่นทั่วไป อยู่มาวันหนึ่งอุชิโอะไปเจอห้องใต้ดินที่ห้องเก็บของในบ้านตัวเอง ด้วยความอยากรู้อยากเห็นเขาตัดสินใจเปิดประตูและเดินเข้าไปสำรวจ อุชิโอะได้พบกับอสูรร่างใหญ่ที่ถูกจองจำพร้อมกับหอกสมิงมานานกว่า 500 ปี การพบเจอกันในครั้งนี้ทำให้ชีวิตเด็กหนุ่มและเจ้าอสูรตนนั้น (โทร่า) เปลี่ยนไปตลอด อุชิโอะต้องออกเดินทางไปตามหาความลับของแม่ผู้ให้กำเนิดและร่วมมือกับโทร่าปราบปีศาจร้าย ยิ่งเข้าใกล้ความจริงมากเท่าไหร่เหมือนทั้งคู่ยิ่งเข้าใกล้หายนะครั้งใหญ่มากยิ่งขึ้น",
    "state": 1,
    "reverse_loop": 0,
    "studio": ["Muse Thailand"],
    "genres": ["อนิเมะญี่ปุ่น", "ซับไทย", "แอ็คชั่น", "ผจญภัย", "คอมเมดี้", "เหนือธรรมชาติ"],
    "directors": ["Satoshi Nishimura"],
    "actors": ["Rikiya Koyama", "Tasuku Hatanaka", "Ai Kayano", "Ai Satou", "Aki Toyosaki", "Ayahi Takagaki", "Daisuke Namikawa", "Fumiko Orikasa", "Hidekatsu Shibata", "Kana Hanazawa", "Keiji Fujiwara"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url": "https://www.youtube.com/playlist?list=PLs12_b9cOtEgEPK60rf0F0lIuxN7YyJqP",
    "published_year": "2558"
}

series_json = {
    "title": "6 ฉากพระโขนง",
    "keyword": "WorkpointOfficial",
    "description": "“ตลก6ฉาก” ฮาไม่หยุดส่งซิทคอมมุกสั้น “6ฉากพระโขนง” ลงจอความเฮี้ยนที่มาพร้อมเสียงหัวเราะไปกับเรื่องราวผีผี สิ่งลี้ลับ ความเชื่อ และสิ่งที่มองไม่เห็น มาเปลี่ยนความเฮี้ยนให้เป็นความฮาในแบบฉบับหกฉาก เรียกว่าเป็นอีกหนึ่งซิทคอมที่ทั้งฮาทั้งหลอนในตอนเดียว",
    "state": 1,
    "reverse_loop": 0,
    "studio": ["WorkpointOfficial"],
    "genres": ["ซีรี่ส์ไทย", "ซิตคอม", "สยองขวัญ", "คอมเมดี้"],
    "directors": [],
    "actors": ["เจริญพร อ่อนละม้าย", "กพล ทองพลับ", "รัศมีแข ฟ้าเกื้อล้น", "อิศรา กิจนิตย์ชีว์", "นลินทิพย์ เพิ่มภัทรสกุล", "จรรยา ธนาสว่างกุล", "อาจารียา พรหมพฤกษ์", "นลิน โฮเลอร์"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url": "https://www.youtube.com/playlist?list=PLcwQy6DvJjsy6LSxnJDzg0dkM9OcBbMqT",
    "published_year": "2563"
}

series_json = {
    "title": "สาวน้อยร้อยหม้อ",
    "keyword": "WorkpointOfficial",
    "description": "“สาวน้อยร้อยหม้อ” เรื่องราวเริ่มจาก กะทิ สาวซ่าส์ฝีปากแซ่บจากนครนายก เธอเข้ามาเรียนที่มหาวิทยาลัยในกรุงเทพเพื่อต้องการมีชีวิตที่ดีขึ้น และหาเงินเลี้ยงแม่ จะได้ให้แม่หยุดพักเลิกขายข้าวแกงที่บ้านนอก หลังจากเรียนจบมาเธอจึงได้เอาเงินเก็บจากการทำงานพิเศษด้วยเป็นพริ้ตติ้มาหุ้นกับเพื่อนเปิดร้านชาบูสมุนไพร",
    "state": 1,
    "reverse_loop": 0,
    "studio": ["WorkpointOfficial"],
    "genres": ["ซีรี่ส์ไทย", "โรแมนติก", "คอมเมดี้"],
    "directors": ["ธนวัฒน์ แท่งทอง"],
    "actors": ["กันต์ กันตถาวร", "ทิฆัมพร ฤทธิ์ธาอภินันท์", "สมเกียรติ จันทร์พราหมณ์", "สุนารี ราชสีมา", "นลิน โฮเลอร์", "ทองภูมิ สิริพิพัฒน์", "ณภศศิ สุรวรรณ", "ศานติ สันติเวชกุล", "สุพจน์ จันทร์เจริญ", "รัชเมศฐ์ ไชยพิชญารัตน์"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url": "https://www.youtube.com/playlist?list=PLcwQy6DvJjsx-EcVho00T8dvyy4X4_yr7",
    "published_year": "2561"
}

series_json = {
    "title": "ไซอิ๋ว อภินิหารลิงเทวดา",
    "keyword": "WorkpointOfficial",
    "description": "ละครไซอิ๋ว อภินิหารลิงเทวดา ดัดแปลงมาจากภาพยนตร์ฮ่องกงเรื่องไซอิ๋ว 95 เดี๋ยวลิงเดี๋ยวคนภาค 1 และ 2 ที่นำแสดงโดยโจวซิงฉือ เนื้อหากล่าวถึงสัจธรรมที่ใดมีรัก ที่นั่นมีทุกข์ โดยนำเสนอผ่านประสบการณ์ความรักและการพลัดพรากของจื้อจุนเป่า (หรือซุนหงอคงที่กลับชาติไปเกิดเป็นมนุษย์) เมื่อซุนหงอคงตระหนักถึงความทุกข์อันแสนสาหัสที่เกิดจากความรักเลยอยากหลุดพ้นจากความทุกข์และวัฏสงสาร เขาจึงยอมสวมรัดเกล้า (มงคล) แล้วติดตามพระถังซำจั๋งไปยังชมพูทวีปเพื่ออัญเชิญพระไตรปิฎก",
    "state": 1,
    "reverse_loop": 0,
    "studio": ["WorkpointOfficial"],
    "genres": ["ซีรี่ส์ฮ่องกง", "ซีรี่ส์จีน", "พากย์ไทย", "แฟนตาซี", "ย้อนยุค", "คอมเมดี้", "โรแมนติก"],
    "directors": ["หลิวเจิ้นเหว่ย", "จูรุ่ยปิน"],
    "actors": ["หวงจื่อเทา", "อิ่นเจิ้ง", "หลิวเทียนจั่ว", "จ้าวอี้", "ตู้รั่วซี", "เวินซิน"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url": "https://www.youtube.com/playlist?list=PLK_A87FDG6rRgefi3w_5v7LSKtZLdGQ8G",
    "published_year": "2561"
}

series_json = {
    "title": "เภสัชกรเทพสองโลก Isekai Yakkyoku",
    "keyword": "Muse Thailand",
    "description": "นักเภสัชศาสตร์หนุ่มผู้หมกมุ่นและทุ่มเทชีวิตให้กับงานวิจัย จนเสียชีวิตจากการโหมงานหนัก ดวงจิตของเขาได้ทะลุมิติไปอยู่ในร่างของฟาร์มา บุตรชายแห่งตระกูลแพทย์โอสถหลวงชื่อดัง เพื่อช่วยเหลือผู้คนในโลกต่างมิติ ที่การรักษาและใช้ยาแบบผิดๆกลายเป็นเรื่องปกติ เขาจึงใช้ความรู้ด้านเภสัชศาสตร์ร่วมสมัยจากในชาติก่อน และความสามารถสุดโกงที่เพิ่งได้รับมาเพื่อสู้กับสารพัดโรคร้าย",
    "state": 0,
    "reverse_loop": 0,
    "studio": ["Muse Thailand"],
    "genres": ["อนิเมะญี่ปุ่น", "การ์ตูน", "แฟนตาซี"],
    "directors": ["Keizou Kusakawa"],
    "actors": ["Aki Toyosaki", "Kaede Hondo", "Kenji Nomura", "Maria Naganawa", "Reina Ueda", "Shizuka Itou", "Aoi Ichikawa"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url": "https://www.youtube.com/playlist?list=PLIa05JMgYhhYdp8k2yd2pM96gSb9a7LjK",
    "published_year": "2565"
}

series_json = {
    "title": "Made in Abyss ผ่าเหวนรก",
    "keyword": "Muse Thailand",
    "description": "นักบุกเบิกหลุมยักษ์ ถ้ำที่เหลือหลุมขนาดใหญ่ “Abyss” ถูกค้นพบบนเกาะเมื่อเกือบสองพันปีก่อน เมื่อทำการสำรวจได้มีคนพบทั้งสิ่งมีชีวิตที่ไม่เคยเห็นบนผืนดินแล้วยังมีการค้นพบโบราณวัตถุที่ล้ำค่ามากมายจากคนรุ่นก่อน ทำให้มีคนพยายามเข้าไปสำรวจ แม้จะเสี่ยงอันตรายถึงชีวิตก็ตาม จนกลายเป็นสถานที่มีชื่อเสียง นอกจากอันตรายที่พบรอบด้านแล้ว การสำรวจชั้นที่ลึกที่ซึ่งสภาพแวดล้อมต่างจากภายนอก บรรกาศมืดมิดไร้แสงสว่าง กลิ่นอับชื้นที่ชวนขนลุก เป็นอันตรายต่อสภาพจิตใจ ซึ่งต้องอาศัยความกล้าหาญอย่างมากที่จะกลับมาได้ ริโกะ เด็กสาวที่เกิดในเมืองโอซึ ฝันที่จะได้สำรวจด้านใน Abyss ตามรอยแม่ของเธอที่เคยเป็นนักผจญภัยที่มีชื่อเสียงในอดีตเพื่อไขปริศนาของถ้ำ จนกระทั่งเธอได้พบกับโรบ็อตหนุ่มที่หลงมายังเมืองนี้ โดยเสียความทรงจำไม่ทราบชื่อและที่มาของตน การผจญภัยของเธอและเขาจึงได้เริ่มต้นขึ้น",
    "state": 0,
    "reverse_loop": 1,
    "studio": ["Muse Thailand"],
    "genres": ["อนิเมะญี่ปุ่น", "ซับไทย", "การ์ตูน", "ผจญภัย", "ดราม่า", "แฟนตาซี", "ลึกลับ", "ไซไฟ"],
    "directors": ["Masayuki Kojima"],
    "actors": ["Mariya Ise", "Miyu Tomita", "Aki Toyosaki", "Eri Kitamura", "Maaya Sakamoto", "Manami Hanawa", "Manami Numakura", "Mutsumi Tamura"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url": "https://www.youtube.com/playlist?list=PLIa05JMgYhhazlQRWkc4UCxNX-oIqK0ly",
    "published_year": "2560"
}

series_json = {
    "title": "Hoshi no Samidare ศึกอลวนต่างดาวป่วนโลก",
    "keyword": "Muse Thailand",
    "description": "อามามิยะ ยูฮิ…เคยเป็นนักศึกษามหาวิทยาลัยที่แสนจะธรรมดาคนหนึ่ง แต่แล้ววันหนึ่งกิ้งก่าที่จู่ๆ ก็ปรากฏตัวขึ้นก็ขอให้เขาให้ความร่วมมือในการกอบกู้ “วิกฤติของโลก” เขาถูกยัดเยียดแหวนและพลังให้โดยไม่มีเวลาปฏิเสธ แถมยังถูกศัตรูเข้าจู่โจมอย่างรวดเร็ว ผู้ที่ช่วยยูฮิไว้เป็นสาวน้อยเพื่อนบ้าน “ซามิดาเระ” เธอที่คิดว่าเป็นพระผู้ช่วย แต่แท้จริงแล้วกลับเป็นจอมมารที่วางแผนครองโลกซะงั้น!",
    "state": 0,
    "reverse_loop": 0,
    "studio": ["Muse Thailand"],
    "genres": ["อนิเมะญี่ปุ่น", "ซับไทย", "การ์ตูน", "แอ็คชั่น", "ผจญภัย", "คอมเมดี้", "ดราม่า", "วัยรุ่น"],
    "directors": ["Nobuaki Nakanishi"],
    "actors": ["Junya Enoki", "Naomi Ōzora", "Atsuko Tanaka", "Aya Suzaki", "Azusa Tadokoro", "Chihaya Yoshitake", "Chinatsu Hirose", "Gen Sato"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url": "https://www.youtube.com/playlist?list=PLIa05JMgYhhYE1zSfxm3LkcoiEXe7oNd-",
    "published_year": "2565"
}

series_json = {
    "title": "พ่อบ้านใจกล้าสตอรี่",
    "keyword": "WorkpointOfficial",
    "description": "ซัน เจ้าของบริษัทชุดชั้นในสตรีที่สืบทอดมาตั้งแต่บรรพบุรุษ ชายผู้ใช้ชีวิตจืดชืดไร้รสชาติมาตั้งแต่สมัยวัยรุ่น ทำงาน ยันแต่งงานกับ ขิม หญิงสาวเจ้าระเบียบชอบจัดการ...เจ้าของธุรกิจเวดดิ้งแพลนเนอร์ที่คอยวางแผนแต่งงานให้เหล่าคู่รัก...ทั้งสองใช้ชีวิตคู่อย่างราบเรียบไร้ปัญหาจนครบรอบวันแต่งงานปีที่ 16 เรื่องไม่คาดฝันเกิดขึ้น",
    "state": 1,
    "reverse_loop": 0,
    "studio": ["WorkpointOfficial"],
    "genres": ["ซีรี่ส์ไทย", "โรแมนติก", "คอมเมดี้"],
    "directors": ["นฤบดี เวชกรรม"],
    "actors": ["สหรัถ สังคปรีชา", "พรพรรณ ชุนหชัย", "ธนกฤต พานิชวิทย์", "ศกลรัตน์ วรอุไร", "ณฉัตร จันทพันธ์", "ลภัสลัล จิรเวชสุนทรกุล", "เบญจพล เชยอรุณ"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url": "https://www.youtube.com/playlist?list=PLcwQy6DvJjszSVpkqyfkxG1OVBAq09tE1",
    "published_year": "2560"
}

series_json = {
    "title": "Youkoso Jitsuryoku Shijou Shugi no Kyoushitsu e ขอต้อนรับสู่ห้องเรียนนิยม (เฉพาะ) ยอดคน",
    "keyword": "Muse Thailand",
    "description": "โรงเรียน คิโด อิคุเซย์ มีชื่อเสียงจากนักเรียนแทบจะร้อยเปอร์เซนต์ที่สามารถหางานทำหรือเข้าเรียนต่อมหาวิทยาลัยได้ มีชื่อเสียงเรื่องการปล่อยนักเรียนได้รับอิสระหลายอย่างในระหว่างที่อยู่โรงเรียน จนเหมือนเป็นโรงเรียนในฝันที่เหล่าวัยรุ่นอยากเข้าไปเรียน แต่ในความเป็นจริง มีเพียงนักเรียนห้อง A ที่ได้รับการสิทธิพิเศษ",
    "state": 1,
    "reverse_loop": 0,
    "studio": ["Muse Thailand"],
    "genres": ["ญี่ปุ่น", "จิตวิทยา", "ชีวิตประจำวัน", "ดราม่า", "อนิเมะญี่ปุ่น", "วัยรุ่น", "การ์ตูน"],
    "directors": ["Seiji Kishi"],
    "actors": ["Shouya Chiba", "Ayana Taketatsu", "Akari Kitou", "Mao Ichimichi", "Rina Hidaka", "Yurika Kubo", "Nao Touyama"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url": "https://www.youtube.com/playlist?list=PLIa05JMgYhhZmJoBRGrwrz2wz2Q6ZuPoi",
    "published_year": "2560"
}

series_json = {
    "title": "",
    "keyword": "",
    "description": "",
    "state": True,
    "reverse_loop": False,
    "studio": ["TVB"],
    "genres": ["ซีรี่ส์ฮ่องกง", "ซีรี่ส์จีน", "พากย์ไทย", "กำลังภายใน", "ประวัติศาสตร์", "คลาสสิค", "ย้อนยุค"],
    "directors": [],
    "actors": [""],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url": "",
    "published_year": ""
}

    # =======================================================================================
# tvshow_json = {
#     "title": "",
#     "keywords": [""],
#     "reverse_loop": false,
#     "state": false,
#     "description": "",
#     "genres": [""],
#     "actors": [],
#     "studio": [],
#     "season_title": "",
#     "yt_playlist_url":  "",
#     "published_year": ""
# }

tvshow_json = {
    "title": "Film For Fans",
    "keywords": ["One Playground"],
    "reverse_loop": 1,
    "state": 1,
    "description": "Film For Fans คือ ความตั้งใจที่พระเอกหนุ่ม ฟิล์มเซอร์ไพร์สแฟนคลับ ถึงที่ โดยที่แฟนคลับไม่รู้ตัว สร้างช่วงเวลาที่พิเศษร่วมกับแฟนคลับ โดยฟิล์มมีส่วนร่วมในการคิดและหาข้อมูลด้วยตัวเอง แล้วยังลงทุนปลอมตัว เพื่อเซอร์ไพรส์แฟนๆจริงๆ ถือกล้องเอง สัมภาษณ์เอง แบบระยะประชิด",
    "genres": ["รายการไทย", "เรื่องทั่วไป", "วาไรตี้"],
    "actors": ["ธนภัทร กาวิละ"],
    "studio": ["one31", "One Playground"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url":  "https://www.youtube.com/playlist?list=PLbtuab-EGHySiPwD2-8Q3L8x5-ZWSQZSm",
    "published_year": "2563"
}

tvshow_json = {
    "title": "เพื่อนพี่ต้องมีผัว",
    "keywords": ["one31"],
    "reverse_loop": 1,
    "state": 1,
    "description": "ทำไมคนสมัยนี้ หาผัว หาเมีย กันยากจัง?! เมื่อเพื่อนพ้องน้องพี่รอบกายยังโสดสนิท กูรูหนุ่ม เกลือ กิตติ จึงต้องแปลงร่างเป็นกามเทพงัดทุกกลเม็ดเด็ดมาให้ #คนโสด เลิกโสด กันสักที เพราะ เพื่อนพี่ต้องมีผัว",
    "genres": ["รายการไทย", "โรแมนติก", "วาไรตี้"],
    "actors": ["กิตติ เชี่ยววงศ์กุล"],
    "studio": ["one31", "One Playground"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url":  "https://www.youtube.com/playlist?list=PLbtuab-EGHyRglbOJYCl-y-LPIJ5ctfP9",
    "published_year": "2564"
}

tvshow_json = {
    "title": "มะปรางจับไมค์",
    "keywords": ["One Playground"],
    "reverse_loop": 1,
    "state": 0,
    "description": "มะปรางตัดสินใจทำรายการ มะปรางจับไมค์ เพื่อร้องเพลงกับเพื่อนพี่น้องศิลปินที่รู้จัก และได้ช่วยพวกเขาโปรโมทผลงานไปพร้อมกัน รวมถึงอ้อนแขกรับเชิญมาจับไมค์ร้องเพลงต่างๆเวอร์ชั่นใหม่  ให้ทุกคนหายคิดถึง เพลงนี้จะสนุก เศร้า เหงา ซึ้งแค่ไหน บอกเลยว่าต้องฟัง!!!",
    "genres": ["รายการไทย", "ดนตรี-เพลง"],
    "actors": ["อลิสา ขุนแขวง"],
    "studio": ["one31", "One Playground"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url":  "https://www.youtube.com/playlist?list=PLbtuab-EGHySDR6cprR8IMUA3ITLwm2Ab",
    "published_year": "2564"
}

tvshow_json = {
    "title": "กินกัน(น์)มั้ย",
    "keywords": ["one31"],
    "reverse_loop": 0,
    "state": 1,
    "description": "เชฟกันน์ หนุ่มหล่อรองแชมป์ Top Chef Thailand Season2 จะคว้ามีดเข้าครัวทำเมนูสุดว้าวด้วยวัตถุดิบลับจากแขกรับเชิญแบบที่ใครก็คาดไม่ถึงในรายการ กินกันน์มั้ย",
    "genres": ["รายการไทย", "อาหาร"],
    "actors": ["สรวิศ แสงวณิช"],
    "studio": ["one31", "One Playground"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url":  "https://www.youtube.com/playlist?list=PLs12_b9cOtEjltx-QQzpX_VEfDQCl9zDg",
    "published_year": "2564"
}

tvshow_json = {
    "title": "สมรภูมิดาวกีฬา",
    "keywords": ["WorkpointOfficial"],
    "reverse_loop": 0,
    "state": 0,
    "description": "รายการ สมรภูมิดาวกีฬา การแข่งขันที่ผสมผสานกีฬาและความบันเทิงของเหล่าดารา เซเลปคนดัง สู้ศึกกับเหล่านักกีฬาอาชีพ และทีมชาติไทย พร้อมลงสนามดวลกันแบบไม่มีใครยอมใคร เพื่อคว้าชัยชนะและนำเงินรางวัลไปมอบสนับสนุนสมาคมนักกีฬา และสร้างแรงบันดาลใจให้ทุกคนหันมาเล่นกีฬาออกกำลังกายเพื่อสุขภาพกายและใจให้แข็งแรง",
    "genres": ["รายการไทย", "กีฬา"],
    "actors": ["สมชาย เข็มกลัด", "สมจิตร จงจอหอ", "ปลื้มจิตร์ ถินขาว", "วิลาวัณย์ อภิญญาพงศ์"],
    "studio": ["WorkpointOfficial"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url":  "https://www.youtube.com/playlist?list=PLcwQy6DvJjszbQxeb1h9VFuN7P9hFT8VH",
    "published_year": "2565"
}

tvshow_json = {
    "title": "กัน(น์) เดลิเวอรี่",
    "keywords": ["one31"],
    "reverse_loop": 1,
    "state": 1,
    "description": "รายการที่ เชฟกันน์ จะสลัดผ้ากันเปื้อนเชฟเยือนน้องๆพี่ๆเพื่อนๆไปตามสถานที่ต่างๆ เพื่อเรียนรู้การทำงานของแต่ล่ะบทบาทหน้าที่ว่าเหนื่อยแตกต่างกันอย่างไร ได้ประสบการณ์ที่ดีแน่นอน",
    "genres": ["รายการไทย", "เรื่องทั่วไป"],
    "actors": ["สรวิศ แสงวณิช"],
    "studio": ["one31", "One Playground"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url":  "https://www.youtube.com/playlist?list=PLbtuab-EGHyTWjrCGX7Jv06r1FshqCTaV",
    "published_year": "2564"
}

tvshow_json = {
    "title": "Fernstagram",
    "keywords": ["one31"],
    "reverse_loop": 1,
    "state": 1,
    "description": "ใบเฟิร์น อัญชสา จะพาไปหา “มุมถ่ายรูปสุดลับ” พร้อมทริคถ่ายยังไงให้เป๊ะ โพสยังไงให้ปัง ดังสนั่นทั่วโซเชียล! เดี๋ยวนี้เช็คอินธรรมดา...มันไม่พอ ถึงที่เดียวกัน แต่ชั้นต้องปังกว่า “เตรียมชุดให้ปั๊วะ” “แต่งหน้าให้ปัง” “โพสต์อย่างเผลอๆ”  ใบเฟิร์นจะอาสาพาแก๊งเพื่อนไปเที่ยวแบบ Hidden Bangkok!! เพื่อตามหา “มุมถ่ายรูปสุดลับ” ไว้เป็นจุด landmark ใหม่ ให้ใครๆ ก็ตามมาถ่ายรูปแบบชิคๆ",
    "genres": ["รายการไทย", "เรื่องทั่วไป", "ท่องเที่ยว"],
    "actors": ["อัญชสา มงคลสมัย"],
    "studio": ["One Playground", "one31"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url":  "https://www.youtube.com/playlist?list=PLbtuab-EGHyTKU5BNioRA7ZDKd8YBdxYN",
    "published_year": "2564"
}

tvshow_json = {
    "title": "ลองซิจ๊ะ",
    "keywords": ["one31"],
    "reverse_loop": 1,
    "state": 1,
    "description": "ภารกิจโหด มันส์ ฮา ท้าลองทุกอย่าง ลองให้เห็น ลองให้ดูกับประสบการณ์ใหม่ในแบบ ตั้ม โดม ที่ทั้งคู่จะไปลองให้เห็นกันจะจะ และจะทำให้อึ้ง ทึ่ง ไปตามๆกัน ร่วมลุ้นความสนุก ตลก เฮฮา ความกล้า บ้าบิ่น และการแกล้งกันแหย่กันของ ตั้ม วราวุธ และ โดม จารุวัฒน์",
    "genres": ["รายการไทย", "เรื่องทั่วไป"],
    "actors": ["วราวุธ โพธิ์ยิ้ม", "จารุวัฒน์ เชี่ยวอร่าม"],
    "studio": ["one playground", "one31"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url":  "https://www.youtube.com/playlist?list=PLbtuab-EGHySTOdgCbyQ2gZstHQIUe1ZJ",
    "published_year": "2564"
}

tvshow_json = {
    "title": "MillyNikki",
    "keywords": ["One Playground"],
    "reverse_loop": 1,
    "state": 0,
    "description": "ส่องความสวยสดใสของสองสาวฝาแฝดสุดฮอต นิกกี้ นิโคล และ มิลลี่ คามิลล่า ทั้งคู่เป็นลูกครึ่งไทย-เยอรมัน ลูกสาวของอดีตนางแบบชื่อดัง รุ่งนภา กิตติวัฒน์ นิกกี้และนิโคลเคยมีผลงานการแสดงผ่านตาให้แฟน ๆ ได้เห็นอยู่บ้าง และทั้งคู่พร้อมจะมาเปิดใจหมดเปลือกเกี่ยวกับชีวิตของตัวเอง",
    "genres": ["รายการไทย", "เรื่องทั่วไป"],
    "actors": ["คามิลล่า กิตติวัฒน์", "นิโคล กิตติวัฒน์"],
    "studio": ["One Playground"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url":  "https://www.youtube.com/playlist?list=PLbtuab-EGHyTKugMAnWsCDT7R-4eNrW6_",
    "published_year": "2565"
}

tvshow_json = {
    "title": "ตามตง",
    "keywords": ["One Playground"],
    "reverse_loop": 1,
    "state": 0,
    "description": "รายการที่จะตามตงไปป่วน เฮฮา ทำตัวสนุกๆตามสถานที่ต่างๆ รวมถึง ตงตง จะได้รับภารกิจที่ต้องบรรลุให้ได้อีกด้วย ไม่ว่าจะปลอมตัวเป็นเด็กเสิร์ฟไอติม, พลิกวิกฤติร้านก๊วยเตี๋ยวใกล้เจ๊ง, หรือแม้แต่ ช่วยพี่ๆคนเก็บขยะ งานนี้สนุกสนานเฮฮายังไง ก็ต้องลองไปติดตามกันให้ได้",
    "genres": ["รายการไทย", "ท่องเที่ยว", "เรื่องทั่วไป"],
    "actors": ["กฤษกร กนกธร"],
    "studio": ["One Playground"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url":  "https://www.youtube.com/playlist?list=PLbtuab-EGHyRC81uT7iGfUzVuHCVq7Qn4",
    "published_year": "2565"
}

tvshow_json = {
    "title": "Honey Hero คู่รักนักสู้",
    "keywords": ["WorkpointOfficial"],
    "reverse_loop": 1,
    "state": 1,
    "description": "Honey Hero คู่รักนักสู้ เป็นรายการเกมโชว์ที่มีรูปแบบจากรายการ Mein Mann kann ของบริษัท Red Arrow International ประเทศเยอรมัน โดยความสนุกสนานของรายการจะอยู่ที่เกมในแต่ละด่านของผู้เข้าแข่งขันที่จะต้องเจอในเกมที่แต่ละคนเกินจะคาดเดา",
    "genres": ["รายการไทย", "เกมโชว์", "โรแมนติก"],
    "actors": ["เพ็ชรทาย วงษ์คำเหลา", "สุดารัตน์ โพธิ์น้ำคำ", "เจริญพร อ่อนละม้าย"],
    "studio": ["WorkpointOfficial"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url":  "https://www.youtube.com/playlist?list=PLcwQy6DvJjsw3Ld9CmxLUyl4RYt1Ayrx5",
    "published_year": "2559"
}

tvshow_json = {
    "title": "กู้อีจู้ผจญภัย",
    "keywords": ["WorkpointOfficial"],
    "reverse_loop": 1,
    "state": 1,
    "description": "น่ารักกับปรากฎการณ์ ที่จะทำให้คุณหัวใจละลายใน “กู้อีจู้ผจญภัย” พร้อม 2 พิธีกรคู่หู รถเมล์ คะนึงนิจ จักรสมิทธานนท์ และ เจี๊ยบ เชิญยิ้ม ที่จะพาน้องๆ ผจญภัยไปกับโลกแห่งจิตนาการ และการค้นหาคำตอบกับของปริศนา??? ที่ไม่เคยเห็นมาก่อน เพื่อแลกมากับของรางวัล สนุกไปพร้อมกับดารารับเชิญที่ขึ้นชื่อว่ารักเด็ก",
    "genres": ["รายการไทย", "เด็ก", "เกมโชว์"],
    "actors": ["คะนึงนิจ จักรสมิทธานนท์", "เฉลิม ปานเกิด"],
    "studio": ["WorkpointOfficial"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url":  "https://www.youtube.com/playlist?list=PLcwQy6DvJjsxXk54STzx9Ah558W9yM-il",
    "published_year": "2559"
}

tvshow_json = {
    "title": "เที่ยว ทิ้ง ตัว",
    "keywords": ["WorkpointOfficial"],
    "reverse_loop": 0,
    "state": 0,
    "description": "ท่ามกลางทิวเขาสีเขียวสวยงาม และไอหมอกในช่วงกลางปี อิ่มท้องไปกับอาหารท้องถิ่น พร้อมกับสัมผัสวิถีชีวิตชุมชน เที่ยว ทิ้ง จะพาทุกท่านทิ้งความเหนื่อยล้าจากทุกสิ่ง แล้วไปทิ้งตัวกันที่กับสถานที่ท่องเที่ยว Unseen มากมาย",
    "genres": ["รายการไทย", "ท่องเที่ยว", "รีวิว"],
    "actors": ["ธนัชพันธ์ บูรณาชีวาวิไล"],
    "studio": ["WorkpointOfficial"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url":  "https://www.youtube.com/playlist?list=PLcwQy6DvJjsyPHXHGbp2UeuaDPxkPiTHR",
    "published_year": "2565"
}

tvshow_json = {
    "title": "ร้อยเรื่องรอบโลก",
    "keywords": ["รอบโลก by กรุณา บัวคำศรี"],
    "reverse_loop": 0,
    "state": 0,
    "description": "รายการสารคดีข่าวที่นำเสนอประเด็นทางสังคมที่ซุกซ่อนอยู่ตามหลืบมุมต่างๆ ทั่วโลก",
    "genres": ["รายการไทย", "เรื่องน่ารู้", "สารคดี"],
    "actors": ["กรุณา บัวคำศรี"],
    "studio": ["รอบโลก by กรุณา บัวคำศรี"],
    "season_title": "ปี 2020",
    "yt_playlist_url":  "https://www.youtube.com/playlist?list=PLD_SIx8TTqmg11HJo7Sfa8vfx2DAuFe8e",
    "published_year": "2563"
}

tvshow_json = {
    "title": "วันกรรชัยทอล์ค",
    "keywords": ["วันกรรชัย"],
    "reverse_loop": 1,
    "state": 0,
    "description": "ทอล์คสบายๆสไตล์หนุ่ม กรรชัย กับดารา นักแสดง และคนในวงการบันเทิงหลากหลาย เปิดมุมมอง รู้จักตัวตน คุยตรงประเด็น ถามตรงๆไม่อ้อมค้อม โดยเจ้าพ่อโหนกระแส กรรชัย กำเนิดพลอย",
    "genres": ["รายการไทย", "ทอล์กโชว์"],
    "actors": ["กรรชัย กำเนิดพลอย"],
    "studio": ["วันกรรชัย"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url":  "https://www.youtube.com/playlist?list=PL0hEuRPtya1fEQbDjzRkJ053Si0vkIGX5",
    "published_year": "2565"
}

tvshow_json = {
    "title": "MORE MOD",
    "keywords": ["MORE MOD"],
    "reverse_loop": 0,
    "state": 0,
    "description": "รายการ MORE MOD สารคดีมดที่จะมาสอนวิธีการเลี้ยงมดอย่างถูกวิธี รวมถึงสอนสายพันธุ์มดที่น่าสนใจ ใครที่อยากเลี้ยงมดต้องไม่พลาด",
    "genres": ["รายการไทย", "สัตว์", "สารคดี"],
    "actors": [],
    "studio": ["MORE MOD"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url":  "https://www.youtube.com/playlist?list=PLs12_b9cOtEj-lT_8ov3iEoVsecXxa75S",
    "published_year": "2564"
}

tvshow_json = {
    "title": "บัดดี้ตีไข่",
    "keywords": ["WorkpointOfficial"],
    "reverse_loop": 1,
    "state": 1,
    "description": "รายการบัดดี้ตีไข่ รายการที่จะนำดาราทั่วฟ้าเมืองไทย มาล้วงความลับและตีไข่ใส่กัน เลือกไข่ที่หมนุเป็นรูเล็ตให้ดี ไข่ต้มรอด ไข่ดิบโดนล้วง",
    "genres": ["รายการไทย", "วาไรตี้"],
    "actors": ["ภาคภูมิ จงมั่นวัฒนา "],
    "studio": ["WorkpointOfficial"],
    "season_title": "ซี่ซั่น 1",
    "yt_playlist_url":  "https://www.youtube.com/playlist?list=PLcwQy6DvJjszJxHkBRepOYRMwL0L72_fS",
    "published_year": "2561"
}


tvshow_json = {
    "title": "Let Me In Thailand",
    "keywords": ["WorkpointOfficial"],
    "reverse_loop": 0,
    "state": 1,
    "description": "Let Me In อีกหนึ่งรายการที่โด่งดังมาก ในประเทศเกาหลี รายการที่เปลี่ยนชีวิต เปลี่ยนหน้าของผู้ผ่านการคัดเลือก ให้ได้ไปศัลยกรรมพลิกชีวิต ในรายการไม่ได้ส่งเสริมให้คนทำศัลยกรรมเพื่อให้แค่ดูดีแค่รูปลักษณ์ภายนอกเท่านั้น แต่เป็นการช่วยเหลือให้คนที่มีความผิดปกติทางด้านบุคคลิกภาพและหน้าตา ที่เป็นปัญหาในการดำรงชีวิต ให้สามารถใช้ชีวิตอยู่ได้ในสังคมอย่างปกติได้ และมีชีวิตใหม่ที่ดียิ่งขึ้น",
    "genres": ["รายการไทย"],
    "actors": ["วรัทยา นิลคูหา", "อรนภา กฤษฎี"],
    "studio": ["WorkpointOfficial"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url":  "https://www.youtube.com/playlist?list=PLpLC08ueLfB_NmLMbYloKgLhpDXR09h9V",
    "published_year": "2559"
}

tvshow_json = {
    "title": "The Mask Line Thai",
    "keywords": ["WorkpointOfficial"],
    "reverse_loop": 1,
    "state": 1,
    "description": "The Mask Line Thai เป็นรายการโทรทัศน์ประเภทเรียลลิตี้มิวสิกโชว์ฤดูกาลพิเศษของ The Mask Singer หน้ากากนักร้อง ของประเทศไทย โดยรูปแบบการแข่งขันของฤดูกาลนี้ยังคงมีรูปแบบการแข่งขันเหมือนกับ The Mask Project A ทั้งหมด แต่ในฤดูกาลนี้จะแตกต่างจากฤดูกาลที่แล้ว คือจะมีการผสมผสานอัตลักษณ์ความเป็นไทยเข้าไปด้วยในรายการ ไม่ว่าจะเป็นดนตรี หน้ากาก เสื้อผ้าเครื่องแต่งกาย และอื่น ๆ",
    "genres": ["รายการไทย", "ดนตรี-เพลง", "เรียลลิตี้"],
    "actors": ["กันต์ กันตถาวร"],
    "studio": ["WorkpointOfficial"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url":  "https://www.youtube.com/playlist?list=PLcwQy6DvJjswjF19zLcREIsMnKA9VRJIe",
    "published_year": "2561"
}

tvshow_json = {
    "title": "ฟ้าแลบเด็ก",
    "keywords": ["WorkpointOfficial"],
    "reverse_loop": 0,
    "state": 1,
    "description": "เป็นเทปพิเศษที่มีผู้ดำเนินรายการ โดยการแข่งขันในแต่ละครั้งจะมีผู้เข้าแข่งขัน 2 ทีม ทีมละ 4 คน ประกอบไปด้วยเด็กที่มีชื่อเสียง 3 คน และอีก 1 คนเป็นหัวหน้าที่เป็นดารา, นักแสดงหรือนักร้อง มารับหน้าที่ผู้จัดการทีม (โดยจะไม่มีส่วนร่วมในการตอบคำถาม) โดยให้ทั้ง 2 ทีมส่งตัวแทนทีมละ 1 คนออกมาแข่งขันตอบคำถามชุดเดียวกันภายในเวลา 2 นาที",
    "genres": ["รายการไทย", "เกมโชว์"],
    "actors": ["ภานุพันธ์ ครุฑโต"],
    "studio": ["WorkpointOfficial"],
    "season_title": "ปี 2017",
    "yt_playlist_url":  "https://www.youtube.com/playlist?list=PLNI0sbc9hw9xeP7WCe3j-jXCGZWT1cmbX",
    "published_year": "2560"
}

tvshow_json = {
    "title": "Kids Stronger ภารกิจเด็กแกร่ง",
    "keywords": ["WorkpointOfficial"],
    "reverse_loop": 1,
    "state": 1,
    "description": "Kids Stronger ‘ภารกิจเด็กแกร่ง’ เป็นรายการนอกกระแสที่เปิดพื้นที่ให้เหล่านักกีฬาน้อย จากพื้นที่ห่างไกลได้โชว์ความสามารถ ความฝัน และความตั้งใจที่มีมากไม่แพ้ใคร เป็นโอกาสที่เปิดมาเพื่อเด็กที่มีทักษะด้านการกีฬาให้มาปะลองกัน ซึ่งการแข่งขันนี้ไม่ได้แข่งกับใคร แต่เป็นการแข่งกับตัวเองและเวลาเป็นสำคัญ",
    "genres": ["รายการไทย", "กีฬา"],
    "actors": ["ฑิฆัมพร ฤทธาอภินันท์", "วรชาติ ธรรมวิจินต์"],
    "studio": ["WorkpointOfficial"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url":  "https://www.youtube.com/playlist?list=PLcwQy6DvJjszEXiv4LWDUU-o_dJNmDTP1",
    "published_year": "2561"
}

tvshow_json = {
    "title": "BNK48 SENPAI",
    "keywords": ["BNK48"],
    "reverse_loop": 0,
    "state": 1,
    "description": "รายการนี้เป็นรายการเรียลลิตี้ที่ตามติดชีวิตของสมาชิกในวงแต่ละคนตั้งแต่เริ่มออดิชั่นในรอบสัมภาษณ์ที่คณะกรรมการจะได้เห็นผู้สมัครกันเลยทีเดียว แต่รายการนี้ก็ไม่ได้จบที่งานประกาศผลว่าใครจะได้อยู่วง พวกเขายังมีการถ่ายทำแบบตามติดชิวิตของเหล่าสมาชิกของแต่ละคนแบบตั้งแต่กิจกรรมแรก จนถึงกิจกรรมสุดท้ายที่เหล่าสมาชิกวงทำในชีวิตประจำวันอีกด้วย",
    "genres": ["รายการไทย", "เรียลลิตี้", "ไอดอล"],
    "actors": [],
    "studio": ["BNK48", "WorkpointOfficial"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url":  "https://www.youtube.com/playlist?list=PLPW9IgM1jwdt95rKARywBxtFxRjMH8JzI",
    "published_year": "2561"
}

tvshow_json = {
    "title": "CGM48 SENPAI",
    "keywords": ["CGM48"],
    "reverse_loop": False,
    "state": False,
    "description": "รายการ Senpai รายการเรียลลิตี้ที่จะทำให้แฟนคลับ หรือผู้ที่ติดตามดูรู้ว่ากว่าจะเป็นวง CGM48 ขึ้นมาได้ต้องผ่านอะไรมาบ้าง เริ่มแรกสมาชิกแต่ละคนเป็นอย่างไร ตอนออดิชั่นเป็นอย่างไร ตอนฝึกซ้อมพัฒนาขึ้นอย่างไรบ้าง พวกเธอต้องผ่านอะไรมาบ้าง และที่สำคัญคุณจะได้รู้ว่าสมาชิกวงชาวเหนือวงนี้จะมีวิถีเป็นอย่างไรบ้าง",
    "genres": ["รายการไทย", "ไอดอล", "เรียลลิตี้"],
    "actors": [],
    "studio": ["CGM48"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url":  "https://www.youtube.com/playlist?list=PL8aEdSGJXUmnGmJM64VILncCw69kXEy_u",
    "published_year": "2563"
}

tvshow_json = {
    "title": "VICTORY BNK48",
    "keywords": ["WorkpointOfficial"],
    "reverse_loop": 1,
    "state": 1,
    "description": "เป็นการแข่งขันโดยแบ่งทีมเป็น 2 ฝ่าย คือทีม Victory Red และทีม Victory Blue โดยแต่ละทีมจะประกอบด้วยสมาชิกจากวง BNK48 ประมาณ 5-6 คน ซึ่งจะสลับเปลี่ยนหมุนเวียนมาร่วมแข่งขันกันในแต่ละสัปดาห์ โดยในช่วงแรกของรายการจะมีการเปิดตัวไอคอนหรือดารารับเชิญของรายการหลังจากนั้นช่วงต่อมาก็จะเข้าสู่ช่วงเกมการแข่งขันต่าง ๆ ซึ่งจะแข่งขันอยู่ 2-3 เกม โดยแต่ละเกมจะเป็นไปตามที่รายการและไอคอนประจำสัปดาห์กำหนดให้",
    "genres": ["รายการไทย", "วาไรตี้"],
    "actors": ["ปราโมทย์ ปาทาน", "ภาคภูมิ จงมั่นวัฒนา", "วรชาติ ธรรมวิจินต์"],
    "studio": ["WorkpointOfficial"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url":  "https://www.youtube.com/playlist?list=PLcwQy6DvJjswZOwrEQeBENMD9a09p-_9I",
    "published_year": "2561"
}

tvshow_json = {
    "title": "THE SHOW ศึกชิงเวที",
    "keywords": ["WorkpointOfficial"],
    "reverse_loop": 1,
    "state": 1,
    "description": "The Show ศึกชิงเวที เป็นรายการโทรทัศน์ประเภทเรียลลิตี้เกมโชว์ รายการนี้เป็นรายการที่แบ่งออกเป็นทีมหญิงและทีมชาย โดยมีกัปตันและผู้ช่วย กติกาคือ แต่ละทีมจะเอาศิลปินมาแสดงโชว์ชนกันคู่ต่อคู่ การให้คะแนนจะเกิดจากการให้คะแนนของกรรมการ และทีมไหนที่ทำคะแนนได้ 15 คะแนนก่อนก็จะได้ถ้วยรางวัลไป",
    "genres": ["รายการไทย", "ดนตรี-เพลง", "เรียลลิตี้", "เกมโชว์"],
    "actors": ["ยุทธนา บุญอ้อม", "รสสุคนธ์ กองเกตุ", "พรชิตา ณ สงขลา", "นิติพงษ์ ห่อนาค", "อภิวัชร์ เอื้อถาวรสุข", "ศิริพร อยู่ยอด", "ปราโมทย์ ปาทาน", "นลิน โฮเลอร์"],
    "studio": ["WorkpointOfficial"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url":  "https://www.youtube.com/playlist?list=PLcwQy6DvJjswEeV5VRv_aaHGGvXjhc_Tb",
    "published_year": "2561"
}

tvshow_json = {
    "title": "หัวหน้าห้าขวบ",
    "keywords": ["WorkpointOfficial"],
    "reverse_loop": 0,
    "state": 1,
    "description": "หัวหน้าห้าขวบ เป็นรายการโทรทัศน์ประเภทเกมโชว์ที่ให้เด็กหรือเยาวชน รับบทบาทในฐานะหัวหน้าที่จะต้องปฏิบัติภารกิจออกคำสั่งหรือแสดงความสามารถทางด้านต่าง ๆ เพื่อให้ฝ่ายผู้ใหญ่หรือลูกน้องที่ตนได้เลือกไว้ต้องร่วมปฏิบัติภารกิจให้สำเร็จ",
    "genres": ["รายการไทย", "เกมโชว์", "วาไรตี้"],
    "actors": ["ศิวัฒน์ โชติชัยชรินทร์", "เจริญพร อ่อนละม้าย", "ณัฐพงษ์ แตงเกษม", "ดนู ชุตินาวี", "สุดารัตน์ บุตรพรม"],
    "studio": ["WorkpointOfficial"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url":  "https://www.youtube.com/playlist?list=PLcwQy6DvJjswDTzUUC01DRrXflFK2QNsD",
    "published_year": "2561"
}


tvshow_json = {
    "title": "นักร้องสองไมค์",
    "keywords": ["WorkpointOfficial"],
    "reverse_loop": 1,
    "state": 1,
    "description": "นักร้องสองไมค์ เป็นรายการประกวดร้องเพลง ที่เปิดโอกาสให้บุคคลไม่จำกัดเพศและอายุ การศึกษา และอาชีพ เข้ามาร่วมร้องเพลงกับศิลปินชื่อดังของประเทศในทุก ๆ แนวเพลง",
    "genres": ["รายการไทย", "ดนตรี-เพลง", "เรียลลิตี้"],
    "actors": ["ศิวัฒน์ โชติชัยชรินทร์", "จักรวาร เสาธงยุติธรรม"],
    "studio": ["WorkpointOfficial"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url":  "https://www.youtube.com/playlist?list=PLcwQy6DvJjsw_bID7rxgveELie8DFSdZn",
    "published_year": "2561"
    }

tvshow_json = {
    "title": "THE MASK PROJECT A",
    "keywords": ["WorkpointOfficial"],
    "reverse_loop": 1,
    "state": 1,
    "description": "The Mask Project A รายการโทรทัศน์ประเภทเรียลลิตีโชว์มิวสิกโชว์และเป็นฤดูกาลพิเศษของรายการ The Mask Singer หน้ากากนักร้อง แข่งขันร้องเพลงโดยปกปิดตัวตนด้วยชุดและหน้ากาก ซึ่งคณะกรรมการจะพยายามทายว่าหน้ากากนั้นคือใคร",
    "genres": ["รายการไทย", "เรียลลิตี้", "เกมโชว์", "ดนตรี-เพลง"],
    "actors": ["กันต์ กันตถาวร", "มณีนุช เสมรสุต", "จักรวาล เสาธงยุติธรรม", "ศักดิ์สิทธิ์ เวชสุภาพร", "เกียรติศักดิ์ อุดมนาค", "ธนวัฒน์ ประสิทธิสมพร", "ศิริพร อยู่ยอด", "อภิษฎา เครือคงคา", "ยุทธนา บุญอ้อม", "ณัฐวุฒิ ศรีหมอก", "ศรัณยู วินัยพานิช", "นลิน โฮเลอร์", "ณปภา ตันตระกูล", "ธนกฤต พานิชวิทย์", "วิชญาณี เปียกลิ่น", "อภิวัชร์ เอื้อถาวรสุข", "สุนารี ราชสีมา", "ธนิดา ธรรมวิมล", "ปองกูล สืบซึ้ง", "ปราโมทย์ ปาทาน"],
    "studio": ["WorkpointOfficial"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url":  "https://www.youtube.com/playlist?list=PLcwQy6DvJjszIVs2_g8ws_ekaJc4K34Py",
    "published_year": "2561"
}

tvshow_json = {
    "title": "ชิงช้าสวรรค์",
    "keywords": ["WorkpointOfficial"],
    "reverse_loop": 1,
    "state": 0,
    "description": "‘ชิงช้าสวรรค์’ รายการประกวดวงดนตรีลูกทุ่งเยาวชนชิงแชมป์ประเทศไทยที่ยิ่งใหญ่ละยาวนานที่สุดของวงการโทรทัศน์ไทยมาถึง 17 ปี สมการรอคอยอย่างแน่นอนสำหรับการกลับมาอย่างยิ่งใหญ่ของรายการประกวดวงดนตรีลูกทุ่งเยาวชนที่อยู่คู่คนไทยมายาวนาน",
    "genres": ["รายการไทย", "ดนตรี-เพลง", "เรียลลิตี้"],
    "actors": ["สลา คุณวุฒิ", "ชุติเดช ทองอยู่", "จักรวาร เสาธงยุติธรรม"],
    "studio": ["WorkpointOfficial"],
    "season_title": "ปี 2022",
    "yt_playlist_url":  "https://www.youtube.com/playlist?list=PLcwQy6DvJjswXbWtGKDVb-oFNLRZJZ9L5",
    "published_year": "2565"
}

tvshow_json = {
    "title": "The Mask Singer หน้ากากนักร้อง",
    "keywords": ["WorkpointOfficial"],
    "reverse_loop": 1,
    "state": 1,
    "description": "หน้ากากนักร้อง เป็นรายการโทรทัศน์ประเภทเรียลลิตี้เกมโชว์และมิวสิกโชว์ เป็นรายการที่ถูกนำไปผลิตในหลายๆประเทศ จนกลายเป็นรูปแบบรายการระดับโลกไปแล้ว สำหรับรายการประกวดร้องเพลงของคนดัง ที่ถูกซ่อนไว้ภายใต้หน้ากาก",
    "genres": ["รายการไทย", "เรียลลิตี้", "ดนตรี-เพลง"],
    "actors": ["กันต์ กันตถาวร"],
    "studio": ["WorkpointOfficial"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url":  "https://www.youtube.com/playlist?list=PLcwQy6DvJjsyXGUUW4Knd1ZKk7wHTVM6A",
    "published_year": "2560"
}

tvshow_json = {
    "title": "Diva Makeover เสียงเปลี่ยนสวย",
    "keywords": ["WorkpointOfficial"],
    "reverse_loop": 1,
    "state": 1,
    "description": "“Diva Makeover เสียงเปลี่ยนสวย” ฉีกทุกกฎของรายการประกวดร้องเพลงที่ไม่ต้องพึงหน้าตาอีกต่อไป!!! ขอแค่ “เสียงสวย” เราจะเปลี่ยน “คุณ” ให้สวยตั้งแต่หัวจรดเท้า เฉิดฉายเป็น DIVA คนใหม่ของเมืองไทยบนเวทีแห่งนี้ และมีคอนเสิร์ตเป็นของตัวเอง!!!",
    "genres": ["รายการไทย", "ดนตรี-เพลง", "เรียลลิตี้"],
    "actors": ["กันต์ กันตถาวร"],
    "studio": ["WorkpointOfficial"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url":  "https://www.youtube.com/playlist?list=PLcwQy6DvJjsxfiqRMtBXzKwc67zw3CQwn",
    "published_year": "2561"
}

tvshow_json = {
    "title": "DIVA MAKEOVER เสียงเปลี่ยนสวย",
    "keywords": ["WorkpointOfficial"],
    "reverse_loop": 1,
    "state": 1,
    "description": "รายการ “DIVA MAKEOVER เสียงเปลี่ยนสวย” เมื่อรูปร่างหน้าตาไม่เป็นผล แข่งขันโชว์พลังเสียงระดับดีว่าอย่างเดียว ใครเป็นผู้ชนะจะได้เดินทางไปเมคโอเวอร์โดยทีมแพทย์ แถวหน้าของประเทศเกาหลีใต้ พร้อมกลับมาทำให้สวย หัวจรดเท้ากับทีมเมคโอเวอร์ระดับโลก",
    "genres": ["รายการไทย", "ดนตรี-เพลง", "เรียลลิตี้"],
    "actors": ["กันต์ กันตถาวร"],
    "studio": ["WorkpointOfficial"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url":  "https://www.youtube.com/playlist?list=PLcwQy6DvJjsxfiqRMtBXzKwc67zw3CQwn",
    "published_year": "2561"
}

tvshow_json = {
    "title": "Show Me Your Son ลูกแม่หล่อมาก",
    "keywords": ["WorkpointOfficial"],
    "reverse_loop": 1,
    "state": 1,
    "description": "Show Me Your Son ลูกแม่หล่อมาก รายการโทรทัศน์ของไทยประเภทเกมโชว์ซึ่งซื้อลิขสิทธิ์มาจากประเทศเกาหลีใต้ เพื่อเสริมสร้างความเข้าใจกันระหว่างแม่สามีและลูกสะใภ้และลดปัญหาความบาดหมางของทั้งสอง",
    "genres": ["รายการไทย", "วาไรตี้", "เกมโชว์"],
    "actors": ["ธนกฤต พานิชวิทย์", "อภิษฎา เครือคงคา"],
    "studio": ["WorkpointOfficial"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url":  "https://www.youtube.com/playlist?list=PLcwQy6DvJjswK6i7YU2farPIAVq7FNn3B",
    "published_year": "2561"
}

tvshow_json = {
    "title": "Tabi Japan with James Jirayu",
    "keywords": ["Ch3Thailand"],
    "reverse_loop": 0,
    "state": 1,
    "description": "รายการ “Tabi Japan With James Jirayu” โดยเจมส์ จิรายุ จะเป็นผู้ดำเนินรายการ ซึ่งเป็นรายการท่องเที่ยวรูปแบบใหม่ ที่จะทำให้คุณผู้ชมเห็นทิวทัศน์ที่สวยงามอย่างที่ไม่เคยเห็นมาก่อน จาก 6 จังหวัด ในภาคตะวันออกเฉียงเหนือ ของประเทศญี่ปุ่น และยังได้ชมฝีมือการถ่ายภาพจากหนุ่มเจมส์อีกด้วย",
    "genres": ["รายการไทย", "ท่องเที่ยว"],
    "actors": ["จิรายุ ตั้งศรีสุข"],
    "studio": ["Ch3Thailand"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url":  "https://www.youtube.com/playlist?list=PL0VVVtBqsouomPZsg5E1NOIxy0K6fMznP",
    "published_year": "2559"
}

tvshow_json = {
    "title": "BEAUTY NO.9",
    "keywords": ["WorkpointOfficial"],
    "reverse_loop": 1,
    "state": 1,
    "description": "ไม่ต้องพึ่งการศัลยกรรม คุณก็สามารถสวยและดูดีในแบบฉบับสาวเกาหลี เพียงแค่รับชมรายการจากช่องเวิร์คพอยท์ รายการ “Beauty No.9” (บิวตี้ นัมเบอร์ ไนน์) ที่จะมาเสกและเสิร์ฟความสวยให้กับสาวไทย",
    "genres": ["รายการไทย", "แฟชั่น"],
    "actors": ["แพรเพชร อุดมศาสตร์พร", "เอสเธอร์ สุปรีย์ลีลา", "อีทึก", "ปาร์ค แทยุน"],
    "studio": ["WorkpointOfficial"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url":  "https://www.youtube.com/playlist?list=PLcwQy6DvJjsxv5mtBFapepw-tE3hMTm5R",
    "published_year": "2562"
}

tvshow_json = {
    "title": "Art Of Luxury กูรูมีสไตล์",
    "keywords": ["WorkpointOfficial"],
    "reverse_loop": 1,
    "state": 1,
    "description": "Art Of Luxury กูรูมีสไตล์ รายการที่จะพาคนดูไปสัมผัสอีกระดับ และความหรูหราที่ไม่ควรพลาด โดยรายการจะพาคนดูได้สัมผัสถึงสิ่งของที่ดูสวยงามหรูหราของเหล่าคนรวยที่คุณต้องน้ำลายยืด พร้อมทั้งการบรรยายถึงความรวยเหล่านั้นว่ามันมีสไตล์มากขนาดไหน",
    "genres": ["รายการไทย", "ศิลปะ", "เล่าเรื่อง"],
    "actors": ["นนทพร ธีระวัฒนสุข", "ธนนท์ พงศ์ธนา"],
    "studio": ["WorkpointOfficial"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url":  "https://www.youtube.com/playlist?list=PLcwQy6DvJjsyCMol5DVUn-SiCdWcHOziQ",
    "published_year": "2560"
}

tvshow_json = {
    "title": "Amazing Trip Battle เกมแข่งเที่ยว",
    "keywords": ["WorkpointOfficial"],
    "reverse_loop": 0,
    "state": 1,
    "description": "ททท. ได้ใช้กลยุทธ์ Local Tourism ส่งเสริมการท่องเที่ยวในชุมชน ด้วยการสร้างสรรค์รายการวาไรตี้เกมส์โชว์ “เกมแข่งเที่ยว Amazing Trip Battle” เพื่อเปิดมุมมองที่น่าสนใจของการท่องเที่ยวในชุมชน ภายใต้แนวคิด “ท่องเที่ยว วิถีไทย เก๋ไก๋ สไตล์ลึกซึ้ง”",
    "genres": ["รายการไทย", "ท่องเที่ยว", "วาไรตี้", "เกมโชว์"],
    "actors": ["สมเกียรติ จันทร์พราหมณ์", "อนุสรณ์ มณีเทศ", "ธัณย์สิตา สุวัชราธนากิตติ์", "พงษ์พิสุทธิ์ ผิวอ่อน", "จันจิรา จันทร์พิทักษ์ชัย", "ภัทรนันท์ ดีรัศมี", "เชษฐวุฒิ วัชรคุณ", "เอนก อินทะจันทร์", "ภัณฑิลา ฟูกลิ่น", "ศิรภัสรา สินตระการผล", "ภานุพันธ์ ครุฑโต"],
    "studio": ["WorkpointOfficial"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url":  "https://www.youtube.com/playlist?list=PLcwQy6DvJjswq6n2PgGSgQEpiLJqRFHwo",
    "published_year": "2560"
}

tvshow_json = {
    "title": "อีจันสืบสยอง",
    "keywords": ["WorkpointOfficial"],
    "reverse_loop": 1,
    "state": 1,
    "description": "“อีจัน สืบสยอง” เอาใจคุณผู้ชมพาสืบค้นคดีเด็ด เจาะลึกคดีใหญ่ โดย 2 พิธีกร ลูกตาล ทิพย์รัตน์ อมาตยกุล และ แจนโล่ ธนภัทร ศุภวรรณาวิวัฒน์ จะพาไปหาสาเหตุจูงใจของคดีอาชญกรรมหลายคดี ว่าแท้จริงแล้ว ฆ่าตัวตาย หรือ ฆาตกรรม ?",
    "genres": ["รายการไทย", "เล่าเรื่อง"],
    "actors": ["ทิพย์รัตน์ อมาตยกุล", "ธนภัทร ศุภวรรณาวิวัฒน์"],
    "studio": ["WorkpointOfficial"],
    "season_title": "ปี 2561",
    "yt_playlist_url":  "https://www.youtube.com/playlist?list=PLK_A87FDG6rS-NAUc4Zn-d5pzCwXWHPE-",
    "published_year": "2561"
}

tvshow_json = {
    "title": "คืนศุกร์ลุกซู่",
    "keywords": ["คืนพุธ มุดผ้าห่ม [ Official ]"],
    "reverse_loop": 0,
    "state": 0,
    "description": "“คืนศุกร์ขนลุกซู่” รายการนำเสนอเรื่องราวสยองขวัญที่มาจากประเทศญี่ปุ่นเป็นส่วนใหญ่โดยไม่จำกัดประเภท มีทั้งเรื่องผี ปีศาจ หรือเรื่องราวแปลกประหลาดที่ได้จากมนุษย์ปุถุชนธรรมดาแต่มีความไม่ธรรมดาในสไตล์ญี่ปุ่น ",
    "genres": ["รายการไทย", "สยองขวัญ", "เล่าเรื่อง", "ยอดนิยม"],
    "actors": ["มิ่งบุญ ฮาตะ"],
    "studio": ["RUBSARB production"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url":  "https://www.youtube.com/playlist?list=PLWCAXUIOVLThA4jPrj5qOo12esNQLdpKV",
    "published_year": "2565"
}

tvshow_json = {
    "title": "The Unicorn สตาร์ทอัพ พันล้าน",
    "keywords": ["WorkpointOfficial"],
    "reverse_loop": 0,
    "state": 1,
    "description": "The Unicorn สตาร์ทอัพ พันล้าน เป็นรายการเกมโชว์ที่ต่อยอดความสำเร็จจาก SME ตีแตก ที่ช่วยสร้างแรงบันดาลใจและปลุกกระแสการนำเทคโนโลยีมาใช้ทั้งในชีวิตส่วนตัว และธุรกิจ เพื่อชิงความเป็นสุดยอดเทคสตาร์ทอัพ",
    "genres": ["รายการไทย", "เกมโชว์", "แวดวงธุรกิจ"],
    "actors": ["เกตุเสพย์สวัสดิ์ ปาลกะวงศ์ ณ อยุธยา"],
    "studio": ["WorkpointOfficial"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url":  "https://www.youtube.com/playlist?list=PLcwQy6DvJjsxl9BgsfgikyfTK_BDMU3YT",
    "published_year": "2565"
}

tvshow_json = {
    "title": "Bao Young Blood ดนตรีสร้างคุณค่าชีวิต",
    "keywords": ["WorkpointOfficial"],
    "reverse_loop": 0,
    "state": 1,
    "description": "Bao Young Blood ดนตรีสร้างคุณค่าชีวิต เป็นรายการประกวดวงดนตรีระดับเยาวชนที่ใช้เฉพาะเพลงของวงคาราบาวเท่านั้นในการประกวด และนำมาเรียบเรียงใหม่ตามรูปแบบเพลงของแต่ละวง เพื่อส่งเสริมให้เยาวชนได้ใช้เวลาว่างให้เกิดประโยชน์ ตามเจตนารมณ์เดิมของโครงการดนตรีสร้างคุณค่าชีวิต โดย มูลนิธิคาราบาว",
    "genres": ["รายการไทบ", "ดนตรี-เพลง", "เรียลลิตี้"],
    "actors": ["ปิยะวัฒน์ เข็มเพชร", "กันต์ กันตถาวร", "เกตุเสพย์สวัสดิ์ ปาลกะวงศ์ ณ อยุธยา", "กีรติ พรหมสาขา ณ สกลนคร", "จิรศักดิ์ ปานพุ่ม", "พลพล พลกองเส็ง", "มณีนุช เสมรสุต", "จักรวาล เสาธงยุติธรรม", "จิรากร สมพิทักษ์"],
    "studio": ["WorkpointOfficial"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url":  "https://www.youtube.com/playlist?list=PLWgE8IgC7ANl5Bq8haBRHxXvG47TK7Y6n",
    "published_year": "2558"
}

tvshow_json = {
    "title": "ตะลุยตลาดสด",
    "keywords": ["WorkpointOfficial"],
    "reverse_loop": 1,
    "state": 1,
    "description": "รายการวาไรตี้ ตะลุยตลาดสด ที่หยิบยกเรื่องราวต่างๆที่เกี่ยวข้องกับการค้าขาย และเรื่องใกล้ตัว มานำเสนอในรูปแบบเป็นกันเองผ่านพิธีกรอารมณ์ดี แนะนำที่เที่ยว ที่กินยอดฮิตชื่อดัง พร้อมทั้งพิธีกรชื่อดังอย่าง พี่อี๊ด โปงลางสะออน และ พี่ส้มเช้ง สามช่า เข้ามามอบความสุขและความสนุกให้พี่น้องชาวตลาด",
    "genres": ["รีวิว", "รายการไทย", "วาไรตี้", "ท่องเที่ยว"],
    "actors": ["สมพงษ์ คุนาประถม", "บุญญาวัลย์ พงษ์สุวรรณ"],
    "studio": ["WorkpointOfficial"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url":  "https://www.youtube.com/playlist?list=PLcwQy6DvJjsxdP8O6pIFdIGB3t9ggvUt5",
    "published_year": "2559"
}

tvshow_json = {
    "title": "𝗜 𝗞𝗔𝗡 𝗧𝗘𝗔𝗖𝗛𝗔",
    "keywords": ["Ticha Kanticha"],
    "reverse_loop": 0,
    "state": 0,
    "description": "มันคือความชอบ! ติช่า กันติชา เปิดรายการเพศศึกษา หวังให้ความรู้-วิธีป้องกัน ลั่นผู้หญิงพูดเรื่องเซ็กซ์ได้ ไม่ใช่สิ่งน่าอาย ดีใจยังไม่เจอดราม่า เม้าธ์มอยเกี่ยวกับเรื่องเพศศึกษา มุ่งเน้นให้ความรู้และวิธีป้องกันอย่างถูกต้อง",
    "genres": ["รายการไทย", "วาไรตี้", "โรแมนติก"],
    "actors": ["กันติชา ชุมมะ"],
    "studio": ["Ticha Kanticha"],
    "season_title": "ซีซั่น 1",
    "yt_playlist_url":  "https://www.youtube.com/playlist?list=PLs12_b9cOtEhC4a0MOXjbFB_EdyJvl1Gu",
    "published_year": "2564"
}

# print(id_generator())
# deleteAll(Season, 1523511715, "Season")
# deleteAll(Movie, 539, "Movie")
# deleteAll(Series, 240, "Series")
# deleteAll(Tvshow, 135, "Tvshow")
# deleteSeason(Tvshow, 3, 474)
# deleteSeason(96904653095)
# deleteEpisodeFromYTURL("smiLU_vzRao")
# removeSeason(Tvshow, 107, 1523511715)
# removeSeason(Series, 3, 474)
# removeSeason(Series, 3, 475)
#

#db.session.commit()
# initialMovie(["พระนครฟิล์ม"])
# initialMovieV2(movie_json)
# initialSeries(series_json)
# initialTvshow(tvshow_json)

#
# deleteGenre(Series, 108, "ประวัติศาสตร์")
# deleteCast(Movie, 548, "")
# deleteDirector(Movie, 95, " สมเกียรติ์ วิทุรานิช")
# deleteForever(Genre, 149)
# addGenre(Movie, 608, "หนังไทย")
# addGenre(Movie, 485, "หนังสั้น")
# addGenre(Movie, 615, "ซับไทย")
# addGenre(Series, 40, "อนิเมะ")
# addGenre(Series, 30, "เด็ก")
# addGenre(Movie, 28, "หนังญี่ปุ่น")
# addGenre(Series, 231, "ญี่ปุ่น")
# addGenre(Series, 190, "พากย์ไทย")
# addGenre(Movie, 147, "ดราม่า")
# addGenre(Movie, 61, "หนังลาว")
# addGenre(Movie, 3, "หนังจีน")
# addGenre(Movie, 141, "ย้อนยุค")
# addGenre(Movie, 147, "ประวัติศาสตร์")
# addGenre(Movie, 590, "สร้างจากเรื่องจริง")
# addGenre(Movie, 139, "มิวสิคัล")
# addGenre(Movie, 83, "วาย")
# addGenre(Series, 61, "วัยรุ่น")
# addGenre(Series, 118, "ดราม่า")
# addGenre(Movie, 35, "ไซไฟ")
# addGenre(Movie, 35, "ลึกลับ")
# addGenre(Series, 3, "ผจญภัย")
# addGenre(Series, 3, "แฟนตาซี")
# addGenre(Movie, 27, "หนังฝรั่ง")
# addGenre(Series, 118, "แอ็คชั่น")
# addGenre(Series, 3, "คอมเมดี้")
# addGenre(Movie, 330, "ระทึกขวัญ")
# addGenre(Series, 108, "ดราม่า")
# addGenre(Movie, 289, "เพลง")
# addGenre(Movie, 97, "ดนตรี")
# addGenre(Series, 108, "ซีรี่ส์จีน")
# # addGenre(Movie, 502, "สยองขวัญ")
# addGenre(Tvshow, 13, "รีวิว")
# addGenre(Tvshow, 13, "กล่องสุ่ม")
# # # addGenre(Movie, 26, "ดราม่า")
# addGenre(Movie, 105, "โรแมนติก")
# addGenre(Tvshow, 33, "ท่องเที่ยว")
# addGenre(Tvshow, 114, "สารคดี")
# addGenre(Series, 32, "อนิเมะ")
# addGenre(Series, 196, "คลาสสิค")
# addGenre(Tvshow, 77, "อาหาร")

# changeSeasonName(187, "ซีซั่น 1")
# changeSeasonName(191, "ซีซั่น 1")
# changeSeasonName(192, "ซีซั่น 2")
# changeSeasonName(193, "ซีซั่น 3")
# changeState(Series, 32, True)
#
# changeStudio(Tvshow, 4, ["ทัวร์ตัวแตก Food Fanatic"])
# changeStudio(Series, 2, ["MCOT"])
# changeStudio(Series, 32, ["Muse Thailand"])
# changeStudio(Series, 63, ["Mr Bean"])
# changeStudio(Series, 1, ["GDH"])
# changeStudio(Tvshow, 29, ["TubTimTube"])
# changeStudio(Tvshow, 17, ["VRZO"])
# changeStudio(Tvshow, 33, ["RUBSARB production"])
# changeStudio(Movie, 335, ["พระนครฟิล์ม"])
# changeStudio(Movie, 564, ["พระนครฟิล์ม", "Right Comedy"])
# changeStudio(Movie, 330, ["พระนครฟิล์ม", "อาร์เอสฟิล์ม"])
# changeStudio(Movie, 28, ["พระนครฟิล์ม", "NBC Universal Japan", "Kadokawa"])
# changeStudio(Movie, 93, ["พระนครฟิล์ม", "M-Thirtynine"])
# changeStudio(Movie, 336, ["พระนครฟิล์ม", "ห้า สี่ สาม สอง แอ็คชั่น ฟิล์ม"])
# changeStudio(Movie, 72, ["พระนครฟิล์ม" ,"Golden A Entertainment"])
# changeStudio(Movie, 123, ["พระนครฟิล์ม" ,"ซี.เอ็ม.ฟิล์ม"])
# changeStudio(Movie, 109, ["พระนครฟิล์ม" ,"เอ.จี.เอ็นเตอร์เทนเม้นท์"])
# changeStudio(Movie, 35, ["พระนครฟิล์ม", "แอพพลาย กรุ๊ป"])
# changeStudioName("Muse", "Muse Thailand")
# changeDescription(Movie, 568, 'คุณชายเป็นลูกผู้ร่ำรวยกิจกาค้ามากมายถูกตามใจตั่งแต่เด็กไม่ว่าจะอาบน้ำหรือ ทานข้าวจะมีคนทำให้ตลอดเวลา จนทนไม่ไหวอยากเป็นอิสระจึงหนีออกจากบ้านเหลือเพียง กางเกงในตัวเดียวโซซัดโซเซไปเจอบ้านๆหนึ่งที่เก็บขยะขาย หนุ่มคนนั้นชื่อเอ๋ เป็นคนดีแต่มีความลับแอบแฝงเอาไว้ได้ช่วยคุณชายให้มาอยู่ที่บ้าน และได้พบรักกับ น้องต่าย ซึ่งอยู่กับเพื่อนที่ร้านทำผมแห่งหนึ่ง แต่ความรักของเขามีอุปศักดิ ถึงแม้นคุณชาย จะไม่บอกว่าตัวเองเป็นลูกเศรษฐี เพื่อจะดูใจน้องต่าย เถ้าแก่ใหญ่รู้ว่าลูกชายหายก็ให้คน ติดตามจนมาพบ คุณชายจึงจะพากลับบ้านเพื่อให้แต่งงานกับลูกสาวของเพื่อนซึ่งเป็นคนมีเงิน เช่นกัน อะไรจะเกิดขึ้นกับคุณชายโซ เขาจะแก้ปัญหาเรื่องความรักได้ให้ติดตามชม')
# # # # # # # #
# addNewDirector(Movie, 526, "อุบล ยุคล ณ อยุธยา")
# addNewCast(Movie, 595, "ปิติศักดิ์ เยาวนานนท์")
# addNewCast(Movie, 526, "มิสจิ้นหลู")
# addNewCast(Movie, 526, "แมน ธีระพล")
# addNewCast(Movie, 526, "รุจน์ รณภพ")
# addNewCast(Movie, 526, "สมควร กระจ่างศาสตร์")
# addNewCast(Movie, 526, "อรสา อิศรางกูร ณ อยุธยา")
# addNewCast(Movie, 526, "สิงห์ มิลินทราศรัย")
# addNewCast(Movie, 526, "สมพล กงสุวรรณ")
# addNewCast(Movie, 526, "สุวิน สว่างรัตน์")
# addNewCast(Movie, 526, "อดินันท์ สิงห์หิรัญ")
# addNewCast(Movie, 485, "พิจักขณา วงศารัตนศิลป์")
# addNewCast(Tvshow, 95, "กพล ทองพลับ")
# addNewCast(Movie, 335, "ซูซานน่า เรโนล")
# addNewCast(Movie, 335, "เดวิด อัศวนนท์")
# addNewCast(Movie, 335, "เปรมอนันต์ ศรีพานิช")
# changePublishedYearMovie(557, 2562)
# changeRuntime(Movie, 588, 49)
# changeThumbnail(Movie, 571, "รองต๊ะ-แล่บแปล๊บ.jpg")

# addNewSeason(Series, 190, "Chowder Thailand (ชาวเดอร์ พากย์ไทย)","ซีซั่น 1", "https://www.youtube.com/playlist?list=PLrdW5bectSC74-8HlMC_JPdbUhW6-egww", 2550, False)

# addNewSeason(Tvshow, 135, "WorkpointOfficial","ปี 2560", "https://www.youtube.com/playlist?list=PLcwQy6DvJjsyz1IXgxNmWwk5HOgAY_LAe", 2560, True)
# addNewSeason(Tvshow, 135, "WorkpointOfficial","ปี 2561", "https://www.youtube.com/playlist?list=PLcwQy6DvJjsxd5z11VOgwGPA8WGx45JxP", 2561, True)
# addNewSeason(Tvshow, 135, "WorkpointOfficial","ปี 2562", "https://www.youtube.com/playlist?list=PLcwQy6DvJjsyARmpN4o2B2IWLA2-uknMa", 2562, True)
# addNewSeason(Tvshow, 135, "WorkpointOfficial","ปี 2563", "https://www.youtube.com/playlist?list=PLcwQy6DvJjswwS3sHOc4ml9oGnZevxLkV", 2563, True)
# addNewSeason(Tvshow, 135, "WorkpointOfficial","ปี 2564", "https://www.youtube.com/playlist?list=PLcwQy6DvJjswTjDBKgo0OOZSOBz0fvTe4", 2564, True)
# addNewSeason(Tvshow, 135, "WorkpointOfficial","ปี 2565", "https://www.youtube.com/playlist?list=PLcwQy6DvJjszFbZmABYzXrrHpV1KYR_II", 2565, False)
# addNewSeason(Tvshow, 135, "WorkpointOfficial","ปี 2559", "https://www.youtube.com/playlist?list=PLcwQy6DvJjszfLFz_QyG2T3rpyo2aVUk8", 2559, True)
#
# addSeasonWithIndex(Tvshow, 38, season_json)
# addNewEpisodeWithUpdateLastUpdated(Tvshow, 69, "6g-3OXCXVJ0", 'อายุน้อยร้อยล้าน | EP.240 | KOTA Thailand', 939656)
# replaceYTPlaylistToSFPlaylistWithUpdateLastUpdated(Series, 82, "https://www.youtube.com/playlist?list=PL_PBBHM4rU_PVww1TpV7t7DqU-fBj1rev", "YOUKU Thailand", 297, False)
# insertEP(Tvshow, 128, "mmj12wWAMnU", "แม่ยกบุกตลาด | EP.6 | ตลาด เอ.ซี. ลำลูกกา คลอง 4 | 22 ก.พ. 65 | Full EP", 37804287486, 6)
# replaceYTPlaylistToSFPlaylist(Tvshow, 130, "https://www.youtube.com/playlist?list=PLs12_b9cOtEiNGhN3CY-ez0sRcjR_Iw3s", "WorkpointOfficial", 93161315834, False)
# addYTPlaylistToSFPlaylist(Tvshow, 135, "https://www.youtube.com/playlist?list=PLcwQy6DvJjsxU6LUR3s8bGuT_puuKSy9l", "WorkpointOfficial", 75138290419, True)
# deleteVdoFromEpisodes(Series, 170, 1, "jokVCK_42HA")
#changePublishedYearInSeason(Series, 10, 1, 2563)
