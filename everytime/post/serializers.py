from post.models import Post
from rest_framework import serializers

from user.models import UserProfile

class PostSerializer(serializers.ModelSerializer):
    nickname = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            'id',
            'user_id',
            'nickname',
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

    def get_nickname(self, post):
        user = post.user
        profile = UserProfile.objects.get(user=user)
        return profile.nickname

    def validate_tags(self, value):
        #TAGS = ('잡담', '고민', '정보', '진로')
        #if not str(value) in TAGS:
        #    raise serializers.ValidationError("Invalid tag.")
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
        if 'is_anonym' in validated_data:
            instance.is_anonym = validated_data['is_anonym']
            instance.save()
        return instance
