from facebook import get_user_from_cookie, GraphAPI
from flask import g, render_template, redirect, request, session, url_for, jsonify

from app import app, db
from app.models import User, Tag, Tagging

from app.utils import get_user_friends

# Facebook app details
FB_APP_ID = '687248731410966'
FB_APP_NAME = 'Taaag'
FB_APP_SECRET = '***REMOVED***'


@app.route('/', methods=['GET', 'POST'])
def index():
    # If a user was set in the get_current_user function before the request,
    # the user is logged in.
    if g.user:
        return render_template('index.html', app_id=FB_APP_ID,
                               app_name=FB_APP_NAME, user_name=g.user,
                               friends=get_user_friends(g.user.access_token))
    # Otherwise, a user is not logged in.
    return render_template('login.html', app_id=FB_APP_ID, name=FB_APP_NAME)


@app.route('/api', methods=['GET'])
def api():
    supported_apis = {
        'tag': {'all': api_tag_all,
                'search': api_tag_search,
                'insert': api_tag_insert}
    }
    target = request.args.get('target', '')
    method = request.args.get('method', '')
    payload = request.args.get('payload', '')
    if target in supported_apis and method in supported_apis[target]:
        return jsonify(supported_apis[target][method](payload))

    return jsonify({'message': 'API endpoint is working!'})


def api_tag_all(payload):
    return {'response': [_.to_dict() for _ in Tag.all_tags() or []]}


def api_tag_search(payload):
    return {'response': [_.to_dict() for _ in Tag.query_tags_by_name(payload).all() or []]}


def api_tag_insert(payload):
    tag = Tag(name=payload)
    db.session.add(tag)
    db.session.commit()
    return {'response': tag.to_dict()}


@app.route('/test')
def test():
    return render_template('test.html')


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

                new_user = User(id=profile['id'], name=profile['name'],
                            profile_url=profile['link'],
                            access_token=access_token['access_token'])
                new_user.insert()
            session['user'] = user.id

    g.uid = session.get('user', None)
    g.user = User.get_by_id(g.uid) if g.uid else None
