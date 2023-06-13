
@main.route('/genre/<genre_id>/<genre_list_group_scroll_position>')
def existed_genre_list_group_redirect(genre_id, genre_list_group_scroll_position):
    url = "/genre/" + genre_id + "/" + genre_list_group_scroll_position  + "/page/1"
    return redirect(url)


@main.route('/genre/<genre_id>/<genre_list_group_scroll_position>/page/<curr_page>')
def existed_genre_list_group(genre_id, genre_list_group_scroll_position, curr_page):
    movies = []
    continue_content_arr = []
    if genre_id == "new-release":
        new_movies = Movie.query.order_by(desc(Movie.last_updated)).all()
        new_series = Series.query.order_by(desc(Series.last_updated)).all()
        new_tvshow = Tvshow.query.order_by(desc(Tvshow.last_updated)).all()
        movies.extend(new_movies)
        movies.extend(new_series)
        movies.extend(new_tvshow)
        title = "ใหม่และล่าสุด"
        genre_name = "ใหม่และล่าสุด"
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
        genre_name = "ยังไม่จบ"
    elif genre_id == "completed":
        series = Series.query.filter_by(state=True).all()
        tvshow = Tvshow.query.filter_by(state=True).all()
        title = "จบแล้ว"
        movies.extend(series)
        movies.extend(tvshow)
        genre_name = "จบแล้ว"

    elif genre_id == "continue-content":
        continue_content_arr = get_continued_watching_content_of_all_genre()
        title="ดูเนื้อหาต่อ สำหรับ คุณ"
        genre_name = "ดูต่อ"

    elif genre_id.isdigit() is not True:
        genre = Genre.query.filter(Genre.name == genre_id).first()
        if genre is not None:
            genre_id = genre.id
            return redirect(url_for('main.existed_genre_list_group', genre_id=genre_id, genre_list_group_scroll_position=genre_list_group_scroll_position))
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
        url = '/genre/' + genre_id + '/' + genre_list_group_scroll_position + '/page/' + curr_page
    else:
        num_page = check_num_page(movies)
        movies = get_content_in_each_page(movies, curr_page)
        url = '/genre/' + genre_id + '/' + genre_list_group_scroll_position + '/page/' + curr_page


    return render_template('genre.html', movies=movies, title=title, genre_name=genre_name, genre_list_group=genre_list_group, genre_list_group_scroll_position=genre_list_group_scroll_position, continue_content_arr=continue_content_arr, curr_page=int(curr_page), url=url, num_page=num_page)
