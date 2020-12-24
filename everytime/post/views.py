from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from post.models import Post
# Create your views here.

# GET /find/board/article/list list posts
# POST /save/board/article write a post
# PUT /save/board/article/vote like a post
# DELETE /remove/board/article delete a post
