from rest_framework import serializers
from .models import Game


class GameSerializer(serializers.ModelSerializer):
    similarity = serializers.SerializerMethodField()

    class Meta:
        model = Game
        exclude = ["content"]

    def get_similarity(self, obj):
        similarity_map = self.context.get("similarity_map", {})
        return similarity_map.get(obj.appid, 0.0)
