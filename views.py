from decimal import Decimal
from uuid import uuid4
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Sum, Count
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Medicine, Sale, SaleItem
from .forms import MedicineForm

@login_required
def dashboard(request):
    today = timezone.localdate()
    context = {
        "medicine_count": Medicine.objects.count(),
        "low_stock": Medicine.objects.filter(quantity__lte=models_f("min_quantity")).count(),
        "sales_today": Sale.objects.filter(created_at__date=today).aggregate(v=Sum("total"))["v"] or Decimal("0"),
        "sales_count": Sale.objects.filter(created_at__date=today).count(),
        "recent_sales": Sale.objects.order_by("-created_at")[:6],
        "alerts": Medicine.objects.filter(expiry_date__lte=today + timezone.timedelta(days=60)).order_by("expiry_date")[:6],
    }
    return render(request, "pharmacy/dashboard.html", context)

def models_f(name):
    from django.db.models import F
    return F(name)

@login_required
def medicine_list(request):
    q = request.GET.get("q", "").strip()
    medicines = Medicine.objects.select_related("supplier").order_by("name")
    if q: medicines = medicines.filter(name__icontains=q) | medicines.filter(barcode__icontains=q)
    return render(request, "pharmacy/medicine_list.html", {"medicines": medicines, "q": q})

@login_required
def medicine_create(request):
    form = MedicineForm(request.POST or None)
    if form.is_valid():
        form.save(); messages.success(request, "تمت إضافة الدواء بنجاح."); return redirect("medicine_list")
    return render(request, "pharmacy/medicine_form.html", {"form": form, "title": "إضافة دواء"})

@login_required
def medicine_edit(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    form = MedicineForm(request.POST or None, instance=medicine)
    if form.is_valid():
        form.save(); messages.success(request, "تم تحديث بيانات الدواء."); return redirect("medicine_list")
    return render(request, "pharmacy/medicine_form.html", {"form": form, "title": "تعديل دواء"})

@login_required
def medicine_delete(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    if request.method == "POST":
        medicine.delete(); messages.success(request, "تم حذف الدواء."); return redirect("medicine_list")
    return render(request, "pharmacy/confirm_delete.html", {"object": medicine})

@login_required
def sales_list(request):
    return render(request, "pharmacy/sales_list.html", {"sales": Sale.objects.order_by("-created_at")[:100]})

@login_required
def sale_create(request):
    medicines = Medicine.objects.filter(quantity__gt=0).order_by("name")
    if request.method == "POST":
        med_id = request.POST.get("medicine")
        try:
            qty = int(request.POST.get("quantity", "0"))
            with transaction.atomic():
                med = Medicine.objects.select_for_update().get(pk=med_id)
                if qty < 1: raise ValueError("الكمية يجب أن تكون واحداً أو أكثر.")
                if med.quantity < qty: raise ValueError("الكمية المطلوبة غير متوفرة في المخزون.")
                sale = Sale.objects.create(invoice_no="INV-" + uuid4().hex[:8].upper(), total=med.sale_price * qty)
                SaleItem.objects.create(sale=sale, medicine=med, quantity=qty, unit_price=med.sale_price)
                med.quantity -= qty; med.save(update_fields=["quantity"])
            messages.success(request, f"تم إنشاء الفاتورة {sale.invoice_no} بنجاح.")
            return redirect("sales_list")
        except Medicine.DoesNotExist:
            messages.error(request, "الدواء المحدد غير موجود.")
        except (ValueError, TypeError) as e:
            messages.error(request, str(e) or "يرجى إدخال بيانات صحيحة.")
    return render(request, "pharmacy/sale_form.html", {"medicines": medicines})
