import os
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import ToDataBaseSerializer
from rest_framework.views import APIView



path ='/home/_VideoArchive'


@api_view(['GET', 'POST'])
def take_video_list(request):
    result = {'video':[]}
    if request.method == "POST":
        video_id = request.data
        try:
            files = os.listdir(path+'/cam{}'.format(video_id))
            result = {'videos':files}
        except OSError as e:
            result = {'video':[]}
    return Response(result)


class StatisticList(APIView):

    def get(self,request):
        serializer = ToDataBaseSerializer
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ToDataBaseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
