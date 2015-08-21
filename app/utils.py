import facebook
import requests

def get_user_friends(access_token):
    graph = facebook.GraphAPI(access_token)
    user = graph.get_object("me")
    data = graph.get_connections(user["id"], "friends")
    combined_data = data['data']
    while 'next' in data['paging']:
        data = requests.get(data['paging']['next']).json()
        combined_data.extend(data['data'])
    return combined_data
