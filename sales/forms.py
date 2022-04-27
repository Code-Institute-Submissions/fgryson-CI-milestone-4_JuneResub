from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget


class CheckoutForm(forms.Form):
    street_address = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Ballyboffin Lane'})
    )
    apartment_address = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'House name'})
    )
    country = CountryField(blank_label='(select country)').formfield(
        required=False,
        widget=CountrySelectWidget(
            attrs={'class': 'custom-select d-block w-100'})
    )
    postcode = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': ''})
    )
    same_shipping_address = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput()
    )
    save = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput()
    )
