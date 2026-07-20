from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, CropPredictionRecord, FarmerFeedback

SOIL_TYPE_CHOICES = [
    ('Loamy', 'Loamy Soil (Ideal balance of sand, silt & clay)'),
    ('Clayey', 'Clayey Soil (Heavy water retention)'),
    ('Sandy', 'Sandy Soil (Well-drained, light)'),
    ('Alluvial', 'Alluvial Soil (Rich river basin soil)'),
    ('Black', 'Black Soil / Regur (High moisture retention)'),
    ('Red/Laterite', 'Red / Laterite Soil (Iron & Aluminum rich)'),
]

SEASON_CHOICES = [
    ('Kharif', 'Kharif (Monsoon / Summer Crop: June - Oct)'),
    ('Rabi', 'Rabi (Winter Crop: Oct - March)'),
    ('Zaid', 'Zaid (Summer Crop: March - June)'),
    ('Whole Year', 'Perennial / All Season'),
]

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter strong password'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Confirm password'
    }))
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'e.g. +91 9876543210'
    }))
    location = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'e.g. Punjab, India'
    }))
    farm_size = forms.FloatField(required=False, initial=2.5, widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'placeholder': 'Size in acres'
    }))

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter unique username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@example.com'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match. Please re-enter.")
        return cleaned_data


class UserLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control form-control-lg',
        'placeholder': 'Username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control form-control-lg',
        'placeholder': 'Password'
    }))


class UserProfileForm(forms.ModelForm):
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    location = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    farm_size = forms.FloatField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class CropRecommendationForm(forms.Form):
    nitrogen = forms.FloatField(
        min_value=0, max_value=200, label="Nitrogen (N) - ratio in soil (0 - 140 kg/ha)",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 90', 'step': '0.1'})
    )
    phosphorus = forms.FloatField(
        min_value=0, max_value=200, label="Phosphorus (P) - ratio in soil (5 - 145 kg/ha)",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 42', 'step': '0.1'})
    )
    potassium = forms.FloatField(
        min_value=0, max_value=250, label="Potassium (K) - ratio in soil (5 - 205 kg/ha)",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 43', 'step': '0.1'})
    )
    temperature = forms.FloatField(
        min_value=0, max_value=60, label="Temperature (°C) (8 - 45 °C)",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 25.5', 'step': '0.1'})
    )
    humidity = forms.FloatField(
        min_value=0, max_value=100, label="Relative Humidity (%) (14 - 100%)",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 80.0', 'step': '0.1'})
    )
    ph = forms.FloatField(
        min_value=1, max_value=14, label="Soil pH Value (3.5 - 10.0)",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 6.5', 'step': '0.1'})
    )
    rainfall = forms.FloatField(
        min_value=0, max_value=500, label="Rainfall (mm) (20 - 300 mm)",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 200.0', 'step': '0.1'})
    )
    soil_type = forms.ChoiceField(
        choices=SOIL_TYPE_CHOICES, label="Soil Type",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    season = forms.ChoiceField(
        choices=SEASON_CHOICES, label="Cropping Season",
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class FarmerFeedbackForm(forms.ModelForm):
    class Meta:
        model = FarmerFeedback
        fields = ['subject', 'message']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Question about Rice fertilizer advice'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe your question, observation, or feedback...'}),
        }


class AdminFeedbackReplyForm(forms.ModelForm):
    class Meta:
        model = FarmerFeedback
        fields = ['admin_reply', 'status']
        widgets = {
            'admin_reply': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Type your official reply here...'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
