from rest_framework.views import APIView
from .models import ChatBot
from .serializers import ChatBotSerializer
from rest_framework.response import Response
from rest_framework import authentication, permissions
from rest_framework.permissions import IsAuthenticated
from .chatbot import chatbot_call
from account.models import User

class ChatBotAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        logs = ChatBot.objects.all()
        Serializer = ChatBotSerializer(logs, many=True)
        return Response(Serializer.data)

    def post(self, request):
        genre_names = ", ".join([genre.name for genre in request.user.preferred_genre.all()])
        serializer = ChatBotSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            answer = chatbot_call(request.data.get("question"), request.user.username, genre_names)
            serializer.save(answer=answer, user=request.user)
            return Response(serializer.data)
