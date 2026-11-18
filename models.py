from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator

class Supplier(models.Model):
    name = models.CharField("اسم المورد", max_length=150)
    phone = models.CharField("الهاتف", max_length=30, blank=True)
    address = models.CharField("العنوان", max_length=250, blank=True)
    def __str__(self): return self.name

class Customer(models.Model):
    name = models.CharField("اسم العميل", max_length=150)
    phone = models.CharField("الهاتف", max_length=30, blank=True)
    def __str__(self): return self.name

class Medicine(models.Model):
    name = models.CharField("اسم الدواء", max_length=180)
    barcode = models.CharField("الباركود", max_length=80, blank=True, unique=True, null=True)
    category = models.CharField("التصنيف", max_length=100, blank=True)
    company = models.CharField("الشركة المصنعة", max_length=150, blank=True)
    purchase_price = models.DecimalField("سعر الشراء", max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    sale_price = models.DecimalField("سعر البيع", max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    quantity = models.PositiveIntegerField("الكمية", default=0)
    min_quantity = models.PositiveIntegerField("حد التنبيه", default=5)
    expiry_date = models.DateField("تاريخ الصلاحية", null=True, blank=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="المورد")
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.name
    @property
    def is_low_stock(self): return self.quantity <= self.min_quantity
    @property
    def is_expired(self): return bool(self.expiry_date and self.expiry_date < timezone.localdate())

class Sale(models.Model):
    invoice_no = models.CharField("رقم الفاتورة", max_length=30, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="العميل")
    total = models.DecimalField("الإجمالي", max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField("تاريخ البيع", auto_now_add=True)
    def __str__(self): return self.invoice_no

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="items")
    medicine = models.ForeignKey(Medicine, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    @property
    def subtotal(self): return self.quantity * self.unit_price
