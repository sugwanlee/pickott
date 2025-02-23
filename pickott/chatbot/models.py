from django.db import models


# Create your models here.
class ChatBot(models.Model):
    user = models.ForeignKey(
        "account.User", on_delete=models.CASCADE, related_name="chatbots"
    )
    question = models.TextField()
    answer = models.TextField()
    language = models.CharField(max_length=20)