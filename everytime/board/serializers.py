from board.models import Board
from rest_framework import serializers

class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = (
            'id',
            'title',
            'has_post_title',
            'has_preview',
            'created_at',
            'updated_at',
        )