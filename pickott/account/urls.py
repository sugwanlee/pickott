from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path("signup/", views.CreateUserView.as_view()),
    path("signin/", TokenObtainPairView.as_view()),
    path("token/refresh/", TokenRefreshView.as_view()),
    path("logout/", views.LogoutView.as_view()),
    # 프로필 페이지 API 추가
    path("profile/", views.UserDetailView.as_view()),
]
