from django.contrib import admin
from stocks import models

# Register your models here.
admin.site.register(models.Company)
admin.site.register(models.Price)
admin.site.register(models.UserFollowedCompanies)
admin.site.register(models.UserStockTransactions)