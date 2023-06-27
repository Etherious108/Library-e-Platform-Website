from datetime import date
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Customer as User


class UserRegister(UserCreationForm):
    CustFName = forms.CharField(label='First name: ', widget=forms.TextInput(attrs={'class': 'form-control'}))
    CustLName = forms.CharField(label='Last name: ', widget=forms.TextInput(attrs={'class': 'form-control'}))
    CustEmail = forms.EmailField(label='Email: ', widget=forms.EmailInput(attrs={'class': 'form-control'}))
    username = forms.CharField(label='Username: ', widget=forms.TextInput(attrs={'class': 'form-control'}))
    CustomerPNo = forms.CharField(label='Phone Number ', widget=forms.NumberInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username','CustFName', 'CustLName', 'CustEmail','CustomerPNo']

class LoginForm(forms.Form):
    CustEmail = forms.CharField(label="Registered Email",widget=forms.TextInput(attrs={"class": "form-control"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))
    
class SearchForm(forms.Form):
    searchtext = forms.CharField(label="Search Books",widget=forms.TextInput(attrs={"class": "form-control"}))
    
class BorrowForm(forms.Form):
    IssueDate = forms.DateField(label="Borrow From", widget=forms.DateInput(attrs={'class': 'form-control',"type":"date", 'min': date.today()}))
    ReleaseDate = forms.DateField(label="Borrow Until", widget=forms.DateInput(attrs={'class': 'form-control',"type":"date", 'min': date.today()}))
    