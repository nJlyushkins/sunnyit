from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class CustomUser(AbstractUser):
    pass

class UserBalance(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

class VKGroup(models.Model):
    group_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255, blank=True, null=True)  # Добавляем поле для названия группы
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=255)
    verification_status = models.CharField(max_length=50, default='Новый')

class ChatBot(models.Model):
    vk_group = models.ForeignKey(VKGroup, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=50, default='Неактивен')
    library_path = models.CharField(max_length=255)

class ConfirmCode(models.Model):
    vk_group = models.ForeignKey(VKGroup, on_delete=models.CASCADE)
    code = models.CharField(max_length=20)
    date = models.DateTimeField(default=timezone.now)

class GroupStatistics(models.Model):
    vk_group = models.ForeignKey(VKGroup, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    subscribers = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    messages = models.IntegerField(default=0)
    activity_score = models.IntegerField(default=0)

class BotStatistics(models.Model):
    chat_bot = models.ForeignKey(ChatBot, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    messages_processed = models.IntegerField(default=0)
    interactions = models.IntegerField(default=0)
    active_users = models.JSONField(default=list)

class States(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Messages(models.Model):
    bot = models.ForeignKey(ChatBot, on_delete=models.CASCADE)
    text = models.TextField()
    state = models.ForeignKey(States, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message #{self.id} - {self.text[:50]}"

class Media(models.Model):
    message = models.ForeignKey(Messages, on_delete=models.CASCADE, related_name='media_items')
    url = models.URLField(max_length=500)
    type = models.CharField(max_length=50, default='image')  # Например, 'image', 'video'

    def __str__(self):
        return f"Media for Message #{self.message_id} - {self.url}"