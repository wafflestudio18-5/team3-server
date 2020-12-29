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
            'tag',
            'created_at',
            'updated_at',
        )

    def validate_tags(self, value):
        TAGS = ('잡담', '고민', '정보', '진로')  # 임시로 정한 tag 목록
        if not str(value) in TAGS:
            raise serializers.ValidationError("Invalid tag.")
        return value

    def create(self, validated_data):
        post = Post.objects.create(**validated_data)
        return post

    def update(self, instance, validated_data):
        if 'title' in validated_data:
            instance.title = validated_data['title']
        if 'content' in validated_data:
            instance.content = validated_data['content']
        if 'tag' in validated_data:
            instance.tag = validated_data['tag']
        return instance