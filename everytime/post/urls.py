from django.urls import include, path
from rest_framework.routers import SimpleRouter

from post.views import PostViewSet

app_name = 'post'

#TODO: change this url

#임시 url
router = SimpleRouter()
router.register('post', PostViewSet, basename='post')  # /api/post/

urlpatterns = [
    path('', include((router.urls))),
]