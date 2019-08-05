import requests
import json
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import APIException
from .models import Server, Camera, CameraGroup, NotificationCamera, Quadrator,QuadratorGroup
from .serializers import ServerSerializer, CameraSerializer,CameraGroupSerializer, NotificationSerializer, QuadratorSerializer,QuadratorGroupSerializer
from theorema.permissions import ReadOnly
from theorema.users.models import CamSet
from rest_framework.decorators import api_view
from rest_framework.response import Response
from theorema.orgs.models import *
import hashlib

class NotificationViewSet(ModelViewSet):
    queryset = NotificationCamera.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            return queryset.filter(organization=self.request.user.organization)
        return queryset

class ServerViewSet(ModelViewSet):
    queryset = Server.objects.all()
    serializer_class = ServerSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            return queryset.filter(organization=self.request.user.organization)
        param = self.request.query_params.get('organization', None)
        if param is not None:
            return queryset.filter(organization__id=param)
        return queryset


class CameraViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Camera.objects.all()
    serializer_class = CameraSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            return queryset.filter(organization=self.request.user.organization)
        param = self.request.query_params.get('organization', None)
        if param is not None:
            return queryset.filter(organization__id=param)
        return queryset

    def destroy(self, request, pk=None):
        try:
            worker_data={'id': pk, 'type': 'cam'}
            camera = Camera.objects.get(id=pk)
            raw_response = requests.delete('http://{}:5005'.format(camera.server.address), json=worker_data)
            worker_response = json.loads(raw_response. content.decode())

            if camera.camera_group.camera_set.exclude(id=camera.id).count() == 0:
                camera_group_to_delete = camera.camera_group
            else:
                camera_group_to_delete = None

            for camset in CamSet.objects.all():
                if camera.id in camset.cameras:
                    camset.cameras.remove(camera.id)
                    camset.save()

        except Exception as e:
            raise APIException(code=400, detail={'message': str(e)})
        if worker_response['status']:
            raise APIException(code=400, detail={'message': worker_response['message']})
        res = super().destroy(request, pk)
        if camera_group_to_delete:
            camera_group_to_delete.delete()
        return res

class CameraGroupViewSet(ModelViewSet):
    queryset = CameraGroup.objects.all()
    serializer_class = CameraGroupSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            return queryset.filter(organization=self.request.user.organization)
        param = self.request.query_params.get('organization', None)
        if param is not None:
            return queryset.filter(organization__id=param)
        return queryset



class QuadratorGroupViewSet(ModelViewSet):
    queryset = QuadratorGroup.objects.all()
    serializer_class = QuadratorGroupSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            return queryset.filter(organization=self.request.user.organization)
        param = self.request.query_params.get('organization', None)
        if param is not None:
            return queryset.filter(organization__id=param)
                                                                                                        
