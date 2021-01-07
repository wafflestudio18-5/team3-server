from django.urls import include, path
from rest_framework.routers import SimpleRouter

from comment.views import CommentViewSet

app_name = 'comment'

router = SimpleRouter()
router.register('comment', CommentViewSet, basename='comment')  # /comment/

urlpatterns = [
    path('', include((router.urls))),
]
