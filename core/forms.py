from django import forms
from .models import Customer, Dress, Rental

class DateInput(forms.DateInput):
    input_type = 'date'

class RentalForm(forms.ModelForm):
    class Meta:
        model = Rental
        fields = '__all__'
        widgets = {
            'start_date': DateInput(),
            'end_date': DateInput(),
        }

class DressForm(forms.ModelForm):
    class Meta:
        model = Dress
        fields = '__all__'

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'