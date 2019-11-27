import json

import requests
from django.conf import settings
from jose import jwt, jws
from openid_connect._oidc import OpenIDClient


class OIDCClient(OpenIDClient):

    def get_id(self, token_response):
        header, payload, signing_input, signature = jws._load(token_response.id_token)
        kid = header.get('kid')
        key = None
        for k in json.loads(self.keys).get('keys', {}):
            if k.get('kid', None) == kid:
                key = k

        return jwt.decode(
            token_response.id_token,
            key,
            algorithms=['RS256'],
            audience=self.client_id,
            issuer=self.issuer,
            options=dict(verify_at_hash=False),
        )

    def get_userinfo(self, access_token):
        """ Get user info from userinfo endpoint and access_token"""
        user_info = super().get_userinfo(access_token)

        info_from_token = jwt.decode(access_token, settings.AUTH_JWT_KEY,
                                     algorithms=settings.AUTH_JWT_ALGS,
                                     audience=self.client_id,
                                     # issuer=self.issuer,  # можно передавать, но были прицеденты непрохождения верификации
                                     # (вероятно, из-з наличия/отсутствия порта)
                                     options=dict(verify_at_hash=False, ),
                                     )
        info_from_token.update(user_info)
        return info_from_token

    def refresh_token(self, refresh_token, scope=('openid', )):
        res = requests.post(self.token_endpoint, data=dict(
            client_id=self.client_id,
            client_secret=self.client_secret,
            grant_type="refresh_token",
            refresh_token=refresh_token,
            scope=' '.join(scope),
        ), headers={'Accept': 'application/json'})
        res.raise_for_status()

        if 'token_id' in res:
            # TODO: validation http://openid.net/specs/openid-connect-core-1_0.html#rfc.section.12.2
            pass

        return res.json()

    def __init__(self, url, client_id=None, client_secret=None, initial_auth=None, initial_access_token=None,
                 registration_client_uri=None, registration_auth=None, registration_access_token=None):

        # Повторяет __init__ родительского класса за исключением того, что не получает конфигурацию сразу.
        self.url = url
        self.client_id = client_id
        self.client_secret = client_secret

        if initial_auth:
            self.initial_auth = initial_auth
        self.initial_access_token = initial_access_token

        self.registration_client_uri = registration_client_uri
        if registration_auth:
            self.registration_auth = registration_auth
        self.registration_access_token = registration_access_token

        self._configuration = None

    @property
    def configuration(self):
        conf = getattr(self, '_configuration', None)
        if conf is None:
            conf = self.get_configuration()

        self._configuration = conf
        return self._configuration

    # Ниже переопределены свойства, которые используют конфигурацию.
    # Обращение к атрибуту `_configuration` заменено на обращение к свойству `configuration`

    @property
    def issuer(self):
        return self.configuration["issuer"]

    @property
    def authorization_endpoint(self):
        return self.configuration["authorization_endpoint"]

    @property
    def token_endpoint(self):
        return self.configuration["token_endpoint"]

    @property
    def jwks_uri(self):
        return self.configuration["jwks_uri"]

    @property
    def userinfo_endpoint(self):
        return self.configuration["userinfo_endpoint"]

    @property
    def end_session_endpoint(self):
        return self.configuration.get("end_session_endpoint")

    @property
    def registration_endpoint(self):
        return self.configuration.get("registration_endpoint")

    @property
    def keys(self):
        r = requests.get(self.configuration["jwks_uri"])
        r.raise_for_status()
        return r.content.decode('utf-8')

