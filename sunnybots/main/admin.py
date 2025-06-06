from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Wallet,Group,Bot, ConfirmCode, Payment

# Define an inline admin descriptor for Employee model
# which acts a bit like a singleton
class WalletInline(admin.StackedInline):
    model = Wallet
    can_delete = False
    verbose_name_plural = 'wallet'

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (WalletInline,)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register(Bot)
admin.site.register(Group)
admin.site.register(ConfirmCode)
admin.site.register(Payment)