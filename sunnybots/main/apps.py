from django.apps import AppConfig, registry
from datetime import datetime, timedelta
from django import db

class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'
    def ready(self):
        from .monitors import dateMonitor
        print("run background task")
        dateMonitor(repeat=15,repeat_until=None)