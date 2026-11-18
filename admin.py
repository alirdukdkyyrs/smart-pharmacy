from django.contrib import admin
from .models import Supplier, Customer, Medicine, Sale, SaleItem
admin.site.register([Supplier, Customer, Medicine, Sale, SaleItem])
