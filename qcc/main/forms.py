from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Campaign, Donation, CampaignImage

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    phone_number = forms.CharField(required=True)
    street_name = forms.CharField(required=True)
    city = forms.CharField(required=True)
    country = forms.CharField(required=True)
    postal_code = forms.CharField(required=True)
    preferred_contact = forms.ChoiceField(
        choices=[
            ('email', 'Email'),
            ('phone', 'Phone'),
            ('whatsapp', 'WhatsApp')
        ],
        required=True
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('phone_number', 'street_name', 'city', 'country', 'postal_code', 'preferred_contact')

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = ('title', 'description', 'goal_amount', 'end_date', 'featured_image', 'is_active')
        widgets = {
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

class CampaignImageForm(forms.ModelForm):
    class Meta:
        model = CampaignImage
        fields = ('image',)

class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = ('amount', 'anonymous', 'message')
