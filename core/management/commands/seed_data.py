from django.core.management.base import BaseCommand
from core.models import Profile, Hardware, Order, DesignItem
from core.services.cutting_engine import generate_cut_pieces

class Command(BaseCommand):
    help = 'Seeds the database with initial Profiles, Hardware, and sample Orders'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding data...')

        # 1. Profiles
        Profile.objects.get_or_create(name='Standard Frame 60', type='frame', defaults={'bar_length': 6000, 'cost_per_bar': 120.0})
        Profile.objects.get_or_create(name='Standard Sash 60', type='sash', defaults={'bar_length': 6000, 'cost_per_bar': 100.0})
        Profile.objects.get_or_create(name='Standard Bead', type='bead', defaults={'bar_length': 6000, 'cost_per_bar': 30.0})

        # 2. Hardware
        Hardware.objects.get_or_create(name='Sliding Roller', typology='sliding', defaults={'quantity_formula': '2 * panels'})
        Hardware.objects.get_or_create(name='Casement Handle', typology='casement', defaults={'quantity_formula': '1'})
        Hardware.objects.get_or_create(name='Friction Stay (Pair)', typology='casement', defaults={'quantity_formula': '1'})
        Hardware.objects.get_or_create(name='Crescent Lock', typology='sliding', defaults={'quantity_formula': '1'})

        # 3. Sample Orders
        if not Order.objects.exists():
            order1 = Order.objects.create(code='ORD-001', customer_name='John Doe')
            
            d1 = DesignItem.objects.create(
                order=order1, product_type='window', width=1200, height=1200, typology='sliding', 
                glass_type='5mm Clear', finish='White Powder Coat', mesh=False, quantity=2
            )
            generate_cut_pieces(d1)

            d2 = DesignItem.objects.create(
                order=order1, product_type='window', width=600, height=1200, typology='casement', 
                glass_type='5mm Frosted', finish='White Powder Coat', mesh=True, quantity=1
            )
            generate_cut_pieces(d2)

            order2 = Order.objects.create(code='ORD-002', customer_name='Acme Corp')
            d3 = DesignItem.objects.create(
                order=order2, product_type='door', width=1000, height=2100, typology='sliding', 
                glass_type='6mm Toughened', finish='Black Anodized', mesh=False, quantity=3
            )
            generate_cut_pieces(d3)

            self.stdout.write(self.style.SUCCESS('Sample orders created.'))
        else:
            self.stdout.write(self.style.WARNING('Orders already exist. Skipping order seed.'))

        self.stdout.write(self.style.SUCCESS('Seeding complete.'))
