from django.core.management.base import BaseCommand
from django.db import transaction

from product_app.models import Release, Product, ReleaseProductImage
from product_app.data import PATCH_DATA

class Command(BaseCommand):
    help = 'Populates the database with image data from data.py'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting image data population...'))
        
        # Keep track of what was done
        created_count = 0
        updated_count = 0

        # This line was correct, it uses the PATCH_DATA variable we just imported
        for release_name, products_data in PATCH_DATA.items():
            # Get or create the Release object
            release_obj, created = Release.objects.get_or_create(name=release_name)
            if created:
                self.stdout.write(f'  Created Release: {release_name}')

            for product_name, images_data in products_data.items():
                # Get or create the Product object
                product_obj, created = Product.objects.get_or_create(name=product_name)
                if created:
                    self.stdout.write(f'  Created Product: {product_name}')

                for image_key, sources_data in images_data.items():
                    # Extract data for each source, handling potentially missing keys
                    try:
                        registry_src = sources_data['registry']
                        ot2paas_src = sources_data['ot2paas']
                        local_src = sources_data['local']
                    except KeyError as e:
                        self.stdout.write(self.style.ERROR(f"Missing source data for {release_name}/{product_name}/{image_key}: {e}"))
                        continue

                    # Prepare the data for the fields that will be updated or created
                    defaults_data = {
                        'registry_registry': registry_src.get('registry', ''),
                        'registry_path': registry_src.get('path', ''),
                        'registry_image_name': registry_src.get('image_name', ''),

                        'ot2paas_registry': ot2paas_src.get('registry', ''),
                        'ot2paas_path': ot2paas_src.get('path', ''),
                        'ot2paas_image_name': ot2paas_src.get('image_name', ''),

                        'local_registry': local_src.get('registry', ''),
                        'local_path': local_src.get('path', ''),
                        'local_image_name': local_src.get('image_name', ''),
                    }

                    # Use update_or_create to avoid duplicates and allow re-running the script
                    image_obj, created = ReleaseProductImage.objects.update_or_create(
                        release=release_obj,
                        product=product_obj,
                        image_name=image_key,
                        defaults=defaults_data
                    )

                    if created:
                        created_count += 1
                        self.stdout.write(f'    - CREATED: {image_key}')
                    else:
                        updated_count += 1
                        self.stdout.write(f'    - UPDATED: {image_key}')

        self.stdout.write(self.style.SUCCESS(
            f'\nPopulation complete! Created: {created_count}, Updated: {updated_count}.'
        ))