from django.contrib import admin
from .models import Customer,Dress,Rental

# Register your models here.

admin.site.register(Customer)
admin.site.register(Dress)
admin.site.register(Rental)