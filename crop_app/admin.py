from django.contrib import admin
from django.utils.html import format_html
from .models import CropInformation, CropPredictionRecord, UserProfile, FarmerFeedback


@admin.register(CropInformation)
class CropInformationAdmin(admin.ModelAdmin):
    """
    Admin interface for the Crop Catalog.
    Provides list view, search, filtering, import management,
    and inline deactivation without touching the public catalog.
    """
    list_display = [
        'display_name', 'scientific_name_display', 'category',
        'ideal_ph_range', 'ideal_temp_range', 'active_badge', 'updated_at'
    ]
    list_filter = ['category', 'active']
    search_fields = ['display_name', 'name', 'slug', 'scientific_name', 'description']
    readonly_fields = ['slug', 'created_at', 'updated_at']
    ordering = ['category', 'display_name']
    list_per_page = 25

    fieldsets = (
        ('Core Identity', {
            'fields': ('name', 'slug', 'display_name', 'scientific_name', 'category', 'icon_class', 'active')
        }),
        ('Description', {
            'fields': ('description',)
        }),
        ('Indicative Nutrient Ranges (Display)', {
            'description': (
                'These are reference/knowledge display strings \u2014 NOT personalised fertiliser prescriptions. '
                'Use indicative, typical, suitable terminology.'
            ),
            'fields': ('ideal_n_range', 'ideal_p_range', 'ideal_k_range')
        }),
        ('Numeric Bounds (Validation Only)', {
            'description': 'Used by the seeder validator to catch data entry errors. Not shown in the public catalog.',
            'classes': ('collapse',),
            'fields': (
                ('n_min', 'n_max'),
                ('p_min', 'p_max'),
                ('k_min', 'k_max'),
                ('ph_min', 'ph_max'),
                ('temp_min', 'temp_max'),
            )
        }),
        ('Climate & Soil Reference', {
            'fields': ('ideal_temp_range', 'ideal_ph_range', 'water_requirement', 'harvest_duration',
                       'soil_characteristics', 'climate_requirements')
        }),
        ('Fertility & Notes', {
            'description': 'Reference guidance only. Must not prescribe universal exact rates.',
            'fields': ('fertilizer_tips', 'crop_notes')
        }),
        ('Metadata', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at')
        }),
    )

    actions = ['deactivate_crops', 'activate_crops']

    @admin.display(description='Scientific Name')
    def scientific_name_display(self, obj):
        if obj.scientific_name:
            return format_html('<em>{}</em>', obj.scientific_name)
        return '—'

    @admin.display(description='Status', boolean=False)
    def active_badge(self, obj):
        if obj.active:
            return format_html(
                '<span style="color:#2d6a4f; font-weight:bold;">\u2714 Active</span>'
            )
        return format_html(
            '<span style="color:#999;">\u2014 Inactive</span>'
        )

    @admin.action(description='Deactivate selected crops (hide from public catalog)')
    def deactivate_crops(self, request, queryset):
        updated = queryset.update(active=False)
        self.message_user(request, f'{updated} crop(s) deactivated.')

    @admin.action(description='Activate selected crops (show in public catalog)')
    def activate_crops(self, request, queryset):
        updated = queryset.update(active=True)
        self.message_user(request, f'{updated} crop(s) activated.')


@admin.register(CropPredictionRecord)
class CropPredictionRecordAdmin(admin.ModelAdmin):
    list_display = [
        'predicted_crop', 'user', 'nitrogen', 'phosphorus', 'potassium',
        'ph', 'temperature', 'humidity', 'confidence_score', 'created_at'
    ]
    list_filter = ['predicted_crop', 'soil_type', 'season']
    search_fields = ['predicted_crop', 'user__username']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    list_per_page = 30


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_type', 'location', 'farm_size', 'created_at']
    list_filter = ['user_type']
    search_fields = ['user__username', 'user__email', 'location']


@admin.register(FarmerFeedback)
class FarmerFeedbackAdmin(admin.ModelAdmin):
    list_display = ['subject', 'user', 'status', 'created_at', 'updated_at']
    list_filter = ['status']
    search_fields = ['subject', 'user__username', 'message']
    readonly_fields = ['created_at', 'updated_at']
