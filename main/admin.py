from django.contrib import admin

from main.models import CustomUser, ChatBot, VKGroup, UserBalance, ConfirmCode, GroupStatistics, BotStatistics

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(UserBalance)
admin.site.register(VKGroup)
admin.site.register(ChatBot)
admin.site.register(ConfirmCode)
admin.site.register(BotStatistics)
admin.site.register(GroupStatistics)