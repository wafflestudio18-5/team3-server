from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist


from post.models import Post, UserLikePost
from post.serializers import PostSerializer
from board.models import Board
from user.models import UserProfile

# GET /find/board/article/list | list posts
# POST /save/board/article | write a post
# PUT /save/board/article/vote | like a post
# DELETE /remove/board/article | delete a post

class PostViewSet(viewsets.GenericViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated(), )

    def get_permissions(self):
        if self.action in ('listAllPosts', 'listPosts', 'infoPost', 'hotPosts'):
            return (AllowAny(), )
        return self.permission_classes

    @action(detail=False, methods=['GET'], url_path='listall')
    def listAllPosts(self, request): # GET /post/listall/ | list all posts
    # (모든 board에 있는 post를 보여줌, 개발용 api)
        post = Post.objects.all()
        data = self.get_serializer(post, many=True).data
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path='list')
    def listPosts(self, request): # GET /post/list/ | list posts
        try:
            start_num = int(request.query_params.get('start_num'))
            if 'limit_num' in request.query_params:
                limit_num = int(request.query_params.get('limit_num'))
            else:
                limit_num = 20 # default
            board_id = int(request.query_params.get('board'))
            try:
                board = Board.objects.get(id=board_id)
            except ObjectDoesNotExist:
                return Response({"error": "Board does not exist."}, status=status.HTTP_404_NOT_FOUND)

        except TypeError:
            return Response({"error": "start_num, limit_num and board must be integers."}, status=status.HTTP_400_BAD_REQUEST)

        if 'tag' in request.data:
            tag = request.data.get('tag')
            post = Post.objects.filter(board_id=board_id, tag=tag).order_by('-id')[start_num:start_num+limit_num]
        else:
            post = Post.objects.filter(board_id=board_id).order_by('-id')[start_num:start_num+limit_num]

        data = self.get_serializer(post, many=True).data
        return Response(data, status = status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path='write')
    def writePost(self, request): # POST /post/write/ | write a post
        user = request.user
        is_verified = UserProfile.objects.get(user=user).is_verified
        if not is_verified:
            return Response({"error": "You do not have a permission to write a post."}, status=status.HTTP_403_FORBIDDEN)

        try:
            board_id = int(request.data.get('board'))
        except TypeError:
            return Response({"error": "board must be an integer."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            board = Board.objects.get(id=board_id)
        except ObjectDoesNotExist:
            return Response({"error": "Board does not exist."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        serializer.save(user=user, board_id=board_id)
        return Response(serializer.data, status = status.HTTP_201_CREATED)

    @action(detail=True, methods=['PUT'], url_path='update')
    def updatePost(self, request, pk=None): # PUT /post/{pk}/update/
        user = request.user

        try:
            post = self.get_object()
        except ObjectDoesNotExist:
            return Response({"error": "Post does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(post, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.update(post, serializer.validated_data)
        return Response(serializer.data)

    @transaction.atomic
    @action(detail=True, methods=['PUT'], url_path='like')
    def likePost(self, request, pk=None): # PUT /post/{pk}/like/ | like a post
        user = request.user
        is_verified = UserProfile.objects.get(user=user).is_verified
        if not is_verified:
            return Response({"error": "You do not have a permission to like a post."}, status=status.HTTP_403_FORBIDDEN)

        try:
            post = self.get_object()
        except ObjectDoesNotExist:
            return Response({"error": "Post does not exist."}, status = status.HTTP_404_NOT_FOUND)
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
    def deletePost(self, request, pk=None): # DELETE /post/{pk}/delete/ | delete a post
        user = request.user
        is_verified = UserProfile.objects.get(user=user).is_verified
        if not is_verified:
            return Response({"error": "You do not have a permission to delete a post."}, status=status.HTTP_403_FORBIDDEN)

        try:
            post = self.get_object()
        except ObjectDoesNotExist:
            return Response({"error": "Post does not exist."}, status = status.HTTP_404_NOT_FOUND)

        if user != post.user:
            return Response({"error": "You do not have a permission to delete this post."}, status=status.HTTP_403_FORBIDDEN)
        post.delete()
        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path='hot')
    def hotPosts(self, request): # GET /post/hot/ | list hot posts
        try:
            minLikes = int(request.query_params.get('minLikes'))
        except TypeError:
            return Response({"error": "minLikes must be an integer."}, status=status.HTTP_400_BAD_REQUEST)

        post = Post.objects.filter(numLikes__gte=minLikes).order_by('-id')
        data = self.get_serializer(post, many=True).data
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path='info')
    def infoPost(self, request, pk=None): # GET /post/{post_id}/info/ | get information about a post
        try:
            post = self.get_object()
        except ObjectDoesNotExist:
            return Response({"error": "Post does not exist."}, status = status.HTTP_404_NOT_FOUND)

        data = self.get_serializer(post).data
        return Response(data, status=status.HTTP_200_OK)
      
    @action(detail=False, methods=['GET'], url_path='me')
    def myPost(self, request):
        user = request.user
        post = Post.objects.filter(user=user)
        data = self.get_serializer(post, many=True).data
        return Response(data, status=status.HTTP_200_OK)

