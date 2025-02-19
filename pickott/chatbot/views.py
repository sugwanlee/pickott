from rest_framework.views import APIView
from .models import ChatBot
from .serializers import ChatBotSerializer
from rest_framework.response import Response
from rest_framework import authentication, permissions
from rest_framework.permissions import IsAuthenticated
from .chatbot_2 import chatbot_call
from account.models import User

class ChatBotAPIView(APIView):

    # permission_classes = [IsAuthenticated]

    def get(self, request):
        logs = ChatBot.objects.all()
        Serializer = ChatBotSerializer(logs, many=True)
        return Response(Serializer.data)

    def post(self, request):
        user=User.objects.get(id=1)
        serializer = ChatBotSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            answer = chatbot_call(request.data.get("question"), request.user)
            serializer.save(answer=answer, user=user)
            return Response(serializer.data)
