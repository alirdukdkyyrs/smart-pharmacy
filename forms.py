from django import forms
from .models import Medicine
class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = ["name","barcode","category","company","purchase_price","sale_price","quantity","min_quantity","expiry_date","supplier"]
        widgets = {"expiry_date": forms.DateInput(attrs={"type":"date"})}
