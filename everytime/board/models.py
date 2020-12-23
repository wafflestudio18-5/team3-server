from django.db import models

# Create your models here.

class Board(models.Model):
    title = models.CharField(blank = False, max_length = 150)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    post_title = models.BooleanField(null = False)