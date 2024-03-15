from pydantic import ValidationError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .services.order_service import OrderService


class OrderAPIView(APIView):
    def post(self, request):
        try:
            result = OrderService.create_order(request.data)

            return Response(
                data=result,
                status=status.HTTP_201_CREATED,
            )
        except ValidationError as e:
            return Response(
                data=e.errors(),
                status=status.HTTP_400_BAD_REQUEST,
            )
