from django.db import models
from django.contrib.auth.models import User
from board.models import Board
# Create your models here.

class Post(models.Model):
    user = models.ForeignKey(User, null=True, related_name = 'post', on_delete = models.CASCADE)
    board = models.ForeignKey(Board, null=True, related_name = 'post', on_delete = models.CASCADE)
    title = models.CharField(blank = True, max_length = 150)
    content = models.TextField(blank = False)
    is_anonym = models.BooleanField(default = False)
    numLikes = models.PositiveIntegerField()
    numComments = models.PositiveIntegerField()
    numScraps = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

class UserLikePost(models.Model):
    user = models.ForeignKey(User, null=True, related_name = 'userlikepost', on_delete = models.CASCADE)
    post = models.ForeignKey(Post, null=True, related_name = 'userlikepost', on_delete = models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)