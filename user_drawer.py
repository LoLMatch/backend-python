import json
import random

users_already_matched = []
users_buff = {}


def get_users_already_matched():
    """
    Adds users from database that had already been matched/rejected to a list.
    """
    pass


def get_users_to_buffer():
    """
    Adds users from database to buffer of users possible to match.
    """
    pass


def get_match():
    global users_buff
    match = random.choice(list(users_buff.values()))

    users_already_matched.append(match)
    users_buff = {key: value for key, value in users_buff.items() if value != match}

    return match


