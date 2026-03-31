from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'customer_name', 'full_address', 'city', 'state', 'pincode', 'phone',
            'product', 'amount', 'tag', 'payment_type', 'status', 'order_date'
        ]
        widgets = {
            'order_date': forms.DateInput(attrs={'type': 'date'}),
            'full_address': forms.Textarea(attrs={'rows': 3}),
        }


class BulkUploadForm(forms.Form):
    file = forms.FileField(help_text='Upload CSV or Excel (.xlsx)')
