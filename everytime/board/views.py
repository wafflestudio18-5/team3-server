from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

from board.models import Board
from board.serializers import BoardSerializer


class BoardViewSet(viewsets.GenericViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = (IsAuthenticated(), )

    def get_permissions(self):
        if self.action in ('listBoards',):
            return (AllowAny(), )
        return self.permission_classes

    @action(detail=False, methods=['GET'], url_path='list')
    def listBoards(self, request): # GET /api/board/list: List information about boards.
        board = Board.objects.all().order_by('created_at') # cache?
        data = self.get_serializer(board, many=True).data
        #return Response("test", status=status.HTTP_200_OK)
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path='create')
    def createBoard(self, request): #POST /api/board/create: board 생성 (개발용 api)
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        #TODO: 실제로 이 api를 사용할 것이라면 is_valid 추가
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)



