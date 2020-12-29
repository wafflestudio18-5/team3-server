from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.db import transaction

from post.models import Post, UserLikePost
from post.serializers import PostSerializer

# GET /find/board/article/list | list posts
# POST /save/board/article | write a post
# PUT /save/board/article/vote | like a post
# DELETE /remove/board/article | delete a post

class PostViewSet(viewsets.GenericViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated(),)

    # get_serializer_class() ?
    # UserLikePostSerializer ?
    #TODO: check user permission

    def get(self, request): # GET /find/board/article/list | list posts
        # TODO: implement this function
        start_num = request.data.get('start_num') # request.query_params.get() ?
        board_id = request.data.get('board_id')

        if 'limit_num' in request.data:
            limit_num = request.data.get('limit_num')
        else:
            limit_num = 20 # default

        if 'tag' in request.data:
            tag = request.data.get('tag')
            post = Post.objects.filter(board_id=board_id, tag=tag).order_by('-id')[start_num:start_num+limit_num]
        else:
            post = Post.objects.filter(board_id=board_id).order_by('-id')[start_num:start_num+limit_num]

        data = self.get_serializer(post, many=True).data
        return Response(data, status = status.HTTP_200_OK)

    def write(self, request): # POST /save/board/article | write a post
        user = request.user
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception = True)

        if not user.is_active:
            return Response({"error": "You do not have a permission to write a post."}, status = status.HTTP_403_FORBIDDEN)

        serializer.save()
        return Response(serializer.data, status = status.HTTP_201_CREATED)

    @transaction.atomic
    def like(self, request): # PUT /save/board/article/vote | like a post
        user = request.user
        post = request.data.get("post_id")
        if UserLikePost.objects.get(user = user, post = post): # 이미 좋아요를 누른 경우
            return Response({"error": "You already liked this post."}, status = status.HTTP_400_BAD_REQUEST)

        UserLikePost.objects.create(user = user, post = post)
        #TODO: update numLikes

        return Response(status = status.HTTP_200_OK) # serializer?

    def delete(self, request): # DELETE /remove/board/article | delete a post
        # TODO: implement this function
        pass


