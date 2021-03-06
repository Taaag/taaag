import base64

from facebook import get_user_from_cookie, GraphAPI, parse_signed_request
import requests

from flask import g, render_template, request, session, jsonify, abort, Response, redirect
from app import app
from app.models import User
from app.api import apis, APIException, views, public_cloud
from app.utils import clear_friends_cache


# Facebook app details
FB_APP_ID = app.config['FB_APP_ID']
FB_APP_NAME = app.config['FB_APP_NAME']
FB_APP_SECRET = app.config['FB_APP_SECRET']


@app.route('/', methods=['GET', 'POST'])
def index():
    # If a user was set in the get_current_user function before the request,
    # the user is logged in.
    if g.user and (g.user.id == 0 or g.user.friends_api_authorized()):
        return render_template('base.html', app_id=FB_APP_ID, app_name=FB_APP_NAME, new_user=g.get('new_user', False))
    # Otherwise, a user is not logged in.
    session['user'] = ''
    return render_template('login.html', app_id=FB_APP_ID, name=FB_APP_NAME, user_name=g.user.name if g.user else None)


@app.route('/api/<method>', methods=['GET'])
def api(method):
    if not g.user:
        abort(403)
    if method in apis:
        try:
            return jsonify({'succeed': True, 'response': apis[method](g.user, request.args)})
        except APIException as e:
            return jsonify({'succeed': False, 'message': e.message})
        except (ValueError, KeyError):
            abort(400)
        except Exception as e:
            return jsonify({'succeed': False, 'message': 'Internal Server Error'})
    return jsonify({'message': 'API endpoint is working!'})


@app.route('/change_view/<view_type>', methods=['GET'])
def view(view_type):
    if not g.user:
        abort(403)
    if view_type in views:
        try:
            return views[view_type](g.user, request.args)
        except (ValueError, KeyError):
            abort(400)
        except APIException as e:
            return e.message
        except Exception as e:
            return 'Internal Server Error'
    abort(400)


@app.route('/image_proxy/<uid>', methods=['GET'])
def image_proxy(uid):
    if uid == '0':
        return redirect('https://taaag.sshz.org/static/images/poo-head-s.png')
    else:
        url = 'https://graph.facebook.com/%s/picture?width=100&height=100' % uid
    r = requests.get(url, stream=True, params=request.args)
    headers = dict(r.headers)

    def generate():
        for chunk in r.iter_content(1024):
            yield chunk

    return Response(generate(), headers=headers)


@app.route('/store_image/', methods=['POST'])
def store_image():
    if not g.user:
        abort(403)
    data = request.form['data'].encode('ascii')
    if data.find(b'data:image/png;base64,') == 0:
        data = data.replace(b'data:image/png;base64,', b'')
        payload = {'file': ('cloud.png', base64.b64decode(data), 'image/png')}
        values = {'access_token': g.user.access_token}
        r = requests.post("https://graph.facebook.com/me/staging_resources", files=payload, data=values)

        def generate():
            for chunk in r.iter_content(1024):
                yield chunk

        return Response(generate(), headers=dict(r.headers))
    else:
        abort(400)


@app.route('/tag_cloud/<uid>', methods=['GET'])
def tag_cloud(uid):
    user = User.get_by_id(uid)
    if not user:
        abort(403)
    return public_cloud(user)


@app.route('/deauthorize_callback/', methods=['POST'])
def deauthorize_callback():
    signed_request = request.form['signed_request']
    data = parse_signed_request(signed_request, app_secret=FB_APP_SECRET)
    uid = data['user_id']
    user = User.get_by_id(uid)
    clear_friends_cache(user)
    user.delete()
    return ''


@app.before_request
def get_current_user():
    if not session.get('user'):
        result = get_user_from_cookie(cookies=request.cookies, app_id=FB_APP_ID,
                                      app_secret=FB_APP_SECRET)
        if result:
            graph = GraphAPI(result['access_token'])
            profile = graph.get_object('me', fields='link,name,id')
            access_token = graph.extend_access_token(FB_APP_ID, FB_APP_SECRET)['access_token']
            user = User.get_by_id(result['uid'])
            if not user:
                user = User.create(id=profile['id'], name=profile['name'],
                                   profile_url=profile['link'],
                                   access_token=access_token)
                clear_friends_cache(user)
                user.add_default_tag()
                g.new_user = True
            else:
                user.access_token = access_token
                user.update()

            session['user'] = user.id

    g.uid = session.get('user')
    g.user = User.get_by_id(g.uid) if g.uid else None

    if not g.user:
        session['user'] = ''
