import facebook

def get_user_friends(access_token):
    graph = facebook.GraphAPI(access_token)
    user = graph.get_object("me")
    return graph.get_connections(user["id"], "friends")
