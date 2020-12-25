from board.models import Board
from rest_framework import serializers

class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = (
            'id',
            'title',
            'created_at',
            'updated_at',
            'post_title',
        )