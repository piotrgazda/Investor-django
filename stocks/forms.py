
from django.forms import ModelForm
from stocks import models
from django import forms


class DateInput(forms.DateInput):
    input_type = 'date'


class InvestmentForm(ModelForm):

    class Meta:
        model = models.UserStockTransactions
        fields = ['company', 'quantity', 'price', 'date','buy']
        widgets = {
            'date': DateInput(),
        }
