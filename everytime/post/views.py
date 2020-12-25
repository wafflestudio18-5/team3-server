from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from post.models import Post, UserLikePost
from post.serializers import PostSerializer
# Create your views here.

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

    def get(self, request): # GET /find/board/article/list | list posts
        # TODO: implement this function
        pass

    def write(self, request): # POST /save/board/article | write a post
        user = request.user
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception = True)

        if not user.is_active:
            return Response({"error": "You do not have a permission to write a post."}, status = status.HTTP_403_FORBIDDEN)

        serializer.save()
        return Response(serializer.data, status = status.HTTP_201_CREATED)

    def like(self, request): # PUT /save/board/article/vote | like a post
        user = request.user
        post = request.data.get("post_id")
        if UserLikePost.objects.get(user = user, post = post): # 이미 좋아요를 누른 경우
            return Response({"error": "You already liked this post."}, status = status.HTTP_400_BAD_REQUEST)

        UserLikePost.objects.create(user = user, post = post)
        return Response(status = status.HTTP_200_OK) # serializer?

    def delete(self, request): # DELETE /remove/board/article | delete a post
        # TODO: implement this function
        pass

