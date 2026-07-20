from django.db import models
from django.contrib.auth.models import User

USER_TYPE_CHOICES = (
    ('FARMER', 'Farmer / User'),
    ('ADMIN', 'Administrator'),
)

CROP_CATEGORY_CHOICES = (
    ('Cereal', 'Cereal'),
    ('Pulse', 'Pulse'),
    ('Fruit', 'Fruit'),
    ('Commercial', 'Commercial / Cash Crop'),
)

FEEDBACK_STATUS_CHOICES = (
    ('PENDING', 'Pending Review'),
    ('RESOLVED', 'Resolved / Responded'),
)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='FARMER')
    phone = models.CharField(max_length=20, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True, default='Agricultural Zone')
    farm_size = models.FloatField(default=2.5, help_text="Farm size in acres")
    created_at = models.DateTimeField(auto_now_add=True)

    def is_admin_user(self):
        return self.user_type == 'ADMIN' or self.user.is_superuser

    def __str__(self):
        return f"{self.user.username} ({self.user_type})"


class CropInformation(models.Model):
    name = models.CharField(max_length=50, unique=True) # e.g. rice
    display_name = models.CharField(max_length=100) # e.g. Rice (Paddy)
    category = models.CharField(max_length=50, choices=CROP_CATEGORY_CHOICES, default='Cereal')
    description = models.TextField()
    ideal_n_range = models.CharField(max_length=50, default="80 - 100 kg/ha")
    ideal_p_range = models.CharField(max_length=50, default="35 - 50 kg/ha")
    ideal_k_range = models.CharField(max_length=50, default="35 - 50 kg/ha")
    ideal_temp_range = models.CharField(max_length=50, default="20°C - 27°C")
    ideal_ph_range = models.CharField(max_length=50, default="6.0 - 7.0")
    water_requirement = models.CharField(max_length=100, default="High (1500 - 2500 mm)")
    harvest_duration = models.CharField(max_length=100, default="120 - 150 days")
    fertilizer_tips = models.TextField(default="Apply Nitrogen in 3 split doses: Basal, Tillering, and Panicle initiation.")
    icon_class = models.CharField(max_length=50, default="fa-seedling")

    def __str__(self):
        return self.display_name


class CropPredictionRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='predictions')
    nitrogen = models.FloatField()
    phosphorus = models.FloatField()
    potassium = models.FloatField()
    temperature = models.FloatField()
    humidity = models.FloatField()
    ph = models.FloatField()
    rainfall = models.FloatField()
    soil_type = models.CharField(max_length=50, default='Alluvial')
    season = models.CharField(max_length=50, default='Kharif')
    predicted_crop = models.CharField(max_length=50)
    confidence_score = models.FloatField(default=95.0)
    top_alternatives = models.TextField(blank=True, default="[]")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.predicted_crop} for {self.user.username if self.user else 'Guest'} on {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class FarmerFeedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks')
    subject = models.CharField(max_length=150)
    message = models.TextField()
    admin_reply = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=FEEDBACK_STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.status}] {self.subject} by {self.user.username}"
