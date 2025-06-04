from django.urls import path

from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('panel',views.panel,name='panel'),
    path('login',views.login,name='login'),
    path('signup',views.signup,name='signup'),
    path('logout',views.logout,name='logout'),
    path('group-add',views.groupAdd,name='groupAdd'),
    path('group-confirm',views.groupConfirm,name='groupConfirm'),
    path('callback',views.callback,name='callback'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)