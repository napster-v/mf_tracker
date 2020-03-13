from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models


# Create your models here.

class FundType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Fund(models.Model):
    name = models.CharField(max_length=100)
    fund_type = models.ForeignKey(FundType, on_delete=models.CASCADE)
    scheme_code = models.PositiveSmallIntegerField()

    def __str__(self):
        return f'{self.name} - {self.fund_type.name}'


class UserSelectedFund(models.Model):
    class Mode(models.IntegerChoices):
        sip = 1, 'SIP'
        additional = 2, 'ADDITIONAL/OTI'

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fund = models.ForeignKey(Fund, on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(verbose_name='Monthly Amount')
    duration = models.PositiveSmallIntegerField()
    mode = models.IntegerField(choices=Mode.choices)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.user.username} - {self.fund.name}'


class Transaction(models.Model):
    user_fund = models.ForeignKey(UserSelectedFund, on_delete=models.PROTECT)
    amount = models.PositiveSmallIntegerField(blank=True,
                                              help_text='If no amount, then amount taken from fund selected.')
    nav = models.DecimalField(decimal_places=3, max_digits=7)
    units = models.DecimalField(decimal_places=3, max_digits=7, blank=True)
    date = models.DateField()

    def clean(self):
        if not self.amount:
            self.amount = self.user_fund.amount

        if not self.units:
            self.units = Decimal(self.amount / self.nav)
