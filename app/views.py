import json

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
                               friends=get_user_friends(g.user))
    # Otherwise, a user is not logged in.
    return render_template('login.html', app_id=FB_APP_ID, name=FB_APP_NAME)


@app.route('/api', methods=['GET'])
def api():
    if not g.user:
        abort(403)
    supported_apis = {
        'tag': {
            'all': api_tag_all,
            'search': api_tag_search,
            'insert': api_tag_insert,
            'get_taggees': api_tag_get_taggees
        },
        'user': {
            'my_tags': api_user_my_tags,
            'friend_tags': api_user_friend_tags,
            'add_tag': api_user_add_tag,
            'delete_tag': api_user_delete_tag,
            'search_friends': api_user_search_friends
        }
    }
    target = request.args.get('target', '')
    method = request.args.get('method', '')
    payload = json.loads(request.args.get('payload', '{}'))
    if target in supported_apis and method in supported_apis[target]:
        return jsonify(supported_apis[target][method](g.user, payload))

    return jsonify({'message': 'API endpoint is working!'})


# Debug purpose
def api_tag_all(user, payload):
    # Payload: ignored
    # Return: list of tag dicts
    return {'response': [_.to_dict() for _ in Tag.all_tags() or []]}


# Debug purpose
def api_tag_search(user, payload):
    # Payload: {'keyword': 'foo'}
    # Return: list of tag dicts
    return {'response': [_.to_dict() for _ in Tag.query_tags_by_name(payload['keyword']).all() or []]}


# Debug purpose
def api_tag_insert(user, payload):
    # Payload: {'name': 'foo'}
    # Return: tag dict
    tag = Tag.get_or_create(payload['name'])
    return {'response': tag.to_dict()}


def api_tag_get_taggees(user, payload):
    # Payload: {'name': 'foo'}
    # Return: {'user1': 2, 'user2': 1}
    tag = Tag.query_tags_by_name(payload['name'])
    # TODO: Filter by friends
    return {'response': {i[0]: i[1] for i in tag.get_taggees()}}


def api_user_my_tags(user, payload):
    # Payload: ignored
    # Return: {'tag1': [{'id': 'uid1', 'name': 'name1'}]}
    tags = user.get_tags_with_tagger()
    result = {}
    for tag in tags:
        tag_name = tag[0]
        if not tag_name in result:
            result[tag_name] = []
        result[tag_name].append(tag[1].to_dict())
    return {'response': result}


def api_user_friend_tags(user, payload):
    # Payload: {'id': 'foo'}
    # Return: ???
    tags = User.get_tags_for_user(payload['id'])
    return {'response': tags}


def api_user_add_tag(user, payload):
    # Payload: {'taggee': 'uid', 'tag': 'foo'}
    # Return: ???
    taggee = User.get_by_id(payload['taggee'])
    if not taggee:
        return {'error': 'Taggee does not exist!'}
    if not user.can_tag(taggee):
        return {'error': 'Cannot tag the user!'}
    tag = Tag.get_or_create(payload['tag'])
    if Tagging.create(tagger=user, taggee=taggee, tag=tag):
        return {'response': 'OK'}
    else:
        return {'response': 'OK'}


def api_user_delete_tag(user, payload):
    # Payload: {'name': 'foo'}
    # Return: ???
    if Tag.delete_by_name_for_user(payload['name'], g.user):
        return {'response': ''}
    else:
        return {'response': ''}


def api_user_search_friends(user, payload):
    # Payload: {'keyword': 'foo'}
    # Return: [{'name': 'foo', 'id': 123}]
    friends = get_user_friends(user)
    return {'response': [_ for _ in friends if payload['keyword'].strip().lower() in _['name'].lower()]}


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
