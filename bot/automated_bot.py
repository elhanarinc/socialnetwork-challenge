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


def generate_post(length_of_post=20):
    content = string_generator(length_of_post)
    return {
        'content': content
    }


def create_user_and_post():
    for num in range(USER_NUM):
        user = generate_user()
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        try:
            user_create_response = requests.post(API_URL + '/signup', data=json.dumps(user), headers=headers)
            if user_create_response.status_code == 200:
                print('User is created: Name: %s Email: %s' % (user['name'], user['email']))
                token = user_create_response.json()['token']
                user['token'] = token
                USERS[user['email']] = user
                random_post_num = random.randint(1, POST_COUNT)
                print('Create %s number of posts' % (str(random_post_num)))
                headers['x-access-token'] = token
                for post_num in range(random_post_num):
                    post = generate_post()
                    try:
                        requests.post(API_URL + '/create', data=json.dumps(post), headers=headers)
                    except requests.exceptions.RequestException as e:
                        print('Post Create Error')
                        print(e)
                    print('Post is created: Content: %s' % (post['content']))
                    time.sleep(1)
                print()
            else:
                print('Problem encountered with user creation: Name: %s Email: %s' % (user['name'], user['email']))
        except requests.exceptions.RequestException as e:
            print('User Create Error')
            print(e)


if __name__ == '__main__':
    print('Starting ...\n')
    create_user_and_post()
    print('All done!')
