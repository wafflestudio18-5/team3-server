from django.db import models
from django.contrib.auth.models import User
from post.models import Post

class Comment(models.Model):
    user = models.ForeignKey(User, null=False, related_name='comment', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, null=False, related_name='comment', on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, related_name='reply', on_delete=models.CASCADE)
            # 부모 댓글이 삭제될 일이 없으므로 CASCADE여도 상관없음
    content = models.TextField(blank=False)
    is_anonym = models.BooleanField(default=False)
    numLikes = models.PositiveIntegerField(default=0)
    deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class UserLikeComment(models.Model):
    user = models.ForeignKey(User, null=False, related_name='userlikecomment', on_delete = models.CASCADE)
    comment = models.ForeignKey(Comment, null=False, related_name='userlikecomment', on_delete = models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
