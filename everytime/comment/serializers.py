from comment.models import Comment
from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist

from user.models import UserProfile


class CommentSerializer(serializers.ModelSerializer):
    nickname = serializers.SerializerMethodField()
    reply = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = (
            'id',
            'user_id',
            'nickname',
            'post',
            'parent', #부모 댓글
            'content',
            'is_anonym',
            'numLikes',
            'deleted',
            'created_at',
            'updated_at',
            'reply', # 대댓글, 자식 댓글
        )

    def get_reply(self, comment):
        replys = Comment.objects.filter(parent=comment)
        try:
            return ReplySerializer(replys, context=self.context, many=True).data
        except ObjectDoesNotExist:
            return None

    def get_nickname(self, comment):
        user = comment.user
        profile = UserProfile.objects.get(user=user)
        return profile.nickname


class ReplySerializer(serializers.ModelSerializer):
    nickname = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = (
            'id',
            'user_id',
            'nickname',
            'post',
            'parent',
            'content',
            'is_anonym',
            'numLikes',
            'deleted',
            'created_at',
            'updated_at'
        )

    def get_nickname(self, comment):
        user = comment.user
        profile = UserProfile.objects.get(user=user)
        return profile.nickname