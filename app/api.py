import sqlalchemy

from app.views import render_template
from app.utils import get_user_friends, is_friend_of
from app.models import User, Tag, Tagging

import json


class APIException(Exception):
    def __init__(self, message):
        self.message = message


# Debug purpose
def api_tag_all(user, payload):
    # Payload: ignored
    # Return: list of tag dicts
    # return [_.to_dict() for _ in Tag.all_tags() or []]
    friends = [_['id'] for _ in get_user_friends(user)]
    return Tag.all_tags_filtered(friends)


def api_tag_search(user, payload):
    # Payload: {'keyword': 'foo'}
    # Return: list of tag dicts
    return [_.name for _ in Tag.query_tags_by_name(payload['keyword']) or []]


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
    friends = [_['id'] for _ in get_user_friends(user)]
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
    if is_friend_of(user, payload['id']):
        tags = User.get_tags_for_user(payload['id'])
        return {_[0]: _[1] for _ in tags}
    else:
        raise APIException('You are not friends!')


def api_user_add_tag(user, payload):
    # Payload: {'taggee': 'uid', 'tag': 'foo'}
    # Return: ???
    taggee = User.get_by_id(payload['taggee'])
    if not taggee:
        raise APIException('Taggee does not exist!')
    if not user.can_tag(taggee):
        raise APIException('Cannot tag the user!')
    tag_name = payload['tag'].strip().lower()
    if not tag_name:
        raise APIException('Tag name not allowed!')
    tag = Tag.get_or_create(tag_name)
    try:
        Tagging.create(tagger=user, taggee=taggee, tag=tag)
        return 'OK'
    except sqlalchemy.exc.IntegrityError:
        raise APIException('Already tagged!')


def api_user_add_tags(user, payload):
    # Payload: {'taggee': 'uid', 'tag': 'foo'}
    # Return: ???
    taggee = User.get_by_id(payload['taggee'])
    if not taggee:
        raise APIException('Taggee does not exist!')
    if not user.can_tag(taggee):
        raise APIException('Cannot tag the user!')
    tags_name = [_.strip().lower() for _ in json.loads(payload['tag']) if _]
    succeeded = 0
    for tag_name in tags_name:
        tag = Tag.get_or_create(tag_name)
        try:
            Tagging.create(tagger=user, taggee=taggee, tag=tag)
            succeeded += 1
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
        friends = get_user_friends(user)
        return [_ for _ in friends if keyword in _['name'].lower()]
    else:
        return []


def api_user_all_friends(user, payload):
    return get_user_friends(user)


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
    'all_friends': api_user_all_friends
}


def view_index(user, payload):
    return render_template('view_index.html', user=user.to_dict())


def view_friend(user, payload):
    friend = User.get_by_id(payload['id'])
    tags = api_user_friend_tags(user, payload)
    return render_template('view_friend.html', friend=friend, tags=tags)


def view_tag(user, payload):
    taggees = api_tag_get_taggees(user, payload)
    return render_template('view_tag.html', tag=payload['name'], taggees=taggees)


def view_me(user, payload):
    tags = api_user_my_tags(user, payload)
    return render_template('view_me.html', user=user.to_dict(), tags=tags)


def view_manage(user, payload):
    tags = [{'name': _[0], 'taggers': _[1]} for _ in api_user_my_tags(user, payload).items()]
    tags.sort(key=lambda _: len(_['taggers']), reverse=True)
    return render_template('view_manage.html', user=user.to_dict(), tags=tags)


views = {
    'friend': view_friend,
    'tag': view_tag,
    'me': view_me,
    'manage': view_manage,
    'index': view_index
}
