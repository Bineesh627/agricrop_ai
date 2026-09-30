from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import CropPredictionRecord, CropInformation
from .agronomic_engine import CROP_PROFILES, generate_crop_diagnostics, get_crop_profile
import seed_db

class AgronomicEngineTests(TestCase):
    def setUp(self):
        seed_db.seed_crops()
        self.user = User.objects.create_user(username='testfarmer', password='password123')
        self.client = Client()
        self.client.login(username='testfarmer', password='password123')

    def test_all_22_crop_profiles_complete(self):
        """Verify all 22 crops have complete agronomic metadata with no missing keys."""
        expected_crops = [
            'rice', 'maize', 'chickpea', 'kidneybeans', 'pigeonpeas',
            'mothbeans', 'mungbean', 'blackgram', 'lentil', 'pomegranate',
            'banana', 'mango', 'grapes', 'watermelon', 'muskmelon',
            'apple', 'orange', 'papaya', 'coconut', 'cotton', 'jute', 'coffee'
        ]
        for crop_key in expected_crops:
            self.assertIn(crop_key, CROP_PROFILES, f"Missing crop profile for {crop_key}")
            profile = CROP_PROFILES[crop_key]
            self.assertTrue(profile['display_name'])
            self.assertTrue(profile['scientific_name'])
            self.assertTrue(profile['growth_habit'])
            self.assertTrue(profile['category'])
            self.assertTrue(len(profile['why_selected']) >= 3)
            self.assertTrue(profile['disease_name'])
            self.assertTrue(profile['disease_pathogens'])
            self.assertTrue(profile['disease_advisory'])
            self.assertTrue(profile['climate_advisory']['primary_factor'])
            self.assertTrue(profile['climate_advisory']['details'])
            self.assertTrue(len(profile['fertility_protocol']) >= 3)
            self.assertTrue(len(profile['missing_parameters']) >= 3)
            self.assertTrue(profile['extension_summary'])

    def test_rice_recommendation_no_apple_contamination(self):
        """Verify Rice result contains rice agronomy and zero apple-specific references."""
        rice_record = CropPredictionRecord.objects.create(
            user=self.user,
            nitrogen=90.0,
            phosphorus=42.0,
            potassium=43.0,
            temperature=23.6,
            humidity=82.2,
            ph=6.5,
            rainfall=230.0,
            soil_type='Clayey',
            season='Kharif',
            predicted_crop='rice',
            confidence_score=80.9
        )

        response = self.client.get(f'/result/{rice_record.pk}/')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        # Positive Rice assertions
        self.assertIn('Rice (Paddy)', content)
        self.assertIn('Oryza sativa', content)
        self.assertIn('Annual Semi-Aquatic Cereal Grass', content)
        self.assertIn('Rice Blast', content)
        self.assertIn('Khaira disease', content)
        self.assertIn('puddling', content)

        # Cross-crop contamination assertions: NO Apple artifacts allowed
        forbidden_apple_terms = [
            'Apple Scab',
            'Venturia inaequalis',
            'Fire Blight',
            'Erwinia amylovora',
            'Honeycrisp',
            'Cortland',
            'M.9',
            'M.26',
            'Perennial Deciduous Tree',
            'spur wood',
            'pome fruit',
            'bitter pit',
            'winter chilling hours'
        ]
        for term in forbidden_apple_terms:
            self.assertNotIn(term, content, f"Cross-crop contamination! Forbidden term '{term}' found in Rice result.")

    def test_apple_recommendation_no_rice_contamination(self):
        """Verify Apple result contains apple agronomy and zero rice-specific references."""
        apple_record = CropPredictionRecord.objects.create(
            user=self.user,
            nitrogen=20.0,
            phosphorus=134.0,
            potassium=199.0,
            temperature=22.6,
            humidity=92.3,
            ph=5.9,
            rainfall=112.0,
            soil_type='Loamy',
            season='Rabi',
            predicted_crop='apple',
            confidence_score=82.0
        )

        response = self.client.get(f'/result/{apple_record.pk}/')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        # Positive Apple assertions
        self.assertIn('Apple', content)
        self.assertIn('Malus domestica', content)
        self.assertIn('Perennial Deciduous Fruit Tree', content)
        self.assertIn('Apple Scab', content)
        self.assertIn('Winter Chilling Hours', content)

        # Cross-crop contamination assertions: NO Rice artifacts allowed
        forbidden_rice_terms = [
            'Oryza sativa',
            'Annual Semi-Aquatic Cereal Grass',
            'puddling',
            'standing water',
            'Khaira disease',
            'Rice Blast',
            'Magnaporthe oryzae',
            'submerged paddy'
        ]
        for term in forbidden_rice_terms:
            self.assertNotIn(term, content, f"Cross-crop contamination! Forbidden term '{term}' found in Apple result.")

    def test_scoring_numerical_consistency(self):
        """Verify header suitability score exactly equals the breakdown calibrated score."""
        record = CropPredictionRecord.objects.create(
            user=self.user,
            nitrogen=90.0,
            phosphorus=42.0,
            potassium=43.0,
            temperature=23.6,
            humidity=82.2,
            ph=6.5,
            rainfall=230.0,
            soil_type='Clayey',
            season='Kharif',
            predicted_crop='rice',
            confidence_score=80.9
        )

        response = self.client.get(f'/result/{record.pk}/')
        self.assertEqual(response.status_code, 200)
        
        suitability_score = response.context['suitability_score']
        agronomic_report = response.context['agronomic_report']
        breakdown_score = agronomic_report['scoring_methodology']['calibrated_score']
        
        self.assertEqual(
            suitability_score,
            breakdown_score,
            f"Header score ({suitability_score}) does not match breakdown score ({breakdown_score})"
        )
        self.assertLessEqual(suitability_score, 85.0)
        self.assertGreaterEqual(suitability_score, 50.0)

    def test_cotton_recommendation_and_agronomics(self):
        """Verify Cotton results are conditional, defensible, and free of cereal/apple carryover."""
        cotton_record = CropPredictionRecord.objects.create(
            user=self.user,
            nitrogen=117.0,
            phosphorus=46.0,
            potassium=19.0,
            temperature=24.0,
            humidity=79.8,
            ph=6.9,
            rainfall=80.0,
            soil_type='Black',
            season='Kharif',
            predicted_crop='cotton',
            confidence_score=83.9
        )

        response = self.client.get(f'/result/{cotton_record.pk}/')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        # 1. Verification of Cotton botanical identity
        self.assertIn('Cotton', content)
        self.assertIn('Gossypium hirsutum', content)
        self.assertIn('Preliminary Agronomic Suitability: 83.9 / 100', content)

        # 2. Non-probability disclaimer in UI
        self.assertIn('This score represents environmental and agronomic compatibility', content)
        self.assertIn('probability of yield', content)

        # 3. Two-layer ML and Agronomic breakdown
        self.assertIn('ML Engine: Random Forest', content)
        self.assertIn('Suitability Engine: Weighted Agronomic Model', content)
        self.assertIn('Soil Texture Compatibility (Black)', content)
        self.assertIn('Cropping Season Alignment (Kharif)', content)

        # 4. Strict absence of cereal terminology in Cotton report
        forbidden_cereal_terms = ['tillering', 'panicle', 'tasseling']
        for term in forbidden_cereal_terms:
            self.assertNotIn(term, content, f"Cereal carryover detected in cotton report: '{term}'")

        # 5. Conditional phrasing verification
        self.assertIn('Example spacing range for suitable hybrid cotton systems', content)
        self.assertIn('Actual spacing depends on cultivar', content)
        self.assertIn('If magnesium deficiency or physiological leaf reddening is confirmed', content)
        self.assertIn('Phosphorus and Potassium application rates and timing should be determined from a calibrated laboratory soil test', content)
        self.assertIn('Prolonged cloudy conditions and sudden moisture stress', content)
        self.assertNotIn('4–5 consecutive days', content)
        self.assertNotIn('4-5 consecutive days', content)


class CropCatalogSeederTests(TestCase):
    """Unit tests for the automatic crop catalog database seeding system and views."""

    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='adminuser', email='admin@test.com', password='adminpass123'
        )

    def test_seeder_idempotency(self):
        """Verify seeding creates crops on first run and updates without duplicates on second run."""
        from django.core.management import call_command
        import io

        # Clear CropInformation
        CropInformation.objects.all().delete()
        self.assertEqual(CropInformation.objects.count(), 0)

        # Run 1: Should create 22 crops
        out1 = io.StringIO()
        call_command('seed_catalog', stdout=out1)
        self.assertEqual(CropInformation.objects.count(), 22)
        self.assertIn('Total records : 22', out1.getvalue())
        self.assertIn('Created       : 22', out1.getvalue())

        # Run 2: Should update 22 crops, creating 0 duplicates
        out2 = io.StringIO()
        call_command('seed_catalog', stdout=out2)
        self.assertEqual(CropInformation.objects.count(), 22)
        self.assertIn('Total records : 22', out2.getvalue())
        self.assertIn('Created       : 0', out2.getvalue())
        self.assertIn('Updated       : 22', out2.getvalue())
        self.assertIn('Errors        : 0', out2.getvalue())

    def test_seeder_dry_run_does_not_modify_db(self):
        """Verify --dry-run validates without committing to the database."""
        from django.core.management import call_command
        import io

        CropInformation.objects.all().delete()
        out = io.StringIO()
        call_command('seed_catalog', dry_run=True, stdout=out)
        self.assertEqual(CropInformation.objects.count(), 0)
        self.assertIn('Dry run   : YES', out.getvalue())

    def test_seeder_validation_catches_invalid_data(self):
        """Verify the validator rejects invalid pH, inverted ranges, and missing fields."""
        from crop_app.management.commands.seed_catalog import validate_crop

        seen_slugs = set()
        # Invalid crop: pH min > pH max, N min > N max, missing description
        invalid_record = {
            'name': 'badcrop',
            'display_name': 'Bad Crop',
            'category': 'Cereal',
            # missing 'description'
            'ideal_n_range': '10-20',
            'ideal_p_range': '10-20',
            'ideal_k_range': '10-20',
            'ideal_temp_range': '20-25',
            'ideal_ph_range': '6-7',
            'water_requirement': 'Moderate',
            'harvest_duration': '90 days',
            'fertilizer_tips': 'Apply NPK',
            'n_min': 100,
            'n_max': 50,  # min > max
            'ph_min': 15.0,  # > 14
            'ph_max': 5.0,  # min > max
        }
        errors = validate_crop(invalid_record, seen_slugs)
        self.assertTrue(len(errors) >= 3)
        error_text = ' '.join(errors)
        self.assertIn('description', error_text)
        self.assertIn('n_min (100) > n_max (50)', error_text)
        self.assertIn('outside valid pH range', error_text)

    def test_rice_catalog_cautious_agronomic_wording(self):
        """Verify Rice catalog adheres to all 8 cautious wording rules."""
        from django.core.management import call_command
        call_command('seed_catalog', verbosity=0)

        rice = CropInformation.objects.get(name='rice')
        # 1. Indicative N, P, K ranges
        self.assertIn('indicative', rice.ideal_n_range)
        self.assertIn('indicative', rice.ideal_p_range)
        self.assertIn('indicative', rice.ideal_k_range)
        # 2. Typical suitable pH
        self.assertEqual(rice.ideal_ph_range, '6.0 – 7.0')
        # 3. Water requirement with production-system dependency
        self.assertIn('~1,500 – 2,500 mm/season', rice.water_requirement)
        self.assertIn('production-system dependent', rice.water_requirement)
        # 4. Suitable temp
        self.assertEqual(rice.ideal_temp_range, '22°C – 27°C')
        # 5. Harvest duration
        self.assertIn('110 – 140 days', rice.harvest_duration)
        self.assertIn('cultivar dependent', rice.harvest_duration)
        # 6 & 7. Conditional fertilizer, no fixed zinc dose
        self.assertIn('Apply N, P and K according to soil-test results', rice.fertilizer_tips)
        self.assertNotIn('25 kg/ha', rice.fertilizer_tips)
        self.assertNotIn('25 kg/ha Zinc Sulfate', rice.fertilizer_tips)
        # 8. No claim that all rice requires standing water
        self.assertIn('Suitable soil and water-management requirements vary with cultivar and production system', rice.description)
        self.assertNotIn('requiring abundant standing water', rice.description)

    def test_crop_catalog_view_active_filtering(self):
        """Verify inactive crops are hidden from public catalog but visible to admin."""
        from django.core.management import call_command
        call_command('seed_catalog', verbosity=0)

        # Deactivate coffee
        coffee = CropInformation.objects.get(name='coffee')
        coffee.active = False
        coffee.save()

        # Public catalog: coffee should not appear
        response = self.client.get('/catalog/')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('Rice (Paddy)', content)
        self.assertNotIn('Coffee', content)

        # Reactivate coffee
        coffee.active = True
        coffee.save()
        response = self.client.get('/catalog/')
        self.assertIn('Coffee', response.content.decode('utf-8'))

    def test_crop_detail_view_renders_database_fields(self):
        """Verify crop detail page renders scientific name and extended database fields."""
        from django.core.management import call_command
        call_command('seed_catalog', verbosity=0)

        response = self.client.get('/crop/rice/')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        # Check scientific name
        self.assertIn('Oryza sativa', content)
        # Check indicative labels
        self.assertIn('Indicative Nitrogen (N) Range', content)
        self.assertIn('Typical Suitable Soil pH', content)
        self.assertIn('Indicative Water Requirement:', content)
        self.assertIn('Production-system and irrigation dependent', content)
        self.assertIn('Typical Harvest Duration:', content)
        self.assertIn('Cultivar and growing conditions dependent', content)
        # Check extended fields
        self.assertIn('Suitable Soil Characteristics:', content)
        self.assertIn('Agronomic Reference Notes:', content)

