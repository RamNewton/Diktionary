from flask import render_template, flash, redirect, url_for, request, make_response
from flask_login import current_user, login_required
from app import db
from app.main import bp
from app.models import User, Favorites
from app.main.forms import SearchForm
import urllib.request, json 
from config import KEY

API_Request = 'https://www.dictionaryapi.com/api/v3/references/thesaurus/json/{}?key='+KEY

@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html')

@bp.route('/profile')
@login_required
def profile():
    id = current_user.id
    user = User.query.filter_by(id=id).first()
    favorites = Favorites.query.filter_by(user_id=id).all()
    num = str(len(favorites))
    name = user.firstname + " " + user.lastname
    return render_template('profile.html', title = 'Profile', name = name, user = user, num = num)

@bp.route('/favorites')
@login_required
def favorites():
    favorites = Favorites.query.filter_by(user_id = current_user.id).all()
    cards = []
    for item in favorites:
        tmp = {}
        tmp['word'] = item.word.capitalize()
        tmp['meanings'] = []
        data = fetch_meaning(item.word)
        cnt = 0
        for meaning in data:
            single_meaning = {}
            single_meaning['part'] = meaning['fl']
            single_meaning['def'] = meaning['shortdef'][0]
            tmp['meanings'].append(single_meaning)
            cnt+=1
            if cnt >= 2:
                break
        cards.append(tmp)
    
    rows_of_cards = []
    for i in range(0, len(cards), 3):
        rows_of_cards.append(cards[i:i+3])
    print(rows_of_cards)

    return render_template('favorites.html', title = 'Favorites', favorites = favorites, rows = rows_of_cards)


def fetch_meaning(word):
    req = API_Request.format(word.replace(" ", "%20"))
    url = urllib.request.urlopen(req)
    data = json.loads(url.read().decode())
    return data


@bp.route('/search', methods = ['POST', 'GET'])
@login_required
def search():
    form = SearchForm()
    dne = False
    data = None
    is_favorite = False
    word = ""
    favorites = Favorites.query.filter_by(user_id = current_user.id).all()

    if form.validate_on_submit():
        word = form.word.data
        data = fetch_meaning(word)
        
        try:
            tmp = data[0]['shortdef'][0]
            for item in favorites:
                if item.word == word:
                    is_favorite = True
                    break
        except:
            dne = True
        
        resp = make_response(render_template('search.html', title = 'Search', form = form, is_favorite = is_favorite, dne = dne, data = data, word = word))
        if not dne:
            resp.set_cookie('word', word)
        return resp
    
    if 'word' in request.cookies:
        word = request.cookies.get('word')
    form.word.data = word
    data = fetch_meaning(word)
    for item in favorites:
        if item.word == word:
            is_favorite = True
            break

    return render_template('search.html', title = 'Search', form = form, is_favorite = is_favorite, dne = dne, data = data, word = word)


@bp.route('/AddToFavorites/<word>', methods = ['GET'])
@login_required
def add_to_favorites(word):
    tmp = Favorites.query.filter_by(user_id = current_user.id, word = word).all()
    if len(tmp) == 0:
        entry = Favorites(user_id = current_user.id, word = word)
        db.session.add(entry)
        db.session.commit()
        flash('Added ' + word + ' to favorites')
    else:
        flash(word + 'already in favorites')
    return redirect(url_for('main.search'))

@bp.route('/RemoveFromFavorites/<word>', methods = ['GET'])
@login_required
def remove_from_favorites(word):
    entry = Favorites.query.filter_by(user_id = current_user.id, word = word).first()
    db.session.delete(entry)
    db.session.commit()
    flash('Removed ' + word + ' from favorites')
    return redirect(url_for('main.search'))