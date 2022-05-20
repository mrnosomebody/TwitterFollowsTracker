import bot
import dataclasses
import requests
from config import BEARER

get_users_url = "https://api.twitter.com/2/users/by?usernames="
# if __name__ == '__main__':
#     bot.bot.infinity_polling()
print(requests.get('https://api.twitter.com/2/users/by?usernames=elonmusk',
                   headers={"Authorization": f"Bearer {BEARER}"})
      .json()['data'])
