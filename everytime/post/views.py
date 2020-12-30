from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist


from post.models import Post, UserLikePost
from post.serializers import PostSerializer

# GET /find/board/article/list | list posts
# POST /save/board/article | write a post
# PUT /save/board/article/vote | like a post
# DELETE /remove/board/article | delete a post

class PostViewSet(viewsets.GenericViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    #permission_classes = (IsAuthenticated(),)

    # get_serializer_class() ?
    # UserLikePostSerializer ?
    #TODO: check user permission

    @action(detail=False, methods=['GET'], url_path='list')
    def listPosts(self, request): # GET /api/post/list/ | list posts
        # TODO: implement this function
        try:
            start_num = int(request.data.get('start_num')) # request.query_params.get() ?
            if 'limit_num' in request.data:
                limit_num = int(request.data.get('limit_num'))
            else:
                limit_num = 20 # default
            board_id = int(request.data.get('board')) #TODO: check if board_id valid
        except TypeError:
            return Response({"error": "start_num, limit_num and board_id must be integers."}, status=status.HTTP_400_BAD_REQUEST)

        if 'tag' in request.data:
            tag = request.data.get('tag')
            post = Post.objects.filter(board_id=board_id, tag=tag).order_by('-id')[start_num:start_num+limit_num]
        else:
            post = Post.objects.filter(board_id=board_id).order_by('-id')[start_num:start_num+limit_num]

        data = self.get_serializer(post, many=True).data
        return Response(data, status = status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path='write')
    def writePost(self, request): # POST /api/post/write/ | write a post
        user = request.user
        try:
            board_id = int(request.data.get('board'))
        except TypeError:
            return Response({"error": "board id must be an integer."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        # TODO: title if board.has_title
        # TODO: check if board_id valid

        # TODO: check permissions
        #if not user.is_active:
        #    return Response({"error": "You do not have a permission to write a post."}, status = status.HTTP_403_FORBIDDEN)

        serializer.save(user=user, board_id=board_id)
        return Response(serializer.data, status = status.HTTP_201_CREATED)

    @transaction.atomic
    @action(detail=True, methods=['PUT'], url_path='like')
    def likePost(self, request, pk=None): # PUT /api/post/{pk}/like/ | like a post
        # TODO: pk
        user = request.user
        try:
            post = self.get_object()
        except ObjectDoesNotExist:
            return Response({"error": "Post does not exist."}, status = HTTP_404_NOT_FOUND)
        try:
            UserLikePost.objects.get(user=user, post=post)
        except ObjectDoesNotExist:
            pass
        else: # 이미 좋아요를 누른 경우
            return Response({"error": "You already liked this post."}, status = status.HTTP_400_BAD_REQUEST)
        UserLikePost.objects.create(user = user, post = post)

        post.numLikes += 1
        post.save()

        return Response(status = status.HTTP_200_OK) # serializer?

    @action(detail=True, methods=['DELETE'], url_path='delete')
    def deletePost(self, request): # DELETE /api/post/{pk}/delete/ | delete a post
        # TODO: implement this function
        # TODO: pk
        pass


