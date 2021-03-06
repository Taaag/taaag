from datetime import timezone

import facebook
import requests
from app import mc
from app import app


def get_friends_key(uid):
    return 'friends:' + str(uid)


def get_invitable_friends_key(uid):
    return 'invitable_friends:' + str(uid)


def get_paginated_data(user, resource_id, connection_name, max_pages=None):
    graph = facebook.GraphAPI(user.access_token)
    data = graph.get_connections(resource_id, connection_name)
    combined_data = data['data']
    current_page = 1
    while ('paging' in data) and ('next' in data['paging']) and (max_pages is None or current_page < max_pages):
        data = requests.get(data['paging']['next']).json()
        combined_data.extend(data['data'])
        current_page += 1
    return combined_data


def get_user_friends(user):
    cached_data = mc.get(get_friends_key(user.id))
    if cached_data:
        return cached_data
    combined_data = get_paginated_data(user, str(user.id), "friends")
    mc.set(get_friends_key(user.id), combined_data, time=1800)
    return combined_data


def get_user_invitable_friends(user):
    cached_data = mc.get(get_invitable_friends_key(user.id))
    if cached_data:
        return cached_data
    combined_data = get_paginated_data(user, str(user.id), "invitable_friends", 1)
    mc.set(get_invitable_friends_key(user.id), combined_data, time=1800)
    return combined_data


def is_friend_of(user, other_id):
    if str(other_id) == '0':
        return True
    friends = get_user_friends(user)
    for friend in friends:
        if friend['id'] == str(other_id):
            return True
    return False


def clear_friends_cache(user):
    friends = get_user_friends(user)
    for friend in friends:
        mc.delete(get_friends_key(friend['id']))
        mc.delete(get_invitable_friends_key(friend['id']))


def has_friends_permission(user):
    graph = facebook.GraphAPI(user.access_token)
    try:
        for i in graph.get_connections("me", "permissions")['data']:
            if i['permission'] == 'user_friends' and i['status'] == 'granted':
                return True
    except facebook.GraphAPIError:
        return False
    return False


def display_time(time):
    return time.replace(tzinfo=timezone.utc).astimezone(app.config['DEFAULT_TIMEZONE']).strftime('%d %b, %I:%M %p')
