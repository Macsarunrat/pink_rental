from django import forms
from .models import Customer, Dress, Rental, Accessory


# 1. ฟอร์มสำหรับเพิ่มเครื่องประดับ (Admin)
class AccessoryForm(forms.ModelForm):
    class Meta:
        model = Accessory
        fields = ['name', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control rounded-pill', 'placeholder': 'ชื่อเครื่องประดับ'}),
            'image': forms.FileInput(attrs={'class': 'form-control rounded-pill'}),
        }


class DateInput(forms.DateInput):
    input_type = 'date'

class RentalForm(forms.ModelForm):
    # เราจะเรนเดอร์ accessories แบบพิเศษใน HTML (ไม่ใช้ widget ปกติ)
    # แต่ต้องประกาศ field ไว้เพื่อให้ Django รู้จัก
    accessories = forms.ModelMultipleChoiceField(
        queryset=Accessory.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple # ตัวนี้เดี๋ยวเราจะซ่อน แล้วสร้าง UI ทับ
    )
    class Meta:
        model = Rental
        fields = ['customer', 'dress', 'accessories', 'start_date', 'end_date', 'price_override', 'note']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control rounded-pill'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control rounded-pill'}),
        }

class DressForm(forms.ModelForm):
    class Meta:
        model = Dress
        fields = '__all__'

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'



