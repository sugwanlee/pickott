from django.contrib import admin
from .models import User, Genre

# admin 페이지에서 Genre 모델 변경 가능하게 적용
admin.site.register(Genre)
