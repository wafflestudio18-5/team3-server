from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from comment.models import Comment, UserLikeComment
from comment.serializers import CommentSerializer
from user.models import UserProfile
from post.models import Post

class CommentViewSet(viewsets.GenericViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated(), )

    def get_permissions(self):
        if self.action in ('listComments',) :
            return (AllowAny(), )
        return self.permission_classes

    @action(detail=False, methods=['GET'], url_path='list')
    def listComments(self, request): # GET /comment/list/ | list comments
        try:
            post_id = int(request.query_params.get('post'))
        except TypeError:
            return Response({"error": "post must be an integer."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            post = Post.objects.get(id=post_id)
        except ObjectDoesNotExist:
            return Response({"error": "Post does not exist."}, status=status.HTTP_404_NOT_FOUND)

        comments = Comment.objects.filter(post_id=post_id, parent=None)
        data = self.get_serializer(comments, many=True).data
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path='write')
    def writeComment(self, request): # POST /comment/write/ | write a comment
        user = request.user
        is_verified = UserProfile.objects.get(user=user).is_verified
        if not is_verified:
            return Response({"error": "You do not have a permission to write a comment."}, status=status.HTTP_403_FORBIDDEN)

        try:
            post_id = int(request.data.get('post'))
            post = Post.objects.get(id=post_id)
        except TypeError:
            return Response({"error": "post must be an integer."}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response({"error": "Post does not exist."}, status=status.HTTP_404_NOT_FOUND)

        if "parent" in request.data:
            try:
                parent_id = int(request.data.get('parent'))
                parent = Comment.objects.get(id=parent_id)
            except TypeError:
                return Response({"error": "parent must be an integer."}, status=status.HTTP_400_BAD_REQUEST)
            except ObjectDoesNotExist:
                return Response({"error": "Parent comment does not exist."}, status=status.HTTP_404_NOT_FOUND)
            else:
                if parent.parent != None:
                    return Response({"error": "Nested reply comment is not allowed."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        serializer.save()
        return Response(serializer.data, status = status.HTTP_201_CREATED)

    @transaction.atomic
    @action(detail=True, methods=['PUT'], url_path='like')
    def likeComment(self, request, pk=None): # PUT /comment/{pk}/like/ | like a comment
        user = request.user
        is_verified = UserProfile.objects.get(user=user).is_verified
        if not is_verified:
            return Response({"error": "You do not have a permission to like a comment."}, status=status.HTTP_403_FORBIDDEN)

        try:
            comment = self.get_object()
        except ObjectDoesNotExist:
            return Response({"error": "Comment does not exist."}, status=status.HTTP_404_NOT_FOUND)
        try:
            UserLikeComment.objects.get(user=user, comment=comment)
        except ObjectDoesNotExist:
            pass
        else:  # 이미 좋아요를 누른 경우
            return Response({"error": "You already liked this comment."}, status=status.HTTP_400_BAD_REQUEST)
        UserLikeComment.objects.create(user=user, comment=comment)

        comment.numLikes += 1
        comment.save()

        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['PUT'], url_path='update')
    def updateComment(self, request, pk=None): # PUT /comment/{pk}/update/ | update a comment
        user = request.user
        is_verified = UserProfile.objects.get(user=user).is_verified
        if not is_verified:
            return Response({"error": "You do not have a permission to update a comment."}, status=status.HTTP_403_FORBIDDEN)
        try:
            comment = self.get_object()
        except ObjectDoesNotExist:
            return Response({"error": "Comment does not exist."}, status=status.HTTP_404_NOT_FOUND)

        if user != comment.user:
            return Response({"error": "You do not have a permission to update this comment."}, status=status.HTTP_403_FORBIDDEN)

        if "content" in request.data:
            comment.content = request.data.get('content')

        comment.save()
        return Response(status=status.HTTP_200_OK)


    @action(detail=True, methods=['DELETE'], url_path='delete')
    def deleteComment(self, request, pk=None): # DELETE /comment/{pk}/delete/ | delete a comment
        user = request.user
        is_verified = UserProfile.objects.get(user=user).is_verified
        if not is_verified:
            return Response({"error": "You do not have a permission to delete a comment."}, status=status.HTTP_403_FORBIDDEN)
        try:
            comment = self.get_object()
        except ObjectDoesNotExist:
            return Response({"error": "Comment does not exist."}, status=status.HTTP_404_NOT_FOUND)

        if user != comment.user:
            return Response({"error": "You do not have a permission to delete this post."}, status=status.HTTP_403_FORBIDDEN)
        comment.deleted = True
        comment.save()
        return Response(status=status.HTTP_200_OK)
