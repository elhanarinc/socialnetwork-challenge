from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils.decorators import decorator_from_middleware
from datetime import datetime, timedelta

from .forms import SignupForm, LoginForm, PostForm, LikeAndDislikeForm
from .models import UserData, PostData, UserPostLike
from .middleware import JWTMiddleware
from .utils.emailhunter import check_email
from .utils.clearbit import find_extensive_data

import json
import bcrypt
import jwt
import random

JWT_SECRET = 'tradecore'
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_HOURS = 24


@require_http_methods(['POST'])
def signup(request):
    if len(request.body) < 1:
        return JsonResponse({'result': 'invalid or missing body params'}, status=400)
    body = json.loads(request.body)
    signup_data = SignupForm(body)
    if signup_data.is_valid():
        try:
            user = UserData.objects.get(email=body['email'])
        except UserData.DoesNotExist:
            user = None

        if user is not None:
            return JsonResponse({'result': 'email address already registered'}, status=400)
        else:
            is_valid_email = check_email(body['email'])
            if not is_valid_email:
                return JsonResponse({'result': 'email is not valid'}, status=400)

            hashed_password = bcrypt.hashpw(body['password'].encode('utf-8'), bcrypt.gensalt()).decode()
            extra_info = find_extensive_data(body['email'])

            user_to_insert = UserData(name=body['name'],
                                      password=hashed_password,
                                      email=body['email'],
                                      additional_information=extra_info)
            user_to_insert.save()

            payload = {
                'user_id': user_to_insert.id,
                'exp': datetime.utcnow() + timedelta(hours=JWT_EXP_DELTA_HOURS)
            }
            jwt_token = jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM)
            return JsonResponse({'token': jwt_token.decode('utf-8')})

    else:
        return JsonResponse({'result': 'invalid or missing body params'}, status=400)


@require_http_methods(['POST'])
def login(request):
    if len(request.body) < 1:
        return JsonResponse({'result': 'invalid or missing body params'}, status=400)
    body = json.loads(request.body)
    login_data = LoginForm(body)
    if login_data.is_valid():
        try:
            user = UserData.objects.get(email=body['email'])
        except UserData.DoesNotExist:
            user = None

        if user is None:
            return JsonResponse({'result': 'user not found'}, status=404)
        else:
            check_password = bcrypt.checkpw(body['password'].encode('utf-8'), user.password.encode('utf-8'))
            if not check_password:
                return JsonResponse({'result': 'password is wrong'}, status=403)
            else:
                payload = {
                    'user_id': user.id,
                    'exp': datetime.utcnow() + timedelta(hours=JWT_EXP_DELTA_HOURS)
                }
                jwt_token = jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM)
                return JsonResponse({'token': jwt_token.decode('utf-8')})
    else:
        return JsonResponse({'result': 'invalid or missing body params'}, status=400)


@require_http_methods(['POST'])
@decorator_from_middleware(JWTMiddleware)
def like(request):
    if len(request.body) < 1:
        return JsonResponse({'result': 'invalid or missing body params'}, status=400)
    return like_dislike_helper_func(request, 'like')


@require_http_methods(['POST'])
@decorator_from_middleware(JWTMiddleware)
def unlike(request):
    if len(request.body) < 1:
        return JsonResponse({'result': 'invalid or missing body params'}, status=400)
    return like_dislike_helper_func(request, 'unlike')


@require_http_methods(['POST'])
@decorator_from_middleware(JWTMiddleware)
def create(request):
    if len(request.body) < 1:
        return JsonResponse({'result': 'invalid or missing body params'}, status=400)
    body = json.loads(request.body)
    post_data = PostForm(body)
    if post_data.is_valid():
        user_id = request.user_id
        try:
            user = UserData.objects.get(id=user_id)
        except UserData.DoesNotExist:
            user = None

        if user is None:
            return JsonResponse({'result': 'user not found'}, status=404)
        else:
            post_to_insert = PostData(content=body['content'],
                                      owner=user)
            post_to_insert.save()
            user.current_post_count = user.current_post_count + 1
            user.save(update_fields=['current_post_count'])
            return JsonResponse({'result': 'OK'})
    else:
        return JsonResponse({'result': 'invalid or missing body params'}, status=400)


####################
#                  #
# HELPER FUNCTIONS #
#                  #
####################
def like_dislike_helper_func(request, selector):
    body = json.loads(request.body)
    data = LikeAndDislikeForm(body)
    if data.is_valid():
        user_id = request.user_id
        try:
            user = UserData.objects.get(id=user_id)
        except UserData.DoesNotExist:
            user = None

        if user is None:
            return JsonResponse({'result': 'user not found'}, status=404)
        else:
            try:
                post = PostData.objects.get(id=body['post_id'])
            except PostData.DoesNotExist:
                post = None

            if post is None:
                return JsonResponse({'result': 'post not found'}, status=404)
            elif str(post.owner.email) == str(user.email):
                return JsonResponse({'result': 'user cannot like his/hers own post'}, status=406)
            else:
                if 'max_count' in body and int(user.current_like_count) >= int(body['max_count']):
                    return JsonResponse({'result': 'user cannot like more than max like count'}, status=403)

                try:
                    liked_post = UserPostLike.objects.get(post=post, user=user)
                except UserPostLike.DoesNotExist:
                    liked_post = None

                if selector == 'like':
                    if liked_post is not None:
                        return JsonResponse({'result': 'user already liked this post'}, status=403)

                    user.current_like_count = user.current_like_count + 1
                    liked_post = UserPostLike(user=user, post=post)
                    liked_post.save()

                elif selector == 'unlike':
                    if liked_post is None:
                        return JsonResponse({'result': 'user haven`t liked this post'}, status=403)

                    liked_post.delete()
                    user.current_like_count = user.current_like_count - 1

                user.save(update_fields=['current_like_count'])
                return JsonResponse({'result': 'OK'})

    else:
        return JsonResponse({'result': 'invalid or missing body params'}, status=400)


@require_http_methods(['GET'])
def find_user(request):
    if len(request.body) < 1:
        return JsonResponse({'result': 'invalid or missing body params'}, status=400)
    body = json.loads(request.body)
    max_like_count = body['max_like_count']
    user_data = UserData.objects.all()\
        .filter(current_like_count__lt=int(max_like_count))\
        .order_by('-current_post_count')

    if len(user_data) <= 0:
        return JsonResponse({'result': 'no user found'}, status=404)
    else:
        return JsonResponse({'user_email': user_data[0].email})


@require_http_methods(['GET'])
def check_posts(request):
    not_liked_posts = PostData.objects\
        .exclude(id__in=UserPostLike.objects.values_list('post__id', flat=True))\
        .values_list('id', flat=True)
    if not_liked_posts is None:
        return JsonResponse({'result': '0'})
    count_of_not_liked_posts = len(list(not_liked_posts))
    return JsonResponse({'result': count_of_not_liked_posts})


@require_http_methods(['GET'])
@decorator_from_middleware(JWTMiddleware)
def get_random_post(request):
    user_id = request.user_id

    # Exclude with two conditions is buggy, so i call them in order
    available_users = PostData.objects\
        .exclude(id__in=UserPostLike.objects.values_list('post__id', flat=True))\
        .exclude(owner__id__exact=user_id)\
        .values_list('owner', flat=True)

    if available_users is None:
        return JsonResponse({'result': -1})

    available_users = list(set(available_users))
    length_of_avail_users = len(available_users)
    if length_of_avail_users == 0:
        return JsonResponse({'result': -1})

    random_index = random.randint(0, length_of_avail_users - 1)
    random_user = available_users[random_index]

    post_to_be_liked = PostData.objects.filter(owner__id=random_user).random()
    post_values = list(post_to_be_liked.values())[0]

    return JsonResponse({'result': post_values['id']})


######################
#                    #
# FOR DEBUG PURPOSES #
#                    #
######################
@require_http_methods(['GET'])
def delete_all(request):
    UserPostLike.objects.all().delete()
    PostData.objects.all().delete()
    UserData.objects.all().delete()
    return JsonResponse({'result': 'OK'})


@require_http_methods(['GET'])
def get_users(request):
    all_users = UserData.objects.all().values_list('id', 'name', 'email', 'current_post_count', 'current_like_count')
    all_users_return = []
    for user in all_users:
        user_as_dict = {
            'id': user[0],
            'name': user[1],
            'email': user[2],
            'post': user[3],
            'like': user[4]
        }
        all_users_return.append(user_as_dict)
    return JsonResponse(all_users_return, safe=False)


@require_http_methods(['GET'])
def get_posts(request):
    all_posts = PostData.objects.all().values_list('id', 'content', 'owner__id')
    all_posts_return = []
    for post in all_posts:
        post_as_dict = {
            'id': post[0],
            'content': post[1],
            'user_id': post[2]
        }
        all_posts_return.append(post_as_dict)
    return JsonResponse(all_posts_return, safe=False)


@require_http_methods(['GET'])
def get_likes(request):
    all_likes = UserPostLike.objects.all().values_list('id', 'user__id', 'post__id')
    all_likes_return = []
    for one_like in all_likes:
        like_as_dict = {
            'id': one_like[0],
            'user_id': one_like[1],
            'post_id': one_like[2]
        }
        all_likes_return.append(like_as_dict)
    return JsonResponse(all_likes_return, safe=False)
