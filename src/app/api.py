import json

from collections import OrderedDict
import sqlalchemy
from app.views import render_template
from app.models import User, Tag, Tagging
from app.utils import display_time
import random


class APIException(Exception):
    def __init__(self, message):
        self.message = message


# Debug purpose
def api_tag_all(user, payload):
    # Payload: ignored
    # Return: list of tag dicts
    # return [_.to_dict() for _ in Tag.all_tags() or []]
    friends = [_['id'] for _ in user.get_friends()]
    return Tag.all_tags_filtered(friends)


def api_tag_search(user, payload):
    # Payload: {'keyword': 'foo'}
    # Return: list of tag dicts
    if not payload.get('keyword', ''):
        return []
    result = [_.name for _ in Tag.query_tags_by_name(payload['keyword']) or [] if _.name != payload['keyword']]
    return list(OrderedDict.fromkeys(result))


# Debug purpose
def api_tag_insert(user, payload):
    # Payload: {'name': 'foo'}
    # Return: tag dict
    tag = Tag.get_or_create(payload['name'])
    return tag.to_dict()


def api_tag_get_taggees(user, payload):
    # Payload: {'name': 'foo'}
    # Return: {'user1': 2, 'user2': 1}
    tag = Tag.get_or_create(payload['name'])
    friends = [_['id'] for _ in user.get_friends()]
    return [{'id': i[0].id, 'name': i[0].name, 'count': i[1]} for i in tag.get_taggees_filtered(friends)]


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
    return result


def api_user_friend_tags(user, payload):
    # Payload: {'id': 'foo'}
    # Return: {'tag': 2, 'tag2': 1}
    if user.is_friend_of(payload['id']):
        tags = User.get_tags_for_user(payload['id'])
        tags_added_by_me = [_[0] for _ in Tag.get_by_tagger_and_taggee(user.id, payload['id'])]
        return {_[0]: (_[1], _[0] in tags_added_by_me) for _ in tags}
    else:
        raise APIException('You are not friends!')


def api_user_add_tag(user, payload):
    # Payload: {'taggee': 'uid', 'tag': 'foo'}
    # Return: ???
    # taggee = User.get_by_id(payload['taggee'])
    # if not taggee:
    # raise APIException('Taggee does not exist!')
    # if not user.can_tag(taggee):
    # raise APIException('Cannot tag the user!')
    # tag_name = payload['tag'].strip().lower()
    # if not tag_name:
    # raise APIException('Tag name not allowed!')
    # tag = Tag.get_or_create(tag_name)
    # try:
    #     Tagging.create(tagger=user, taggee=taggee, tag=tag)
    #     return 'OK'
    # except sqlalchemy.exc.IntegrityError:
    #     raise APIException('Already tagged!')
    raise APIException('Method deprecated')


def api_user_add_tags(user, payload):
    # Payload: {'taggee': 'uid', 'tag': 'foo'}
    # Return: ???
    taggee = User.get_by_id(payload['taggee'])
    if not taggee:
        raise APIException('Taggee does not exist!')
    if not user.can_tag(taggee):
        raise APIException('Cannot tag the user!')
    tags_name = [_.strip().lower() for _ in json.loads(payload['tags'])]
    tags_name = [_ for _ in tags_name if len(_) <= 32]
    succeeded = []
    for tag_name in tags_name:
        tag = Tag.get_or_create(tag_name)
        try:
            Tagging.create(tagger=user, taggee=taggee, tag=tag)
            succeeded.append(tag_name)
        except sqlalchemy.exc.IntegrityError:
            pass
    return succeeded


def api_user_delete_tag(user, payload):
    # Payload: {'name': 'foo'}
    # Return: ???
    if Tag.delete_by_name_for_user(payload['name'], user):
        return 'OK'
    else:
        raise APIException('Error!')


def api_user_search_friends(user, payload):
    # Payload: {'keyword': 'foo'}
    # Return: [{'name': 'foo', 'id': 123}]
    keyword = payload['keyword'].strip().lower()
    if keyword:
        friends = user.get_friends()
        return [_ for _ in friends if keyword in _['name'].lower()]
    else:
        return []


def api_user_all_friends(user, payload):
    return user.get_friends()


def api_user_invitable_friends(user, payload):
    return user.get_invitable_friends()


def api_user_like_friend(user, payload):
    likee = User.get_by_id(payload['likee'])
    event_id = payload['event_id'].strip().lower()
    if not likee:
        raise APIException('Likee does not exist!')
    elif not user.is_friend_of(payload['likee']):
        raise APIException('You are not friends!')
    elif not event_id:
        raise APIException('You need a facebook event!')
    if user.like(likee, event_id):
        return 'OK'
    else:
        raise APIException('Unknown error!')


def api_user_unlike_friend(user, payload):
    likee = User.get_by_id(payload['likee'])
    if not likee:
        raise APIException('Likee does not exist!')
    elif not user.is_friend_of(payload['likee']):
        raise APIException('You are not friends!')
    event_id = user.unlike(likee)
    if event_id:
        return event_id
    else:
        raise APIException('Unknown error!')


def api_user_change_settings(user, payload):
    public = payload.get('public', '').strip().lower()
    if public:
        public_internal = {'true': 1, 'false': 0}.get(public, -1)
        if user.update_privacy(public_internal):
            return 'OK'
        else:
            raise APIException('invalid input!')
    else:
        raise APIException('Unknown type of settings!')


apis = {
    'all_tags': api_tag_all,
    'search_tags': api_tag_search,
    'insert_tag': api_tag_insert,
    'get_taggees': api_tag_get_taggees,
    'my_tags': api_user_my_tags,
    'friend_tags': api_user_friend_tags,
    'add_tag': api_user_add_tag,
    'add_tags': api_user_add_tags,
    'delete_tag': api_user_delete_tag,
    'search_friends': api_user_search_friends,
    'all_friends': api_user_all_friends,
    'invitable_friends': api_user_invitable_friends,
    'like_friend': api_user_like_friend,
    'unlike_friend': api_user_unlike_friend,
    'change_settings': api_user_change_settings
}


def view_index(user, payload):
    all_friends = [_ for _ in user.get_friends() if _['id'] != '0']
    if len(all_friends) >= 3:
        selected_friends = random.sample(all_friends, 3)
    else:
        selected_friends = all_friends
    return render_template('view_index.html', user=user.to_dict(), friends=selected_friends)


def view_friend(user, payload):
    friend = User.get_by_id(payload['id'])
    tags = api_user_friend_tags(user, payload)
    liked_by_me = user.is_liking(friend)
    return render_template('view_friend.html', friend=friend, tags=tags, liked=liked_by_me)


def view_friends(user, payload):
    friends = user.get_friends()
    return render_template('view_friends.html', friends=friends)


def view_tag(user, payload):
    taggees = api_tag_get_taggees(user, payload)
    return render_template('view_tag.html', tag=payload['name'], taggees=taggees)


def view_me(user, payload):
    tags = api_user_my_tags(user, payload)
    return render_template('view_me.html', user=user.to_dict(), tags=tags)


def view_manage(user, payload):
    tag_with_taggers = api_user_my_tags(user, payload)
    tags_order_by_votes = [{'name': _[0], 'votes': len(_[1])} for _ in api_user_my_tags(user, payload).items()]
    tags_order_by_votes.sort(key=lambda _: _['votes'], reverse=True)
    tags_order_by_time = [{'name': _[0],
                           'created_time': display_time(_[1])} for _ in user.get_tags_order_by_time()]
    return render_template('view_manage.html', user=user.to_dict(), tag_with_taggers=tag_with_taggers,
                           tags_order_by_votes=tags_order_by_votes,
                           tags_order_by_time=tags_order_by_time)


def view_settings(user, payload):
    return render_template('view_settings.html', user=user.to_dict())


views = {
    'friend': view_friend,
    'friends': view_friends,
    'tag': view_tag,
    'me': view_me,
    'manage': view_manage,
    'index': view_index,
    'settings': view_settings
}


def public_cloud(user):
    tags = User.get_tags_for_user(user.id)
    return render_template('public_cloud.html', user=user, public=user.public_cloud(), tags={_[0]: _[1] for _ in tags})
