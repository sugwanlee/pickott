from rest_framework import status
from rest_framework.response import Response
from .serializers import CreateUserSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken # 예외처리 import 추가

class CreateUserView(APIView):
    def post(self, request):
        serializer = CreateUserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {"message": "User created successfully"}, status=status.HTTP_201_CREATED
            )


class LogoutView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"detail": "Successfully logged out."}, status=status.HTTP_200_OK
            )
        except InvalidToken as e: # InvalidToken 예외 처리 추가!
            return Response({"detail": f"Invalid token: {e}"}, status=status.HTTP_400_BAD_REQUEST) # 더 자세한 오류 메시지
        except TokenError as e: # TokenError 예외 처리 추가!
            return Response({"detail": f"Token error: {e}"}, status=status.HTTP_400_BAD_REQUEST) # 더 자세한 오류 메시지
        except Exception as e: # 그 외 예외 처리 (혹시 모를 에러 대비)
            print(f"Unexpected error during logout: {e}") # 서버 로그에 예외 정보 기록 (디버깅 용이)
            return Response(
                {"detail": "An unexpected error occurred during logout."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )