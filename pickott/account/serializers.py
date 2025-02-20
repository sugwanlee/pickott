from rest_framework import serializers
from .models import User, Genre


class CreateUserSerializer(serializers.ModelSerializer):

    preferred_genre = serializers.PrimaryKeyRelatedField(
        queryset=Genre.objects.all(), many=True, required=False
    )

    class Meta:
        model = User
        fields = ["email", "username", "password", "preferred_genre"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User(email=validated_data["email"], username=validated_data["username"])
        user.set_password(validated_data["password"])
        user.save()
        return user

    def to_representation(self, instance):
        """유저 정보 조회 시 장르 ID가 아닌 장르 이름으로 변환"""
        representation = super().to_representation(instance)
        representation["preferred_genre"] = [
            genre.name for genre in instance.preferred_genre.all()
        ]
        return representation

    def update(self, instance, validated_data):
        """유저 정보 수정 시, ManyToManyField 데이터 업데이트 처리"""
        preferred_genres = validated_data.pop("preferred_genre", None)
        if preferred_genres is not None:
            instance.preferred_genre.set(
                preferred_genres
            )  # 🔥 기존 데이터 대체 업데이트
        return super().update(instance, validated_data)
