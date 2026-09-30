"""
Django Management Command: seed_catalog
========================================
Reads structured crop data from crop_catalog_data.json, validates every record,
then performs an idempotent upsert (create or update) into CropInformation.

Usage:
    python manage.py seed_catalog
    python manage.py seed_catalog --file path/to/custom.json
    python manage.py seed_catalog --dry-run
    python manage.py seed_catalog --deactivate wheat  # mark a crop inactive

Output:
    Crop Catalog Import
    -------------------
    Total records : 22
    Created       : 3
    Updated       : 19
    Skipped       : 0
    Errors        : 0
"""

import json
import os
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify
from django.db import transaction

from crop_app.models import CropInformation

# ──────────────────────────────────────────────────────────────────────────────
# Validation helpers
# ──────────────────────────────────────────────────────────────────────────────

REQUIRED_FIELDS = [
    'name', 'display_name', 'category', 'description',
    'ideal_n_range', 'ideal_p_range', 'ideal_k_range',
    'ideal_temp_range', 'ideal_ph_range',
    'water_requirement', 'harvest_duration', 'fertilizer_tips',
]

VALID_CATEGORIES = {'Cereal', 'Pulse', 'Fruit', 'Commercial'}

VALID_PH_RANGE = (0.0, 14.0)


def _check_range(errors, crop_name, field_min, field_max, label, value_min, value_max):
    """Validate that min <= max and both values are within the allowed range."""
    if value_min is not None and value_max is not None:
        if value_min > value_max:
            errors.append(
                f"[{crop_name}] {label}: min ({value_min}) > max ({value_max})"
            )
    if value_min is not None and value_max is not None:
        lo, hi = _check_range.valid_range if hasattr(_check_range, 'valid_range') else (-1e9, 1e9)
        # no universal bound check for N/P/K; only pH has hard bounds


def validate_crop(record: dict, seen_slugs: set) -> list:
    """
    Validate a single crop record dictionary.
    Returns a list of human-readable error strings (empty = valid).
    """
    errors = []
    name = record.get('name', '<unnamed>')

    # 1. Required fields
    for field in REQUIRED_FIELDS:
        if not record.get(field):
            errors.append(f"[{name}] Required field '{field}' is missing or empty.")

    # 2. Category must be valid
    cat = record.get('category', '')
    if cat and cat not in VALID_CATEGORIES:
        errors.append(
            f"[{name}] Invalid category '{cat}'. Must be one of: {sorted(VALID_CATEGORIES)}"
        )

    # 3. Numeric range consistency
    for prefix, label in [('n', 'Nitrogen'), ('p', 'Phosphorus'), ('k', 'Potassium'),
                           ('ph', 'Soil pH'), ('temp', 'Temperature')]:
        lo = record.get(f'{prefix}_min')
        hi = record.get(f'{prefix}_max')
        if lo is not None and hi is not None:
            if not isinstance(lo, (int, float)) or not isinstance(hi, (int, float)):
                errors.append(f"[{name}] {label} min/max must be numeric.")
            elif lo > hi:
                errors.append(
                    f"[{name}] {label}: {prefix}_min ({lo}) > {prefix}_max ({hi})."
                )

    # 4. pH must be within 0–14
    ph_min = record.get('ph_min')
    ph_max = record.get('ph_max')
    for val, lbl in [(ph_min, 'ph_min'), (ph_max, 'ph_max')]:
        if val is not None:
            if not isinstance(val, (int, float)):
                errors.append(f"[{name}] {lbl} must be numeric.")
            elif not (VALID_PH_RANGE[0] <= val <= VALID_PH_RANGE[1]):
                errors.append(
                    f"[{name}] {lbl} ({val}) is outside valid pH range "
                    f"{VALID_PH_RANGE[0]}–{VALID_PH_RANGE[1]}."
                )

    # 5. Duplicate slug check
    slug = record.get('slug') or slugify(record.get('name', ''))
    if not slug:
        errors.append(f"[{name}] Cannot derive a valid slug from name '{name}'.")
    elif slug in seen_slugs:
        errors.append(f"[{name}] Duplicate slug '{slug}'. Each crop must have a unique slug.")
    else:
        seen_slugs.add(slug)

    return errors


# ──────────────────────────────────────────────────────────────────────────────
# Management command
# ──────────────────────────────────────────────────────────────────────────────

class Command(BaseCommand):
    help = (
        'Seed or update the Crop Catalog database from a structured JSON file. '
        'The operation is idempotent \u2014 running it multiple times is safe.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default=None,
            help='Path to the JSON data file. Defaults to crop_catalog_data.json in the project root.',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Validate and report what would happen without modifying the database.',
        )
        parser.add_argument(
            '--deactivate',
            type=str,
            metavar='SLUG',
            help='Deactivate a crop by its slug (name). No other action is taken.',
        )

    def handle(self, *args, **options):
        # ── Deactivate mode ────────────────────────────────────────────────────
        if options['deactivate']:
            slug = slugify(options['deactivate'])
            try:
                crop = CropInformation.objects.get(slug=slug)
                crop.active = False
                crop.save(update_fields=['active', 'updated_at'])
                self.stdout.write(
                    self.style.WARNING(f"Crop '{crop.display_name}' (slug: {slug}) deactivated.")
                )
            except CropInformation.DoesNotExist:
                raise CommandError(f"No crop found with slug '{slug}'.")
            return

        # ── Resolve data file ──────────────────────────────────────────────────
        if options['file']:
            data_path = options['file']
        else:
            project_root = os.path.dirname(  # manage.py directory
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            )
            data_path = os.path.join(project_root, 'crop_catalog_data.json')

        if not os.path.exists(data_path):
            raise CommandError(
                f"Data file not found: {data_path}\n"
                "Specify a path with --file or place crop_catalog_data.json in the project root."
            )

        # ── Load JSON ──────────────────────────────────────────────────────────
        try:
            with open(data_path, 'r', encoding='utf-8') as fh:
                crops_data = json.load(fh)
        except json.JSONDecodeError as exc:
            raise CommandError(f"Invalid JSON in {data_path}: {exc}")

        if not isinstance(crops_data, list):
            raise CommandError("JSON root must be an array of crop objects.")

        self.stdout.write(self.style.HTTP_INFO(
            f"\n{'='*60}\n Crop Catalog Import\n{'='*60}"
        ))
        self.stdout.write(f" Data file : {data_path}")
        self.stdout.write(f" Dry run   : {'YES -- no database changes will be made' if options['dry_run'] else 'No'}\n")

        # -- Phase 1: Validate ALL records before touching the DB ---------------
        all_errors = []
        seen_slugs: set = set()

        for idx, record in enumerate(crops_data, start=1):
            errors = validate_crop(record, seen_slugs)
            if errors:
                all_errors.extend([f"  Record #{idx}: {e}" for e in errors])

        if all_errors:
            self.stderr.write(self.style.ERROR("\n[FAIL] Validation FAILED. No database changes made.\n"))
            for err in all_errors:
                self.stderr.write(self.style.ERROR(err))
            self.stderr.write(self.style.ERROR(
                f"\n  Fix {len(all_errors)} validation error(s) above, then re-run the command.\n"
            ))
            raise CommandError("Validation failed -- database was NOT modified.")

        self.stdout.write(self.style.SUCCESS(
            f" [OK] All {len(crops_data)} records passed validation.\n"
        ))

        if options['dry_run']:
            self.stdout.write(self.style.WARNING(
                " Dry-run mode: stopping here. No database writes performed.\n"
            ))
            # Show what would happen
            created_preview, updated_preview = [], []
            for record in crops_data:
                slug = record.get('slug') or slugify(record['name'])
                crop_name = record['name'].lower()
                if (CropInformation.objects.filter(name=crop_name).exists() or
                        CropInformation.objects.filter(slug=slug).exists()):
                    updated_preview.append(record['display_name'])
                else:
                    created_preview.append(record['display_name'])
            self.stdout.write(f" Would create: {len(created_preview)}")
            for c in created_preview:
                self.stdout.write(f"   + {c}")
            self.stdout.write(f" Would update: {len(updated_preview)}")
            for u in updated_preview:
                self.stdout.write(f"   ~ {u}")
            return

        # ── Phase 2: Upsert inside a single atomic transaction ─────────────────
        created_count = 0
        updated_count = 0
        skipped_count = 0
        error_count = 0
        error_details = []

        # Field mapping: JSON key → model field name
        MODEL_FIELDS = [
            'name', 'slug', 'display_name', 'scientific_name', 'category', 'description',
            'ideal_n_range', 'ideal_p_range', 'ideal_k_range',
            'n_min', 'n_max', 'p_min', 'p_max', 'k_min', 'k_max',
            'ph_min', 'ph_max', 'temp_min', 'temp_max',
            'ideal_temp_range', 'ideal_ph_range',
            'water_requirement', 'harvest_duration',
            'soil_characteristics', 'climate_requirements',
            'fertilizer_tips', 'crop_notes', 'icon_class', 'active',
        ]

        try:
            with transaction.atomic():
                for record in crops_data:
                    crop_name = record['name'].lower()
                    slug = record.get('slug') or slugify(crop_name)
                    record.setdefault('slug', slug)
                    record.setdefault('active', True)

                    # Build defaults dict from only known model fields
                    defaults = {
                        k: record[k]
                        for k in MODEL_FIELDS
                        if k in record
                    }
                    defaults['name'] = crop_name
                    defaults['slug'] = slug

                    try:
                        # Idempotent match on canonical crop name or slug
                        obj = (
                            CropInformation.objects.filter(name=crop_name).first() or
                            CropInformation.objects.filter(slug=slug).first()
                        )
                        if obj:
                            for key, val in defaults.items():
                                setattr(obj, key, val)
                            obj.save()
                            created = False
                        else:
                            obj = CropInformation.objects.create(**defaults)
                            created = True

                        if created:
                            created_count += 1
                            self.stdout.write(
                                self.style.SUCCESS(f"  [+] Created : {obj.display_name} ({obj.category})")
                            )
                        else:
                            updated_count += 1
                            self.stdout.write(
                                f"  [~] Updated : {obj.display_name} ({obj.category})"
                            )
                    except Exception as exc:
                        error_count += 1
                        msg = f"  [!] Error on '{record.get('name', '?')}': {exc}"
                        error_details.append(msg)
                        self.stderr.write(self.style.ERROR(msg))

                if error_count > 0:
                    raise CommandError(
                        f"{error_count} record(s) failed to save. Transaction rolled back."
                    )

        except CommandError:
            raise
        except Exception as exc:
            raise CommandError(f"Unexpected error during database write: {exc}")

        # -- Summary ------------------------------------------------------------
        total = len(crops_data)
        self.stdout.write(self.style.HTTP_INFO(
            f"\n{'-'*40}\n Crop Catalog Import Summary\n{'-'*40}"
        ))
        self.stdout.write(f" Total records : {total}")
        self.stdout.write(self.style.SUCCESS(f" Created       : {created_count}"))
        if updated_count:
            self.stdout.write(f" Updated       : {updated_count}")
        if skipped_count:
            self.stdout.write(self.style.WARNING(f" Skipped       : {skipped_count}"))
        if error_count:
            self.stdout.write(self.style.ERROR(f" Errors        : {error_count}"))
        else:
            self.stdout.write(self.style.SUCCESS(" Errors        : 0"))
        self.stdout.write(f"{'-'*40}\n")

        if error_count == 0:
            self.stdout.write(self.style.SUCCESS(
                f" [OK] Crop catalog successfully seeded with {total} crops.\n"
            ))
