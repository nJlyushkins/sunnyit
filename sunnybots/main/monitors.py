from django.apps import registry
from datetime import datetime, timedelta
from django.utils import timezone
import time
from background_task import background
from vk_api import VkApi


@background(queue="dateMonitor",schedule=5)
def dateMonitor():
    if(registry.apps.ready):
        from django.contrib.auth.models import User
        from .models import Bot, Wallet, Payment, ConfirmCode, Group
        passed = timezone.now() - timedelta(minutes=30)
        if ConfirmCode.objects.filter(date__lte=passed).exists():
            for code in ConfirmCode.objects.filter(date__lte=passed).all():
                code.delete()
        passed = timezone.now() - timedelta(days=30)
        if Bot.objects.filter(payment_date=passed).exists():
            for bot in Bot.objects.filter(date=passed).all():
                if User.objects.filter(id=bot.owner_id).exists():
                    owner = User.objects.get(id=bot.owner_id)[0]
                    if owner.Wallet.balance >= bot.cost:
                        owner.Wallet.balance -= bot.cost
                        owner.save()
                        bot.payment_date = timezone.now()
                        bill = Payment(owner=owner.id, status=0, total=-bot.cost,
                                       description="Оплата хостинга")
                        bill.save()
                    else:
                        bot.running = False
                    bot.save()
                else:
                    bot.running = False
                    bot.save()
        if Group.objects.filter(status=1).exists():
          for group in Group.objects.filter(status=1):
            api = VkApi(token=group.token).get_api()
            checkConfirm = api.groups.getCallbackServers(group_id=group.group_id)
            try:
              status = checkConfirm['items'][0]['status']
            except Exception as e:
              status = None
            if (status == 'ok'):
              group.status = 2
              group.save()
            elif (status == 'failed'):
              group.status = -1
              group.save()
        time.sleep(30)