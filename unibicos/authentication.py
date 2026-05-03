from rest_framework_simplejwt.authentication import JWTAuthentication

class CustomJWTAuthentication(JWTAuthentication):
    pass

# from django.utils.translation import gettext
# from rest_framework import exceptions
# from rest_framework_simplejwt.authentication import JWTAuthentication

# from public.models import TokenBlacklist


# class CustomJWTAuthentication(JWTAuthentication):
#     def authenticate(self, request):
#         header = self.get_header(request)
#         if header is None:
#             return None

#         raw_token = self.get_raw_token(header)
#         if raw_token is None:
#             return None

#         if TokenBlacklist.objects.filter(token=raw_token).exists():
#             msg = gettext('Token has expired.')
#             raise exceptions.AuthenticationFailed(msg)

#         validated_token = self.get_validated_token(raw_token)
#         return self.get_user(validated_token), validated_token
