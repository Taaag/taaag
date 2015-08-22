from app.utils import get_user_friends, is_friend_of
from app.models import User, Tag, Tagging

# Debug purpose
def api_tag_all(user, payload):
    # Payload: ignored
    # Return: list of tag dicts
    return {'response': [_.to_dict() for _ in Tag.all_tags() or []]}


def api_tag_search(user, payload):
    # Payload: {'keyword': 'foo'}
    # Return: list of tag dicts
    return {'response': [_.to_dict() for _ in Tag.query_tags_by_name(payload['keyword']) or []]}


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
    # Return: {'tag': 2, 'tag2': 1}
    if is_friend_of(user, payload['id']):
        tags = User.get_tags_for_user(payload['id'])
        return {'response': {_[0]: _[1] for _ in tags}}
    else:
        return {'error': 'You are not friends!'}


def api_user_add_tag(user, payload):
    # Payload: {'taggee': 'uid', 'tag': 'foo'}
    # Return: ???
    taggee = User.get_by_id(payload['taggee'])
    if not taggee:
        return {'error': 'Taggee does not exist!'}
    if not user.can_tag(taggee):
        return {'error': 'Cannot tag the user!'}
    tag_name = payload['tag'].strip().lower()
    if not tag_name:
        return {'error': 'Tag name not allowed!'}
    tag = Tag.get_or_create(tag_name)
    if Tagging.create(tagger=user, taggee=taggee, tag=tag):
        return {'response': 'OK'}
    else:
        return {'response': 'OK'}


def api_user_delete_tag(user, payload):
    # Payload: {'name': 'foo'}
    # Return: ???
    if Tag.delete_by_name_for_user(payload['name'], user):
        return {'response': ''}
    else:
        return {'response': ''}


def api_user_search_friends(user, payload):
    # Payload: {'keyword': 'foo'}
    # Return: [{'name': 'foo', 'id': 123}]
    keyword = payload['keyword'].strip().lower()
    if keyword:
        friends = get_user_friends(user)
        return {'response': [_ for _ in friends if keyword in _['name'].lower()]}
    else:
        return {'response': []}

apis = {
    'all_tags': api_tag_all,
    'search_tags': api_tag_search,
    'insert_tag': api_tag_insert,
    'get_taggees': api_tag_get_taggees,
    'my_tags': api_user_my_tags,
    'friend_tags': api_user_friend_tags,
    'add_tag': api_user_add_tag,
    'delete_tag': api_user_delete_tag,
    'search_friends': api_user_search_friends
}
