from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from board.models import Board
from board.serializers import BoardSerializer


class BoardViewSet(viewsets.GenericViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = (IsAuthenticated(),)

    @action(detail=False, methods=['GET'])
    def list(self, request): # GET /find/board/list: List information about boards.
        board = Board.objects.all().order_by('created_at') # cache?
        data = self.get_serializer(board, many=True).data
        return Response(data, status=status.HTTP_200_OK)

