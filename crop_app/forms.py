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
        min_value=0, max_value=200,
        label="Nitrogen (N) - Soil Available N (kg/ha equivalent)",
        help_text="Estimated available mineral N (NO3- / NH4+). Note: Soil N is transient; leaf tissue analysis is standard for perennial crops.",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 20.0', 'step': '0.1'})
    )
    phosphorus = forms.FloatField(
        min_value=0, max_value=200,
        label="Phosphorus (P) - Available P (kg/ha equivalent, e.g. Bray/Mehlich)",
        help_text="Extractable available soil phosphorus (lab extraction method dependent).",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 134.0', 'step': '0.1'})
    )
    potassium = forms.FloatField(
        min_value=0, max_value=250,
        label="Potassium (K) - Exchangeable K (kg/ha equivalent)",
        help_text="Exchangeable soil potassium reserve (K2O / exchangeable K basis).",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 199.0', 'step': '0.1'})
    )
    temperature = forms.FloatField(
        min_value=0, max_value=60,
        label="Mean Temperature (°C)",
        help_text="Average daytime ambient temperature during the growing season.",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 22.6', 'step': '0.1'})
    )
    humidity = forms.FloatField(
        min_value=0, max_value=100,
        label="Relative Humidity (%)",
        help_text="Mean relative humidity. Note: High humidity (>85%) significantly elevates fungal disease pressure.",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 92.3', 'step': '0.1'})
    )
    ph = forms.FloatField(
        min_value=1, max_value=14,
        label="Soil pH (1:2.5 soil-water suspension)",
        help_text="Measured soil reaction. Target for apples is typically 6.0 to 6.5.",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 5.9', 'step': '0.1'})
    )
    rainfall = forms.FloatField(
        min_value=0, max_value=500,
        label="Monthly Precipitation / Rainfall (mm / month)",
        help_text="Average monthly precipitation during the growing / vegetative cycle.",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 112.0', 'step': '0.1'})
    )
    soil_type = forms.ChoiceField(
        choices=SOIL_TYPE_CHOICES, label="Soil Texture & Type",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    season = forms.ChoiceField(
        choices=SEASON_CHOICES, label="Cropping Season / Cycle",
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
