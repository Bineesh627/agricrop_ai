# Generated manually — extends CropInformation with catalog schema v2 fields.
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crop_app', '0001_initial'),
    ]

    operations = [
        # Slug (unique URL-safe identifier)
        migrations.AddField(
            model_name='cropinformation',
            name='slug',
            field=models.SlugField(blank=True, max_length=60, unique=True, null=True,
                                   help_text='URL-safe unique identifier auto-derived from name'),
        ),
        # Scientific name
        migrations.AddField(
            model_name='cropinformation',
            name='scientific_name',
            field=models.CharField(blank=True, default='', max_length=120,
                                   help_text='Binomial scientific name'),
        ),
        # Numeric bounds for validation
        migrations.AddField(model_name='cropinformation', name='n_min',
                            field=models.FloatField(null=True, blank=True)),
        migrations.AddField(model_name='cropinformation', name='n_max',
                            field=models.FloatField(null=True, blank=True)),
        migrations.AddField(model_name='cropinformation', name='p_min',
                            field=models.FloatField(null=True, blank=True)),
        migrations.AddField(model_name='cropinformation', name='p_max',
                            field=models.FloatField(null=True, blank=True)),
        migrations.AddField(model_name='cropinformation', name='k_min',
                            field=models.FloatField(null=True, blank=True)),
        migrations.AddField(model_name='cropinformation', name='k_max',
                            field=models.FloatField(null=True, blank=True)),
        migrations.AddField(model_name='cropinformation', name='ph_min',
                            field=models.FloatField(null=True, blank=True)),
        migrations.AddField(model_name='cropinformation', name='ph_max',
                            field=models.FloatField(null=True, blank=True)),
        migrations.AddField(model_name='cropinformation', name='temp_min',
                            field=models.FloatField(null=True, blank=True)),
        migrations.AddField(model_name='cropinformation', name='temp_max',
                            field=models.FloatField(null=True, blank=True)),
        # Extended text fields
        migrations.AddField(
            model_name='cropinformation',
            name='soil_characteristics',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='cropinformation',
            name='climate_requirements',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='cropinformation',
            name='crop_notes',
            field=models.TextField(blank=True, default=''),
        ),
        # Status and timestamps
        migrations.AddField(
            model_name='cropinformation',
            name='active',
            field=models.BooleanField(default=True,
                                      help_text='Inactive crops are excluded from the public catalog.'),
        ),
        migrations.AddField(
            model_name='cropinformation',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='cropinformation',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        # Widen existing display string fields that may need more room
        migrations.AlterField(
            model_name='cropinformation',
            name='ideal_n_range',
            field=models.CharField(default='', max_length=80,
                                   verbose_name='Indicative Nitrogen (N) Range'),
        ),
        migrations.AlterField(
            model_name='cropinformation',
            name='ideal_p_range',
            field=models.CharField(default='', max_length=80,
                                   verbose_name='Indicative Phosphorus (P) Range'),
        ),
        migrations.AlterField(
            model_name='cropinformation',
            name='ideal_k_range',
            field=models.CharField(default='', max_length=80,
                                   verbose_name='Indicative Potassium (K) Range'),
        ),
        migrations.AlterField(
            model_name='cropinformation',
            name='ideal_temp_range',
            field=models.CharField(default='', max_length=80,
                                   verbose_name='Typical Suitable Temperature Range'),
        ),
        migrations.AlterField(
            model_name='cropinformation',
            name='ideal_ph_range',
            field=models.CharField(default='', max_length=80,
                                   verbose_name='Typical Suitable Soil pH Range'),
        ),
        migrations.AlterField(
            model_name='cropinformation',
            name='water_requirement',
            field=models.CharField(default='', max_length=150,
                                   verbose_name='Indicative Water Requirement'),
        ),
        migrations.AlterField(
            model_name='cropinformation',
            name='harvest_duration',
            field=models.CharField(default='', max_length=150,
                                   verbose_name='Typical Harvest Duration'),
        ),
    ]
