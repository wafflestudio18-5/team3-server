from comment.models import Comment
from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist

class CommentSerializer(serializers.ModelSerializer):
    reply = serializers.SerializerMethodField()
    class Meta:
        model = Comment
        fields = (
            'id',
            'user_id',
            'post_id',
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

class ReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = (
            'id',
            'user_id',
            'parent',
            'content',
            'is_anonym',
            'numLikes',
            'deleted',
            'created_at',
            'updated_at'
        )