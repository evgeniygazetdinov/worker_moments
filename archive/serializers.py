from rest_framework import serializers


class ToDataBaseSerializer(serializers.Serializer):
    date = serializers.DateTimeField()
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()
    cam = serializers.IntegerField()

    def create(self,validated_data):
        res = super().create(validated_data)
        return res


    def to_representation(self,date):
        pass
