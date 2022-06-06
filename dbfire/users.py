"""
© 2019 Rouge Media All Rights Reserved.

Users Table DB Connection & Query Functions

"""
from collections import OrderedDict

from dbfire.db_connect import get_db_ref

# Getting Users Table DB Reference
db_users = get_db_ref('/Users/')
# List of available social media linked to users
all_social_types = ('instagram', 'twitter')


class User:
    """
    Table Class for Firebase Storage Table Users
    """
    def __init__(self, instagram, invited_by_user_profile, name, num_followers, num_following,
                 time_created, twitter, user_id, username, photo_url=None):
        self.instagram = instagram
        self.invited_by_user_profile = invited_by_user_profile
        self.name = name
        self.num_followers = num_followers
        self.num_following = num_following
        self.photo_url = photo_url
        self.time_created = time_created
        self.twitter = twitter
        self.user_id = user_id
        self.username = username


def db_to_user(db_objects):
    """
    Converts List of Dict from Database to Users object
    :param db_objects: List of dictionary of users returned by database
    :returns List of User objects
    """
    if isinstance(db_objects, list):
        return [User(**user) for user in db_objects]
    if isinstance(db_objects, OrderedDict):
        return [User(**user) for user in db_objects.values()]


def get_all_users():
    """
    Gets all the users in the Realtime Database
    :returns Tuple: Total Number of Users and List of User objects
    """
    all_users = db_to_user(db_users.get())
    num_of_users = len(all_users)
    return num_of_users, all_users


def get_social_users(social_type=all_social_types, exclusive=False):
    """
    Get users based on social media account existence. It looks for users with any of the social media account specified
    :param social_type: Tuple of Type of social account (for eg. ('instagram', 'twitter'))
    :param exclusive: Boolean to tell whether exclusive account (for e.g. if social type is 'instagram' and exclusive
                      is true, the method gets all users with just instagram account and no other social account,
                      if exclusive is false it gets all users with instagram accounts irrespective of whether
                      they have other social accounts or not)
    :return List of User objects satisfying the social media account criteria
    """
    user_query = db_users
    null_user_ids = set()
    for social in social_type:
        null_data = db_users.order_by_child(social).equal_to('null')
        null_ids = set(user.user_id for user in db_to_user(null_data.get()))
        if not null_user_ids:
            null_user_ids = null_ids
        else:
            null_user_ids.intersection(null_ids)
    _, all_users = get_all_users()
    social_users = [user for user in all_users if user.user_id not in null_user_ids]
    if exclusive or not social_type:
        null_social = set(all_social_types).difference(set(social_type))
        user_query = db_users
        null_user_ids = set()
        for social in null_social:
            null_data = db_users.order_by_child(social).equal_to('null')
            null_ids = set(user.user_id for user in db_to_user(null_data.get()))
            if not null_user_ids:
                null_user_ids = null_ids
            else:
                null_user_ids.intersection(null_ids)
        social_users = [user for user in social_users if user.user_id in null_user_ids]
    return social_users


def get_filtered_users(filters, limit=None, order='asc', limit_by='user_id'):
    """
    Get users based on filter conditions
    :param filters: Dictionary of filters {'key':('value', 'condition')} where condition is lte, eq, gte
    :param limit: Limit the number of users returned.
    :param order: asc or desc
    :param limit_by: Sort the users before limiting. By default orders by user_id
    :returns List of User objects satisfying filter criteria
    """
    user_query = db_users
    for key, value in filters.items():
        condition = value[1]
        value = value[0]
        if condition == 'eq':
            data = user_query.order_by_child(key).equal_to(value).get()
        elif condition == 'lte':
            data = user_query.order_by_child(key).end_at(value).get()
        elif condition == 'gte':
            data = user_query.order_by_child(key).start_at(value).get()
        else:
            print(f'Invalid Condition on filter: {condition}\n Should be one of eq, lte, gte')

    if limit:
        print(limit, limit_by, order)
        if order == 'asc':
            data = user_query.order_by_child(limit_by).limit_to_first(limit).get()
        elif order == 'desc':
            data = user_query.order_by_child(limit_by).limit_to_last(limit).get()
    return db_to_user(data)


def get_user_by_id(user_id):
    """
    Fetch a User by User ID
    :param user_id: User ID of the user. Unique to every user
    :returns User object
    """
    user = db_to_user(db_users.order_by_child('user_id').equal_to(user_id).get())
    if user:
        return user[0]
    else:
        return None


def get_users_by_name(name):
    """
    Fetch all Users by name
    :param name: Name of the user. Can be multiple users with same name
    :returns List of User objects with same name
    """
    return db_to_user(db_users.order_by_child('name').equal_to(name).get())


def get_user_by_insta(insta_id):
    """
    Fetch a User by Instagram ID
    :param insta_id: Instagram ID of the user. Unique to every user
    :returns User object
    """
    user = db_to_user(db_users.order_by_child('instagram').equal_to(insta_id).get())
    if user:
        return user[0]
    else:
        return None


def get_user_by_twitter(twitter_id):
    """
    Fetch a User by Twitter ID
    :param twitter_id: Twitter ID of the user. Unique to every user
    :returns User object
    """
    user = db_to_user(db_users.order_by_child('twitter').equal_to(twitter_id).get())
    if user:
        return user[0]
    else:
        return None


def get_user_by_username(username):
    """
    Fetch a User by username
    :param username: User Name of the user. Unique to every user
    :returns User object
    """
    user = db_to_user(db_users.order_by_child('username').equal_to(username).get())
    if user:
        return user[0]
    else:
        return None
