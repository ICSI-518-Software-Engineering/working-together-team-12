from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile
from .models import PaymentDetail
import datetime
from django.core.validators import RegexValidator


# class PaymentDetailForm(forms.ModelForm):
#     class Meta:
#         model = PaymentDetail
#         fields = ['card_number', 'cvv', 'expiry_date', 'card_holder_name']
#         widgets = {
#             'cvv': forms.PasswordInput(), 
#         }
class PaymentDetailForm(forms.ModelForm):
    expiry_month = forms.ChoiceField(choices=[(str(i), str(i)) for i in range(1, 13)], label="Expiry Month")
    expiry_year = forms.ChoiceField(choices=[(str(i), str(i)) for i in range(datetime.datetime.now().year, datetime.datetime.now().year + 20)], label="Expiry Year")

    class Meta:
        model = PaymentDetail
        fields = ['card_number', 'cvv', 'card_holder_name', 'expiry_month', 'expiry_year']
        exclude = ['expiry_date']  

    def clean(self):
        cleaned_data = super().clean()
        month = cleaned_data.get('expiry_month')
        year = cleaned_data.get('expiry_year')
        cleaned_data['expiry_date'] = datetime.date(year=int(year), month=int(month), day=29)
        return cleaned_data
    def save(self, commit=True):
        instance = super().save(commit=False)

        month = self.cleaned_data.get('expiry_month')
        year = self.cleaned_data.get('expiry_year')
        if month and year: 
            instance.expiry_date = datetime.date(year=int(year), month=int(month), day=28)

        if commit:
            instance.save()  
        return instance

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        for fieldname in ['username', 'email', 'password1', 'password2']:
            self.fields[fieldname].help_text = None
            self.fields[fieldname].error_messages = {'required': 'This field is required.'}      

class UserLoginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['name', 'profile_pic','address','phno']

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    username = forms.CharField(
        max_length=150,
        required=True,
        help_text='Alphanumerics and @/./+/-/_ only.',
        validators=[RegexValidator(regex='^[a-zA-Z0-9@.+-_]+$',
                                   message='Enter a valid username. This value may contain only letters, numbers, and @/./+/-/_ characters.')],
        error_messages={'required': 'Please enter a username.'}
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2',)