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
                               app_name=FB_APP_NAME, user=g.user,
                               friends=get_user_friends(g.user['access_token']))
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
    """Set g.user to the currently logged in user.

    Called before each request, get_current_user sets the global g.user
    variable to the currently logged in user.  A currently logged in user is
    determined by seeing if it exists in Flask's session dictionary.

    If it is the first time the user is logging into this application it will
    create the user and insert it into the database.  If the user is not logged
    in, None will be set to g.user.
    """

    # Set the user in the session dictionary as a global g.user and bail out
    # of this function early.
    if session.get('user'):
        g.user = session.get('user')
        return

    # Attempt to get the short term access token for the current user.
    result = get_user_from_cookie(cookies=request.cookies, app_id=FB_APP_ID,
                                  app_secret=FB_APP_SECRET)

    # If there is no result, we assume the user is not logged in.
    if result:
        # Check to see if this user is already in our database.
        user = User.query.filter(User.id == result['uid']).first()

        if not user:
            # Not an existing user so get info
            graph = GraphAPI(result['access_token'])
            profile = graph.get_object('me')

            # Create the user and insert it into the database
            user = User(id=str(profile['id']), name=profile['name'],
                        access_token=result['access_token'])
            db.session.add(user)
        elif user.access_token != result['access_token']:
            # If an existing user, update the access token
            user.access_token = result['access_token']

        # Add the user to the current session
        session['user'] = dict(name=user.name,
                               id=user.id, access_token=user.access_token)

    # Commit changes to the database and set the user as a global g.user
    db.session.commit()
    g.user = session.get('user', None)
