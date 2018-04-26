from django import forms

class RiskFreeRateForm(forms.Form):
    rate = forms.FloatField(label='Risk Free Rate:', min_value=0, max_value=1)