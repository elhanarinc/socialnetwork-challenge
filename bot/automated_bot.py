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


# LOCAL HELPER FUNCTIONS #
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


# HELPER FUNCTIONS FOR USING API #
def like_post(user_token, post):
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'x-access-token': user_token}
    try:
        like_response = requests.post(API_URL + '/like', data=json.dumps(post), headers=headers)
        if like_response.status_code == 200:
            print('Post liked: id=%s' % (post['post_id']))
            return True
        elif like_response.status_code == 403:
            print('User cannot like more than max allowed like count')
            return False
        elif like_response.status_code == 406:
            print('User cannot like his/hers own post')
            return False
    except requests.exceptions.RequestException as e:
        print('Like Post Error')
        print(e)
    return False


def available_user():
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    max_like_count = {
        'max_like_count': LIKE_COUNT
    }
    try:
        user_find_response = requests.get(API_URL + '/finduser', data=json.dumps(max_like_count), headers=headers)
        if user_find_response.status_code == 200:
            available_email = user_find_response.json()['user_email']
            print('Available user email: %s' % available_email)
            return available_email
        else:
            print('No user available')
            return None
    except requests.exceptions.RequestException as e:
        print('Available User Error')
        print(e)
        return None


def check_available_post_number():
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    try:
        posts_response = requests.get(API_URL + '/checkposts', headers=headers)
        if posts_response.status_code == 200:
            available_post_num = posts_response.json()['result']
            return available_post_num
    except requests.exceptions.RequestException as e:
        print('Check Posts Error')
        print(e)
        return None


def get_available_post(user_token):
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'x-access-token': user_token}
    try:
        available_post_response = requests.get(API_URL + '/getrandompost', headers=headers)
        if available_post_response.status_code == 200:
            return available_post_response.json()['result']
    except requests.exceptions.RequestException as e:
        print('Get Available Post Error')
        print(e)
        return None


def create_user_and_post():
    for num in range(USER_NUM):
        user = generate_user()
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        try:
            user_create_response = requests.post(API_URL + '/signup', data=json.dumps(user), headers=headers)
            if user_create_response.status_code == 200:
                print('User is created: Name: %s Email: %s' % (user['name'], user['email']))
                user_token = user_create_response.json()['token']
                user['token'] = user_token
                USERS[user['email']] = user
                random_post_num = random.randint(1, POST_COUNT)
                print('Create %s number of posts' % (str(random_post_num)))
                headers['x-access-token'] = user_token
                for post_num in range(random_post_num):
                    post = generate_post()
                    try:
                        requests.post(API_URL + '/create', data=json.dumps(post), headers=headers)
                        print('Post is created: Content: %s' % (post['content']))
                    except requests.exceptions.RequestException as e:
                        print('Post Create Error')
                        print(e)
                    time.sleep(1)
                print()
            else:
                print('Problem encountered with user creation: Name: %s Email: %s' % (user['name'], user['email']))
        except requests.exceptions.RequestException as e:
            print('User Create Error')
            print(e)


def show_users():
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    users_response = requests.get(API_URL + '/getusers', headers=headers)
    if users_response.status_code == 200:
        user_array = users_response.json()
        print('# USER TABLE #')
        for user in user_array:
            print(user)
        print()


def show_posts():
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    posts_response = requests.get(API_URL + '/getposts', headers=headers)
    if posts_response.status_code == 200:
        posts_array = posts_response.json()
        print('# POST TABLE #')
        for post in posts_array:
            print(post)
        print()


def show_likes():
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    likes_response = requests.get(API_URL + '/getlikes', headers=headers)
    if likes_response.status_code == 200:
        likes_array = likes_response.json()
        print('# LIKE TABLE #')
        for like in likes_array:
            print(like)
        print()


def delete_all():
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    delete_all_response = requests.get(API_URL + '/deleteall', headers=headers)
    if delete_all_response.status_code == 200:
        print('All tables are cleared!')


if __name__ == '__main__':
    print('Starting ...\n')

    create_user_and_post()
    time.sleep(1)

    available_post_number = check_available_post_number()
    time.sleep(1)
    if available_post_number is None:
        print('There is a problem when getting available post number.')

    while available_post_number != 0:
        print('Available post number: %s' % available_post_number)

        available_user_email = available_user()
        if available_user_email is None:
            break
        time.sleep(1)

        token = USERS[available_user_email]['token']

        available_post_id = get_available_post(token)
        if available_post_id == -1:
            print('No available post for: %s' % available_user_email)
            continue
        print('Available post id: %s' % available_post_id)
        time.sleep(1)

        post_to_like = {
            'post_id': available_post_id
        }
        like_or_not = like_post(token, post_to_like)
        time.sleep(1)

        available_post_number = check_available_post_number()
        print()
        time.sleep(1)

    print('All done!')
    print()
    show_users()
    time.sleep(1)
    show_posts()
    time.sleep(1)
    show_likes()
    time.sleep(1)
    delete_all()
    time.sleep(1)
