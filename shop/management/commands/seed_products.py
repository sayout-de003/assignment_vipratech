from django.core.management.base import BaseCommand
from shop.models import Product

class Command(BaseCommand):
    help = "Seeds initial product data"

    def handle(self, *args, **kwargs):
        products = [
            ("Product A", 10000, "Product A desc"),
            ("Product B", 20000, "Product B desc"),
            ("Product C", 30000, "Product C desc"),
        ]

        for name, price, desc in products:
            obj, created = Product.objects.update_or_create(
                name=name,
                defaults={'price': price, 'description': desc}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created {name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Updated {name}"))

        self.stdout.write(self.style.SUCCESS("Product seeding complete!"))
