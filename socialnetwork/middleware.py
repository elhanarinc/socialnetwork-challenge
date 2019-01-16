from django.http import JsonResponse
import jwt


JWT_SECRET = 'tradecore'
JWT_ALGORITHM = 'HS256'


class JWTMiddleware:
    def process_request(self, request):
        jwt_token_name = 'HTTP_X_ACCESS_TOKEN'
        if jwt_token_name not in request.META:
            return JsonResponse({'result': 'no jwt token on header'}, status=403)
        else:
            jwt_token = request.META[jwt_token_name]
            decoded = jwt.decode(jwt_token, JWT_SECRET, JWT_ALGORITHM)
            request.user_id = decoded['user_id']
