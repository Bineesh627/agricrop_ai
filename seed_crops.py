"""
Crop Catalog Seeder - CLI Entry Point
======================================
Convenience script to run the database seeder from the repository root.

Usage:
    python seed_crops.py
    python seed_crops.py --dry-run
    python seed_crops.py --file path/to/custom.json
    python seed_crops.py --deactivate wheat
"""
import os
import sys

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agri_project.settings')
    import django
    django.setup()

    from django.core.management import call_command
    args = sys.argv[1:]
    call_command('seed_catalog', *args)
