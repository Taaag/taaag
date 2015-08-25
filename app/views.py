import json

from facebook import get_user_from_cookie, GraphAPI
from flask import g, render_template, redirect, request, session, url_for, jsonify, abort

from app import app, db
from app.models import User, Tag, Tagging
from app.api import apis, APIException, views
from app.utils import clear_friends_cache

# Facebook app details
FB_APP_ID = '687248731410966'
FB_APP_NAME = 'Taaag'
FB_APP_SECRET = '***REMOVED***'


@app.route('/', methods=['GET', 'POST'])
def index():
    # If a user was set in the get_current_user function before the request,
    # the user is logged in.
    if g.user:
        return render_template('base.html', app_id=FB_APP_ID,
                               app_name=FB_APP_NAME)
    # Otherwise, a user is not logged in.
    return render_template('login.html', app_id=FB_APP_ID, name=FB_APP_NAME)


@app.route('/test_login')
def test_login():
    return render_template('login.html', app_id=FB_APP_ID, name=FB_APP_NAME)


@app.route('/test_filter', methods=['GET'])
def test_filter():
    taggees = Tag.get_by_name('haha').get_taggees_filtered([10206287264593411])
    return render_template('test_filter.html', a=taggees)


@app.route('/api/<method>', methods=['GET'])
def api(method):
    if not g.user:
        abort(403)
    if method in apis:
        try:
            return jsonify({'succeed': True, 'response': apis[method](g.user, request.args)})
        except APIException as e:
            return jsonify({'succeed': False, 'message': e.message})
    return jsonify({'message': 'API endpoint is working!'})


@app.route('/change_view/<view_type>', methods=['GET'])
def view(view_type):
    if not g.user:
        abort(403)
    if view_type in views:
        try:
            return views[view_type](g.user, request.args)
        except APIException as e:
            return e.message


@app.before_request
def get_current_user():
    if not session.get('user'):
        result = get_user_from_cookie(cookies=request.cookies, app_id=FB_APP_ID,
                                      app_secret=FB_APP_SECRET)
        if result:
            user = User.get_by_id(result['uid'])
            if not user:
                graph = GraphAPI(result['access_token'])
                profile = graph.get_object('me', fields='link,name,id')
                access_token = graph.extend_access_token(FB_APP_ID, FB_APP_SECRET)

                user = User.create(id=profile['id'], name=profile['name'],
                                   profile_url=profile['link'],
                                   access_token=access_token['access_token'])
                clear_friends_cache(user)

            session['user'] = user.id

    g.uid = session.get('user')
    g.user = User.get_by_id(g.uid) if g.uid else None

    if not g.user:
        session['user'] = ''
