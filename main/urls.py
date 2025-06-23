from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('connect-group-ajax/', views.connect_group_ajax, name='connect_group_ajax'),
    path('check-callback-server/', views.check_callback_server, name='check_callback_server'),
    path('toggle-bot-status/', views.toggle_bot_status, name='toggle_bot_status'),
    path('profile/', views.profile, name='profile'),
    path('faq/', views.faq, name='faq'),
    path('payment/', views.payment, name='payment'),
    path('order-bot/', views.order_bot, name='order_bot'),
    path('vk-callback/', views.vk_callback, name='vk_callback'),
    path('edit-bot/<int:bot_id>/', views.edit_bot, name='edit_bot'),  # Placeholder for bot editing
]