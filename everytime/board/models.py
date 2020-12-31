from django.db import models

class Board(models.Model):
    title = models.CharField(blank=False, max_length=150)
    has_post_title = models.BooleanField(null=False)
    has_preview = models.BooleanField(null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
