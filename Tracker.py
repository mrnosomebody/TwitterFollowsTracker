import dataclasses
import requests
from config import BEARER

get_users_url = "https://api.twitter.com/2/users/by?usernames="


@dataclasses.dataclass
class User:
    username: str
    id: str
    follows: list[dict[str, str]]
    follows_usernames: list[str]

    def get_follows(self):
        return self.follows


class Tracker:

    def __init__(self, usernames: [str], users: list[User]):
        """
        You have to insert:
         1) a list of usernames you want to add
         2) an empty list
        """
        self.usernames = []
        self.users = users

        self.get_users(usernames)
        for user in self.users:
            self.get_user_follows(user)

    def get_users(self, usernames: list[str]) -> str:
        """
        We have to get users' ids by their usernames, because when we get
        user follows we have to insert id instead of username
        ==================================================================
        Explanation for try/except
        If user enters only incorrect usernames the function will
        throw exception, because there will be {'error':smth} in response
        instead of {'data':smth}
        If user enters at least 1 correct username, only correct usernames
        will be written.
        The same principle is used in other functions
        ===================================================================
        """
        try:
            users = requests.get(get_users_url + ','.join(usernames),
                                 headers={"Authorization": f"Bearer {BEARER}"}) \
                .json()['data']
            for user in users:
                self.add_user(user)
        except KeyError:
            return 'None of the usernames you entered is correct'
        return 'Users were added to the track list'

    def add_user(self, user: dict[str, str]) -> str:
        username = user['username']
        if username not in self.usernames:
            id_ = user['id']
            self.users.append(User(username, id_, [], []))
            self.usernames.append(username)
            return f"Account {username} added"
        else:
            return f"{username} is already added"

    def delete_user(self, user: User) -> str:
        username = user.username
        if username in self.usernames:
            self.users.remove(user)
            self.usernames.remove(username)
            return f"Account {username} removed"
        else:
            return f"Account {username} is not tracked"

    @staticmethod
    def get_user_follows(user: User) -> str:
        try:
            user_follows_url = f"https://api.twitter.com/2/users/{user.id}/following?max_results=1000"
            user.follows = requests.get(user_follows_url, headers={"Authorization": f"Bearer {BEARER}"}).json()['data']
            user.follows_usernames = []
            for follow in user.follows:
                user.follows_usernames.append(follow['username'])
        except KeyError:
            return f'User {user.username} does not exist or requests limit exceeded'
        return 'Follows are tracked now'

