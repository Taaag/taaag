import facebook
import requests
from app import mc


def get_user_friends(user):
    cached_data = mc.get('friends:' + str(user.id))
    if cached_data:
        return cached_data

    graph = facebook.GraphAPI(user.access_token)
    data = graph.get_connections(str(user.id), "friends")
    combined_data = data['data']
    while 'next' in data['paging']:
        data = requests.get(data['paging']['next']).json()
        combined_data.extend(data['data'])
    mc.set('friends:' + str(user.id), combined_data, time=1800)
    return combined_data


def is_friend_of(user, other_id):
    friends = get_user_friends(user)
    for friend in friends:
        if friend['id'] == str(other_id):
            return True
    return False
