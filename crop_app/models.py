from django.db import models
from django.utils.text import slugify
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
    """
    Crop Catalog Reference Model.
    Stores indicative agronomic reference data — NOT personalised fertiliser advice.
    All numeric range fields are for cataloguing and UI display only.
    Actual agronomic scoring uses the separate AgronomicEngine profiles.
    """
    # ── Core identity ──────────────────────────────────────────────────────────
    name = models.CharField(
        max_length=50, unique=True,
        help_text="ML key (e.g. 'rice', 'maize') — must match agronomic engine crop keys"
    )
    slug = models.SlugField(
        max_length=60, unique=True, blank=True,
        help_text="URL-safe unique identifier auto-derived from name"
    )
    display_name = models.CharField(max_length=100, help_text="Human-readable name (e.g. 'Rice (Paddy)')")
    scientific_name = models.CharField(
        max_length=120, blank=True, default='',
        help_text="Binomial scientific name (e.g. Oryza sativa)"
    )
    category = models.CharField(
        max_length=50, choices=CROP_CATEGORY_CHOICES, default='Cereal'
    )
    description = models.TextField(
        help_text="Cautious overview. Use indicative, typical, suitable terminology."
    )

    # ── Indicative nutrient ranges (display strings) ───────────────────────────
    ideal_n_range = models.CharField(
        max_length=80, default='',
        verbose_name='Indicative Nitrogen (N) Range',
        help_text="e.g. '60–120 kg/ha (indicative)'. NOT a universal prescription."
    )
    ideal_p_range = models.CharField(
        max_length=80, default='',
        verbose_name='Indicative Phosphorus (P) Range',
    )
    ideal_k_range = models.CharField(
        max_length=80, default='',
        verbose_name='Indicative Potassium (K) Range',
    )

    # ── Numeric bounds for validation (used by seeder validator) ──────────────
    n_min = models.FloatField(null=True, blank=True, help_text="N lower bound (kg/ha)")
    n_max = models.FloatField(null=True, blank=True, help_text="N upper bound (kg/ha)")
    p_min = models.FloatField(null=True, blank=True)
    p_max = models.FloatField(null=True, blank=True)
    k_min = models.FloatField(null=True, blank=True)
    k_max = models.FloatField(null=True, blank=True)
    ph_min = models.FloatField(null=True, blank=True, help_text="Suitable pH lower bound")
    ph_max = models.FloatField(null=True, blank=True, help_text="Suitable pH upper bound")
    temp_min = models.FloatField(null=True, blank=True, help_text="Typical suitable temperature lower bound (°C)")
    temp_max = models.FloatField(null=True, blank=True, help_text="Typical suitable temperature upper bound (°C)")

    # ── Display strings ────────────────────────────────────────────────────────
    ideal_temp_range = models.CharField(
        max_length=80, default='',
        verbose_name='Typical Suitable Temperature Range',
    )
    ideal_ph_range = models.CharField(
        max_length=80, default='',
        verbose_name='Typical Suitable Soil pH Range',
    )
    water_requirement = models.CharField(
        max_length=150, default='',
        verbose_name='Indicative Water Requirement',
    )
    harvest_duration = models.CharField(
        max_length=150, default='',
        verbose_name='Typical Harvest Duration',
    )

    # ── Extended reference fields ──────────────────────────────────────────────
    soil_characteristics = models.TextField(
        blank=True, default='',
        help_text="Indicative suitable soil types and characteristics."
    )
    climate_requirements = models.TextField(
        blank=True, default='',
        help_text="Typical climatic conditions. Use cautious/indicative wording."
    )
    fertilizer_tips = models.TextField(
        default='Apply NPK according to certified soil test and local extension recommendations.',
        verbose_name='Soil & Fertilizer Reference Guidance',
        help_text="Reference guidance only. Must not prescribe universal exact rates."
    )
    crop_notes = models.TextField(
        blank=True, default='',
        help_text="Crop-specific additional notes, warnings, or agronomic context."
    )

    # ── Metadata ───────────────────────────────────────────────────────────────
    icon_class = models.CharField(max_length=50, default='fa-seedling')
    active = models.BooleanField(
        default=True,
        help_text="Inactive crops are excluded from the public catalog."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'display_name']
        verbose_name = 'Crop Information'
        verbose_name_plural = 'Crop Information Catalog'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

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
    top_alternatives = models.TextField(blank=True, default='[]')
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
