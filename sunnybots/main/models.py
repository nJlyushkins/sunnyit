from django.db import models
from django.contrib.auth.models import User

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.IntegerField(default=0)

class Group(models.Model):
    class GroupStatus(models.IntegerChoices):
        WAIT = 0
        VERIFYING = 1
        VERIFY = 2
        ERROR = -1
    group_id = models.CharField(default=0,max_length=50)
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.IntegerField(choices=GroupStatus.choices, default=GroupStatus.WAIT)
    token = models.CharField(max_length=255, default='')

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Группы'

class Bot(models.Model):
    group_id = models.ForeignKey(Group, on_delete=models.CASCADE)
    owner_id = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    lib = models.CharField(max_length=100,default='bottest01')
    running = models.BooleanField(default=False)
    cost = models.IntegerField(default=250)
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Боты'

class ConfirmCode(models.Model):
    group_id = models.ForeignKey(Group, on_delete=models.CASCADE)
    code = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.group_id}'

    class Meta:
        verbose_name = 'Коды подтверждения'

class Payment(models.Model):

    class PaymentStatus(models.IntegerChoices):
        WAIT = 0
        PAID = 1
        ERROR = 2

    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.IntegerField(choices=PaymentStatus.choices, default=PaymentStatus.WAIT)
    date = models.DateTimeField(auto_now_add=True)
    total = models.IntegerField(default=0)
    description = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.owner}'

    class Meta:
        verbose_name = 'Чеки'
