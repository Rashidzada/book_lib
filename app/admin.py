from django.contrib import admin
from .import models
# Register your models here.
admin.site.register([models.UserProfile,models.Book,models.Loan,models.Request,models.Shelf])