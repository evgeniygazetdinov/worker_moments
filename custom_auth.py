import json

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.generic import View
from intraspace.oidc import auth as _auth
from django.http import JsonResponse

User = get_user_model()


class UserIsAdmin(View):
    http_method_names = ['get', ]
    header = 'HTTP_AUTHORIZATION'
    get_param = 'token'

    def get(self, request):
        user = request.user

        if not user.is_authenticated():
            token = None
            if self.header in request.META:
                token = request.META[self.header].replace('Bearer ', '')
            elif self.get_param in request.GET:
                token = request.GET[self.get_param]

            if token is None:
                return HttpResponseBadRequest(json.dumps({'error': 'Token is required'}))

            try:
                user_info = _auth.server.get_userinfo(token)
            except requests.HTTPError as err:
                return HttpResponseBadRequest(json.dumps({'error': str(err)}))

            jwt_field = [jwtfield for (jwtfield, userfield) in settings.AUTH_JWT_USER_FIELD_MAP if userfield == 'email']
            if not jwt_field:
                return HttpResponseBadRequest(json.dumps({'error': 'Can`t fetch user email from jwt token with current mapping.'}))
            else:
                jwt_field = jwt_field[0]

            user = User.objects.filter(email__iexact=user_info[jwt_field]).first()
            if user is None:
                return HttpResponseBadRequest(json.dumps({'error': 'No such user'}))

        user = request.user
        """
        if user is superadmin or user in 'Карта' group return map
        else return badrequest
        """
        has_group = True if 'Карта' in [x for x in user.groups.values_list('name', flat=True)] else False
        if user.is_superuser or has_group:
            # return HttpResponse(json.dumps({'is_admin': True, 'map': has_group}))
            return JsonResponse({'is_admin': True, 'map': has_group})
        else:
            return HttpResponseBadRequest('Please set up the map group or admin')

