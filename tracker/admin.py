from django.apps import apps
from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered

from tracker.models import Transaction, UserSelectedFund

# Register your models here.

app_models = apps.get_app_config('tracker').get_models()


class TransactionAdmin(admin.StackedInline):
    model = Transaction


@admin.register(UserSelectedFund)
class UserSelectedFundAdmin(admin.ModelAdmin):
    inlines = [TransactionAdmin, ]


for model in app_models:
    try:
        admin.site.register(model)
    except AlreadyRegistered:
        pass
