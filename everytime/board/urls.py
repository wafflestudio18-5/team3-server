from django.urls import include, path
from rest_framework.routers import SimpleRouter

from board.views import BoardViewSet

app_name = 'board'

#TODO: change this url


#임시 url
router = SimpleRouter()
router.register('board', BoardViewSet, basename='board')  # /api/board/

urlpatterns = [
    path('', include((router.urls))),
]
