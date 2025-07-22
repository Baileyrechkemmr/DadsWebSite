"""
Django management command to export all data from models to fixtures.
This helps migrate data from SQLite to PostgreSQL on Railway.

Usage:
    python manage.py export_data

This will create JSON fixtures for all your models that can be loaded into PostgreSQL.
"""

from django.core.management.base import BaseCommand
from django.core import serializers
from django.apps import apps
import os


class Command(BaseCommand):
    help = 'Export all model data to JSON fixtures for PostgreSQL migration'

    def handle(self, *args, **options):
        # Get all models from the projects app
        projects_app = apps.get_app_config('projects')
        models = projects_app.get_models()
        
        # Create fixtures directory if it doesn't exist
        fixtures_dir = 'fixtures'
        if not os.path.exists(fixtures_dir):
            os.makedirs(fixtures_dir)
            self.stdout.write(self.style.SUCCESS(f'Created {fixtures_dir} directory'))
        
        exported_data = []
        total_records = 0
        
        for model in models:
            model_name = model._meta.model_name
            queryset = model.objects.all()
            count = queryset.count()
            
            if count > 0:
                self.stdout.write(f'Exporting {count} records from {model_name}...')
                
                # Serialize the data
                serialized_data = serializers.serialize('json', queryset, indent=2)
                
                # Write individual model fixture
                fixture_file = os.path.join(fixtures_dir, f'{model_name}_data.json')
                with open(fixture_file, 'w', encoding='utf-8') as f:
                    f.write(serialized_data)
                
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Exported {count} {model_name} records to {fixture_file}')
                )
                
                # Add to combined export
                exported_data.extend(serializers.deserialize('json', serialized_data))
                total_records += count
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  No data found for {model_name}')
                )
        
        # Create combined fixture file
        if exported_data:
            combined_fixture = os.path.join(fixtures_dir, 'all_data.json')
            with open(combined_fixture, 'w', encoding='utf-8') as f:
                # Re-serialize all data together
                all_objects = [item.object for item in exported_data]
                serialized_all = serializers.serialize('json', all_objects, indent=2)
                f.write(serialized_all)
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Created combined fixture: {combined_fixture}')
            )
        
        # Summary
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Export completed!\n'
                f'📊 Total records exported: {total_records}\n'
                f'📁 Files created in {fixtures_dir}/ directory\n\n'
                f'Next steps:\n'
                f'1. Commit and push these fixture files to git\n'
                f'2. On Railway, they will be available for loading into PostgreSQL\n'
                f'3. Use: python manage.py loaddata fixtures/all_data.json'
            )
        )