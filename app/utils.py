import facebook
import requests
from app import mc
from app.models import User


def get_friends_key(uid):
    return 'friends:' + str(uid)


def get_paginated_data(user, resource_id, connection_name):
    graph = facebook.GraphAPI(user.access_token)
    data = graph.get_connections(resource_id, connection_name)
    combined_data = data['data']
    while 'next' in data['paging']:
        data = requests.get(data['paging']['next']).json()
        combined_data.extend(data['data'])
    return combined_data


def get_user_friends(user):
    cached_data = mc.get(get_friends_key(user.id))
    if cached_data:
        return cached_data
    combined_data = get_paginated_data(user, str(user.id), "friends")
    combined_data = [_ for _ in combined_data if User.get_by_id(_['id'])]
    mc.set(get_friends_key(user.id), combined_data, time=1800)
    return combined_data


def is_friend_of(user, other_id):
    friends = get_user_friends(user)
    for friend in friends:
        if friend['id'] == str(other_id):
            return True
    return False


def clear_friends_cache(user):
    friends = get_user_friends(user)
    for friend in friends:
        mc.delete(get_friends_key(friend['id']))
