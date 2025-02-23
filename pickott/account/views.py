from rest_framework import status
from rest_framework.response import Response
from .serializers import CreateUserSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

# 추가
from .models import User, Genre, Ott
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



class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근 가능하도록 설정


# # get 수정 전 ────────────────────────────────────────────────────────
#     def get_object(self, request):  # 중복 되는 코드 함수로 정의
#         return get_object_or_404(User, pk=request.user.pk)

#     def get(self, request):
#         """유저 정보 조회 (선호 장르 포함)"""
#         user = request.user
#         serializer = CreateUserSerializer(user)
#         response_data = serializer.data

#         # 🔹 `preferred_genre`를 장르 ID 리스트가 아니라 장르 이름 리스트로 변환
#         response_data["preferred_genre"] = [
#             genre.name for genre in user.preferred_genre.all()
#         ]

#         return Response(response_data)


    """ GET 메서드 변경사항
    수정 전: get_object 함수 사용
    수정 후: request.user 로 직접 사용으로 변경
    """

# 수정 된 코드

    # 유저 정보 조회 (선호 장르 포함)
    def get(self, request): 
        user = request.user  # JWT 토큰으로 인증된 현재 유저 정보 가져오기
        serializer = CreateUserSerializer(user)  # 유저 정보 직렬화
        response_data = serializer.data # 직렬화된 데이터 가져오기
        
        # 선호 장르 리스트 변환
        response_data["preferred_genre"] = [
            genre.name for genre in user.preferred_genre.all()
            ]  # ManyToMany 관계에서 장르 이름만 추출
        # 구독 OTT 리스트 변환
        response_data["subscribed_ott"] = [
            ott.name for ott in user.subscribed_ott.all()
            ]  # ManyToMany 관계에서 OTT 이름만 추출
        
        return Response(response_data)


# put 수정 전 ──────────────────────────────────────────────────────────────────────    
#     def put(self, request):
#         # 유저 정보 수정 (선호 장르 변경 가능)
#         user = request.user
#         serializer = CreateUserSerializer(user, data=request.data, partial=True)

#         if serializer.is_valid():
#             preferred_genres = request.data.get("preferred_genre", [])
#             genre_objects = Genre.objects.filter(
#                 name__in=preferred_genres
#             )  # 🔥 장르 객체 찾기
#             user.preferred_genre.set(genre_objects)  # 🔥 ManyToMany 관계 업데이트
#             user.save()
#             return Response(CreateUserSerializer(user).data)  # 🔥 변경된 데이터 반환
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    """ PUT 메서드 변경사항

    수정 전: serializer 검증, filter 사용, save() 호출
    수정 후: set() 메서드로 간단한 업데이트
    """

# 수정 된 코드

    # 유저 정보 수정 (선호 장르 변경 가능)
    def put(self, request):
        user = request.user  # JWT 토큰으로 인증된 현재 유저 정보 가져오기
        preferred_genres = request.data.get("preferred_genre", [])  # 요청 데이터에서 선호 장르 리스트 추출
        
        # 장르 객체 처리
        genre_objects = [ # 장르 객체 생성
            Genre.objects.get_or_create(name=genre_name)[0] 
            for genre_name in preferred_genres]  # 장르가 없으면 생성, 있으면 가져옴
        
        # 선호 장르 업데이트
        user.preferred_genre.set(genre_objects)  # set() 메서드로 ManyToMany 관계를 한 번에 업데이트
        
        # ott 객체 처리
        ott_objects = [
            Ott.objects.get_or_create(name=ott_name)[0]
            for ott_name in request.data.get("subscribed_ott", [])
            ]
        
        # 구독 ott 업데이트
        user.subscribed_ott.set(ott_objects)
        
        # 응답 데이터 생성
        serializer = CreateUserSerializer(user)  # 업데이트된 유저 정보 직렬화
        response_data = serializer.data # 직렬화된 데이터 가져오기
        response_data["preferred_genre"] = [
            genre.name for genre in user.preferred_genre.all()
            ]  # 업데이트된 장르 리스트 포함
        
        response_data["subscribed_ott"] = [
            ott.name for ott in user.subscribed_ott.all()
            ] # 업데이트된 장르 리스트 포함
        
        return Response(response_data)
    
    
# 까지 put수정 후 ──────────────────────────────────────────────────────────────────────



    def delete(self, request):  # 유저 삭제
        user = self.get_object(request)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)