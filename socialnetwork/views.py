from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils.decorators import decorator_from_middleware
from datetime import datetime, timedelta

from .forms import SignupForm, LoginForm, PostForm, LikeAndDislikeForm
from .models import UserData, PostData
from .middleware import JWTMiddleware
from .utils.emailhunter import check_email
from .utils.clearbit import find_extensive_data

import json
import bcrypt
import jwt

JWT_SECRET = 'tradecore'
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_HOURS = 24


@require_http_methods(['POST'])
def signup(request):
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


def login(request):
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


@decorator_from_middleware(JWTMiddleware)
def like(request):
    return like_dislike_helper_func(request, 1)


@decorator_from_middleware(JWTMiddleware)
def dislike(request):
    return like_dislike_helper_func(request, -1)


@decorator_from_middleware(JWTMiddleware)
def create(request):
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


def like_dislike_helper_func(request, counter):
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
            else:
                user.current_like_count = user.current_like_count + counter
                user.save(update_fields=['current_like_count'])
                post.like_count = post.like_count + counter
                post.save(update_fields=['like_count'])
                return JsonResponse({'result': 'OK'})
    else:
        return JsonResponse({'result': 'invalid or missing body params'}, status=400)

