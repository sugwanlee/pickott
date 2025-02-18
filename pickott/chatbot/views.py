from rest_framework.views import APIView
from .models import ChatBot
from .serializers import ChatBotSerializer
from rest_framework.response import Response
from rest_framework import authentication, permissions
from rest_framework.permissions import IsAuthenticated
from .chatbot import chat_call
class ChatBotAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        logs = ChatBot.objects.all()
        Serializer = ChatBotSerializer(logs, many=True)
        return Response(Serializer.data)
    
    def post(self, request):
        serializer = ChatBotSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            answer = chat_call(request.data.get("question"))
            serializer.save(answer = answer, user = request.user)
            return Response(serializer.data)