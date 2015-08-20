from facebook import get_user_from_cookie, GraphAPI
from flask import g, render_template, redirect, request, session, url_for, jsonify, abort

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
                               app_name=FB_APP_NAME, user=g.user,
                               friends=get_user_friends(g.user.access_token))
    # Otherwise, a user is not logged in.
    return render_template('login.html', app_id=FB_APP_ID, name=FB_APP_NAME)


@app.route('/api', methods=['GET'])
def api():
    if not g.user:
        abort(403)
    supported_apis = {
        'tag': {'all': api_tag_all,
                'search': api_tag_search,
                'insert': api_tag_insert}
    }
    target = request.args.get('target', '')
    method = request.args.get('method', '')
    payload = request.args.get('payload', '')
    if target in supported_apis and method in supported_apis[target]:
        return jsonify(supported_apis[target][method](g.user, payload))

    return jsonify({'message': 'API endpoint is working!'})


def api_tag_all(user, payload):
    return {'response': [_.to_dict() for _ in Tag.all_tags() or []]}


def api_tag_search(user, payload):
    return {'response': [_.to_dict() for _ in Tag.query_tags_by_name(payload).all() or []]}


def api_tag_insert(user, payload):
    tag = Tag(name=payload)
    db.session.add(tag)
    db.session.commit()
    return {'response': tag.to_dict()}


def api_my_tags():
    tags = g.user.get_tags_with_tagger()
    result = dict()
    for tag in tags:
        tag_name = tag[0]
        tagger = {'uid': tag[1].id, 'name': tag[1].name}
        if tag_name in result:
            result[tag_name].append(tagger)
        else:
            result[tag_name] = [tagger]
    return {'response': result}


def api_get_friend_tags(user_id):
    tags = User.get_tags_for_user(user_id)
    return {'response': tags}


def api_add_tag_to(taggee, tag_name):
    tag = Tag.get_or_create(tag_name)
    if Tagging.create(tagger=g.user, taggee=taggee, tag=tag):
        return {'response': ''}
    else:
        return {'response': ''}


def api_delete_tag(tag_name):
    if Tag.delete_by_name_for_user(tag_name, g.user):
        return {'response': ''}
    else:
        return {'response': ''}


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

                user = User.create(id=profile['id'], name=profile['name'],
                                   profile_url=profile['link'],
                                   access_token=access_token['access_token'])
            session['user'] = user.id

    g.uid = session.get('user')
    g.user = User.get_by_id(g.uid) if g.uid else None
