import argparse
import json
import string
import random
import requests
import time

parser = argparse.ArgumentParser(description="Sample bot for testing API")
parser.add_argument('-f', '--file', help="Configuration file for bot", required=True)
args = vars(parser.parse_args())

with open(args['file']) as file:
    config_data = json.load(file)

API_URL = config_data['api_url']
LIKE_COUNT = config_data['max_likes_per_user']
POST_COUNT = config_data['max_posts_per_user']
USER_NUM = config_data['number_of_users']
USERS = {}


def string_generator(size=5):
    return ''.join(random.choice(string.ascii_letters) for _ in range(size))


def generate_user():
    name = string_generator()
    email = string_generator() + '@gmail.com'
    password = string_generator(10)
    return {
        'name': name,
        'email': email,
        'password': password
    }


for num in range(USER_NUM):
    user = generate_user()
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(API_URL + '/signup', data=json.dumps(user), headers=headers)
    if r.status_code == 200:
        token = r.json()['token']
        user['token'] = token
        USERS[user['email']] = user
    time.sleep(1)

for key, value in USERS.items():
    print(key)
    print(value)
