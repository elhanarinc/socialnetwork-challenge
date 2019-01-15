from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .forms import SignupForm
from .models import UserData
from .utils.emailhunter import check_email
from .utils.clearbit import find_extensive_data

import json
import bcrypt


@require_http_methods(['GET'])
def index(request):
    return JsonResponse({'result': 'OK'})


@require_http_methods(['POST'])
def signup(request):
    body = json.loads(request.body)
    signup_data = SignupForm(body)
    if signup_data.is_valid():
        try:
            result = UserData.objects.get(email=body['email'])
        except UserData.DoesNotExist:
            result = None

        if result is not None:
            return JsonResponse({'result': 'email address already registered'}, status=400)
        else:
            # is_valid_email = check_email(body['email'])
            # if not is_valid_email:
            #     return JsonResponse({'result': 'email is not valid'}, status=400)

            hashed_password = bcrypt.hashpw(body['password'].encode('utf8'), bcrypt.gensalt())
            # extra_info = find_extensive_data(body['email'])

            user_to_insert = UserData(name=body['name'],
                                      password=hashed_password,
                                      email=body['email'])
                                      # additional_information=extra_info)
            user_to_insert.save()
            return JsonResponse({'result': 'OK'})
        return JsonResponse(body, safe=False)
    else:
        return JsonResponse({'result': 'invalid or missing body params'}, status=400)


def login(request):
    return


def like(request):
    return


def dislike(request):
    return


def create(request):
    return
