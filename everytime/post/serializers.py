from post.models import Post
from rest_framework import serializers

class PostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = (
            'id',
            'user_id',
            'board_id',
            'title',
            'content',
            'is_anonym',
            'numLikes',
            'numComments',
            'numScraps',
            'created_at',
            'updated_at',
        )
