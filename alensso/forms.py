from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm

#Create forms here

class ProductForm(forms.ModelForm):
    
    class Meta:
        model = Product
        fields = (['name','category','price','bio','pics','view'])
        widgets = {
            'name':forms.TextInput(attrs={'class':'form-control m-2'}),
            'price':forms.NumberInput(attrs={'class':'form-control m-2'}),
            'bio':forms.Textarea(attrs={'class':'form-control m-2'}),
            'view':forms.CheckboxInput(attrs={'class':'m-2'}),
            }

        labels = {
            'name': 'Product Name:',
            'bio':'Description:',
            'view':'View in home page: ',
            'category':'Category:',
            'price':'Product Price:'
        }
    category  = forms.ModelChoiceField(queryset=Category.objects.all(),widget=forms.Select(attrs={'class':'form-control m-2'}),empty_label='Select a Category')
    pics = forms.ImageField(label='Select an Image: ')
    


class CustomerForm(UserCreationForm):
    password1 = forms.CharField(label='Enter Password',widget=forms.PasswordInput(attrs={'class':'form-control m-2'}))
    password2 = forms.CharField(label='Confirm Password',widget=forms.PasswordInput(attrs={'class':'form-control m-2'}))
    email = forms.CharField(required=False,label='Valid Email',widget = forms.EmailInput(attrs={'class':'form-control m-2'}))
    class Meta:
        model = User
        fields = ['username','email','password1','password2']
        widgets = {'username': forms.TextInput(attrs={'class':'form-control m-2'})}


class LoginUserForm(forms.Form):
    username = forms.CharField(required=True,label='Enter Username',widget=forms.TextInput(attrs={'class':'form-control m-2'}))
    password = forms.CharField(required=True,label='Enter Password',widget=forms.PasswordInput(attrs={'class':'form-control m-2'}))


class CategoryForm(forms.ModelForm):
    img = forms.ImageField(label='Select an Image: ')    
    class Meta:
        model = Category  
        fields = ("__all__")
        widgets = {
            'name':forms.TextInput(attrs={'class':'form-control m-2 mb-5'})}
        labels = {
            'name': 'Product Name:',}
