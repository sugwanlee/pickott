from rest_framework import status
from rest_framework.response import Response
from .serializers import CreateUserSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

# 추가
from .models import User, Genre
from django.shortcuts import get_object_or_404


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
        except Exception as e:
            return Response(
                {"detail": "token error."}, status=status.HTTP_400_BAD_REQUEST
            )


# 추가
class UserDetailView(APIView):
    def get_object(self, request):  # 중복 되는 코드 함수로 정의
        return get_object_or_404(User, pk=request.user.pk)

    def get(self, request):
        """유저 정보 조회 (선호 장르 포함)"""
        user = request.user
        serializer = CreateUserSerializer(user)
        response_data = serializer.data

        # 🔹 `preferred_genre`를 장르 ID 리스트가 아니라 장르 이름 리스트로 변환
        response_data["preferred_genre"] = [
            genre.name for genre in user.preferred_genre.all()
        ]

        return Response(response_data)

    def put(self, request):
        """유저 정보 수정 (선호 장르 변경 가능)"""
        user = request.user
        serializer = CreateUserSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            preferred_genres = request.data.get("preferred_genre", [])
            genre_objects = Genre.objects.filter(
                name__in=preferred_genres
            )  # 🔥 장르 객체 찾기
            user.preferred_genre.set(genre_objects)  # 🔥 ManyToMany 관계 업데이트
            user.save()
            return Response(CreateUserSerializer(user).data)  # 🔥 변경된 데이터 반환
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):  # 유저 삭제
        user = self.get_object(request)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
