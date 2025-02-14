from django.db import models

# Create your models here.
class ChatBot(models.Model):
    question = models.TextField()
    answer = models.TextField()