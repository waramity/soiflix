from flask import Blueprint, render_template, redirect, request, session, make_response, send_file, url_for, jsonify
from flask_login import login_required, current_user
from main.models import Movie, Genre, Series, Actor, Director, Tvshow, Studio, Season, Episode, Post
from main.server import db
from random import shuffle
from sqlalchemy import desc
import glob
import datetime
import os
import requests
from bs4 import BeautifulSoup

# from flask_uploads import UploadSet, configure_uploads, IMAGES
from werkzeug.utils import secure_filename
from os.path import exists
import json
import string
import random
from werkzeug.useragents import UserAgent

import time
import re


main = Blueprint('main', __name__)

genre_list_group_image_for_browser = [{'genre_image': 'ซีรี่ส์จีน', 'genre_id': 116}, {'genre_image': 'ซีรี่ส์ไทย', 'genre_id': 26}, {'genre_image': 'รายการไทย', 'genre_id': 29}, {'genre_image': 'หนังไทย', 'genre_id': 141}, {'genre_image': 'หนังจีน', 'genre_id': 100}, {'genre_image': 'ญี่ปุ่น', 'genre_id': 33}, {'genre_image': 'การ์ตูน', 'genre_id': 35}, {'genre_image': 'คลาสสิค', 'genre_id': 103}, {'genre_image': 'คอมเมดี้', 'genre_id': 14}, {'genre_image': 'ซิตคอม', 'genre_id': 88},   {'genre_image': 'ดราม่า', 'genre_id': 10}, {'genre_image': 'แอ็คชั่น', 'genre_id': 9}, {'genre_image': 'โรแมนติก', 'genre_id': 12}, {'genre_image': 'สยองขวัญ', 'genre_id': 15}, {'genre_image': 'ผจญภัย', 'genre_id': 11},{'genre_image': 'แฟนตาซี', 'genre_id': 18},{'genre_image': 'ท่องเที่ยว', 'genre_id': 31}, {'genre_image': 'อาหาร', 'genre_id': 22} ]

genre_list_group = [{"genre_name": "สงคราม"}, {"genre_name": "ประวัติศาสตร์"}, {"genre_name": "แอ็คชั่น"}, {"genre_name": "ดราม่า"}, {"genre_name": "ผจญภัย"}, {"genre_name": "โรแมนติก"}, {"genre_name": "คอมเมดี้"}, {"genre_name": "สยองขวัญ"}, {"genre_name": "อาชญากรรม"}, {"genre_name": "ระทึกขวัญ"}, {"genre_name": "แฟนตาซี"}, {"genre_name": "ไซไฟ"}, {"genre_name": "ผจญภัย "}, {"genre_name": "อาหาร"}, {"genre_name": "วัยรุ่น"},  {"genre_name": "ซีรี่ส์ไทย"}, {"genre_name": "วาไรตี้"}, {"genre_name": "รายการผี"}, {"genre_name": "รายการไทย"}, {"genre_name": "บ้านและสวน"}, {"genre_name": "ท่องเที่ยว"}, {"genre_name": "ญี่ปุ่น"}, {"genre_name": "การ์ตูน"}, {"genre_name": "อนิเมะญี่ปุ่น"}, {"genre_name": "ดนตรี-เพลง"},  {"genre_name": "ลึกลับ"}, {"genre_name": "เรียลลิตี้"}, {"genre_name": "สัตว์"}, {"genre_name": "เกม"}, {"genre_name": "รีวิว"}, {"genre_name": "ASMR"}, {"genre_name": "เครื่องสำอาง"}, {"genre_name": "รายการแนะนำ"}, {"genre_name": "VLOG"}, {"genre_name": "สารคดี"},  {"genre_name": "ซิตคอม"}, {"genre_name": "พากย์ไทย"}, {"genre_name": "เกมโชว์"}, {"genre_name": "แวดวงธุรกิจ"}, {"genre_name": "หนังจีน"}, {"genre_name": "สืบสวนสอบสวน"}, {"genre_name": "คลาสสิค"}, {"genre_name": "วาย"}, {"genre_name": "ซับไทย"}, {"genre_name": "พากย์จีน"}, {"genre_name": "ซีรี่ส์จีน"}, {"genre_name": "ไลฟ์สไตล์"}, {"genre_name": "ทอล์กโชว์"}, {"genre_name": "ซีรี่ส์เกาหลี"}, {"genre_name": "ซีรี่ส์ไต้หวัน"}, {"genre_name": "หนังไทย"}, {"genre_name": "หนังฮ่องกง"}, {"genre_name": "หนังฝรั่ง"}, {"genre_name": "หนังญี่ปุ่น"}, {"genre_name": "ซีรี่ส์อินเดีย"}, {"genre_name": "ซับจีน"}]

genre_buttons = [{"genre_name": "🔥ยอดนิยม", "url": "/genre/80"}, {"genre_name": "หนัง", "url": "/movies"}, {"genre_name": "ซีรี่ส์", "url": "/series"}, {"genre_name": "รายการทีวี", "url": "/tvshows"}, {"genre_name": "การ์ตูน", "url": "/genre/35"}, {"genre_name": "ซีรี่ส์จีน", "url": "/genre/116"}, {"genre_name": "ซีรี่ส์ไทย", "url": "/genre/26"}, {"genre_name": "รายการไทย", "url": "/genre/29"}, {"genre_name": "หนังไทย", "url": "/genre/141"}, {"genre_name": "หนังจีน", "url": "/genre/100"}, {"genre_name": "ญี่ปุ่น", "url": "/genre/33"}, {"genre_name": "คลาสสิค", "url": "/genre/103"}, {"genre_name": "ซิตคอม", "url": "/genre/88"}, {"genre_name": "ท่องเที่ยว", "url": "/genre/31"}, {"genre_name": "อาหาร", "url": "/genre/22"}, {"genre_name": "คอมเมดี้", "url": "/genre/14"}, {"genre_name": "ดราม่า", "url": "/genre/10"}, {"genre_name": "โรแมนติก", "url": "/genre/12"}, {"genre_name": "สยองขวัญ", "url": "/genre/15"}, {"genre_name": "แอ็คชั่น", "url": "/genre/9"}, {"genre_name": "แฟนตาซี", "url": "/genre/18"}, {"genre_name": "ผจญภัย", "url": "genre/11"}]

jp_animes = Series.query.filter(Series.genres.any (Genre.name == "อนิเมะญี่ปุ่น")).all()
food_tvshow = Tvshow.query.filter(Tvshow.genres.any (Genre.name == "อาหาร")).all()
travel_tvshow = Tvshow.query.filter(Tvshow.genres.any (Genre.name.contains("ท่องเที่ยว"))).all()

chinese_series = Series.query.filter(Series.genres.any (Genre.name == "ซีรี่ส์จีน")).all()
thai_series = Series.query.filter(Series.genres.any (Genre.name == "ซีรี่ส์ไทย")).all()
chinese_movies = Movie.query.filter(Movie.genres.any (Genre.name == "หนังจีน")).all()
thai_movies = Movie.query.filter(Movie.genres.any (Genre.name == "หนังไทย")).all()

variety_tvshow = Tvshow.query.filter(Tvshow.genres.any (Genre.name == "วาไรตี้")).all()
thai_tvshow = Tvshow.query.filter(Tvshow.genres.any (Genre.name == "รายการไทย")).all()

new_movies = Movie.query.order_by(desc(Movie.last_updated)).all()
new_series = Series.query.order_by(desc(Series.last_updated)).all()
new_tvshow = Tvshow.query.order_by(desc(Tvshow.last_updated)).all()

action_movies = Movie.query.filter(Movie.genres.any (Genre.name == "แอ็คชั่น")).all()
comedy_movies = Movie.query.filter(Movie.genres.any (Genre.name == "คอมเมดี้")).all()
crime_movies = Movie.query.filter(Movie.genres.any (Genre.name == "อาชญากรรม")).all()
drama_movies = Movie.query.filter(Movie.genres.any (Genre.name == "ดราม่า")).all()
romance_movies = Movie.query.filter(Movie.genres.any (Genre.name == "โรแมนติก")).all()

def sub_page_content_based_on_genre(table_name, count_genre_list, count_content, continue_content_arr):

    not_same_count_genre_list = list(set(count_genre_list))
    count_genre_num = []
    count_all = 0
    mobile_tablet_vdo = []
    movies_content = []

    for genre in not_same_count_genre_list:
        if table_name.query.filter(table_name.genres.any (Genre.name == genre.name)).all() != []:
            count_genre_num.append({"genre_name": genre.name, "count_num": count_genre_list.count(genre)})
        # count_all += count_genre_list.count(genre)

    movie_genre_count = int(count_content/len(continue_content_arr) * 100)

    count_genre_num.sort(key=lambda x: x["count_num"], reverse=True)

    # print(count_genre_num)

    for genre in count_genre_num[:5]:
        count_all += genre["count_num"]


    for genre in count_genre_num[:5]:
        content = []
        content_num = int(genre["count_num"]/count_all*20)
        if content_num != 0:
            if table_name.query.filter(table_name.genres.any (Genre.name == genre["genre_name"])).all() != []:
                movies_content = table_name.query.filter(table_name.genres.any (Genre.name == genre["genre_name"])).all()
                shuffle(movies_content)
                movies_content = movies_content[:movie_genre_count * content_num]
                # print(movie_genre_count)
                content.extend(movies_content)
            shuffle(content)
            mobile_tablet_vdo.extend(content[:content_num])
            mobile_tablet_vdo = list(set(mobile_tablet_vdo))
    # if len(mobile_tablet_vdo) < 50:
    #     movies_content = table_name.query.all()
    #     shuffle(movies_content)
    #     mobile_tablet_vdo.extend(movies_content[:50-len(mobile_tablet_vdo)])
    #     mobile_tablet_vdo = list(set(mobile_tablet_vdo))
    return mobile_tablet_vdo

def set_genre_scroll_based_on_interest(count_genre_num):

    genre_list_group = count_genre_num

    genre_list_group_url = ""
    for genre in genre_list_group[:30]:
        genre_list_group_url += str(genre["genre_name"]) + "-"
    session['genre_list_group_url'] = genre_list_group_url
    print(session['genre_list_group_url'])
    return genre_list_group

def get_genre_scroll_from_cookie():
    global genre_list_group

    if session.get('genre_list_group_url'):
        genre_list_group = []
        for genre_name in session["genre_list_group_url"].split("-"):
            genre_list_group.append({"genre_name": genre_name})

    return genre_list_group
            # genre_list_group.append(Genre.query.filter_by(id=genre_id).first())

def generateGenreDescription(value):
        genre_str = ""
        genre_list = value.genres[:4]
        for genre in genre_list:
            genre_str += genre.name
            if genre != genre_list[-1]:
                genre_str += ", "
        return genre_str

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
                #     if len(sorted_last_season) > 2:
                #         second_last_episode = sorted_last_season[-2]
                #         if second_last_episode.youtube_url == str(content[3]):
                #             return "/" + content_type.lower() + "/" + str(val.id) + "/season/" + str(last_season.id) + "/episode/" + str(last_episode.youtube_url)
                #----------------------------------------------------------
                return "/" + content_type.lower() + "/" + str(content[1]) + "/season/" + str(content[2]) + "/episode/" + str(content[3])
    if val.last_updated > d_ago and val.last_updated.microsecond == 999999:
        last_season = max(val.seasons, key=lambda seasons: seasons.id)
        last_episode = max(last_season.episodes, key=lambda episodes: episodes.id)
        return "/" + content_type.lower() + "/" + str(val.id) + "/season/" + str(last_season.id) + "/episode/" + str(last_episode.youtube_url)
    if content_str == "" or content_str is None:
        return "/" + content_type.lower() + "/" + str(val.id)
    return content_str

def getLastEPTitleAndLink(obj, content_link, content_type):
    today = datetime.datetime.now()
    d_ago = datetime.timedelta(days = 5)
    d_ago = today - d_ago
    state = ""
    last_episode_title = ""

    if obj.last_updated > d_ago and obj.last_updated.microsecond == 999999:
        last_season = max(obj.seasons, key=lambda seasons: seasons.id)
        last_episode = max(last_season.episodes, key=lambda episodes: episodes.id)
        last_episode_title = last_episode.title
        content_link = content_link + "/season/" + str(last_season.id) + "/episode/" + str(last_episode.youtube_url)
        state = "NEW_EP"
        content_link = check_series_tvshow_continued_episode_cookies(obj, content_type, content_link)
    elif obj.last_updated > d_ago and obj.last_updated.microsecond != 999999:
        last_season = max(obj.seasons, key=lambda seasons: seasons.id)
        last_episode = max(last_season.episodes, key=lambda episodes: episodes.id)
        last_episode_title = last_episode.title
        content_link = content_link + "/season/" + str(last_season.id) + "/episode/" + str(last_episode.youtube_url)
        state = "NEW_CONTENT"
        content_link = check_series_tvshow_continued_episode_cookies(obj, content_type, content_link)
    else:
        first_season = min(obj.seasons, key=lambda seasons: seasons.id)
        first_episode = min(first_season.episodes, key=lambda episodes: episodes.id)
        first_episode_title = first_episode.title
        content_link = content_link + "/season/" + str(first_season.id) + "/episode/" + str(first_episode.youtube_url)
        content_link = check_series_tvshow_continued_episode_cookies(obj, content_type, content_link)

    return content_link, last_episode_title, state

def convertContentObjToJson(obj):
    thumbnail = ""
    content_link = ""
    last_episode_title = ""
    state = ""

    if hasattr(obj, 'directors') is False:
        thumbnail = "/static/tvshow/thumbnail/" + obj.thumbnail
        content_link = "/tvshow/" + str(obj.id)
        content_link, last_episode_title, state = getLastEPTitleAndLink(obj, content_link, "Tvshow")
    elif hasattr(obj, 'seasons'):
        thumbnail = "/static/series/thumbnail/" + obj.thumbnail
        content_link = "/series/" + str(obj.id)
        content_link, last_episode_title, state = getLastEPTitleAndLink(obj, content_link, "Series")
    else:
        if obj.thumbnail is not None:
            thumbnail = "/static/movies/thumbnail/" + obj.thumbnail
        else:
            thumbnail = "https://img.youtube.com/vi/" + obj.youtube_url + "/mqdefault.jpg"

        today = datetime.datetime.now()
        d_ago = datetime.timedelta(days = 5)
        d_ago = today - d_ago

        if obj.last_updated > d_ago:
            state = "NEW_CONTENT"

        content_link = "/movie/" + str(obj.id)


    # content_str = check_series_tvshow_continued_episode_cookies(value, "Tvshow", content_str)

    return {"title": obj.title, "genre-description": generateGenreDescription(obj), "thumbnail": thumbnail, "content-link": content_link, "last-episode-title": last_episode_title, "state": state}

def getNewContentList(amount):
    movies = Movie.query.order_by(desc(Movie.last_updated)).all()
    series = Series.query.order_by(desc(Series.last_updated)).all()
    tvshow = Tvshow.query.order_by(desc(Tvshow.last_updated)).all()

    new_vdo = []
    new_vdo.extend(movies)
    new_vdo.extend(series)
    new_vdo.extend(tvshow)
    new_vdo.sort(key=lambda x: x.last_updated, reverse=True)

    return new_vdo[:amount]

def get_random_continued_watching_content_for_infinite_scroll(amount):
    continue_content = request.cookies.get('continue_content')
    continue_content_arr = []
    if continue_content is not None:
        continue_content = continue_content.split(",")
        shuffle(continue_content)
        for content in continue_content[:amount]:
            content = content.split("|")
            if content[0] == "Movie" :
                content_obj = Movie.query.filter_by(id=int(content[1])).first()
                if content_obj is not None:
                    thumbnail = "/static/movies/thumbnail/" + content_obj.thumbnail
                    content_link = "/movie/" + str(content_obj.id)
                    state = ""
                    last_episode_title = ""
                    content_json = {"title": content_obj.title, "genre-description": generateGenreDescription(content_obj), "thumbnail": thumbnail, "content-link": content_link, "last-episode-title": last_episode_title, "state": state}
                    continue_content_arr.append(content_json)
            elif content[0] == "Series" :
                content_obj = Series.query.filter_by(id=int(content[1])).first()
                if content_obj is not None:
                    thumbnail = "/static/series/thumbnail/" + content_obj.thumbnail
                    content_link = "/series/" + str(content_obj.id)
                    content_link, last_episode_title, state = getLastEPTitleAndLink(content_obj, content_link, "Series")
                    content_json = {"title": content_obj.title, "genre-description": generateGenreDescription(content_obj), "thumbnail": thumbnail, "content-link": content_link, "last-episode-title": last_episode_title, "state": state}
                    continue_content_arr.append(content_json)
            elif content[0] == "Tvshow":
                content_obj = Tvshow.query.filter_by(id=int(content[1])).first()
                if content_obj is not None:
                    thumbnail = "/static/tvshow/thumbnail/" + content_obj.thumbnail
                    content_link = "/tvshow/" + str(content_obj.id)
                    content_link, last_episode_title, state = getLastEPTitleAndLink(content_obj, content_link, "Tvshow")
                    content_json = {"title": content_obj.title, "genre-description": generateGenreDescription(content_obj), "thumbnail": thumbnail, "content-link": content_link, "last-episode-title": last_episode_title, "state": state}
                    continue_content_arr.append(content_json)
    return continue_content_arr

def get_random_content_based_on_interest_genre_for_infinite_scroll(amount):
    continue_content = request.cookies.get('continue_content')
    continue_content_arr = []
    continue_content_length = 0
    count_genre_list = []
    count_content_type = {"movie": 0, "series": 0, "tvshow": 0}
    continue_content = continue_content.split(",")
    count_genre_num = []
    count_all = 0

    for content in continue_content[:45]:
        content = content.split("|")
        if content[0] == "Movie" :
            content_obj = Movie.query.filter_by(id=int(content[1])).first()
            if content_obj is not None:
                continue_content_length += 1
                count_genre_list.extend(content_obj.genres)
                count_content_type["movie"] += 1
        elif content[0] == "Series" :
            content_obj = Series.query.filter_by(id=int(content[1])).first()
            if content_obj is not None:
                continue_content_length += 1
                count_genre_list.extend(content_obj.genres)
                count_content_type["series"] += 1
        elif content[0] == "Tvshow":
            content_obj = Tvshow.query.filter_by(id=int(content[1])).first()
            if content_obj is not None:
                continue_content_length += 1
                count_genre_list.extend(content_obj.genres)
                count_content_type["tvshow"] += 1

    not_same_count_genre_list = list(set(count_genre_list))
    for genre in not_same_count_genre_list:
        count_genre_num.append({"genre_name": genre.name, "count_num": count_genre_list.count(genre)})

    count_genre_num.sort(key=lambda x: x["count_num"], reverse=True)

    movie_genre_count = int(count_content_type["movie"]/continue_content_length * 100)
    series_genre_count = int(count_content_type["series"]/continue_content_length *100)
    tvshow_genre_count = int(count_content_type["tvshow"]/continue_content_length *100)

    for genre in count_genre_num[:5]:
        count_all += genre["count_num"]

    for genre in count_genre_num[:5]:
        content = []
        content_num = int(genre["count_num"]/count_all*amount)
        if content_num != 0:
            if Movie.query.filter(Movie.genres.any (Genre.name == genre["genre_name"])).all() != []:
                movies_content = Movie.query.filter(Movie.genres.any (Genre.name == genre["genre_name"])).all()
                shuffle(movies_content)
                movies_content = movies_content[:movie_genre_count * content_num]
                content.extend(movies_content)
            if Series.query.filter(Series.genres.any (Genre.name == genre["genre_name"])).all() != []:
                series_content = Series.query.filter(Series.genres.any (Genre.name == genre["genre_name"])).all()
                shuffle(series_content)
                series_content = series_content[:series_genre_count * content_num]
                content.extend(series_content)
            if Tvshow.query.filter(Tvshow.genres.any (Genre.name == genre["genre_name"])).all() != []:
                tvshow_content = Tvshow.query.filter(Tvshow.genres.any (Genre.name == genre["genre_name"])).all()
                shuffle(tvshow_content)
                tvshow_content = tvshow_content[:tvshow_genre_count * content_num]
                content.extend(tvshow_content)

            continue_content_arr.extend(content[:content_num])
    continue_content_arr = list(set(continue_content_arr))
    content_json = []
    for content_obj in continue_content_arr:
        content_json.append(convertContentObjToJson(content_obj))
    return content_json

def get_trending_content(amount, counter):

    movies = Movie.query.filter(Movie.genres.any (Genre.name.contains("ยอดนิยม"))).all()
    series = Series.query.filter(Series.genres.any (Genre.name.contains("ยอดนิยม"))).all()
    tvshow = Tvshow.query.filter(Tvshow.genres.any (Genre.name.contains("ยอดนิยม"))).all()

    mobile_tablet_vdo = []

    mobile_tablet_vdo.extend(movies)
    mobile_tablet_vdo.extend(series)
    mobile_tablet_vdo.extend(tvshow)

    mobile_tablet_vdo.sort(key=lambda x: x.last_updated, reverse=True)

    mobile_tablet_vdo = mobile_tablet_vdo[counter*6:(counter*6)+6]
    content_json = []

    for content_obj in mobile_tablet_vdo:
        content_json.append(convertContentObjToJson(content_obj))

    return content_json

@main.route("/load-mobile-trending-content-main-page")
def load_mobile_trending_content_main_page():
    time.sleep(0.2)  # Used to simulate delay

    if request.args:
       counter = int(request.args.get("c"))  # The 'counter' value sent in the QS
       content_res = []

       content_res.extend(get_trending_content(6, counter))

       res = make_response(jsonify(content_res), 200)
       return res

def get_movie_trending_content(amount, counter):

    mobile_tablet_vdo = Movie.query.filter(Movie.genres.any (Genre.name.contains("ยอดนิยม"))).all()

    mobile_tablet_vdo.sort(key=lambda x: x.last_updated, reverse=True)

    mobile_tablet_vdo = mobile_tablet_vdo[counter*6:(counter*6)+6]
    content_json = []

    for content_obj in mobile_tablet_vdo:
        content_json.append(convertContentObjToJson(content_obj))

    return content_json

@main.route("/load-mobile-trending-content-movie-page")
def load_mobile_trending_content_movie_page():
    time.sleep(0.2)  # Used to simulate delay

    if request.args:
       counter = int(request.args.get("c"))  # The 'counter' value sent in the QS
       content_res = []

       content_res.extend(get_movie_trending_content(6, counter))

       res = make_response(jsonify(content_res), 200)
       return res

def get_series_trending_content(amount, counter):

    mobile_tablet_vdo = Series.query.filter(Series.genres.any (Genre.name.contains("ยอดนิยม"))).all()

    mobile_tablet_vdo.sort(key=lambda x: x.last_updated, reverse=True)

    mobile_tablet_vdo = mobile_tablet_vdo[counter*6:(counter*6)+6]
    content_json = []

    for content_obj in mobile_tablet_vdo:
        content_json.append(convertContentObjToJson(content_obj))

    return content_json

@main.route("/load-mobile-trending-content-series-page")
def load_mobile_trending_content_series_page():
    time.sleep(0.2)  # Used to simulate delay

    if request.args:
       counter = int(request.args.get("c"))  # The 'counter' value sent in the QS
       content_res = []

       content_res.extend(get_series_trending_content(6, counter))

       res = make_response(jsonify(content_res), 200)
       return res

def get_tvshow_trending_content(amount, counter):

    mobile_tablet_vdo = Tvshow.query.filter(Tvshow.genres.any (Genre.name.contains("ยอดนิยม"))).all()

    mobile_tablet_vdo.sort(key=lambda x: x.last_updated, reverse=True)

    mobile_tablet_vdo = mobile_tablet_vdo[counter*6:(counter*6)+6]
    content_json = []

    for content_obj in mobile_tablet_vdo:
        content_json.append(convertContentObjToJson(content_obj))

    return content_json

@main.route("/load-mobile-trending-content-tvshow-page")
def load_mobile_trending_content_tvshow_page():
    time.sleep(0.2)  # Used to simulate delay

    if request.args:
       counter = int(request.args.get("c"))  # The 'counter' value sent in the QS
       content_res = []

       content_res.extend(get_tvshow_trending_content(6, counter))

       res = make_response(jsonify(content_res), 200)
       return res

def get_new_movie_content(amount, counter):

    mobile_tablet_vdo = Movie.query.all()

    mobile_tablet_vdo.sort(key=lambda x: x.last_updated, reverse=True)

    new_content = mobile_tablet_vdo[counter*6:(counter*6)+6]

    content_json = []

    for content_obj in new_content:
        content_json.append(convertContentObjToJson(content_obj))

    return content_json

@main.route("/load-mobile-new-content-movie-page")
def load_mobile_new_content_movie_page():
    time.sleep(0.2)  # Used to simulate delay

    if request.args:
       counter = int(request.args.get("c"))  # The 'counter' value sent in the QS
       content_res = []

       content_res.extend(get_new_movie_content(6, counter))

       res = make_response(jsonify(content_res), 200)
       return res

def get_new_series_content(amount, counter):

    mobile_tablet_vdo = Series.query.all()

    mobile_tablet_vdo.sort(key=lambda x: x.last_updated, reverse=True)


    new_content = []
    for vdo in mobile_tablet_vdo:
        if vdo.last_updated.microsecond != 999999 and len(new_content) != (counter*6) + 6:
            new_content.append(vdo)

    new_content = new_content[counter*6:(counter*6)+6]

    # new_content = mobile_tablet_vdo[counter*6:(counter*6)+6]

    content_json = []

    for content_obj in new_content:
        content_json.append(convertContentObjToJson(content_obj))

    return content_json

@main.route("/load-mobile-new-content-series-page")
def load_mobile_new_content_series_page():
    time.sleep(0.2)  # Used to simulate delay

    if request.args:
       counter = int(request.args.get("c"))  # The 'counter' value sent in the QS
       content_res = []

       content_res.extend(get_new_series_content(6, counter))

       res = make_response(jsonify(content_res), 200)
       return res

def get_new_tvshow_content(amount, counter):

    mobile_tablet_vdo = Tvshow.query.all()

    mobile_tablet_vdo.sort(key=lambda x: x.last_updated, reverse=True)


    new_content = []
    for vdo in mobile_tablet_vdo:
        if vdo.last_updated.microsecond != 999999 and len(new_content) != (counter*6) + 6:
            new_content.append(vdo)

    new_content = new_content[counter*6:(counter*6)+6]

    # new_content = mobile_tablet_vdo[counter*6:(counter*6)+6]

    content_json = []

    for content_obj in new_content:
        content_json.append(convertContentObjToJson(content_obj))

    return content_json

@main.route("/load-mobile-new-content-tvshow-page")
def load_mobile_new_content_tvshow_page():
    time.sleep(0.2)  # Used to simulate delay

    if request.args:
       counter = int(request.args.get("c"))  # The 'counter' value sent in the QS
       content_res = []

       content_res.extend(get_new_tvshow_content(6, counter))

       res = make_response(jsonify(content_res), 200)
       return res


def get_new_content(amount, counter):

    movies = Movie.query.all()
    series = Series.query.all()
    tvshow = Tvshow.query.all()

    mobile_tablet_vdo = []

    mobile_tablet_vdo.extend(movies)
    mobile_tablet_vdo.extend(series)
    mobile_tablet_vdo.extend(tvshow)

    mobile_tablet_vdo.sort(key=lambda x: x.last_updated, reverse=True)

    new_content = []
    for vdo in mobile_tablet_vdo:
        if vdo.last_updated.microsecond != 999999 and len(new_content) != (counter*6) + 6:
            new_content.append(vdo)

    new_content = new_content[counter*6:(counter*6)+6]

    content_json = []

    for content_obj in new_content:
        content_json.append(convertContentObjToJson(content_obj))

    return content_json

@main.route("/load-mobile-new-content-main-page")
def load_mobile_new_content_main_page():
    time.sleep(0.2)  # Used to simulate delay

    if request.args:
       counter = int(request.args.get("c"))  # The 'counter' value sent in the QS
       content_res = []

       content_res.extend(get_new_content(6, counter))

       res = make_response(jsonify(content_res), 200)
       return res

def get_new_ep(amount, counter):

    movies = Movie.query.all()
    series = Series.query.all()
    tvshow = Tvshow.query.all()

    mobile_tablet_vdo = []

    mobile_tablet_vdo.extend(movies)
    mobile_tablet_vdo.extend(series)
    mobile_tablet_vdo.extend(tvshow)

    mobile_tablet_vdo.sort(key=lambda x: x.last_updated, reverse=True)


    new_ep = []
    for vdo in mobile_tablet_vdo:
        if vdo.last_updated.microsecond == 999999 and len(new_ep) != (counter*6) + 6:
            new_ep.append(vdo)

    new_ep = new_ep[counter*6:(counter*6)+6]

    content_json = []

    for content_obj in new_ep:
        content_json.append(convertContentObjToJson(content_obj))

    return content_json

@main.route("/load-mobile-new-ep-main-page")
def load_mobile_new_ep_main_page():
    time.sleep(0.2)  # Used to simulate delay

    if request.args:
       counter = int(request.args.get("c"))  # The 'counter' value sent in the QS
       content_res = []

       content_res.extend(get_new_ep(6, counter))

       res = make_response(jsonify(content_res), 200)
       return res

def get_new_series_ep(amount, counter):

    series = Series.query.all()

    series.sort(key=lambda x: x.last_updated, reverse=True)


    new_ep = []
    for vdo in series:
        if vdo.last_updated.microsecond == 999999 and len(new_ep) != (counter*6) + 6:
            new_ep.append(vdo)

    new_ep = new_ep[counter*6:(counter*6)+6]

    content_json = []

    for content_obj in new_ep:
        content_json.append(convertContentObjToJson(content_obj))

    return content_json

@main.route("/load-mobile-new-ep-series-page")
def load_mobile_new_ep_series_page():
    time.sleep(0.2)  # Used to simulate delay

    if request.args:
       counter = int(request.args.get("c"))  # The 'counter' value sent in the QS
       content_res = []

       content_res.extend(get_new_series_ep(6, counter))

       res = make_response(jsonify(content_res), 200)
       return res

def get_new_tvshow_ep(amount, counter):

    tvshow = Tvshow.query.all()

    tvshow.sort(key=lambda x: x.last_updated, reverse=True)


    new_ep = []
    for vdo in tvshow:
        if vdo.last_updated.microsecond == 999999 and len(new_ep) != (counter*6) + 6:
            new_ep.append(vdo)

    new_ep = new_ep[counter*6:(counter*6)+6]

    content_json = []

    for content_obj in new_ep:
        content_json.append(convertContentObjToJson(content_obj))

    return content_json

@main.route("/load-mobile-new-ep-tvshow-page")
def load_mobile_new_ep_tvshow_page():
    time.sleep(0.2)  # Used to simulate delay

    if request.args:
       counter = int(request.args.get("c"))  # The 'counter' value sent in the QS
       content_res = []

       content_res.extend(get_new_tvshow_ep(6, counter))

       res = make_response(jsonify(content_res), 200)
       return res

def get_random_content_for_infinite_scroll(amount):
    movies = Movie.query.all()
    series = Series.query.all()
    tvshow = Tvshow.query.all()

    mobile_tablet_vdo = []

    mobile_tablet_vdo.extend(movies)
    mobile_tablet_vdo.extend(series)
    mobile_tablet_vdo.extend(tvshow)

    shuffle(mobile_tablet_vdo)

    mobile_tablet_vdo = mobile_tablet_vdo[:amount]
    content_json = []

    for content_obj in mobile_tablet_vdo:
        content_json.append(convertContentObjToJson(content_obj))

    return content_json


@main.route("/load-mobile-content-main-page")
def load_mobile_content_main_page():
    """ Route to return the posts """

    time.sleep(0.2)  # Used to simulate delay

    content_res = []

    content_res.extend(get_random_content_for_infinite_scroll(36))

    res = make_response(jsonify(content_res), 200)
    return res

def get_random_movie_content_for_infinite_scroll(amount):
    movies = Movie.query.all()

    shuffle(movies)

    mobile_tablet_vdo = movies[:amount]

    content_json = []

    for content_obj in mobile_tablet_vdo:
        content_json.append(convertContentObjToJson(content_obj))

    return content_json

@main.route("/load-mobile-content-movie-page")
def load_mobile_content_movie_page():
    """ Route to return the posts """

    time.sleep(0.2)  # Used to simulate delay

    content_res = []

    content_res.extend(get_random_movie_content_for_infinite_scroll(36))

    res = make_response(jsonify(content_res), 200)
    return res

def get_random_series_content_for_infinite_scroll(amount):
    series = Series.query.all()

    shuffle(series)

    mobile_tablet_vdo = series[:amount]

    content_json = []

    for content_obj in mobile_tablet_vdo:
        content_json.append(convertContentObjToJson(content_obj))

    return content_json

@main.route("/load-mobile-content-series-page")
def load_mobile_content_series_page():
    """ Route to return the posts """

    time.sleep(0.2)  # Used to simulate delay

    content_res = []

    content_res.extend(get_random_series_content_for_infinite_scroll(36))

    res = make_response(jsonify(content_res), 200)
    return res

def get_random_tvshow_content_for_infinite_scroll(amount):
    tvshow = Tvshow.query.all()

    shuffle(tvshow)

    mobile_tablet_vdo = tvshow[:amount]

    content_json = []

    for content_obj in mobile_tablet_vdo:
        content_json.append(convertContentObjToJson(content_obj))

    return content_json

@main.route("/load-mobile-content-tvshow-page")
def load_mobile_content_tvshow_page():
    """ Route to return the posts """

    time.sleep(0.2)  # Used to simulate delay

    content_res = []

    content_res.extend(get_random_tvshow_content_for_infinite_scroll(36))

    res = make_response(jsonify(content_res), 200)
    return res

#=====================================================================

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

def convertBlogContentObjToJson(obj):
    return {"title": obj.title, "date": convert_datetime_to_th_str(obj.date_posted), "thumbnail": obj.thumbnail, "id": obj.id}

def get_blog_content_for_main_page(amount, counter):

    posts = Post.query.order_by(desc(Post.date_posted)).all()

    posts = posts[counter*6:(counter*6)+6]
    content_json = []

    for content_obj in posts:
        content_json.append(convertBlogContentObjToJson(content_obj))

    return content_json

@main.route("/load-mobile-blog-content-main-page")
def load_mobile_blog_content_main_page():
    time.sleep(0.2)  # Used to simulate delay

    if request.args:
       counter = int(request.args.get("c"))  # The 'counter' value sent in the QS
       content_res = []

       content_res.extend(get_blog_content_for_main_page(6, counter))

       res = make_response(jsonify(content_res), 200)
       return res

def get_random_blog_content(amount):

    posts = Post.query.all()
    shuffle(posts)

    posts = posts[:6]
    content_json = []

    for content_obj in posts:
        content_json.append(convertBlogContentObjToJson(content_obj))

    return content_json

@main.route("/load-mobile-random-blog-content")
def load_mobile_random_blog_content():

    time.sleep(0.2)  # Used to simulate delay

    if request.args:
       content_res = []

       content_res.extend(get_random_blog_content(6))

       res = make_response(jsonify(content_res), 200)
       return res

#=====================================================================

def get_content_in_each_page(contents, curr_page):
    curr_page = int(curr_page)

    content_index = (curr_page-1)*30
    contents = contents[content_index:content_index+30]
    return contents

def check_num_page(contents):
    num_page = len(contents)/30
    if num_page.is_integer():
        num_page = int(num_page)
    else:
        num_page = int(num_page) + 1
    return num_page


@main.route('/')
def index():

    user_agent = UserAgent(request.headers.get('User-Agent'))
    user_agent = user_agent.platform
    if user_agent is not None:
        user_agent = user_agent.lower()

    global genre_list_group, genre_buttons
    if "iphone" in user_agent or "android" in user_agent or "ipad" in user_agent:
        movies = Movie.query.order_by(desc(Movie.last_updated)).all()
        series = Series.query.order_by(desc(Series.last_updated)).all()
        tvshow = Tvshow.query.order_by(desc(Tvshow.last_updated)).all()



        continue_content = request.cookies.get('continue_content')
        continue_content_arr = []

        if continue_content is not None:
            continue_content_arr, count_genre_list, count_content_type = get_continued_watching_content_and_count_genre()

        mobile_tablet_vdo = []

        mobile_tablet_vdo.extend(movies)
        mobile_tablet_vdo.extend(series)
        mobile_tablet_vdo.extend(tvshow)

        mobile_tablet_vdo.sort(key=lambda x: x.last_updated, reverse=True)

        new_content = []
        new_ep = []
        for vdo in mobile_tablet_vdo:
            if vdo.last_updated.microsecond == 999999 and len(new_ep) != 30:
                new_ep.append(vdo)
            elif vdo.last_updated.microsecond != 999999 and len(new_content) != 30:
                new_content.append(vdo)
            elif len(new_ep) == 30 and len(new_content) == 30:
                break

        new_ep = new_ep[:6]
        new_content = new_content[:6]

        trending_content = []
        suggest_movies = Movie.query.filter(Movie.genres.any (Genre.name.contains("ยอดนิยม"))).all()
        suggest_series = Series.query.filter(Series.genres.any (Genre.name.contains("ยอดนิยม"))).all()
        suggest_tvshow = Tvshow.query.filter(Tvshow.genres.any (Genre.name.contains("ยอดนิยม"))).all()
        trending_content.extend(suggest_movies)
        trending_content.extend(suggest_series)
        trending_content.extend(suggest_tvshow)
        trending_content.sort(key=lambda x: x.last_updated, reverse=True)

        tmp_trending_content = trending_content

        trending_content = trending_content[:6]

        notification_badge_date = request.cookies.get('notification_badge_date')
        notifications = {"trending": 0, "movie": 0, "series": 0, "tvshow": 0}

        if notification_badge_date is None:
            now = datetime.datetime.now()
            now_date_time_str = now.strftime("%m/%d/%Y, %H:%M:%S")
            notification_badge_date = {"trending": now_date_time_str, "movie": now_date_time_str, "series": now_date_time_str, "tvshow": now_date_time_str}
            notification_badge_date = json.dumps(notification_badge_date)

            resp = make_response(render_template('mobile.main.html', active_nav="main", new_ep=new_ep, new_content=new_content, genre_list_group_image_for_browser=genre_list_group_image_for_browser, continue_content_arr=continue_content_arr, trending_content=trending_content, genre_buttons=genre_buttons, notifications=notifications, blog_posts=blog_posts))
            resp.set_cookie('notification_badge_date', notification_badge_date, expires=datetime.datetime.now() + datetime.timedelta(days=365))
            return resp
        else:
            notification_badge_date = json.loads(notification_badge_date)
            for content in tmp_trending_content:

                if notifications["trending"] >= 99:
                    break;
                elif content.last_updated > datetime.datetime.strptime(notification_badge_date["trending"], '%m/%d/%Y, %H:%M:%S'):
                    notifications["trending"] += 1
                else:
                    break;
            for content in movies:

                if notifications["movie"] >= 99:
                    break;
                elif content.last_updated > datetime.datetime.strptime(notification_badge_date["movie"], '%m/%d/%Y, %H:%M:%S'):
                    notifications["movie"] += 1
                else:
                    break;
            for content in series:

                if notifications["series"] >= 99:
                    break;
                elif content.last_updated > datetime.datetime.strptime(notification_badge_date["series"], '%m/%d/%Y, %H:%M:%S'):
                    notifications["series"] += 1
                else:
                    break;
            for content in tvshow:

                if notifications["tvshow"] >= 99:
                    break;
                elif content.last_updated > datetime.datetime.strptime(notification_badge_date["tvshow"], '%m/%d/%Y, %H:%M:%S'):
                    notifications["tvshow"] += 1
                else:
                    break;


        return render_template('mobile.main.html', active_nav="main", new_ep=new_ep, new_content=new_content, genre_list_group_image_for_browser=genre_list_group_image_for_browser, continue_content_arr=continue_content_arr, trending_content=trending_content, genre_buttons=genre_buttons, notifications=notifications)

    else:
        movies = Movie.query.order_by(desc(Movie.last_updated)).all()
        series = Series.query.order_by(desc(Series.last_updated)).all()
        tvshow = Tvshow.query.order_by(desc(Tvshow.last_updated)).all()

        suggest_program = []
        suggest_movies = Movie.query.filter(Movie.genres.any (Genre.name.contains("ยอดนิยม"))).all()
        suggest_series = Series.query.filter(Series.genres.any (Genre.name.contains("ยอดนิยม"))).all()
        suggest_tvshow = Tvshow.query.filter(Tvshow.genres.any (Genre.name.contains("ยอดนิยม"))).all()
        suggest_program.extend(suggest_movies)
        suggest_program.extend(suggest_series)
        suggest_program.extend(suggest_tvshow)
        trending_content = suggest_program
        shuffle(suggest_program)
        suggest_program = suggest_program[:10]

        trending_content.sort(key=lambda x: x.last_updated, reverse=True)

        trending_content = trending_content[:30]

        continue_content = request.cookies.get('continue_content')
        continue_content_arr = []

        if continue_content is not None:
            continue_content_arr, count_genre_list, count_content_type = get_continued_watching_content_and_count_genre()


        desktop_series = series[:30]
        desktop_movie = movies[:30]
        desktop_tvshow = tvshow[:30]

        all_vdo = []

        all_vdo.extend(movies)
        all_vdo.extend(series)
        all_vdo.extend(tvshow)

        all_vdo.sort(key=lambda x: x.last_updated, reverse=True)

        new_content = []
        new_ep = []
        for vdo in all_vdo:
            if vdo.last_updated.microsecond == 999999 and len(new_ep) != 30:
                new_ep.append(vdo)
            elif vdo.last_updated.microsecond != 999999 and len(new_content) != 30:
                new_content.append(vdo)
            elif len(new_ep) == 30 and len(new_content) == 30:
                break

        new_ep = new_ep[:30]
        new_content = new_content[:30]

        return render_template('desktop.main.html', active_nav="main", new_ep=new_ep, new_content=new_content, suggest_program=suggest_program, genre_list_group_image_for_browser=genre_list_group_image_for_browser, continue_content_arr=continue_content_arr, desktop_series=desktop_series, desktop_movie=desktop_movie, desktop_tvshow=desktop_tvshow, trending_content=trending_content, genre_buttons=genre_buttons)


def get_continued_watching_content_of_all_genre():
    continue_content = request.cookies.get('continue_content')
    continue_content_arr = []
    if continue_content is not None:
        continue_content = continue_content.split(",")
        for content in continue_content[:45]:
            content = content.split("|")
            if content[0] == "Movie" :
                content_obj = Movie.query.filter_by(id=int(content[1])).first()
                if content_obj is not None:
                    content_json = {
                    "type": "Movie",
                    "id": content[1],
                    "thumbnail": content_obj.thumbnail,
                    "title": content_obj.title,
                    "youtube_url": content_obj.youtube_url,
                    "last_updated": content_obj.last_updated
                    }
                    continue_content_arr.append(content_json)
            elif content[0] == "Series" :
                content_obj = Series.query.filter_by(id=int(content[1])).first()
                if content_obj is not None:
                    content_json = {
                    "type": "Series",
                    "id": content[1],
                    "thumbnail": content_obj.thumbnail,
                    "title": content_obj.title,
                    "season": content[2],
                    "episode": content[3],
                    "last_updated": content_obj.last_updated
                    }
                    continue_content_arr.append(content_json)
            elif content[0] == "Tvshow":
                content_obj = Tvshow.query.filter_by(id=int(content[1])).first()
                if content_obj is not None:
                    content_json = {
                    "type": "Tvshow",
                    "id": content[1],
                    "thumbnail": content_obj.thumbnail,
                    "title": content_obj.title,
                    "season": content[2],
                    "episode": content[3],
                    "last_updated": content_obj.last_updated
                    }
                    continue_content_arr.append(content_json)
    return continue_content_arr

def get_continued_watching_content_and_count_genre():
    continue_content = request.cookies.get('continue_content')
    continue_content_arr = []
    count_genre_list = []
    count_content_type = {"movie": 0, "series": 0, "tvshow": 0}
    if continue_content is not None:
        continue_content = continue_content.split(",")
        for content in continue_content[:45]:
            content = content.split("|")
            if content[0] == "Movie" :
                content_obj = Movie.query.filter_by(id=int(content[1])).first()
                if content_obj is not None:
                    content_json = {
                    "type": "Movie",
                    "id": content[1],
                    "thumbnail": content_obj.thumbnail,
                    "title": content_obj.title,
                    "youtube_url": content_obj.youtube_url,
                    "last_updated": content_obj.last_updated
                    }
                    continue_content_arr.append(content_json)
                    count_genre_list.extend(content_obj.genres)
                    count_content_type["movie"] += 1
            elif content[0] == "Series" :
                content_obj = Series.query.filter_by(id=int(content[1])).first()
                if content_obj is not None:
                    content_json = {
                    "type": "Series",
                    "id": content[1],
                    "thumbnail": content_obj.thumbnail,
                    "title": content_obj.title,
                    "season": content[2],
                    "episode": content[3],
                    "last_updated": content_obj.last_updated
                    }
                    continue_content_arr.append(content_json)
                    count_genre_list.extend(content_obj.genres)
                    count_content_type["series"] += 1
            elif content[0] == "Tvshow":
                content_obj = Tvshow.query.filter_by(id=int(content[1])).first()
                if content_obj is not None:
                    content_json = {
                    "type": "Tvshow",
                    "id": content[1],
                    "thumbnail": content_obj.thumbnail,
                    "title": content_obj.title,
                    "season": content[2],
                    "episode": content[3],
                    "last_updated": content_obj.last_updated
                    }
                    continue_content_arr.append(content_json)
                    count_genre_list.extend(content_obj.genres)
                    count_content_type["tvshow"] += 1
    return continue_content_arr, count_genre_list, count_content_type


@main.route('/profile')
def profile():
    return render_template('profile.html', username=current_user.username)

@main.route('/search',methods = ['POST', 'GET'])
def search():
   if request.method == 'POST':
      search_keyword = request.form['search']
      # session['search'] = search_keyword
      search_keyword = re.sub("[$@&?#]","",search_keyword)
      url = '/search-template/' + search_keyword + '/page/1'
      return redirect(url)

@main.route('/search-template/<search_keyword>/page/<curr_page>')
def search_template(search_keyword, curr_page):
  search_keyword = search_keyword.strip()
  movies = Movie.query.filter(Movie.title.contains (search_keyword)).all()
  series = Series.query.filter(Series.title.contains (search_keyword)).all()
  tvshows = Tvshow.query.filter(Tvshow.title.contains (search_keyword)).all()
  movies.extend(series)
  movies.extend(tvshows)

  movies2 = Movie.query.filter(Movie.genres.any (Genre.name.contains (search_keyword))).all()
  series = Series.query.filter(Series.genres.any (Genre.name.contains (search_keyword))).all()
  tvshows = Tvshow.query.filter(Tvshow.genres.any (Genre.name.contains (search_keyword))).all()
  movies.extend(movies2)
  movies.extend(series)
  movies.extend(tvshows)

  movies2 = Movie.query.filter(Movie.studio.any (Studio.name.contains (search_keyword))).all()
  series = Series.query.filter(Series.studio.any (Studio.name.contains (search_keyword))).all()
  tvshows = Tvshow.query.filter(Tvshow.studio.any (Studio.name.contains (search_keyword))).all()
  movies.extend(movies2)
  movies.extend(series)
  movies.extend(tvshows)

  movies2 = Movie.query.filter(Movie.actors.any (Actor.name.contains (search_keyword))).all()
  series = Series.query.filter(Series.actors.any (Actor.name.contains (search_keyword))).all()
  tvshows = Tvshow.query.filter(Tvshow.actors.any (Actor.name.contains (search_keyword))).all()
  movies.extend(movies2)
  movies.extend(series)
  movies.extend(tvshows)
  movies = list(set(movies))
  movies.sort(key=lambda x: x.last_updated, reverse=True)
  title = search_keyword

  global genre_list_group

  continue_content = request.cookies.get('continue_content')
  continue_content_arr = []

  num_page = check_num_page(movies)
  movies = get_content_in_each_page(movies, curr_page)
  url = '/search-template/' + search_keyword + '/page/'

  return render_template('genre.html', movies=movies, title=title, curr_page=int(curr_page), url=url, num_page=num_page)

@main.route('/blog')
def blog():
    url = "/blog/page/1"
    return redirect(url)

@main.route('/blog/page/<curr_page>')
def blog_page(curr_page):
    blog_posts = Post.query.order_by(desc(Post.date_posted)).all()


    title = "บล็อกทั้งหมด"

    num_page = check_num_page(blog_posts)
    blog_posts = get_content_in_each_page(blog_posts, curr_page)
    url = '/blog/page/'

    return render_template('genre_blog.html', blog_posts=blog_posts, title=title, curr_page=int(curr_page), num_page=num_page, url=url)

@main.route('/blog/<blog_id>')
def blog_post(blog_id):
    post = Post.query.filter_by(id=blog_id).first()
    blog_posts = Post.query.all()
    shuffle(blog_posts)
    blog_posts = blog_posts[:6]
    title = post.title
    return render_template('blog.html', post=post, blog_posts=blog_posts, title=title)

@main.route('/genre/blog/<genre_id>')
def genre_blog(genre_id):
    url = "/genre/blog/" + genre_id + "/page/1"
    return redirect(url)

@main.route('/genre/blog/<genre_id>/page/<curr_page>')
def genre_blog_page(genre_id, curr_page):

    blog_posts = Post.query.filter(Post.genres.any (id=genre_id)).all()
    genre_name = Genre.query.filter_by(id=genre_id).first().name

    title = "บล็อก" + genre_name
    num_page = check_num_page(blog_posts)
    blog_posts = get_content_in_each_page(blog_posts, curr_page)
    url = '/genre/blog/' + genre_id  + '/page/'

    return render_template('genre_blog.html', blog_posts=blog_posts, curr_page=int(curr_page), num_page=num_page, genre_name=genre_name, url=url, genre_id=genre_id)

@main.route('/actor/blog/<actor_id>')
def actor_blog(actor_id):
    url = "/actor/blog/" + actor_id + "/page/1"
    return redirect(url)

@main.route('/actor/blog/<actor_id>/page/<curr_page>')
def actor_blog_page(actor_id, curr_page):
    blog_posts = Post.query.filter(Post.actors.any (id=actor_id)).all()
    genre_name = Actor.query.filter_by(id=actor_id).first().name

    title = "บล็อก" + genre_name
    num_page = check_num_page(blog_posts)
    blog_posts = get_content_in_each_page(blog_posts, curr_page)
    url = '/actor/blog/' + actor_id  + '/page/'

    return render_template('genre_blog.html', blog_posts=blog_posts, curr_page=int(curr_page), num_page=num_page, genre_name=genre_name, url=url)

@main.route('/movies')
def movies():

    global genre_list_group

    user_agent = UserAgent(request.headers.get('User-Agent'))
    user_agent =user_agent.platform

    if user_agent is not None:
        user_agent = user_agent.lower()

    if "iphone" in user_agent or "android" in user_agent or "ipad" in user_agent:
        new_movies = Movie.query.order_by(desc(Movie.last_updated)).all()

        mobile_tablet_vdo = []
        mobile_tablet_vdo.extend(new_movies)

        mobile_tablet_vdo = mobile_tablet_vdo[:6]

        trending_content = Movie.query.filter(Movie.genres.any (Genre.name.contains("ยอดนิยม"))).all()

        trending_content.sort(key=lambda x: x.last_updated, reverse=True)

        trending_content = trending_content[:6]

        notification_badge_date = request.cookies.get('notification_badge_date')
        if notification_badge_date is None:
            now = datetime.datetime.now()
            now_date_time_str = now.strftime("%m/%d/%Y, %H:%M:%S")
            notification_badge_date = {"trending": now_date_time_str, "movie": now_date_time_str, "series": now_date_time_str, "tvshow": now_date_time_str}
            notification_badge_date = json.dumps(notification_badge_date)
        else:
            now = datetime.datetime.now()
            now_date_time_str = now.strftime("%m/%d/%Y, %H:%M:%S")
            notification_badge_date = json.loads(notification_badge_date)
            notification_badge_date = {"trending": notification_badge_date["trending"], "movie": now_date_time_str, "series": notification_badge_date["series"], "tvshow": notification_badge_date["tvshow"]}
            notification_badge_date = json.dumps(notification_badge_date)

        resp = make_response(render_template('mobile.movies.html', active_nav="movie", title="หนัง", mobile_tablet_vdo=mobile_tablet_vdo, trending_content=trending_content))
        resp.set_cookie('notification_badge_date', notification_badge_date, expires=datetime.datetime.now() + datetime.timedelta(days=365))
        return resp
    else:
        new_movies = Movie.query.order_by(desc(Movie.last_updated)).all()[:45]

        new_vdo = []
        new_vdo.extend(new_movies)

        suggest_program = Movie.query.filter(Movie.genres.any (Genre.name.contains("ยอดนิยม"))).all()
        trending_content = suggest_program
        shuffle(suggest_program)
        suggest_program = suggest_program[:10]

        trending_content.sort(key=lambda x: x.last_updated, reverse=True)

        trending_content = trending_content[:30]

        action_movies = Movie.query.filter(Movie.genres.any (Genre.name == "แอ็คชั่น")).all()
        horror_movies = Movie.query.filter(Movie.genres.any (Genre.name == "สยองขวัญ")).all()
        comedy_movies = Movie.query.filter(Movie.genres.any (Genre.name == "คอมเมดี้")).all()
        crime_movies = Movie.query.filter(Movie.genres.any (Genre.name == "อาชญากรรม")).all()
        classic_movies = Movie.query.filter(Movie.genres.any (Genre.name == "คลาสสิค")).all()
        drama_movies = Movie.query.filter(Movie.genres.any (Genre.name == "ดราม่า")).all()
        romance_movies = Movie.query.filter(Movie.genres.any (Genre.name == "โรแมนติก")).all()

        action_movies.sort(key=lambda x: x.last_updated, reverse=True)
        horror_movies.sort(key=lambda x: x.last_updated, reverse=True)
        comedy_movies.sort(key=lambda x: x.last_updated, reverse=True)
        crime_movies.sort(key=lambda x: x.last_updated, reverse=True)
        classic_movies.sort(key=lambda x: x.last_updated, reverse=True)
        drama_movies.sort(key=lambda x: x.last_updated, reverse=True)
        romance_movies.sort(key=lambda x: x.last_updated, reverse=True)

        action_movies = action_movies[:30]
        horror_movies = horror_movies[:30]
        comedy_movies = comedy_movies[:30]
        crime_movies = crime_movies[:30]
        classic_movies = classic_movies[:30]
        drama_movies = drama_movies[:30]
        romance_movies = romance_movies[:30]


        continue_content = request.cookies.get('continue_content')
        continue_content_arr = []
        if continue_content is not None:
            continue_content_arr, count_genre_list, count_content_type = get_continued_watching_content_and_count_genre()

        return render_template('desktop.movies.html', active_nav="movie", title="หนัง", action_movies=action_movies, horror_movies=horror_movies, comedy_movies=comedy_movies, suggest_program=suggest_program,  new_vdo=new_vdo, crime_movies=crime_movies, classic_movies=classic_movies, drama_movies=drama_movies, romance_movies=romance_movies, continue_content_arr=continue_content_arr, trending_content=trending_content)


@main.route('/movie/genres/<genre_id>')
def movie_genre_redirect(genre_id):
    url = "/movie/genres/" + genre_id + "/page/1"
    return redirect(url)

@main.route('/movie/genres/<genre_id>/page/<curr_page>')
def movie_genre(genre_id, curr_page):
    if genre_id == 'new-release':
        movies = Movie.query.order_by(desc(Movie.last_updated)).all()[:360]
        movies.sort(key=lambda x: x.last_updated, reverse=True)
        title = "หนังใหม่ล่าสุด"
        num_page = check_num_page(movies)
        movies = get_content_in_each_page(movies, curr_page)
        url = '/movie/genres/' + genre_id + '/page/'

        return render_template('genre.html', active_nav="movie", title=title, movies=movies, url=url, curr_page=int(curr_page), num_page=num_page)
    else:
        if genre_id != "movie":
            genre_name = Genre.query.filter(Genre.id == genre_id).first().name
        else:
            genre_name = "หนัง"
        movies = Movie.query.filter(Movie.genres.any (Genre.name.contains(genre_name))).all()[:360]
        movies.sort(key=lambda x: x.last_updated, reverse=True)
        if "movie" == genre_id:
            title = "หนัง"
        else:
            title = "หนัง" + genre_name

    num_page = check_num_page(movies)
    movies = get_content_in_each_page(movies, curr_page)
    url = '/movie/genres/' + genre_id + '/page/'

    return render_template('genre.html', active_nav="movie", title=title, movies=movies, url=url, curr_page=int(curr_page), num_page=num_page)

@main.route('/series/genres/<genre_id>')
def series_genre_redirect(genre_id):
    url = "/series/genres/" + genre_id + "/page/1"
    return redirect(url)

@main.route('/series/genres/<genre_id>/page/<curr_page>')
def series_genre(genre_id, curr_page):
    if genre_id == 'new-release':
        series = Series.query.order_by(desc(Series.last_updated)).all()
        series.sort(key=lambda x: x.last_updated, reverse=True)
        title = "ละคร/ซีรี่ส์ใหม่ล่าสุด"


        num_page = check_num_page(series)
        series = get_content_in_each_page(series, curr_page)
        url = '/series/genres/' + genre_id + '/page/'

        return render_template('genre.html', active_nav="series", title=title, movies=series,  url=url, curr_page=int(curr_page), num_page=num_page)
    elif genre_id == "new-content":
        series = Series.query.order_by(desc(Series.last_updated)).all()
        tmp_series = series
        series = []
        for content in tmp_series:
            if content.last_updated.microsecond != 999999:
                    series.append(content)
        title = "ละคร/ซีรี่ส์มาใหม่"
        genre_name = "ใหม่และล่าสุด"
        genre_name = genre_id
    elif genre_id == "new-ep":
        series = Series.query.order_by(desc(Series.last_updated)).all()
        tmp_series = series
        series = []
        for content in tmp_series:
            if content.last_updated.microsecond == 999999:
                    series.append(content)
        title = "ละคร/ซีรี่ส์ตอนล่าสุด"
        genre_name = "ใหม่และล่าสุด"
        genre_name = genre_id
    else:
        if genre_id != "series":
            genre_name = Genre.query.filter(Genre.id == genre_id).first().name
            series = Series.query.filter(Series.genres.any (Genre.name.contains(genre_name))).all()
        else:
            genre_name = "ซีรี่ส์"
            series = Series.query.order_by(desc(Series.last_updated)).all()
        series.sort(key=lambda x: x.last_updated, reverse=True)
        if "series" == genre_id:
            title = "ซีรี่ส์"
        elif "ละคร" in genre_name or "ซีรี่ส์" in genre_name or "อนิเมะ" in genre_name:
            title = genre_name
        else:
            title = "ละคร/ซีรี่ส์" + genre_name

    num_page = check_num_page(series)
    series = get_content_in_each_page(series, curr_page)
    url = '/series/genres/' + genre_id + '/page/'

    return render_template('genre.html', active_nav="series", title=title, movies=series,  url=url, curr_page=int(curr_page), num_page=num_page)

@main.route('/tvshow/genres/<genre_id>')
def tvshow_genre_redirect(genre_id):
    url = "/tvshow/genres/" + genre_id + "/page/1"
    return redirect(url)

@main.route('/tvshow/genres/<genre_id>/page/<curr_page>')
def tvshow_genre(genre_id, curr_page):
    if genre_id == 'new-release':
        tvshow = Tvshow.query.order_by(desc(Tvshow.last_updated)).all()
        tvshow.sort(key=lambda x: x.last_updated, reverse=True)
        title = "รายการทีวีล่าสุด"


        num_page = check_num_page(tvshow)
        tvshow = get_content_in_each_page(tvshow, curr_page)
        url = '/tvshow/genres/' + genre_id + '/page/'
        return render_template('genre.html', active_nav="tv_show", title=title, movies=tvshow, url=url, curr_page=int(curr_page), num_page=num_page)

    elif genre_id == "new-content":
        tvshow = Tvshow.query.order_by(desc(Tvshow.last_updated)).all()
        tmp_tvshow = tvshow
        tvshow = []
        for content in tmp_tvshow:
            if content.last_updated.microsecond != 999999:
                    tvshow.append(content)
        title = "รายการทีวีมาใหม่"
        genre_name = "ใหม่และล่าสุด"
        genre_name = genre_id
    elif genre_id == "new-ep":
        tvshow = Tvshow.query.order_by(desc(Tvshow.last_updated)).all()
        tmp_tvshow = tvshow
        tvshow = []
        for content in tmp_tvshow:
            if content.last_updated.microsecond == 999999:
                    tvshow.append(content)
        title = "รายการทีวีตอนล่าสุด"
        genre_name = "ใหม่และล่าสุด"
        genre_name = genre_id
    else:
        if genre_id != "tvshow":
            genre_name = Genre.query.filter(Genre.id == genre_id).first().name
        else:
            genre_name = "รายการ"
        tvshow = Tvshow.query.filter(Tvshow.genres.any (Genre.name.contains(genre_name))).all()
        tvshow.sort(key=lambda x: x.last_updated, reverse=True)

        if "tvshow" == genre_id:
            title = "รายการทีวี"
        elif "รายการ" in genre_name:
            title = genre_name
        else:
            title = "รายการ" + genre_name

    num_page = check_num_page(tvshow)
    tvshow = get_content_in_each_page(tvshow, curr_page)
    url = '/tvshow/genres/' + genre_id + '/page/'

    return render_template('genre.html', active_nav="tv_show", title=title, movies=tvshow, url=url, curr_page=int(curr_page), num_page=num_page)

@main.route('/movie/<id>')
def movie(id):
    movie = Movie.query.filter_by(id=id).first()
    title = movie.title
    random_movies = Movie.query.all()
    shuffle(random_movies)
    random_movies = random_movies[:10]
    continue_content = request.cookies.get('continue_content')
    resp = make_response(render_template('movie.html', title=title, movie=movie, random_movies=random_movies, active_nav="movie"))

    if continue_content is None:
        continue_content_str = "Movie|" + id
    else:
        continue_content_str = "Movie|" + id + "," + continue_content
        continue_content = continue_content_str.split(",")
        continue_content = list(dict.fromkeys(continue_content))[:90]
        continue_content_str = ""
        for content in continue_content:
            continue_content_str += content + ","
    resp.set_cookie('continue_content', continue_content_str, expires=datetime.datetime.now() + datetime.timedelta(days=365))
    return resp

@main.route('/tvshows')
def all_tvshows():

    global genre_list_group

    user_agent = UserAgent(request.headers.get('User-Agent'))
    user_agent = user_agent.platform
    if user_agent is not None:
        user_agent = user_agent.lower()

    if "iphone" in user_agent or "android" in user_agent or "ipad" in user_agent:
        new_tvshow = Tvshow.query.order_by(desc(Tvshow.last_updated)).all()

        mobile_tablet_vdo = []
        mobile_tablet_vdo.extend(new_tvshow)

        new_content = []
        new_ep = []
        for vdo in mobile_tablet_vdo:
            if vdo.last_updated.microsecond == 999999 and len(new_ep) != 6:
                new_ep.append(vdo)
            elif vdo.last_updated.microsecond != 999999 and len(new_content) != 6:
                new_content.append(vdo)
            elif len(new_ep) == 6 and len(new_content) == 6:
                break

        mobile_tablet_vdo = mobile_tablet_vdo[:6]

        trending_content = Tvshow.query.filter(Tvshow.genres.any (Genre.name.contains("ยอดนิยม"))).all()
        trending_content.sort(key=lambda x: x.last_updated, reverse=True)

        trending_content = trending_content[:6]

        notification_badge_date = request.cookies.get('notification_badge_date')
        if notification_badge_date is None:
            now = datetime.datetime.now()
            now_date_time_str = now.strftime("%m/%d/%Y, %H:%M:%S")
            notification_badge_date = {"trending": now_date_time_str, "movie": now_date_time_str, "series": now_date_time_str, "tvshow": now_date_time_str}
            notification_badge_date = json.dumps(notification_badge_date)
        else:
            now = datetime.datetime.now()
            now_date_time_str = now.strftime("%m/%d/%Y, %H:%M:%S")
            notification_badge_date = json.loads(notification_badge_date)
            notification_badge_date = {"trending": notification_badge_date["trending"], "movie": notification_badge_date["movie"], "series": notification_badge_date["series"], "tvshow": now_date_time_str}
            notification_badge_date = json.dumps(notification_badge_date)

        resp = make_response(render_template('mobile.tvshows.html', active_nav="tv_show", title="รายการทีวี", new_content=new_content, new_ep=new_ep, trending_content=trending_content))
        resp.set_cookie('notification_badge_date', notification_badge_date, expires=datetime.datetime.now() + datetime.timedelta(days=365))
        return resp

    else:
        new_tvshow = Tvshow.query.order_by(desc(Tvshow.last_updated)).all()

        new_vdo = []
        new_vdo.extend(new_tvshow)

        new_content = []
        new_ep = []
        for vdo in new_vdo:
            if vdo.last_updated.microsecond == 999999 and len(new_ep) != 30:
                new_ep.append(vdo)
            elif vdo.last_updated.microsecond != 999999 and len(new_content) != 30:
                new_content.append(vdo)
            elif len(new_ep) == 30 and len(new_content) == 30:
                break

        suggest_program = Tvshow.query.filter(Tvshow.genres.any (Genre.name.contains("ยอดนิยม"))).all()
        trending_content = suggest_program
        shuffle(suggest_program)
        suggest_program = suggest_program[:10]

        trending_content.sort(key=lambda x: x.last_updated, reverse=True)

        trending_content = trending_content[:30]


        food_tvshow = Tvshow.query.filter(Tvshow.genres.any (Genre.name == "อาหาร")).all()
        travel_tvshow = Tvshow.query.filter(Tvshow.genres.any (Genre.name.contains("ท่องเที่ยว"))).all()
        variety_tvshow = Tvshow.query.filter(Tvshow.genres.any (Genre.name.contains("วาไรตี้"))).all()
        reality_tvshow = Tvshow.query.filter(Tvshow.genres.any (Genre.name.contains("เรียลลิตี้"))).all()
        comedy_tvshow = Tvshow.query.filter(Tvshow.genres.any (Genre.name.contains("คอมเมดี้"))).all()


        food_tvshow.sort(key=lambda x: x.last_updated, reverse=True)
        travel_tvshow.sort(key=lambda x: x.last_updated, reverse=True)
        variety_tvshow.sort(key=lambda x: x.last_updated, reverse=True)
        reality_tvshow.sort(key=lambda x: x.last_updated, reverse=True)
        comedy_tvshow.sort(key=lambda x: x.last_updated, reverse=True)

        food_tvshow = food_tvshow[:30]
        travel_tvshow = travel_tvshow[:30]
        variety_tvshow = variety_tvshow[:30]
        reality_tvshow = reality_tvshow[:30]
        comedy_tvshow = comedy_tvshow[:30]

        continue_content = request.cookies.get('continue_content')
        continue_content_arr = []

        if continue_content is not None:
            continue_content_arr, count_genre_list, count_content_type = get_continued_watching_content_and_count_genre()

        return render_template('desktop.tvshows.html', active_nav="tv_show", title="รายการทีวี", suggest_program=suggest_program, food_tvshow=food_tvshow, travel_tvshow=travel_tvshow, new_ep=new_ep, new_content=new_content, variety_tvshow=variety_tvshow, reality_tvshow=reality_tvshow, comedy_tvshow=comedy_tvshow, continue_content_arr=continue_content_arr, trending_content=trending_content)

@main.route('/tvshow/<tvshow_id>')
def tvshow(tvshow_id):
    tvshow = Tvshow.query.filter_by(id=tvshow_id).first()
    seasons = tvshow.seasons
    first_season = min(seasons, key=lambda seasons: seasons.id)
    season_id = first_season.id
    episodes = first_season.episodes
    first_episode = min(episodes, key=lambda episodes: episodes.id)
    first_yt_url = first_episode.youtube_url
    url = "/tvshow/" + str(tvshow.id) + "/season/" + str(season_id) + "/episode/" + str(first_yt_url)
    return redirect(url)

@main.route('/tvshow/<series_id>/season/<season_id>')
def tvshow_season(series_id, season_id):
    series = Tvshow.query.filter_by(id=series_id).first()
    curr_season = None
    for season in series.seasons:
        if str(season.id) == season_id:
            curr_season = season
            break
    episodes = curr_season.episodes
    first_episode = min(episodes, key=lambda episodes: episodes.id)
    first_yt_url = first_episode.youtube_url
    url = "/tvshow/" + str(series.id) + "/season/" + str(season_id) + "/episode/" + str(first_yt_url)
    return redirect(url)

@main.route('/tvshow/<tvshow_id>/season/<season_id>/episode/<episode_yt_url>')
def tvshow_episode(tvshow_id, season_id, episode_yt_url):
    series = Tvshow.query.filter_by(id=tvshow_id).first()
    curr_season = None
    prev_season = None
    next_season = None
    curr_episode = None
    prev_episode = None
    next_episode = None
    next_season_episode = None
    prev_season_episode = None
    first_episode = None
    last_episode = None

    i = 0
    sorted_seasons = sorted(series.seasons, key=lambda season: season.id)
    for season in sorted_seasons:
        if str(season.id) == season_id:
            curr_season = season
            try:
                next_season = sorted_seasons[i+1]
                sorted_episodes = sorted(next_season.episodes, key=lambda episodes: episodes.id)
                next_season_episode = sorted_episodes[0]
            except IndexError:
                next_season = None

            try:
                if i != 0:
                    prev_season = sorted_seasons[i-1]
                    sorted_episodes = sorted(prev_season.episodes, key=lambda episodes: episodes.id)
                    prev_season_episode = sorted_episodes[-1]
            except IndexError:
                prev_season = None
            break
        i += 1

    episodes = curr_season.episodes
    sorted_episodes = sorted(episodes, key=lambda episodes: episodes.id)

    first_episode = sorted_episodes[0].youtube_url
    last_episode = sorted_episodes[-1].youtube_url

    for i, episode in enumerate(sorted_episodes):
        if str(episode.youtube_url) == episode_yt_url:
            if i != 0:
                prev_episode = sorted_episodes[i-1]
            curr_episode = episode
            if i+1 != len(sorted_episodes):
                next_episode = sorted_episodes[i+1]
            break

    random_tvshow = Tvshow.query.all()
    shuffle(random_tvshow)
    random_tvshow = random_tvshow[:10]

    continue_content = request.cookies.get('continue_content')
    resp = make_response(render_template('tvshow-episodes.html', active_nav="tv_show", title=series.title, series=series, curr_season = curr_season, curr_episode=curr_episode, prev_episode=prev_episode, next_episode=next_episode, random_tvshow=random_tvshow, next_season=next_season, prev_season=prev_season, next_season_episode=next_season_episode, prev_season_episode=prev_season_episode, first_episode=first_episode, last_episode=last_episode))

    if continue_content is None:
        continue_content_str = "Tvshow|" + tvshow_id + "|" + season_id + "|" + episode_yt_url
    else:
        continue_content_str = "Tvshow|" + tvshow_id + "|" + season_id + "|" + episode_yt_url + "," + continue_content
        continue_content = continue_content_str.split(",")
        continue_content = list(dict.fromkeys(continue_content))[:45]
        continue_content_str = ""

        continue_series_duplicate_check = []
        for content in continue_content:
            if "Tvshow" in content:
                split_series = content.split("|")
                if split_series[1] in continue_series_duplicate_check:
                    continue
                continue_series_duplicate_check.append(split_series[1])
            continue_content_str += content + ","


    resp.set_cookie('continue_content', continue_content_str, expires=datetime.datetime.now() + datetime.timedelta(days=365))
    return resp

@main.route('/series')
def all_series():

    user_agent = UserAgent(request.headers.get('User-Agent'))
    user_agent = user_agent.platform
    if user_agent is not None:
        user_agent = user_agent.lower()

    global genre_list_group

    if "iphone" in user_agent or "android" in user_agent or "ipad" in user_agent:
        new_series = Series.query.order_by(desc(Series.last_updated)).all()

        mobile_tablet_vdo = []
        mobile_tablet_vdo.extend(new_series)

        new_content = []
        new_ep = []
        for vdo in mobile_tablet_vdo:
            if vdo.last_updated.microsecond == 999999 and len(new_ep) != 6:
                new_ep.append(vdo)
            elif vdo.last_updated.microsecond != 999999 and len(new_content) != 6:
                new_content.append(vdo)
            elif len(new_ep) == 6 and len(new_content) == 6:
                break

        mobile_tablet_vdo = mobile_tablet_vdo[:6]

        trending_content = Series.query.filter(Series.genres.any (Genre.name.contains("ยอดนิยม"))).all()

        trending_content.sort(key=lambda x: x.last_updated, reverse=True)

        trending_content = trending_content[:6]

        notification_badge_date = request.cookies.get('notification_badge_date')
        if notification_badge_date is None:
            now = datetime.datetime.now()
            now_date_time_str = now.strftime("%m/%d/%Y, %H:%M:%S")
            notification_badge_date = {"trending": now_date_time_str, "movie": now_date_time_str, "series": now_date_time_str, "tvshow": now_date_time_str}
            notification_badge_date = json.dumps(notification_badge_date)
        else:
            now = datetime.datetime.now()
            now_date_time_str = now.strftime("%m/%d/%Y, %H:%M:%S")
            notification_badge_date = json.loads(notification_badge_date)
            notification_badge_date = {"trending": notification_badge_date["trending"], "movie": notification_badge_date["movie"], "series": now_date_time_str, "tvshow": notification_badge_date["tvshow"]}
            notification_badge_date = json.dumps(notification_badge_date)


        resp = make_response(render_template('mobile.series.html', active_nav="series", title="ละคร/ซีรี่ส์", trending_content=trending_content, new_ep=new_ep, new_content=new_content))
        resp.set_cookie('notification_badge_date', notification_badge_date, expires=datetime.datetime.now() + datetime.timedelta(days=365))
        return resp

    else:
        new_series = Series.query.order_by(desc(Series.last_updated)).all()

        new_vdo = []
        new_vdo.extend(new_series)

        new_content = []
        new_ep = []
        for vdo in new_vdo:
            if vdo.last_updated.microsecond == 999999 and len(new_ep) != 30:
                new_ep.append(vdo)
            elif vdo.last_updated.microsecond != 999999 and len(new_content) != 30:
                new_content.append(vdo)
            elif len(new_ep) == 30 and len(new_content) == 30:
                break

        suggest_program = Series.query.filter(Series.genres.any (Genre.name.contains("ยอดนิยม"))).all()
        trending_content = suggest_program
        shuffle(suggest_program)
        suggest_program = suggest_program[:10]

        trending_content.sort(key=lambda x: x.last_updated, reverse=True)

        trending_content = trending_content[:30]

        jp_animes = Series.query.filter(Series.genres.any (Genre.name == "อนิเมะญี่ปุ่น")).all()
        chinese_series = Series.query.filter(Series.genres.any (Genre.name == "ซีรี่ส์จีน")).all()
        th_dub_series = Series.query.filter(Series.genres.any (Genre.name == "พากย์ไทย")).all()
        classic_series = Series.query.filter(Series.genres.any (Genre.name == "คลาสสิค")).all()
        fantasy_series = Series.query.filter(Series.genres.any (Genre.name == "แฟนตาซี")).all()
        romance_series = Series.query.filter(Series.genres.any (Genre.name == "โรแมนติก")).all()
        history_series = Series.query.filter(Series.genres.any (Genre.name == "ย้อนยุค")).all()
        comedy_series = Series.query.filter(Series.genres.any (Genre.name == "คอมเมดี้")).all()

        jp_animes.sort(key=lambda x: x.last_updated, reverse=True)
        chinese_series.sort(key=lambda x: x.last_updated, reverse=True)
        th_dub_series.sort(key=lambda x: x.last_updated, reverse=True)
        classic_series.sort(key=lambda x: x.last_updated, reverse=True)
        fantasy_series.sort(key=lambda x: x.last_updated, reverse=True)
        romance_series.sort(key=lambda x: x.last_updated, reverse=True)
        history_series.sort(key=lambda x: x.last_updated, reverse=True)
        comedy_series.sort(key=lambda x: x.last_updated, reverse=True)

        jp_animes = jp_animes[:30]
        chinese_series = chinese_series[:30]
        th_dub_series = th_dub_series[:30]
        classic_series = classic_series[:30]
        fantasy_series = fantasy_series[:30]
        romance_series = romance_series[:30]
        history_series = history_series[:30]
        comedy_series = comedy_series[:30]

        continue_content = request.cookies.get('continue_content')
        continue_content_arr = []

        if continue_content is not None:
            continue_content_arr, count_genre_list, count_content_type = get_continued_watching_content_and_count_genre()

        return render_template('desktop.series.html', active_nav="series", title="ละคร/ซีรี่ส์", suggest_program=suggest_program, jp_animes=jp_animes, new_content=new_content, new_ep=new_ep, chinese_series=chinese_series, th_dub_series=th_dub_series, classic_series=classic_series, fantasy_series=fantasy_series, romance_series=romance_series, history_series=history_series, comedy_series=comedy_series, continue_content_arr=continue_content_arr, trending_content=trending_content)


@main.route('/series/<series_id>')
def series(series_id):
    series = Series.query.filter_by(id=series_id).first()
    seasons = series.seasons
    print(seasons)
    first_season = min(seasons, key=lambda seasons: seasons.id)
    season_id = first_season.id
    episodes = first_season.episodes
    first_episode = min(episodes, key=lambda episodes: episodes.id)
    first_yt_url = first_episode.youtube_url
    url = "/series/" + str(series.id) + "/season/" + str(season_id) + "/episode/" + str(first_yt_url)
    return redirect(url)

@main.route('/series/<series_id>/season/<season_id>')
def series_season(series_id, season_id):
    series = Series.query.filter_by(id=series_id).first()
    curr_season = None
    for season in series.seasons:
        if str(season.id) == season_id:
            curr_season = season
            break
    episodes = curr_season.episodes
    first_episode = min(episodes, key=lambda episodes: episodes.id)
    first_yt_url = first_episode.youtube_url
    url = "/series/" + str(series.id) + "/season/" + str(season_id) + "/episode/" + str(first_yt_url)
    return redirect(url)


@main.route('/series/<series_id>/season/<season_id>/episode/<episode_yt_url>')
def episode(series_id, season_id, episode_yt_url):
    series = Series.query.filter_by(id=series_id).first()
    curr_season = None
    prev_season = None
    next_season = None
    curr_episode = None
    prev_episode = None
    next_episode = None
    next_season_episode = None
    prev_season_episode = None
    first_episode = None
    last_episode = None
    i = 0
    sorted_seasons = sorted(series.seasons, key=lambda season: season.id)
    for season in sorted_seasons:
        if str(season.id) == season_id:
            curr_season = season
            try:
                next_season = sorted_seasons[i+1]
                sorted_episodes = sorted(next_season.episodes, key=lambda episodes: episodes.id)
                next_season_episode = sorted_episodes[0]
            except IndexError:
                next_season = None

            try:
                if i != 0:
                    prev_season = sorted_seasons[i-1]
                    sorted_episodes = sorted(prev_season.episodes, key=lambda episodes: episodes.id)
                    prev_season_episode = sorted_episodes[-1]
            except IndexError:
                prev_season = None
            break
        i += 1

    episodes = curr_season.episodes
    sorted_episodes = sorted(episodes, key=lambda episodes: episodes.id)

    first_episode = sorted_episodes[0].youtube_url
    last_episode = sorted_episodes[-1].youtube_url
    for i, episode in enumerate(sorted_episodes):
        if str(episode.youtube_url) == episode_yt_url:
            if i != 0:
                prev_episode = sorted_episodes[i-1]
            curr_episode = episode
            if i+1 != len(sorted_episodes):
                next_episode = sorted_episodes[i+1]
            break

    random_series = Series.query.all()
    shuffle(random_series)
    random_series = random_series[:10]

    continue_content = request.cookies.get('continue_content')
    resp = make_response(render_template('episodes.html', active_nav="series", title=series.title, series=series, curr_season = curr_season, curr_episode=curr_episode, prev_episode=prev_episode, next_episode=next_episode, random_series=random_series, next_season=next_season, prev_season=prev_season, next_season_episode=next_season_episode, prev_season_episode=prev_season_episode, first_episode=first_episode, last_episode=last_episode))

    if continue_content is None:
        continue_content_str = "Series|" + series_id + "|" + season_id + "|" + episode_yt_url
    else:
        continue_content_str = "Series|" + series_id + "|" + season_id + "|" + episode_yt_url + "," + continue_content
        continue_content = continue_content_str.split(",")
        continue_content = list(dict.fromkeys(continue_content))[:45]
        continue_content_str = ""

        continue_series_duplicate_check = []
        for content in continue_content:
            if "Series" in content:
                split_series = content.split("|")
                if split_series[1] in continue_series_duplicate_check:
                    continue
                continue_series_duplicate_check.append(split_series[1])
            continue_content_str += content + ","

    resp.set_cookie('continue_content', continue_content_str, expires=datetime.datetime.now() + datetime.timedelta(days=365))
    return resp

@main.route('/genre/<genre_id>')
def genre_redirect(genre_id):
    url = "/genre/" + genre_id + "/page/1"
    return redirect(url)

@main.route('/genre/<genre_id>/page/<curr_page>')
def genre(genre_id, curr_page):
    movies = []
    continue_content_arr = []
    if genre_id == "new-release":
        new_movies = Movie.query.order_by(desc(Movie.last_updated)).all()
        new_series = Series.query.order_by(desc(Series.last_updated)).all()
        new_tvshow = Tvshow.query.order_by(desc(Tvshow.last_updated)).all()
        movies.extend(new_movies)
        movies.extend(new_series)
        movies.extend(new_tvshow)
        title = "ตอนใหม่และล่าสุด"
        genre_name = genre_id
    elif genre_id == "new-content-release":
        new_movies = Movie.query.order_by(desc(Movie.last_updated)).all()
        new_series = Series.query.order_by(desc(Series.last_updated)).all()
        new_tvshow = Tvshow.query.order_by(desc(Tvshow.last_updated)).all()
        movies.extend(new_movies)
        movies.extend(new_series)
        movies.extend(new_tvshow)
        tmp_movies = movies
        movies = []
        for content in tmp_movies:
            if content.last_updated.microsecond != 999999:
                    movies.append(content)
        title = "เนื้อหาใหม่"
        genre_name = "ใหม่และล่าสุด"
        genre_name = genre_id
    elif genre_id == "new-ep-release":
        new_movies = Movie.query.order_by(desc(Movie.last_updated)).all()
        new_series = Series.query.order_by(desc(Series.last_updated)).all()
        new_tvshow = Tvshow.query.order_by(desc(Tvshow.last_updated)).all()
        movies.extend(new_movies)
        movies.extend(new_series)
        movies.extend(new_tvshow)
        tmp_movies = movies
        movies = []
        for content in tmp_movies:
            if content.last_updated.microsecond == 999999:
                    movies.append(content)
        title = "ตอนล่าสุด"
        genre_name = "ใหม่และล่าสุด"
        genre_name = genre_id
    elif genre_id == "ongoing":
        series = Series.query.filter_by(state=None).all()
        tvshow = Tvshow.query.filter_by(state=None).all()
        movies.extend(series)
        movies.extend(tvshow)
        series = Series.query.filter_by(state=False).all()
        tvshow = Tvshow.query.filter_by(state=False).all()
        title = "ยังไม่จบ"
        movies.extend(series)
        movies.extend(tvshow)
        genre_name = genre_id
    elif genre_id == "completed":
        series = Series.query.filter_by(state=True).all()
        tvshow = Tvshow.query.filter_by(state=True).all()
        title = "จบแล้ว"
        movies.extend(series)
        movies.extend(tvshow)
        genre_name = genre_id
    elif genre_id == "continue-content":
        continue_content_arr = get_continued_watching_content_of_all_genre()
        title="ดูเนื้อหาต่อ สำหรับ คุณ"
        genre_name = genre_id
    elif genre_id.isdigit() is not True:
        genre = Genre.query.filter(Genre.name == genre_id).first()
        if genre is not None:
            genre_id = genre.id
            return redirect(url_for('main.genre', genre_id=genre_id))
        else:
            return redirect(url_for('main.index'))
    else:
        genre_name = Genre.query.filter(Genre.id == genre_id).first().name
        movies = Movie.query.filter(Movie.genres.any (Genre.name.contains(genre_name))).all()
        series = Series.query.filter(Series.genres.any (Genre.name.contains(genre_name))).all()
        tvshow = Tvshow.query.filter(Tvshow.genres.any (Genre.name.contains(genre_name))).all()
        movies.extend(series)
        movies.extend(tvshow)
        title = genre_name

    genre_list_group = get_genre_scroll_from_cookie()

    if movies != []:
        movies.sort(key=lambda x: x.last_updated, reverse=True)

    if genre_id == "continue-content":
        num_page = check_num_page(continue_content_arr)
        continue_content_arr = get_content_in_each_page(continue_content_arr, curr_page)
        url = '/genre/' + genre_id + '/page/'
    else:
        num_page = check_num_page(movies)
        movies = get_content_in_each_page(movies, curr_page)
        url = '/genre/' + genre_id + '/page/'

    if genre_id == str(80):
        notification_badge_date = request.cookies.get('notification_badge_date')
        if notification_badge_date is None:
            now = datetime.datetime.now()
            now_date_time_str = now.strftime("%m/%d/%Y, %H:%M:%S")
            notification_badge_date = {"trending": now_date_time_str, "movie": now_date_time_str, "series": now_date_time_str, "tvshow": now_date_time_str}
            notification_badge_date = json.dumps(notification_badge_date)
            resp = make_response(render_template('genre.html', movies=movies, title=title, genre_name=genre_name, genre_list_group=genre_list_group, continue_content_arr=continue_content_arr, num_page=num_page, url=url, curr_page=int(curr_page)))
            resp.set_cookie('notification_badge_date', notification_badge_date, expires=datetime.datetime.now() + datetime.timedelta(days=365))
            return resp
        else:
            now = datetime.datetime.now()
            now_date_time_str = now.strftime("%m/%d/%Y, %H:%M:%S")
            notification_badge_date = json.loads(notification_badge_date)
            notification_badge_date = {"trending": now_date_time_str, "movie": notification_badge_date["movie"], "series": notification_badge_date["series"], "tvshow": notification_badge_date["tvshow"]}
            notification_badge_date = json.dumps(notification_badge_date)
            resp = make_response(render_template('genre.html', movies=movies, title=title, genre_name=genre_name, genre_list_group=genre_list_group, continue_content_arr=continue_content_arr, num_page=num_page, url=url, curr_page=int(curr_page)))
            resp.set_cookie('notification_badge_date', notification_badge_date)
            return resp



    return render_template('genre.html', movies=movies, title=title, genre_name=genre_name, genre_list_group=genre_list_group, continue_content_arr=continue_content_arr, num_page=num_page, url=url, curr_page=int(curr_page))

@main.route('/actor/<actor_id>')
def actor_redirect(actor_id):
    url = "/actor/" + actor_id + "/page/1"
    return redirect(url)

@main.route('/actor/<actor_id>/page/<curr_page>')
def actor(actor_id, curr_page):
    if actor_id.isdigit() is not True:
        actor = Actor.query.filter(Actor.name == actor_id).first()
        if actor is not None:
            actor_id = actor.id
            return redirect(url_for('main.actor', actor_id=actor_id, curr_page=curr_page))
        else:
            return redirect(url_for('main.index'))


    actor_name = Actor.query.filter(Actor.id == actor_id).first().name

    series = Series.query.filter(Series.actors.any (Actor.name == actor_name)).all()
    movies = Movie.query.filter(Movie.actors.any (Actor.name == actor_name)).all()
    tvshow = Tvshow.query.filter(Tvshow.actors.any (Actor.name == actor_name)).all()

    movies.extend(series)
    movies.extend(tvshow)

    movies.sort(key=lambda x: x.last_updated, reverse=True)

    title = actor_name

    num_page = check_num_page(movies)
    movies = get_content_in_each_page(movies, curr_page)
    url = '/actor/' + actor_id + '/page/'

    return render_template('genre.html', movies=movies, title=title, actor_name=actor_name, curr_page=int(curr_page), num_page=num_page, url=url)

@main.route('/director/<director_id>')
def director_redirect(director_id):
    url = "/director/" + director_id + "/page/1"
    return redirect(url)

@main.route('/director/<director_id>/page/<curr_page>')
def director(director_id, curr_page):
    if director_id.isdigit() is not True:
        director = Director.query.filter(Director.name == director_id).first()
        if director is not None:
            director_id = director.id
            return redirect(url_for('main.director', director_id=director_id))
        else:
            return redirect(url_for('main.index'))

    director_name = Director.query.filter(Director.id == director_id).first().name

    series = Series.query.filter(Series.directors.any (Director.name == director_name)).all()
    movies = Movie.query.filter(Movie.directors.any (Director.name == director_name)).all()

    movies.extend(series)

    movies.sort(key=lambda x: x.last_updated, reverse=True)

    title = director_name

    num_page = check_num_page(movies)
    movies = get_content_in_each_page(movies, curr_page)
    url = '/director/' + director_id + '/page/'

    return render_template('genre.html', movies=movies, title=title, director_name=director_name, num_page=num_page, curr_page=int(curr_page), url=url)

@main.route('/studio/<studio_id>')
def studio_redirect(studio_id):
    url = "/studio/" + studio_id + "/page/1"
    return redirect(url)


@main.route('/studio/<studio_id>/page/<curr_page>')
def studio(studio_id, curr_page):
    if studio_id.isdigit() is not True:
        studio = Studio.query.filter(Studio.name == studio_id).first()
        if studio is not None:
            studio_id = studio.id
            return redirect(url_for('main.studio', studio_id=studio_id))
        else:
            return redirect(url_for('main.index'))

    studio_name = Studio.query.filter(Studio.id == studio_id).first().name

    series = Series.query.filter(Series.studio.any (Studio.name == studio_name)).all()
    movies = Movie.query.filter(Movie.studio.any (Studio.name == studio_name)).all()
    tvshow = Tvshow.query.filter(Tvshow.studio.any (Studio.name == studio_name)).all()

    movies.extend(series)
    movies.extend(tvshow)

    title = studio_name

    movies.sort(key=lambda x: x.last_updated, reverse=True)

    num_page = check_num_page(movies)
    movies = get_content_in_each_page(movies, curr_page)
    url = '/studio/' + studio_id + '/page/'

    return render_template('genre.html', movies=movies, title=title, studio_name=studio_name, num_page=num_page, curr_page=int(curr_page), url=url)

@main.route('/ads.txt')
def google_adsense_txt():
	try:
		return send_file('./static/ads.txt', attachment_filename='ads.txt')
	except Exception as e:
		return str(e)

def id_generator(size=11, chars=string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def initialSeriesV2(series_json):
    season_list = []
    genre_list = []
    director_list = []
    actor_list = []
    studio_list = []

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

    r = bytes(series_json["yt_playlist_xml"], 'utf-8')
    soup = BeautifulSoup(r, 'html.parser')
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
                prev_ep = None
                for ytContent in reversed(ytJson[:100]):
                    new_ep_id = ""
                    randomIdCheck = True
                    while randomIdCheck == True:
                        if prev_ep is None:
                            new_ep_id = id_generator()
                            ep_id_check = Episode.query.filter_by(id=new_ep_id).first()
                            if ep_id_check is None:
                                randomIdCheck = False
                        else:
                            random_num = random.randint(0, 1000000)
                            new_ep_id = int(random_num) + int(prev_ep)
                            ep_id_check = Episode.query.filter_by(id=new_ep_id).first()
                            if ep_id_check is None:
                                randomIdCheck = False
                    episode_data = Episode(id=int(new_ep_id), title=ytContent["playlistVideoRenderer"]["title"]["runs"][0]["text"], youtube_url=ytContent["playlistVideoRenderer"]["videoId"])
                    db.session.add(episode_data)
                    episode_list.append(episode_data)
                    print(episode_data)
                    prev_ep = new_ep_id

            else:
                prev_ep = None
                for ytContent in ytJson[:100]:
                    new_ep_id = ""
                    randomIdCheck = True
                    while randomIdCheck == True:
                        if prev_ep is None:
                            new_ep_id = id_generator()
                            ep_id_check = Episode.query.filter_by(id=new_ep_id).first()
                            if ep_id_check is None:
                                randomIdCheck = False
                        else:
                            random_num = random.randint(0, 1000000)
                            new_ep_id = int(random_num) + int(prev_ep)
                            ep_id_check = Episode.query.filter_by(id=new_ep_id).first()
                            if ep_id_check is None:
                                randomIdCheck = False
                    episode_data = Episode(id=int(new_ep_id), title=ytContent["playlistVideoRenderer"]["title"]["runs"][0]["text"], youtube_url=ytContent["playlistVideoRenderer"]["videoId"])
                    db.session.add(episode_data)
                    episode_list.append(episode_data)
                    print(episode_data)
                    prev_ep = new_ep_id


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
                randomIdCheck = False
        else:
            random_num = random.randint(0, 1000000)
            new_season_id = int(random_num) + int(previous_season.id)
            season_id_check = Season.query.filter_by(id=new_season_id).first()
            if season_id_check is None:
                randomIdCheck = False
            #=============================================
    season_data = Season(id=int(new_season_id), season_title=series_json["season_title"], yt_playlist_url=series_json['yt_playlist_url'], episodes=episode_list, published_year=series_json['published_year'])
    db.session.add(season_data)
    season_list.append(season_data)


    randomIdCheck = True
    new_series_id = ""
    while randomIdCheck == True:
        new_series_id = id_generator()
        series_id_check = Series.query.filter_by(id=new_series_id).first()
        if series_id_check is None:
            randomIdCheck = False
    series_data = Series(id=int(new_series_id), title=series_json["title"], description=series_json["description"], genres=genre_list, seasons=season_list, last_updated=datetime.datetime.now(), directors=director_list, actors=actor_list, thumbnail=series_json["thumbnail"], studio=studio_list, state=series_json["state"])
    db.session.add(series_data)
    db.session.commit()
    print(series_data)
    return True

def deleteAllSeries(row_id):
    check = Series.query.filter_by(id=row_id).first()
    for season in check.seasons:
        for ep in season.episodes:
            Episode.query.filter_by(id=ep.id).delete()
        Season.query.filter_by(id=season.id).delete()
    Series.query.filter_by(id=row_id).delete()
    db.session.commit()

import pyotp
t = pyotp.TOTP('OD4CY5IDEUS7ML72PDC4RBBD5IRPNHQJ')
auth_str = t.provisioning_uri(name="Admin Soiflix", issuer_name="Soiflix")

@main.route('/thirtynine',methods = ['GET'])
def thirtynine():
   genres = Genre.query.all()
   posts = Post.query.all()
   if session.get("admin") != ",ug'bo.=h":
        return redirect("/thirtynine-login")

   return render_template('thirtynine.html', genres=genres, login=True, posts=posts)

@main.route('/thirtynine-login',methods = ['POST', 'GET'])
def thirtynine_login():
    if session.get("admin") == ",ug'bo.=h":
        return redirect("/thirtynine")

    if request.method == "POST" and t.verify(request.form['OEM-LOG']):
        session["admin"] = ",ug'bo.=h"
        return redirect("/thirtynine")
    return render_template("thirtynine.html")

@main.route('/thirtynine-add-series',methods = ['POST'])
def thirtynine_add_series():
   genres = Genre.query.all()

   if request.method == 'POST' and t.verify(request.form['OEM']):
      series_json = str(request.form['JAS'])
      file = request.files['IOC']
      series_json = json.loads(series_json)
      series_json["thumbnail"] = file.filename
      series_json["yt_playlist_xml"] = str(request.form['SYT-PL-XML'])
      state = initialSeriesV2(series_json)

      if state:
          if file:
              file_exists = exists(os.path.join('./main/static/series/thumbnail',file.filename))
              if file_exists:
                return render_template('thirtynine.html', alert_msg="ชื่อรูปภาพมีการใช้งานแล้ว", genres=genres, login=True)

              file.save(os.path.join('./main/static/series/thumbnail',file.filename))

          else:
              return render_template('thirtynine.html', alert_msg="กรุณาอัพโหลดรูปภาพ", genres=genres, login=True)
      return render_template('thirtynine.html', alert_msg="เพิ่มซีรี่ส์ใหม่แล้ว", genres=genres, login=True)

   return '404'

def initialTvshow(tvshow_json):
    season_list = []
    genre_list = []
    actor_list = []
    studio_list = []

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


    r = bytes(tvshow_json["yt_playlist_xml"], 'utf-8')
    soup = BeautifulSoup(r, 'html.parser')
    items = soup.findAll('script')
    ytJson = ""
    episode_list = []
    for item in items:
        for keyword in tvshow_json["keywords"]:
            result = str(item).find(keyword)
            if result != -1:
                ytJson = item.text[:-1]
                ytJson = ytJson.replace("var ytInitialData = ", "")
                ytJson = json.loads(ytJson)
                ytJson = ytJson["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][0]["tabRenderer"]["content"]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"][0]["playlistVideoListRenderer"]["contents"]
                if tvshow_json['reverse_loop']:
                    prev_ep = None
                    for ytContent in reversed(ytJson[:100]):
                        new_ep_id = ""
                        randomIdCheck = True
                        while randomIdCheck == True:
                            if prev_ep is None:
                                new_ep_id = id_generator()
                                ep_id_check = Episode.query.filter_by(id=new_ep_id).first()
                                if ep_id_check is None:
                                    randomIdCheck = False
                            else:
                                random_num = random.randint(0, 1000000)
                                new_ep_id = int(random_num) + int(prev_ep)
                                ep_id_check = Episode.query.filter_by(id=new_ep_id).first()
                                if ep_id_check is None:
                                    randomIdCheck = False
                        episode_data = Episode(id=int(new_ep_id),title=ytContent["playlistVideoRenderer"]["title"]["runs"][0]["text"], youtube_url=ytContent["playlistVideoRenderer"]["videoId"])
                        db.session.add(episode_data)
                        episode_list.append(episode_data)
                        print(episode_data)
                        prev_ep = new_ep_id
                else:
                    prev_ep = None
                    for ytContent in ytJson[:100]:
                        new_ep_id = ""
                        randomIdCheck = True
                        while randomIdCheck == True:
                            if prev_ep is None:
                                new_ep_id = id_generator()
                                ep_id_check = Episode.query.filter_by(id=new_ep_id).first()
                                if ep_id_check is None:
                                    randomIdCheck = False
                            else:
                                random_num = random.randint(0, 1000000)
                                new_ep_id = int(random_num) + int(prev_ep)
                                ep_id_check = Episode.query.filter_by(id=new_ep_id).first()
                                if ep_id_check is None:
                                    randomIdCheck = False
                        episode_data = Episode(id=int(new_ep_id),title=ytContent["playlistVideoRenderer"]["title"]["runs"][0]["text"], youtube_url=ytContent["playlistVideoRenderer"]["videoId"])
                        db.session.add(episode_data)
                        episode_list.append(episode_data)
                        print(episode_data)
                        prev_ep = new_ep_id

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
              randomIdCheck = False

      else:
          random_num = random.randint(0, 1000000)
          new_season_id = int(random_num) + int(previous_season.id)
          season_id_check = Season.query.filter_by(id=new_season_id).first()
          if season_id_check is None:
              randomIdCheck = False
    season_data = Season(id=int(new_season_id),season_title=tvshow_json["season_title"], yt_playlist_url=tvshow_json['yt_playlist_url'], episodes=episode_list, published_year=tvshow_json['published_year'])
    db.session.add(season_data)
    season_list.append(season_data)

    randomIdCheck = True
    new_tvshow_id = ""
    while randomIdCheck == True:
        new_tvshow_id = id_generator()
        tvshow_id_check = Tvshow.query.filter_by(id=new_tvshow_id).first()
        if tvshow_id_check is None:
            randomIdCheck = False
    tvshow_data = Tvshow(id=int(new_tvshow_id),title=tvshow_json["title"], description=tvshow_json["description"], genres=genre_list, seasons=season_list, last_updated=datetime.datetime.now(), actors=actor_list, thumbnail=tvshow_json["thumbnail"], studio=studio_list, state=tvshow_json["state"])
    db.session.add(tvshow_data)
    db.session.commit()
    return True

@main.route('/thirtynine-add-tvshow',methods = ['POST'])
def thirtynine_add_tvshow():
   genres = Genre.query.all()

   if request.method == 'POST' and t.verify(request.form['OEM-ATS']):
      tvshow_json = str(request.form['JAS-ATS'])
      file = request.files['IOC-ATS']
      tvshow_json = json.loads(tvshow_json)
      tvshow_json["thumbnail"] = file.filename
      tvshow_json["yt_playlist_xml"] = str(request.form['TSYT-PL-XML'])
      state = initialTvshow(tvshow_json)

      if state:
          if file:
              file_exists = exists(os.path.join('./main/static/tvshow/thumbnail',file.filename))
              if file_exists:
                return render_template('thirtynine.html', alert_msg="ชื่อรูปภาพมีการใช้งานแล้ว", genres=genres, login=True)

              file.save(os.path.join('./main/static/tvshow/thumbnail',file.filename))

          else:
              return render_template('thirtynine.html', alert_msg="กรุณาอัพโหลดรูปภาพ", genres=genres, login=True)
      return render_template('thirtynine.html', alert_msg="เพิ่มรายการทีวีใหม่แล้ว", genres=genres, login=True)

   return '404'

@main.route('/thirtynine-delete-series',methods = ['POST'])
def thirtynine_delete_series():
   genres = Genre.query.all()

   if request.method == 'POST' and t.verify(request.form['OEM2']):
       deleteAllSeries(int(request.form['SDELALL']))
       return render_template('thirtynine.html', alert_msg="ลบซีรี่ส์แล้ว", genres=genres, login=True)

   return '404'

def deleteAllTvshow(row_id):
    check = Tvshow.query.filter_by(id=row_id).first()
    for season in check.seasons:
        for ep in season.episodes:
            Episode.query.filter_by(id=ep.id).delete()
        Season.query.filter_by(id=season.id).delete()
    Tvshow.query.filter_by(id=row_id).delete()
    db.session.commit()

@main.route('/thirtynine-delete-tvshow',methods = ['POST'])
def thirtynine_delete_tvshow():
   genres = Genre.query.all()

   if request.method == 'POST' and t.verify(request.form['OEM-DTS']):
       deleteAllTvshow(int(request.form['TID-DTS']))
       return render_template('thirtynine.html', alert_msg="ลบรายการทีวีแล้ว", genres=genres, login=True)

   return '404'

def addNewEpisodeWithUpdateLastUpdated(table_name, row_id, yt_url, ep_title, season_id):
    check = table_name.query.filter_by(id=row_id).first()
    episode_list = []

    for season in check.seasons:
        if season.id == season_id:
            episode_list.extend(season.episodes)
            check.last_updated = datetime.datetime.now().replace(microsecond=999999)

    if episode_list != []:
        prev_ep = max(episode_list, key=lambda eps: eps.id)
    else:
        prev_ep = None
    randomIdCheck = True

    new_ep_id = ""
    while randomIdCheck == True:
        if prev_ep is None:
            new_ep_id = id_generator()
            ep_id_check = Episode.query.filter_by(id=new_ep_id).first()
            if ep_id_check is None:
                randomIdCheck = False
        else:
            random_num = random.randint(0, 1000000)
            new_ep_id = int(random_num) + int(prev_ep.id)
            ep_id_check = Season.query.filter_by(id=new_ep_id).first()
            if ep_id_check is None:
                randomIdCheck = False

    episode_data = Episode(id=int(new_ep_id),title=ep_title, youtube_url=yt_url)
    print(episode_data)
    db.session.add(episode_data)
    episode_list.append(episode_data)
    for season in check.seasons:
        if season.id == season_id:
            season.episodes = episode_list
    db.session.commit()


@main.route('/thirtynine-add-ep',methods = ['POST'])
def thirtynine_add_ep():
   genres = Genre.query.all()

   if request.method == 'POST' and t.verify(request.form['OEM-ANE']):
       if request.form['CTS-ANE'] == "series":
           addNewEpisodeWithUpdateLastUpdated(Series, int(request.form['CID-ANE']), request.form['YT-ANE'], request.form['CTT-ANE'], int(request.form['SSID-ANE']))
       elif request.form['CTS-ANE'] == "tvshow":
           addNewEpisodeWithUpdateLastUpdated(Tvshow, int(request.form['CID-ANE']), request.form['YT-ANE'], request.form['CTT-ANE'], int(request.form['SSID-ANE']))

       return render_template('thirtynine.html', alert_msg="เพิ่ม ep ใหม่แล้ว", genres=genres, login=True)
   return '404'

def addNewSeason(table_name, row_id, keyword, season_title, yt_playlist_url, published_year, reverse_loop, yt_playlist_xml):
    check = table_name.query.filter_by(id=row_id).first()

    season_list = []
    for season in check.seasons:
        if season.episodes is not None:
            season_list.append(season)

    r = bytes(yt_playlist_xml, 'utf-8')
    soup = BeautifulSoup(r, 'html.parser')
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
                prev_ep = None
                for ytContent in reversed(ytJson[:100]):
                    new_ep_id = ""
                    randomIdCheck = True
                    if 'playlistVideoRenderer' in ytContent:
                        while randomIdCheck == True:
                            if prev_ep is None:
                                new_ep_id = id_generator()
                                ep_id_check = Episode.query.filter_by(id=new_ep_id).first()
                                if ep_id_check is None:
                                    randomIdCheck = False
                            else:
                                random_num = random.randint(0, 1000000)
                                new_ep_id = int(random_num) + int(prev_ep)
                                ep_id_check = Episode.query.filter_by(id=new_ep_id).first()
                                if ep_id_check is None:
                                    randomIdCheck = False
                        episode_data = Episode(id=int(new_ep_id), title=ytContent["playlistVideoRenderer"]["title"]["runs"][0]["text"], youtube_url=ytContent["playlistVideoRenderer"]["videoId"])
                        db.session.add(episode_data)
                        episode_list.append(episode_data)
                        print(episode_data)
                        prev_ep = new_ep_id

            else:
                prev_ep = None
                for ytContent in ytJson[:100]:
                    new_ep_id = ""
                    randomIdCheck = True
                    if 'playlistVideoRenderer' in ytContent:
                        while randomIdCheck == True:
                            if prev_ep is None:
                                new_ep_id = id_generator()
                                ep_id_check = Episode.query.filter_by(id=new_ep_id).first()
                                if ep_id_check is None:
                                    randomIdCheck = False
                            else:
                                random_num = random.randint(0, 1000000)
                                new_ep_id = int(random_num) + int(prev_ep)
                                ep_id_check = Episode.query.filter_by(id=new_ep_id).first()
                                if ep_id_check is None:
                                    randomIdCheck = False
                        episode_data = Episode(id=int(new_ep_id), title=ytContent["playlistVideoRenderer"]["title"]["runs"][0]["text"], youtube_url=ytContent["playlistVideoRenderer"]["videoId"])
                        db.session.add(episode_data)
                        episode_list.append(episode_data)
                        print(episode_data)
                        prev_ep = new_ep_id


    previous_season = None
    if season_list != []:
        previous_season = max(season_list, key=lambda seasons: seasons.id)
    else:
        previous_season = None
    randomIdCheck = True

    while randomIdCheck == True:
      if previous_season is None:
          new_season_id = id_generator()
          season_id_check = Season.query.filter_by(id=new_season_id).first()
          if season_id_check is None:
              randomIdCheck = False
      else:
          random_num = random.randint(0, 1000000)
          new_season_id = int(random_num) + int(previous_season.id)
          season_id_check = Season.query.filter_by(id=new_season_id).first()
          if season_id_check is None:
              randomIdCheck = False

    if episode_list == []:
        return "keyword ผิดพลาด"
    season_data = Season(id=int(new_season_id),season_title=season_title, yt_playlist_url=yt_playlist_url, episodes=episode_list, published_year=published_year)
    db.session.add(season_data)
    season_list.append(season_data)
    check.seasons = season_list
    db.session.commit()
    return "เพิ่ม season ใหม่แล้ว"

@main.route('/thirtynine-add-new-season',methods = ['POST'])
def thirtynine_add_new_season():
   genres = Genre.query.all()

   if request.method == 'POST' and t.verify(request.form['OEM-ANS']):
       if request.form['RL-ANS'] == "true":
           RL_ANS = True
       elif request.form['RL-ANS'] == "false":
           RL_ANS = False

       if request.form['CTS-ANS'] == "series":
           alert_msg = addNewSeason(Series, int(request.form['CID-ANS']), request.form['K-ANS'], request.form['SSTT-ANS'], request.form['YT-ANS'], request.form['PY-ANS'], RL_ANS, str(request.form['SSYT-PL-XML']))
       elif request.form['CTS-ANS'] == "tvshow":
           alert_msg = addNewSeason(Tvshow, int(request.form['CID-ANS']), request.form['K-ANS'], request.form['SSTT-ANS'], request.form['YT-ANS'], request.form['PY-ANS'], RL_ANS, str(request.form['SSYT-PL-XML']))

       return render_template('thirtynine.html', alert_msg=alert_msg, genres=genres, login=True)
   return '404'

def changeThumbnail(table_name, row_id, new_thumnail):
    check = table_name.query.filter_by(id=row_id).first()
    check.thumbnail = new_thumnail
    db.session.commit()

@main.route('/thirtynine-change-thumbnail',methods = ['POST'])
def thirtynine_change_thumbnail():
   genres = Genre.query.all()
   if request.method == 'POST' and t.verify(request.form['OEM-CTN']):
       file = request.files['IOC-CTN']

       file_dir = ''
       if request.form['CTS-CTN'] == "series":
           changeThumbnail(Series, int(request.form['CID-CTN']), file.filename)
           file_dir = './main/static/series/thumbnail'
       elif request.form['CTS-CTN'] == "tvshow":
           changeThumbnail(Tvshow, int(request.form['CID-CTN']), file.filename)
           file_dir = './main/static/tvshow/thumbnail'
       elif request.form['CTS-CTN'] == "movie":
           changeThumbnail(Movie, int(request.form['CID-CTN']), file.filename)
           file_dir = './main/static/movies/thumbnail'
       else:
           return render_template('thirtynine.html', alert_msg="ข้อมูลไม่ถูกต้อง", genres=genres, login=True)


       if file:
           file_exists = exists(os.path.join(file_dir, file.filename))
           if file_exists:
               return render_template('thirtynine.html', alert_msg="ชื่อรูปภาพมีการใช้งานแล้ว", genres=genres, login=True)
           file.save(os.path.join(file_dir,file.filename))
           return render_template('thirtynine.html', alert_msg="อัพโหลดรูปเรียบร้อยแล้ว", genres=genres, login=True)

   return '404'


def insertEP(table_name, row_id, yt_url, ep_title, season_id, ep_num):
    check = table_name.query.filter_by(id=row_id).first()
    episode_list = []

    for season in check.seasons:
        if season.id == season_id:
            episode_list.extend(season.episodes)

    #=============================================
    if episode_list != []:
        prev_ep = max(episode_list, key=lambda episodes: episodes.id)
    else:
        prev_ep = None
    randomIdCheck = True

    new_ep_id = ""
    while randomIdCheck == True:
        if prev_ep is None:
            new_ep_id = id_generator()
            ep_id_check = Episode.query.filter_by(id=int(new_ep_id)).first()
            if ep_id_check is None:
                randomIdCheck = False
        else:
            random_num = random.randint(0, 1000000)
            new_ep_id = int(random_num) + int(prev_ep.id)
            ep_id_check = Episode.query.filter_by(id=int(new_ep_id)).first()
            if ep_id_check is None:
                randomIdCheck = False
    #=============================================
    episode_data = Episode(id=int(new_ep_id), title=ep_title, youtube_url=yt_url)
    print(episode_data)
    inserted_ep_id = episode_data.id
    db.session.add(episode_data)
    db.session.commit()

    episode_list = sorted(episode_list, key=lambda episodes: episodes.id)
    new_episode_list = []
    #=========================================
    if int(ep_num) == 1:
        new_episode_list = []
    else:
        new_episode_list.extend(episode_list[:ep_num-1])
    #=========================================
    prev_ep = inserted_ep_id
    for ep in episode_list[ep_num-1:]:
        tmp_ep_title = ep.title
        tmp_ep_yt_url = ep.youtube_url
        tmp_ep_id = ep.id
        Episode.query.filter_by(id=tmp_ep_id).delete()
        db.session.commit()
        #=========================================
        new_ep_id = ""
        randomIdCheck = True
        while randomIdCheck == True:
            if prev_ep is None:
                new_ep_id = id_generator()
                ep_id_check = Episode.query.filter_by(id=new_ep_id).first()
                if ep_id_check is None:
                    randomIdCheck = False
            else:
                random_num = random.randint(0, 1000000)
                new_ep_id = int(random_num) + int(prev_ep)
                ep_id_check = Episode.query.filter_by(id=new_ep_id).first()
                if ep_id_check is None:
                    randomIdCheck = False
        #=========================================
        episode_data = Episode(id=int(new_ep_id), title=tmp_ep_title, youtube_url=tmp_ep_yt_url)
        db.session.add(episode_data)
        db.session.commit()
        new_episode_list.append(episode_data)
        print(episode_data)
        prev_ep = new_ep_id

    episode_check = Episode.query.filter_by(id=inserted_ep_id).first()
    new_episode_list.append(episode_check)
    for season in check.seasons:
        if season.id == season_id:
            season.episodes = new_episode_list
    db.session.commit()

@main.route('/thirtynine-insert-ep',methods = ['POST'])
def thirtynine_insert_ep():
   genres = Genre.query.all()
   if request.method == 'POST' and t.verify(request.form['OEM-IEP']):
          if request.form['CTS-IEP'] == "series":
              insertEP(Series, int(request.form['CID-IEP']), request.form['YTU-IEP'], request.form['EPT-IEP'], int(request.form['SSID-IEP']), int(request.form['EPO-IEP']))
          elif request.form['CTS-IEP'] == "tvshow":
              insertEP(Tvshow, int(request.form['CID-IEP']), request.form['YTU-IEP'], request.form['EPT-IEP'], int(request.form['SSID-IEP']), int(request.form['EPO-IEP']))
          return render_template('thirtynine.html', alert_msg="แทรก ep เรียบร้อยแล้ว", genres=genres, login=True)

   return '404'


def addYTPlaylistToSFPlaylist(table_name, row_id, yt_playlist_url, keyword, season_id, reverse_loop, yt_playlist_xml):
    check = table_name.query.filter_by(id=row_id).first()
    r = bytes(yt_playlist_xml, 'utf-8')
    soup = BeautifulSoup(r, 'html.parser')
    items = soup.findAll('script')
    ytJson = ""
    episode_list = []
    curr_season = None
    for season in check.seasons:
        if season.id == season_id:
            curr_season = season
    episode_list.extend(curr_season.episodes)
    if episode_list != []:
        prev_ep = max(episode_list, key=lambda episodes: episodes.id)
    else:
        prev_ep = None
    print(prev_ep.id)
    for item in items:
        result = str(item).find(keyword)
        if result != -1:
            ytJson = item.text[:-1]
            ytJson = ytJson.replace("var ytInitialData = ", "")
            ytJson = json.loads(ytJson)
            ytJson = ytJson["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][0]["tabRenderer"]["content"]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"][0]["playlistVideoListRenderer"]["contents"]

            if reverse_loop:
                for ytContent in reversed(ytJson[:100]):
                    randomIdCheck = True
                    new_ep_id = ""
                    while randomIdCheck == True:
                        if prev_ep is None:
                            new_ep_id = id_generator()
                            ep_id_check = Episode.query.filter_by(id=int(new_ep_id)).first()
                            if ep_id_check is None:
                                randomIdCheck = False
                        else:
                            random_num = random.randint(0, 1000000)
                            new_ep_id = int(random_num) + int(prev_ep.id)
                            ep_id_check = Episode.query.filter_by(id=int(new_ep_id)).first()
                            if ep_id_check is None:
                                randomIdCheck = False
                    episode_data = Episode(id=int(new_ep_id), title=ytContent["playlistVideoRenderer"]["title"]["runs"][0]["text"], youtube_url=ytContent["playlistVideoRenderer"]["videoId"])
                    db.session.add(episode_data)
                    episode_list.append(episode_data)
                    print(episode_data)
                    prev_ep = episode_data
            else:
                for ytContent in ytJson[:100]:
                    randomIdCheck = True
                    new_ep_id = ""
                    while randomIdCheck == True:
                        if prev_ep is None:
                            new_ep_id = id_generator()
                            ep_id_check = Episode.query.filter_by(id=int(new_ep_id)).first()
                            if ep_id_check is None:
                                randomIdCheck = False
                        else:
                            random_num = random.randint(0, 1000000)
                            print(prev_ep)
                            new_ep_id = int(random_num) + int(prev_ep.id)
                            ep_id_check = Episode.query.filter_by(id=int(new_ep_id)).first()
                            if ep_id_check is None:
                                randomIdCheck = False
                    episode_data = Episode(id=int(new_ep_id), title=ytContent["playlistVideoRenderer"]["title"]["runs"][0]["text"], youtube_url=ytContent["playlistVideoRenderer"]["videoId"])
                    db.session.add(episode_data)
                    episode_list.append(episode_data)
                    print(episode_data)
                    prev_ep = episode_data

    curr_season.episodes = episode_list
    db.session.commit()

@main.route('/thirtynine-add-yt-playlist',methods = ['POST'])
def thirtynine_add_yt_playlist():
   genres = Genre.query.all()
   if request.method == 'POST' and t.verify(request.form['OEM-AYP']):
          if request.form['RL-AYP'] == "true":
              RL_AYP = True
          elif request.form['RL-AYP'] == "false":
              RL_AYP = False
          if request.form['CTS-AYP'] == "series":
              addYTPlaylistToSFPlaylist(Series, int(request.form['CID-AYP']), request.form['YTU-AYP'], request.form['KW-AYP'], int(request.form['SSID-AYP']), RL_AYP, str(request.form['YTSF-PL-XML']))
          elif request.form['CTS-AYP'] == "tvshow":
              addYTPlaylistToSFPlaylist(Tvshow, int(request.form['CID-AYP']), request.form['YTU-AYP'], request.form['KW-AYP'], int(request.form['SSID-AYP']), RL_AYP, str(request.form['YTSF-PL-XML']))
          return render_template('thirtynine.html', alert_msg="เพิ่ม Youtube playlist to Soiflix playlist เรียบร้อยแล้ว", genres=genres, login=True)

   return '404'

def deleteSeason(season_id):
    check = Season.query.filter_by(id=season_id).first()
    Season.query.filter_by(id=season_id).delete()
    db.session.commit()

@main.route('/thirtynine-delete-season',methods = ['POST'])
def thirtynine_delete_season():
   genres = Genre.query.all()

   if request.method == 'POST' and t.verify(request.form['OEM-DSS']):
       deleteSeason(int(request.form['SSID-DSS']))
       return render_template('thirtynine.html', alert_msg="ลบซีซั่นแล้ว", genres=genres, login=True)

   return '404'

def deleteEP(table, row_id, season_id, youtube_url):
    check = table.query.filter_by(id=row_id).first()
    for season in check.seasons:
        if season_id == season.id:
            for ep in season.episodes:
                if youtube_url == ep.youtube_url:
                    Episode.query.filter_by(id=ep.id).delete()
                    break
    db.session.commit()


@main.route('/thirtynine-delete-ep',methods = ['POST'])
def thirtynine_delete_ep():
  genres = Genre.query.all()

  if request.method == 'POST' and t.verify(request.form['OEM-DEP']):
      if request.form['CTS-DEP'] == "series":
          deleteEP(Series, int(request.form['CID-DEP']), int(request.form['SSID-DEP']), request.form['YTID-DEP'])
      elif request.form['CTS-DEP'] == "tvshow":
          deleteEP(Tvshow, int(request.form['CID-DEP']), int(request.form['SSID-DEP']), request.form['YTID-DEP'])

      return render_template('thirtynine.html', alert_msg="ลบ EP แล้ว", genres=genres, login=True)

  return '404'

def initialMovie(movie_json):
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

    randomIdCheck = True
    new_movie_id = ""
    while randomIdCheck == True:
        new_movie_id = id_generator()
        movie_id_check = Movie.query.filter_by(id=new_movie_id).first()
        if movie_id_check is None:
            randomIdCheck = False

    movie_data = Movie(id=int(new_movie_id),title=movie_json["title"], last_updated=datetime.datetime.now(), description=movie_json["description"], youtube_url=movie_json["youtube_url"], genres=genre_list, actors=actor_list, directors=director_list, studio=studio_list, published_year=movie_json["published_year"], thumbnail=movie_json["thumbnail"], runtime_min=movie_json["runtime_min"])
    db.session.add(movie_data)
    db.session.commit()
    return True

@main.route('/thirtynine-add-movie',methods = ['POST'])
def thirtynine_add_movie():
   genres = Genre.query.all()

   if request.method == 'POST' and t.verify(request.form['OEM-AMV']):
      movie_json = str(request.form['JAS-AMV'])
      file = request.files['IOC-AMV']
      print(file)
      movie_json = json.loads(movie_json)
      movie_json["thumbnail"] = file.filename
      state = initialMovie(movie_json)

      if state:
          if file:
              file_exists = exists(os.path.join('./main/static/movies/thumbnail',file.filename))
              if file_exists:
                return render_template('thirtynine.html', alert_msg="ชื่อรูปภาพมีการใช้งานแล้ว", genres=genres, login=True)

              file.save(os.path.join('./main/static/movies/thumbnail',file.filename))

          else:
              return render_template('thirtynine.html', alert_msg="กรุณาอัพโหลดรูปภาพ", genres=genres, login=True)
      return render_template('thirtynine.html', alert_msg="เพิ่มหนังใหม่แล้ว", genres=genres, login=True)

   return '404'

def deleteMovie(row_id):
    Movie.query.filter_by(id=row_id).delete()
    db.session.commit()

@main.route('/thirtynine-delete-movie',methods = ['POST'])
def thirtynine_delete_movie():
   genres = Genre.query.all()

   if request.method == 'POST' and t.verify(request.form['OEM-DMV']):
       deleteMovie(int(request.form['CID-DMV']))
       return render_template('thirtynine.html', alert_msg="ลบหนังแล้ว", genres=genres, login=True)

   return '404'

@main.route('/thirtynine-delete-ep-order',methods = ['POST'])
def thirtynine_delete_ep_order():
  genres = Genre.query.all()

  if request.method == 'POST' and t.verify(request.form['OEM-DEPO']):
      if request.form['CTS-DEPO'] == "series":
          alert_msg = deleteEPOrder(Series, int(request.form['CID-DEPO']), int(request.form['SSID-DEPO']), request.form['ID-DEPO'])
      elif request.form['CTS-DEPO'] == "tvshow":
          alert_msg = deleteEPOrder(Tvshow, int(request.form['CID-DEPO']), int(request.form['SSID-DEPO']), request.form['ID-DEPO'])

      return render_template('thirtynine.html', alert_msg=alert_msg, genres=genres, login=True)

  return '404'

def deleteEPOrder(table, row_id, season_id, order):
    check = table.query.filter_by(id=row_id).first()
    for season in check.seasons:
        if season_id == season.id:
            episode_list = sorted(season.episodes, key=lambda episodes: episodes.id)
            Episode.query.filter_by(id=episode_list[int(order)-1].id).delete()
            alert_msg = episode_list[int(order)-1].title
            db.session.commit()
            return "ลบ EP " + alert_msg + " แล้ว"

def changeState(table_name, row_id, new_state):
    check = table_name.query.filter_by(id=row_id).first()
    check.state = new_state
    db.session.commit()

@main.route('/thirtynine-change-state',methods = ['POST'])
def thirtynine_change_state():
   genres = Genre.query.all()
   if request.method == 'POST' and t.verify(request.form['OEM-CST']):
       new_state = False
       if request.form['ST-CST'] == "false":
           new_state = False
       elif request.form['ST-CST'] == "true":
           new_state = True

       if request.form['CTS-CST'] == "series":
           changeState(Series, int(request.form['CID-CST']), new_state)
           alert_msg = "เปลี่ยน state แล้ว"
           return render_template('thirtynine.html', alert_msg=alert_msg, genres=genres, login=True)
       elif request.form['CTS-CST'] == "tvshow":
           changeState(Tvshow, int(request.form['CID-CST']), new_state)
           alert_msg = "เปลี่ยน state แล้ว"
           return render_template('thirtynine.html', alert_msg=alert_msg, genres=genres, login=True)
       else:
           return render_template('thirtynine.html', alert_msg="ข้อมูลไม่ถูกต้อง", genres=genres, login=True)

   return '404'

def changeSeasonName(row_id, new_ss_name):
    check = Season.query.filter_by(id=row_id).first()
    check.season_title = new_ss_name
    db.session.commit()

@main.route('/thirtynine-change-season-name',methods = ['POST'])
def thirtynine_change_season_name():
   genres = Genre.query.all()
   if request.method == 'POST' and t.verify(request.form['OEM-CSSN']):
       alert_msg = "เปลี่ยน season name แล้ว"
       changeSeasonName(int(request.form['SSID-CSSN']), request.form['NSSN-CSSN'])
       return render_template('thirtynine.html', alert_msg=alert_msg, genres=genres, login=True)

   return '404'


def changeGenreName(old_genre_name, new_genre_name):
    check = Genre.query.filter_by(name=old_genre_name).first()
    check.name = new_genre_name
    db.session.commit()

@main.route('/thirtynine-change-genre-name',methods = ['POST'])
def thirtynine_change_genre_name():
   genres = Genre.query.all()
   if request.method == 'POST' and t.verify(request.form['OEM-CGN']):
       alert_msg = "เปลี่ยน genre name แล้ว"
       changeGenreName(request.form['GN-CGN'], request.form['NGN-CGN'])
       return render_template('thirtynine.html', alert_msg=alert_msg, genres=genres, login=True)

   return '404'

def changePublishedYear(table_name, row_id, new_published_year):
    check = table_name.query.filter_by(id=row_id).first()
    if hasattr(check,'seasons'):
        minSeason = min(check.seasons, key=lambda x:x.id)
        minSeason.published_year = new_published_year
    else:
        check.published_year = new_published_year
    db.session.commit()

@main.route('/thirtynine-change-published-year',methods = ['POST'])
def thirtynine_change_published_year():
   genres = Genre.query.all()
   if request.method == 'POST' and t.verify(request.form['OEM-CPY']):

       alert_msg = "เปลี่ยน published year แล้ว"
       if request.form['CTS-CPY'] == "series":
           changePublishedYear(Series, int(request.form['CID-CPY']), int(request.form['NPY-CPY']))
           return render_template('thirtynine.html', alert_msg=alert_msg, genres=genres, login=True)
       elif request.form['CTS-CPY'] == "tvshow":
           changePublishedYear(Tvshow, int(request.form['CID-CPY']), int(request.form['NPY-CPY']))
           return render_template('thirtynine.html', alert_msg=alert_msg, genres=genres, login=True)
       elif request.form['CTS-CPY'] == "movie":
           changePublishedYear(Movie, int(request.form['CID-CPY']), int(request.form['NPY-CPY']))
           return render_template('thirtynine.html', alert_msg=alert_msg, genres=genres, login=True)
       else:
           return render_template('thirtynine.html', alert_msg="ข้อมูลไม่ถูกต้อง", genres=genres, login=True)

   return '404'

def changeContentName(table_name, row_id, new_content_name):
    check = table_name.query.filter_by(id=row_id).first()
    check.title = new_content_name
    db.session.commit()

@main.route('/thirtynine-change-content-name',methods = ['POST'])
def thirtynine_change_content_name():
   genres = Genre.query.all()
   if request.method == 'POST' and t.verify(request.form['OEM-CCN']):

       alert_msg = "เปลี่ยน content name แล้ว"
       if request.form['CTS-CCN'] == "series":
           changeContentName(Series, int(request.form['CID-CCN']), request.form['NCN-CCN'])
           return render_template('thirtynine.html', alert_msg=alert_msg, genres=genres, login=True)
       elif request.form['CTS-CCN'] == "tvshow":
           changeContentName(Tvshow, int(request.form['CID-CCN']), request.form['NCN-CCN'])
           return render_template('thirtynine.html', alert_msg=alert_msg, genres=genres, login=True)
       elif request.form['CTS-CCN'] == "movie":
           changeContentName(Movie, int(request.form['CID-CCN']), request.form['NCN-CCN'])
           return render_template('thirtynine.html', alert_msg=alert_msg, genres=genres, login=True)
       else:
           return render_template('thirtynine.html', alert_msg="ข้อมูลไม่ถูกต้อง", genres=genres, login=True)

   return '404'

def deleteActor(name_actor):
    Actor.query.filter_by(name=name_actor).delete()
    db.session.commit()

@main.route('/thirtynine-delete-actor',methods = ['POST'])
def thirtynine_delete_actor():
   genres = Genre.query.all()

   if request.method == 'POST' and t.verify(request.form['OEM-DAT']):
       deleteActor(request.form['NAT-DAT'])
       return render_template('thirtynine.html', alert_msg="ลบชื่อนักแสดงแล้ว", genres=genres, login=True)

   return '404'

def addActor(table, row_id, actor):
    check = table.query.filter_by(id=row_id).first()
    actor_list = []
    actor_list.extend(check.actors)
    actor = actor.strip()
    actor_check = Actor.query.filter_by(name=actor).first()
    if actor_check is None:
        actor_data = Actor(name=actor)
        db.session.add(actor_data)
        actor_list.append(actor_data)
    else:
        actor_list.append(actor_check)
    check.actors = actor_list
    db.session.commit()

@main.route('/thirtynine-add-actor',methods = ['POST'])
def thirtynine_add_actor():
   genres = Genre.query.all()

   if request.method == 'POST' and t.verify(request.form['OEM-AAT']):

       alert_msg = "เพิ่มชื่อนักแสดงใหม่แล้ว"
       if request.form['CTS-AAT'] == "series":
           addActor(Series, int(request.form['CID-AAT']), request.form['NAT-AAT'])
           return render_template('thirtynine.html', alert_msg=alert_msg, genres=genres, login=True)
       elif request.form['CTS-AAT'] == "tvshow":
           addActor(Tvshow, int(request.form['CID-AAT']), request.form['NAT-AAT'])
           return render_template('thirtynine.html', alert_msg=alert_msg, genres=genres, login=True)
       elif request.form['CTS-AAT'] == "movie":
           addActor(Movie, int(request.form['CID-AAT']), request.form['NAT-AAT'])
           return render_template('thirtynine.html', alert_msg=alert_msg, genres=genres, login=True)
       else:
           return render_template('thirtynine.html', alert_msg="ข้อมูลไม่ถูกต้อง", genres=genres, login=True)

   return '404'

def deleteDirector(name_director):
    Director.query.filter_by(name=name_director).delete()
    db.session.commit()

@main.route('/thirtynine-delete-director',methods = ['POST'])
def thirtynine_delete_director():
   genres = Genre.query.all()

   if request.method == 'POST' and t.verify(request.form['OEM-DDRT']):
       deleteDirector(request.form['NAT-DDRT'])
       return render_template('thirtynine.html', alert_msg="ลบชื่อผู้กำกับแล้ว", genres=genres, login=True)

   return '404'

def addDirector(table, row_id, director):
    check = table.query.filter_by(id=row_id).first()
    director_list = []
    director_list.extend(check.directors)
    director = director.strip()
    director_check = Director.query.filter_by(name=director).first()
    if director_check is None:
        director_data = Director(name=director)
        db.session.add(director_data)
        director_list.append(director_data)
    else:
        director_list.append(director_check)
    check.directors = director_list
    db.session.commit()

@main.route('/thirtynine-add-director',methods = ['POST'])
def thirtynine_add_director():
   genres = Genre.query.all()

   if request.method == 'POST' and t.verify(request.form['OEM-ADRT']):

       alert_msg = "เพิ่มชื่อผู้กำกับใหม่แล้ว"
       if request.form['CTS-ADRT'] == "series":
           addDirector(Series, int(request.form['CID-ADRT']), request.form['NDRT-ADRT'])
           return render_template('thirtynine.html', alert_msg=alert_msg, genres=genres, login=True)
       elif request.form['CTS-ADRT'] == "tvshow":
           addDirector(Tvshow, int(request.form['CID-ADRT']), request.form['NDRT-ADRT'])
           return render_template('thirtynine.html', alert_msg=alert_msg, genres=genres, login=True)
       elif request.form['CTS-ADRT'] == "movie":
           addDirector(Movie, int(request.form['CID-ADRT']), request.form['NDRT-ADRT'])
           return render_template('thirtynine.html', alert_msg=alert_msg, genres=genres, login=True)
       else:
           return render_template('thirtynine.html', alert_msg="ข้อมูลไม่ถูกต้อง", genres=genres, login=True)

   return '404'

def deleteGenre(name_genre):
    Genre.query.filter_by(name=name_genre).delete()
    db.session.commit()

@main.route('/thirtynine-delete-genre',methods = ['POST'])
def thirtynine_delete_genre():
   genres = Genre.query.all()

   if request.method == 'POST' and t.verify(request.form['OEM-DG']):
       deleteGenre(request.form['NAT-DG'])
       return render_template('thirtynine.html', alert_msg="ลบแนวเรื่องแล้ว", genres=genres, login=True)

   return '404'

def addGenre(table, row_id, genre):
    check = table.query.filter_by(id=row_id).first()
    genre_list = []
    genre_list.extend(check.genres)
    genre = genre.strip()
    genre_check = Genre.query.filter_by(name=genre).first()
    if genre_check is None:
        genre_data = Genre(name=genre)
        db.session.add(genre_data)
        genre_list.append(genre_data)
    else:
        genre_list.append(genre_check)
    check.genres = genre_list
    db.session.commit()

@main.route('/thirtynine-add-genre',methods = ['POST'])
def thirtynine_add_genre():
   genres = Genre.query.all()

   if request.method == 'POST' and t.verify(request.form['OEM-AG']):

       alert_msg = "เพิ่มแนวเรื่องแล้ว"
       if request.form['CTS-AG'] == "series":
           addGenre(Series, int(request.form['CID-AG']), request.form['NG-AG'])
           return render_template('thirtynine.html', alert_msg=alert_msg, genres=genres, login=True)
       elif request.form['CTS-AG'] == "tvshow":
           addGenre(Tvshow, int(request.form['CID-AG']), request.form['NG-AG'])
           return render_template('thirtynine.html', alert_msg=alert_msg, genres=genres, login=True)
       elif request.form['CTS-AG'] == "movie":
           addGenre(Movie, int(request.form['CID-AG']), request.form['NG-AG'])
           return render_template('thirtynine.html', alert_msg=alert_msg, genres=genres, login=True)
       else:
           return render_template('thirtynine.html', alert_msg="ข้อมูลไม่ถูกต้อง", genres=genres, login=True)

   return '404'

def addGenreEWGC(wrong_genre_name, replaced_genre_name):
    checks = Movie.query.filter(Movie.genres.any(Genre.name==wrong_genre_name)).all()
    checks.extend(Series.query.filter(Series.genres.any(Genre.name==wrong_genre_name)).all())
    checks.extend(Tvshow.query.filter(Tvshow.genres.any(Genre.name==wrong_genre_name)).all())

    genre_check = Genre.query.filter_by(name=replaced_genre_name).first()
    if genre_check is None:
        genre_check = Genre(name=genre)
        db.session.add(genre_check)

    for check in checks:
        genres = check.genres
        genres.append(genre_check)
        check.genres = genres

    db.session.commit()

@main.route('/thirtynine-add-genre-EWGC',methods = ['POST'])
def thirtynine_add_genre_EWGC():
   genres = Genre.query.all()

   if request.method == 'POST' and t.verify(request.form['OEM-AG-EWGC']):

       alert_msg = "ใส่แนวเรื่องใหม่ใน genre เก่าที่สะกดผิดแล้ว"
       addGenreEWGC(request.form['WG-AG-EWGC'], request.form['NG-AG-EWGC'])
       return render_template('thirtynine.html', alert_msg=alert_msg, genres=genres, login=True)

   return '404'

def removeGenre(table, row_id, remove_genre):
    check = table.query.filter_by(id=row_id).first()
    genre_list = []
    remove_genre = remove_genre.strip()
    for genre in check.genres:
        if genre.name != remove_genre:
            genre_list.append(genre)
    check.genres = genre_list
    db.session.commit()

@main.route('/thirtynine-remove-genre',methods = ['POST'])
def thirtynine_remove_genre():
   genres = Genre.query.all()

   if request.method == 'POST' and t.verify(request.form['OEM-RG']):

       alert_msg = "ลบแนวเรื่องแล้ว"
       if request.form['CTS-RG'] == "series":
           removeGenre(Series, int(request.form['CID-RG']), request.form['NG-RG'])
           return render_template('thirtynine.html', alert_msg=alert_msg, genres=genres, login=True)
       elif request.form['CTS-RG'] == "tvshow":
           removeGenre(Tvshow, int(request.form['CID-RG']), request.form['NG-RG'])
           return render_template('thirtynine.html', alert_msg=alert_msg, genres=genres, login=True)
       elif request.form['CTS-RG'] == "movie":
           removeGenre(Movie, int(request.form['CID-RG']), request.form['NG-RG'])
           return render_template('thirtynine.html', alert_msg=alert_msg, genres=genres, login=True)
       else:
           return render_template('thirtynine.html', alert_msg="ข้อมูลไม่ถูกต้อง", genres=genres, login=True)

   return '404'


def removeStudio(table, row_id, remove_studio):
    check = table.query.filter_by(id=row_id).first()
    studio_list = []
    remove_studio = remove_studio.strip()
    for studio in check.studio:
        if studio.name != remove_studio:
            studio_list.append(studio)
    check.studio = studio_list
    db.session.commit()

@main.route('/thirtynine-remove-studio',methods = ['POST'])
def thirtynine_remove_studio():
   genres = Genre.query.all()

   if request.method == 'POST' and t.verify(request.form['OEM-RSTD']):

       alert_msg = "ลบสตูดิโอแล้ว"
       if request.form['CTS-RSTD'] == "series":
           removeStudio(Series, int(request.form['CID-RSTD']), request.form['NG-RSTD'])
           return render_template('thirtynine.html', alert_msg=alert_msg, genres=genres, login=True)
       elif request.form['CTS-RSTD'] == "tvshow":
           removeStudio(Tvshow, int(request.form['CID-RSTD']), request.form['NG-RSTD'])
           return render_template('thirtynine.html', alert_msg=alert_msg, genres=genres, login=True)
       elif request.form['CTS-RSTD'] == "movie":
           removeStudio(Movie, int(request.form['CID-RSTD']), request.form['NG-RSTD'])
           return render_template('thirtynine.html', alert_msg=alert_msg, genres=genres, login=True)
       else:
           return render_template('thirtynine.html', alert_msg="ข้อมูลไม่ถูกต้อง", genres=genres, login=True)

   return '404'

def changeEPName(season_id, youtube_url, new_ep_name):
    check = Season.query.filter_by(id=season_id).first()
    for ep in check.episodes:
        if youtube_url == ep.youtube_url:
            ep_check = Episode.query.filter_by(id=ep.id).first()
            ep_check.title = new_ep_name
            break
    db.session.commit()


@main.route('/thirtynine-change-ep-name',methods = ['POST'])
def thirtynine_change_ep_name():
  genres = Genre.query.all()

  if request.method == 'POST' and t.verify(request.form['OEM-CEPN']):
      changeEPName(int(request.form['SSID-CEPN']), request.form['EURL-CEPN'], request.form['EPN-CEPN'])

      return render_template('thirtynine.html', alert_msg="เปลี่ยนชื่อ EP แล้ว", genres=genres, login=True)

  return '404'

def changeMovieYTURL(row_id, new_yt_url):
    check = Movie.query.filter_by(id=row_id).first()
    check.youtube_url = new_yt_url
    db.session.commit()

@main.route('/thirtynine-change-movie-yt-url',methods = ['POST'])
def thirtynine_change_movie_yt_url():
   genres = Genre.query.all()
   if request.method == 'POST' and t.verify(request.form['OEM-CMYT']):
       alert_msg = "เปลี่ยน movie youtube url แล้ว"
       changeMovieYTURL(int(request.form['CID-CMYT']), request.form['YTURL-CMYT'])
       return render_template('thirtynine.html', alert_msg=alert_msg, genres=genres, login=True)

   return '404'

def addStudio(table, row_id, studio):
    check = table.query.filter_by(id=row_id).first()
    studio_list = []
    studio_list.extend(check.studio)
    studio = studio.strip()
    studio_check = Studio.query.filter_by(name=studio).first()
    if studio_check is None:
        studio_data = Studio(name=studio)
        db.session.add(studio_data)
        studio_list.append(studio_data)
    else:
        studio_list.append(studio_check)
    check.studio = studio_list
    db.session.commit()

@main.route('/thirtynine-add-studio',methods = ['POST'])
def thirtynine_add_studio():
   genres = Genre.query.all()

   if request.method == 'POST' and t.verify(request.form['OEM-AS']):

       alert_msg = "เพิ่ม studio แล้ว"
       if request.form['CTS-AS'] == "series":
           addStudio(Series, int(request.form['CID-AS']), request.form['NS-AS'])
           return render_template('thirtynine.html', alert_msg=alert_msg, genres=genres, login=True)
       elif request.form['CTS-AS'] == "tvshow":
           addStudio(Tvshow, int(request.form['CID-AS']), request.form['NS-AS'])
           return render_template('thirtynine.html', alert_msg=alert_msg, genres=genres, login=True)
       elif request.form['CTS-AS'] == "movie":
           addStudio(Movie, int(request.form['CID-AS']), request.form['NS-AS'])
           return render_template('thirtynine.html', alert_msg=alert_msg, genres=genres, login=True)
       else:
           return render_template('thirtynine.html', alert_msg="ข้อมูลไม่ถูกต้อง", genres=genres, login=True)

   return '404'

def deleteStudio(name_studio):
    Studio.query.filter_by(name=name_studio).delete()
    db.session.commit()

@main.route('/thirtynine-delete-studio',methods = ['POST'])
def thirtynine_delete_studio():
   genres = Genre.query.all()

   if request.method == 'POST' and t.verify(request.form['OEM-DSTD']):
       deleteStudio(request.form['NSTD-DSTD'])
       return render_template('thirtynine.html', alert_msg="ลบแนวเรื่องแล้ว", genres=genres, login=True)

   return '404'

def deleteMultipleEPFromIndex(table, row_id, season_id, first_index, last_index):
    alert_msg = ""
    check = table.query.filter_by(id=row_id).first()
    for season in check.seasons:
        if season_id == season.id:
            print("eiei")
            episode_list = sorted(season.episodes, key=lambda episodes: episodes.id)
            for episode in episode_list[first_index-1:last_index]:
                Episode.query.filter_by(id=episode.id).delete()
                alert_msg += episode.title + ", "
                db.session.commit()
                print('kuy')
            return "ลบ EP " + alert_msg + " แล้ว"

@main.route('/thirtynine-delete-multiple-ep-from-index',methods = ['POST'])
def thirtynine_delete_multiple_ep_from_index():
  genres = Genre.query.all()

  if request.method == 'POST' and t.verify(request.form['OEM-DEPFI']):
      if request.form['CTS-DEPFI'] == "series":
          alert_msg = deleteMultipleEPFromIndex(Series, int(request.form['CID-DEPFI']), int(request.form['SSID-DEPFI']), int(request.form['FI-DEPFI']), int(request.form['LI-DEPFI']))
      elif request.form['CTS-DEPFI'] == "tvshow":
          alert_msg = deleteMultipleEPFromIndex(Tvshow, int(request.form['CID-DEPFI']), int(request.form['SSID-DEPFI']), int(request.form['FI-DEPFI']), int(request.form['LI-DEPFI']))

      return render_template('thirtynine.html', alert_msg=alert_msg, genres=genres, login=True)

  return '404'

def moveSingleEP(table_name, row_id, yt_url, season_id, ep_num):
    check = table_name.query.filter_by(id=row_id).first()
    episode_list = []

    for season in check.seasons:
        if season.id == season_id:
            episode_list.extend(season.episodes)

    #=============================================
    if episode_list != []:
        prev_ep = max(episode_list, key=lambda episodes: episodes.id)
    else:
        prev_ep = None
    randomIdCheck = True

    new_ep_id = ""
    while randomIdCheck == True:
        if prev_ep is None:
            new_ep_id = id_generator()
            ep_id_check = Episode.query.filter_by(id=int(new_ep_id)).first()
            if ep_id_check is None:
                randomIdCheck = False
        else:
            random_num = random.randint(0, 1000000)
            new_ep_id = int(random_num) + int(prev_ep.id)
            ep_id_check = Episode.query.filter_by(id=int(new_ep_id)).first()
            if ep_id_check is None:
                randomIdCheck = False
    #=============================================
    tmp_ep_obj = None
    for ep in episode_list:
        if ep.youtube_url == yt_url:
            tmp_ep_obj = ep
            break
    episode_list.remove(tmp_ep_obj)

    episode_data = Episode(id=int(new_ep_id), title=tmp_ep_obj.title, youtube_url=tmp_ep_obj.youtube_url)
    inserted_ep_id = episode_data.id
    db.session.add(episode_data)
    db.session.commit()

    episode_list = sorted(episode_list, key=lambda episodes: episodes.id)
    new_episode_list = []
    #=========================================
    if int(ep_num) == 1:
        new_episode_list = []
    else:
        new_episode_list.extend(episode_list[:ep_num-1])
    #=========================================
    prev_ep = inserted_ep_id
    for ep in episode_list[ep_num-1:]:
        tmp_ep_title = ep.title
        tmp_ep_yt_url = ep.youtube_url
        tmp_ep_id = ep.id
        Episode.query.filter_by(id=tmp_ep_id).delete()
        db.session.commit()
        #=========================================
        new_ep_id = ""
        randomIdCheck = True
        while randomIdCheck == True:
            if prev_ep is None:
                new_ep_id = id_generator()
                ep_id_check = Episode.query.filter_by(id=new_ep_id).first()
                if ep_id_check is None:
                    randomIdCheck = False
            else:
                random_num = random.randint(0, 1000000)
                new_ep_id = int(random_num) + int(prev_ep)
                ep_id_check = Episode.query.filter_by(id=new_ep_id).first()
                if ep_id_check is None:
                    randomIdCheck = False
        #=========================================
        episode_data = Episode(id=int(new_ep_id), title=tmp_ep_title, youtube_url=tmp_ep_yt_url)
        db.session.add(episode_data)
        db.session.commit()
        new_episode_list.append(episode_data)
        print(episode_data)
        prev_ep = new_ep_id

    episode_check = Episode.query.filter_by(id=inserted_ep_id).first()
    new_episode_list.append(episode_check)
    for season in check.seasons:
        if season.id == season_id:
            season.episodes = new_episode_list
    db.session.commit()

@main.route('/thirtynine-move-single-ep-order',methods = ['POST'])
def move_single_ep_order():
   genres = Genre.query.all()
   if request.method == 'POST' and t.verify(request.form['OEM-MSEP']):
          if request.form['CTS-MSEP'] == "series":
              moveSingleEP(Series, int(request.form['CID-MSEP']), request.form['YTU-MSEP'], int(request.form['SSID-MSEP']), int(request.form['NPO-MSEP']))
          elif request.form['CTS-MSEP'] == "tvshow":
              moveSingleEP(Tvshow, int(request.form['CID-MSEP']), request.form['YTU-MSEP'], int(request.form['SSID-MSEP']), int(request.form['NPO-MSEP']))
          return render_template('thirtynine.html', alert_msg="move single ep เรียบร้อยแล้ว", genres=genres, login=True)

   return '404'


def moveMultipleEP(table_name, row_id, season_id, first_order, last_order, ep_num):
    check = table_name.query.filter_by(id=row_id).first()
    episode_list = []

    for season in check.seasons:
        if season.id == season_id:
            episode_list.extend(season.episodes)

    if episode_list != []:
        prev_ep = max(episode_list, key=lambda episodes: episodes.id)
    else:
        prev_ep = None

    episode_list = sorted(episode_list, key=lambda episodes: episodes.id)

    moved_ep = []


    for ep in episode_list[first_order-1: last_order]:
        new_ep_id = ""
        randomIdCheck = True
        while randomIdCheck == True:
            if prev_ep is None:
                new_ep_id = id_generator()
                ep_id_check = Episode.query.filter_by(id=int(new_ep_id)).first()
                if ep_id_check is None:
                    randomIdCheck = False
            else:
                random_num = random.randint(0, 1000000)
                new_ep_id = int(random_num) + int(prev_ep.id)
                ep_id_check = Episode.query.filter_by(id=int(new_ep_id)).first()
                if ep_id_check is None:
                    randomIdCheck = False

        episode_list.remove(ep)

        episode_data = Episode(id=int(new_ep_id), title=ep.title, youtube_url=ep.youtube_url)
        inserted_ep_id = episode_data.id
        db.session.add(episode_data)
        db.session.commit()
        prev_ep = episode_data
        moved_ep.append(episode_data)

    episode_list = sorted(episode_list, key=lambda episodes: episodes.id)
    new_episode_list = []

    if ep_num < first_order:
        reduce_num = 1
    else:
        reduce_num = last_order - first_order + 1

    if int(ep_num) == 1:
        new_episode_list = []
    else:
        new_episode_list.extend(episode_list[:ep_num-reduce_num])

    prev_ep = inserted_ep_id
    for ep in episode_list[ep_num-reduce_num:]:
        tmp_ep_title = ep.title
        tmp_ep_yt_url = ep.youtube_url
        tmp_ep_id = ep.id
        Episode.query.filter_by(id=tmp_ep_id).delete()
        db.session.commit()

        new_ep_id = ""
        randomIdCheck = True
        while randomIdCheck == True:
            if prev_ep is None:
                new_ep_id = id_generator()
                ep_id_check = Episode.query.filter_by(id=new_ep_id).first()
                if ep_id_check is None:
                    randomIdCheck = False
            else:
                random_num = random.randint(0, 1000000)
                new_ep_id = int(random_num) + int(prev_ep)
                ep_id_check = Episode.query.filter_by(id=new_ep_id).first()
                if ep_id_check is None:
                    randomIdCheck = False

        episode_data = Episode(id=int(new_ep_id), title=tmp_ep_title, youtube_url=tmp_ep_yt_url)
        db.session.add(episode_data)
        db.session.commit()
        new_episode_list.append(episode_data)
        prev_ep = new_ep_id

    new_episode_list.extend(moved_ep)

    for season in check.seasons:
        if season.id == season_id:
            season.episodes = new_episode_list

    db.session.commit()

@main.route('/thirtynine-move-multiple-ep-order',methods = ['POST'])
def move_multiple_ep_order():
   genres = Genre.query.all()
   if request.method == 'POST' and t.verify(request.form['OEM-MMEP']):
          if request.form['CTS-MMEP'] == "series":
              moveMultipleEP(Series, int(request.form['CID-MMEP']), int(request.form['SSID-MMEP']), int(request.form['FO-MMEP']), int(request.form['LO-MMEP']),int(request.form['NPO-MMEP']))
          elif request.form['CTS-MMEP'] == "tvshow":
              moveMultipleEP(Tvshow, int(request.form['CID-MMEP']), int(request.form['SSID-MMEP']), int(request.form['FO-MMEP']), int(request.form['LO-MMEP']),int(request.form['NPO-MMEP']))
          return render_template('thirtynine.html', alert_msg="move multiple ep เรียบร้อยแล้ว", genres=genres, login=True)

   return '404'

def removeUpdate(table_name, row_id):
    check = table_name.query.filter_by(id=row_id).first()

    check.last_updated = datetime.datetime.now()
    db.session.commit()

@main.route('/thirtynine-remove-update',methods = ['POST'])
def thirtynine_remove_update():
   genres = Genre.query.all()
   if request.method == 'POST' and t.verify(request.form['OEM-RUD']):
          if request.form['CTS-RUD'] == "series":
              removeUpdate(Series, int(request.form['CID-RUD']))
          elif request.form['CTS-RUD'] == "tvshow":
              removeUpdate(Tvshow, int(request.form['CID-RUD']))
          return render_template('thirtynine.html', alert_msg="remove update เรียบร้อยแล้ว", genres=genres, login=True)

   return '404'

def addUpdate(table_name, row_id):
    check = table_name.query.filter_by(id=row_id).first()

    check.last_updated = datetime.datetime.now().replace(microsecond=999999)
    db.session.commit()

@main.route('/thirtynine-add-update',methods = ['POST'])
def thirtynine_add_update():
   genres = Genre.query.all()
   if request.method == 'POST' and t.verify(request.form['OEM-AUD']):
          if request.form['CTS-AUD'] == "series":
              addUpdate(Series, int(request.form['CID-AUD']))
          elif request.form['CTS-AUD'] == "tvshow":
              addUpdate(Tvshow, int(request.form['CID-AUD']))
          return render_template('thirtynine.html', alert_msg="add update เรียบร้อยแล้ว", genres=genres, login=True)
   return '404'

def insertPlaylist(table_name, row_id, season_id, yt_playlist_url, ep_num, yt_playlist_xml, keyword):
    check = table_name.query.filter_by(id=row_id).first()
    episode_list = []

    for season in check.seasons:
        if season.id == season_id:
            episode_list.extend(season.episodes)

    #=============================================
    if episode_list != []:
        prev_ep = max(episode_list, key=lambda episodes: episodes.id)
    else:
        prev_ep = None


    r = bytes(yt_playlist_xml, 'utf-8')
    soup = BeautifulSoup(r, 'html.parser')
    items = soup.findAll('script')
    ytJson = ""

    inserted_ep_playlist = []

    for item in items:
        result = str(item).find(keyword)
        if result != -1:
            ytJson = item.text[:-1]
            ytJson = ytJson.replace("var ytInitialData = ", "")
            ytJson = json.loads(ytJson)
            ytJson = ytJson["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][0]["tabRenderer"]["content"]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"][0]["playlistVideoListRenderer"]["contents"]

            for ytContent in ytJson[:100]:
                randomIdCheck = True
                new_ep_id = ""
                while randomIdCheck == True:
                    if prev_ep is None:
                        new_ep_id = id_generator()
                        ep_id_check = Episode.query.filter_by(id=int(new_ep_id)).first()
                        if ep_id_check is None:
                            randomIdCheck = False
                    else:
                        random_num = random.randint(0, 1000000)
                        new_ep_id = int(random_num) + int(prev_ep.id)
                        ep_id_check = Episode.query.filter_by(id=int(new_ep_id)).first()
                        if ep_id_check is None:
                            randomIdCheck = False
                episode_data = Episode(id=int(new_ep_id), title=ytContent["playlistVideoRenderer"]["title"]["runs"][0]["text"], youtube_url=ytContent["playlistVideoRenderer"]["videoId"])
                db.session.add(episode_data)
                inserted_ep_playlist.append(episode_data)
                prev_ep = episode_data
                inserted_ep_id = episode_data.id

    episode_list = sorted(episode_list, key=lambda episodes: episodes.id)
    new_episode_list = []
    #=========================================

    if int(ep_num) == 1:
        new_episode_list = []
    else:
        new_episode_list.extend(episode_list[:ep_num-1])
    #=========================================
    prev_ep = inserted_ep_id
    for ep in episode_list[ep_num-1:]:
        tmp_ep_title = ep.title
        tmp_ep_yt_url = ep.youtube_url
        tmp_ep_id = ep.id
        Episode.query.filter_by(id=tmp_ep_id).delete()
        db.session.commit()
        #=========================================
        new_ep_id = ""
        randomIdCheck = True
        while randomIdCheck == True:
            if prev_ep is None:
                new_ep_id = id_generator()
                ep_id_check = Episode.query.filter_by(id=new_ep_id).first()
                if ep_id_check is None:
                    randomIdCheck = False
            else:
                random_num = random.randint(0, 1000000)
                new_ep_id = int(random_num) + int(prev_ep)
                ep_id_check = Episode.query.filter_by(id=new_ep_id).first()
                if ep_id_check is None:
                    randomIdCheck = False
        #=========================================
        episode_data = Episode(id=int(new_ep_id), title=tmp_ep_title, youtube_url=tmp_ep_yt_url)
        db.session.add(episode_data)
        db.session.commit()
        new_episode_list.append(episode_data)
        prev_ep = new_ep_id

    new_episode_list.extend(inserted_ep_playlist)
    for season in check.seasons:
        if season.id == season_id:
            season.episodes = new_episode_list
    db.session.commit()

@main.route('/thirtynine-insert-playlist',methods = ['POST'])
def thirtynine_insert_playlist():
   genres = Genre.query.all()
   if request.method == 'POST' and t.verify(request.form['OEM-IPL']):
          if request.form['CTS-IPL'] == "series":
              insertPlaylist(Series, int(request.form['CID-IPL']), int(request.form['SSID-IPL']), request.form['YTPU-IPL'], int(request.form['PO-IPL']), request.form['YTPL-IPL-XML'], request.form['KW-IPL'])
          elif request.form['CTS-IPL'] == "tvshow":
              insertPlaylist(Tvshow, int(request.form['CID-IPL']), int(request.form['SSID-IPL']), request.form['YTPU-IPL'], int(request.form['PO-IPL']), request.form['YTPL-IPL-XML'], request.form['KW-IPL'])
          return render_template('thirtynine.html', alert_msg="แทรก playlist เรียบร้อยแล้ว", genres=genres, login=True)

   return '404'

import csv
@main.route('/feedback',methods = ['POST'])
def feedback():
    if request.method == 'POST':
        data = request.json
        data = [data['feedbackFormControlInput'], data['feedbackFormControlTextarea']]
        with open('main/support_data.csv', 'a+', newline='', encoding='UTF8') as f:
            writer = csv.writer(f)
            writer.writerow(data)
        return jsonify({'response': '200'})

def changeDescription(table_name, row_id, new_description):
    check = table_name.query.filter_by(id=row_id).first()
    check.description = new_description
    db.session.commit()

@main.route('/thirtynine-change-description',methods = ['POST'])
def thirtynine_change_description():
   genres = Genre.query.all()
   if request.method == 'POST' and t.verify(request.form['OEM-CDS']):

       alert_msg = "เปลี่ยน description แล้ว"
       if request.form['CTS-CDS'] == "series":
           changeDescription(Series, int(request.form['CID-CDS']), request.form['NDS-CDS'])
           return render_template('thirtynine.html', alert_msg=alert_msg, genres=genres, login=True)
       elif request.form['CTS-CDS'] == "tvshow":
           changeDescription(Tvshow, int(request.form['CID-CDS']), request.form['NDS-CDS'])
           return render_template('thirtynine.html', alert_msg=alert_msg, genres=genres, login=True)
       elif request.form['CTS-CDS'] == "movie":
           changeDescription(Movie, int(request.form['CID-CDS']), request.form['NDS-CDS'])
           return render_template('thirtynine.html', alert_msg=alert_msg, genres=genres, login=True)
       else:
           return render_template('thirtynine.html', alert_msg="ข้อมูลไม่ถูกต้อง", genres=genres, login=True)

   return '404'

def create_post(title, content, thumbnail, genres, actors):

    randomIdCheck = True
    new_post_id = ""
    while randomIdCheck == True:
        new_post_id = id_generator()
        post_id_check = Post.query.filter_by(id=new_post_id).first()
        if post_id_check is None:
            randomIdCheck = False

    file_exists = exists(os.path.join('./main/static/post/thumbnail',thumbnail.filename))
    while file_exists:
        file_extension = thumbnail.filename.split(".")
        thumbnail.filename = id_generator() + "." + str(file_extension[-1])
        file_exists = exists(os.path.join('./main/static/post/thumbnail',thumbnail.filename))

    thumbnail.save(os.path.join('./main/static/post/thumbnail',thumbnail.filename))

    genres = genres.split(",")
    genre_list = []
    for genre in genres:
        genre = genre.strip()
        if genre == "":
            continue
        genre_check = Genre.query.filter_by(name=genre).first()
        if genre_check is None:
            genre_data = Genre(name=genre)
            db.session.add(genre_data)
            genre_list.append(genre_data)
        else:
            genre_list.append(genre_check)

    actors = actors.split(",")
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

    post_data = Post(id=int(new_post_id),title=str(title), content=str(content), genres=genre_list, actors=actor_list, thumbnail=str(thumbnail.filename), date_posted=datetime.datetime.now())
    db.session.add(post_data)
    db.session.commit()

@main.route('/thirtynine-create-post',methods = ['POST'])
def thirtynine_create_post():
   genres = Genre.query.all()
   if request.method == 'POST' and t.verify(request.form['OEM-TCP']):
       create_post(request.form['TT-TCP'], request.form['EDT-TCP'], request.files['IOC-TCP'], request.form['G-TCP'], request.form['AT-TCP'])
       return render_template('thirtynine.html', alert_msg="เพิ่ม blog ใหม่แล้ว", genres=genres, login=True)

   return '404'

def delete_post(post_id):
    Post.query.filter_by(id=post_id).delete()
    db.session.commit()

@main.route('/thirtynine-delete-post',methods = ['POST'])
def thirtynine_delete_post():
   genres = Genre.query.all()
   if request.method == 'POST' and t.verify(request.form['OEM-DB']):
       delete_post(int(request.form['BID-DB']))
       return render_template('thirtynine.html', alert_msg="ลบ blog แล้ว", genres=genres, login=True)

   return '404'

def update_post(blog_id, title, content, genres, actors):

    post = Post.query.filter_by(id=blog_id).first()

    genres = genres.split(",")
    genre_list = []
    for genre in genres:
        genre = genre.strip()
        if genre == "":
            continue
        genre_check = Genre.query.filter_by(name=genre).first()
        if genre_check is None:
            genre_data = Genre(name=genre)
            db.session.add(genre_data)
            genre_list.append(genre_data)
        else:
            genre_list.append(genre_check)

    actors = actors.split(",")
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

    post.title = title
    post.content = content
    post.genres = genre_list
    post.actors = actor_list

    db.session.commit()

@main.route('/thirtynine-update-post',methods = ['POST'])
def thirtynine_update_post():
   genres = Genre.query.all()
   if request.method == 'POST' and t.verify(request.form['OEM-TUP']):
       update_post(request.form['BID-TUP'], request.form['TT-TUP'], request.form['EDT-TUP'], request.form['G-TUP'], request.form['AT-TUP'])
       return render_template('thirtynine.html', alert_msg="อัพเดท blog ใหม่แล้ว", genres=genres, login=True)

   return '404'

def get_blog_content(blog_id):
    post = Post.query.filter_by(id=blog_id).first()
    genre_str = ""
    for genre in post.genres:
        if genre != post.genres[-1]:
            genre_str += genre.name + ","
        else:
            genre_str += genre.name

    actor_str = ""
    for actor in post.actors:
        if actor != post.actors[-1]:
            actor_str += actor.name + ","
        else:
            actor_str += actor.name

    post_json = {"id": blog_id, "title": str(post.title), "content": str(post.content), "actor": actor_str, "genre": genre_str}
    return post_json



@main.route('/thirtynine-get-blog-content')
def thirtynine_get_blog_content():
   if request.args:
       BID = int(request.args.get("BID"))
       OEM = int(request.args.get("OEM"))
       if request.method == 'GET' and t.verify(int(OEM)):
           res = make_response(jsonify(get_blog_content(BID)), 200)
           return res
   return '404'

@main.route('/thirtynine-change-thumbnail-post',methods = ['POST'])
def thirtynine_change_thumbnail_post():
   genres = Genre.query.all()
   if request.method == 'POST' and t.verify(request.form['OEM-CTP']):
       thumbnail = request.files['IOC-CTP']

       file_exists = exists(os.path.join('./main/static/post/thumbnail',thumbnail.filename))
       while file_exists:
           file_extension = thumbnail.filename.split(".")
           thumbnail.filename = id_generator() + "." + str(file_extension[-1])
           file_exists = exists(os.path.join('./main/static/post/thumbnail',thumbnail.filename))
       thumbnail.save(os.path.join('./main/static/post/thumbnail',thumbnail.filename))

       post = Post.query.filter_by(id=int(request.form['BID-CTP'])).first()
       post.thumbnail = thumbnail.filename

       db.session.commit()

       return render_template('thirtynine.html', alert_msg="เปลี่ยน thumbnail blog แล้ว", genres=genres, login=True)

   return '404'

def duplicate_blog_post(blog_id, amount):
    post = Post.query.filter_by(id=blog_id).first()
    i = 0
    for i in range(0, amount):
        new_post_id = ""
        randomIdCheck = True
        new_post_id = ""
        while randomIdCheck == True:
            new_post_id = id_generator()
            post_id_check = Post.query.filter_by(id=new_post_id).first()
            if post_id_check is None:
                randomIdCheck = False
        post_data = Post(id=int(new_post_id),title=str(post.title), content=str(post.content), genres=post.genres, actors=post.actors, thumbnail=str(post.thumbnail), date_posted=datetime.datetime.now())
        db.session.add(post_data)
        db.session.commit()


@main.route('/thirtynine-duplicate-post',methods = ['POST'])
def thirtynine_duplicate_post():
   genres = Genre.query.all()
   if request.method == 'POST' and t.verify(request.form['OEM-TDP']):
       duplicate_blog_post(int(request.form['BID-TDP']), int(request.form['A-TDP']))

       return render_template('thirtynine.html', alert_msg="duplicate post succeed", genres=genres, login=True)

   return '404'

import secrets
def save_picture(pic):
    """Save blog picture."""
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(pic.filename)
    pic_fn = random_hex + f_ext
    pic_path = os.path.join('./main/static/post/thumbnail/', pic_fn)

    pic.save(pic_path)

    return pic_fn

@main.route('/thirtynine-upload-blog-image', methods = ['POST'])
def thirtynine_upload_blog_image():

    if request.method == 'POST':

            f = request.files['image']

            new_file_name = save_picture(f)
            return '/static/post/thumbnail/' + new_file_name

def get_season_list(content_id, type):
    if type == "series":
        seasons = Series.query.filter_by(id=content_id).first().seasons
    elif type == "tvshow":
        seasons = Tvshow.query.filter_by(id=content_id).first().seasons

    season_json_list = []
    for season in seasons:
        season_json_list.append({"id": str(season.id), "name": season.season_title})
    return season_json_list



@main.route('/thirtynine-get-season-list')
def thirtynine_get_season_list():
   if request.args:
       SID = int(request.args.get("SID"))
       OEM = int(request.args.get("OEM"))
       CTS = request.args.get("CTS")
       if request.method == 'GET' and t.verify(OEM):
           res = make_response(jsonify(get_season_list(SID, CTS)), 200)
           return res
   return '404'

@main.route('/thirtynine-insert-season',methods = ['POST'])
def thirtynine_insert_season():
   genres = Genre.query.all()

   if request.method == 'POST' and t.verify(request.form['OEM-IS2']):
       if request.form['RL-IS'] == "true":
           RL_IS = True
       elif request.form['RL-IS'] == "false":
           RL_IS = False

       if request.form['CTS-IS2'] == "series":
           alert_msg = insert_season(Series, int(request.form['CID-IS2']), request.form['K-IS'], request.form['SSTT-IS'], request.form['YT-IS'], request.form['PY-IS'], RL_IS, str(request.form['SSYT-IS-XML']), int(request.form['SS-IS']))
       elif request.form['CTS-IS2'] == "tvshow":
           alert_msg = insert_season(Tvshow, int(request.form['CID-IS2']), request.form['K-IS'], request.form['SSTT-IS'], request.form['YT-IS'], request.form['PY-IS'], RL_IS, str(request.form['SSYT-IS-XML']), int(request.form['SS-IS']))

       return render_template('thirtynine.html', alert_msg=alert_msg, genres=genres, login=True)
   return '404'

def insert_season(table_name, row_id, keyword, season_title, yt_playlist_url, published_year, reverse_loop, yt_playlist_xml, before_season_id):
    check = table_name.query.filter_by(id=row_id).first()

    r = bytes(yt_playlist_xml, 'utf-8')
    soup = BeautifulSoup(r, 'html.parser')
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
                prev_ep = None
                for ytContent in reversed(ytJson[:100]):
                    new_ep_id = ""
                    randomIdCheck = True
                    if 'playlistVideoRenderer' in ytContent:
                        while randomIdCheck == True:
                            if prev_ep is None:
                                new_ep_id = id_generator()
                                ep_id_check = Episode.query.filter_by(id=new_ep_id).first()
                                if ep_id_check is None:
                                    randomIdCheck = False
                            else:
                                random_num = random.randint(0, 1000000)
                                new_ep_id = int(random_num) + int(prev_ep)
                                ep_id_check = Episode.query.filter_by(id=new_ep_id).first()
                                if ep_id_check is None:
                                    randomIdCheck = False
                        episode_data = Episode(id=int(new_ep_id), title=ytContent["playlistVideoRenderer"]["title"]["runs"][0]["text"], youtube_url=ytContent["playlistVideoRenderer"]["videoId"])
                        db.session.add(episode_data)
                        episode_list.append(episode_data)
                        print(episode_data)
                        prev_ep = new_ep_id

            else:
                prev_ep = None
                for ytContent in ytJson[:100]:
                    new_ep_id = ""
                    randomIdCheck = True
                    if 'playlistVideoRenderer' in ytContent:
                        while randomIdCheck == True:
                            if prev_ep is None:
                                new_ep_id = id_generator()
                                ep_id_check = Episode.query.filter_by(id=new_ep_id).first()
                                if ep_id_check is None:
                                    randomIdCheck = False
                            else:
                                random_num = random.randint(0, 1000000)
                                new_ep_id = int(random_num) + int(prev_ep)
                                ep_id_check = Episode.query.filter_by(id=new_ep_id).first()
                                if ep_id_check is None:
                                    randomIdCheck = False
                        episode_data = Episode(id=int(new_ep_id), title=ytContent["playlistVideoRenderer"]["title"]["runs"][0]["text"], youtube_url=ytContent["playlistVideoRenderer"]["videoId"])
                        db.session.add(episode_data)
                        episode_list.append(episode_data)
                        print(episode_data)
                        prev_ep = new_ep_id

    season_list = []
    for season in check.seasons:
        if season.episodes is not None:
            season_list.append(season)

    previous_season_id = None
    next_season_id = before_season_id
    season_list = sorted(season_list, key=lambda season: season.id)

    if len(season_list) == 1:
        previous_season_id = 0
    elif season_list[0].id == next_season_id:
        previous_season_id = 0
    else:
        for season in season_list:
            if previous_season_id == None:
                previous_season_id = season.id
                continue
            else:
                if season.id != next_season_id:
                    previous_season_id = season.id
                    continue
                break

    randomIdCheck = True

    while randomIdCheck == True:
      new_season_id = random.randint(previous_season_id, next_season_id)
      season_id_check = Season.query.filter_by(id=new_season_id).first()
      if season_id_check is None:
          randomIdCheck = False

    if episode_list == []:
        return "keyword ผิดพลาด"

    season_data = Season(id=int(new_season_id),season_title=season_title, yt_playlist_url=yt_playlist_url, episodes=episode_list, published_year=published_year)
    db.session.add(season_data)
    season_list.append(season_data)
    check.seasons = season_list
    db.session.commit()

    return "insert season แล้ว"
