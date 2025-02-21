from django.db import models
from django.contrib.auth.models import AbstractUser

# 다대다 관계를 위한 장르 테이블 생성
# admin 페이지에서 직접 장르 넣어줘야 함. 영어로 추가
"""    genre_list = [
        ("Action","액션"),
        ("Adventure","어드벤처"),
        ("Animation","애니메이션"),
        ("Comedy","코미디"),
        ("Crime","범죄"),
        ("Documentary","다큐멘터리"),
        ("Drama","드라마"),
        ("Family","가족"),
        ("Fantasy","판타지"),
        ("History","역사"),
        ("Horror","역사"),
        ("Music","음악"),
        ("Mystery","미스터리"),
        ("Romance","로맨스"),
        ("Science Fiction","SF"),
        ("Thriller","스릴러"),
        ("War","전쟁"),
        ("Western","서부극")
    ]
"""


class Genre(models.Model):
    """장르 모델 (유저가 여러 개 선택 가능)"""

    name = models.CharField(max_length=50, unique=True)


# 선호 장르 컬럼을 추가하여 여러 장르를 선택할 수 있게 설정.
class User(AbstractUser):
    preferred_genre = models.ManyToManyField(Genre, blank=True, related_name="users")
