from django.core.management.base import BaseCommand
from bookings.models import Doctor


class Command(BaseCommand):
    help = 'Create initial doctor records for the booking system'

    def handle(self, *args, **options):
        doctors = [
            {'name': 'Dr. Aisha Khan', 'specialty': 'General Physician', 'location': 'Downtown Clinic'},
            {'name': 'Dr. Sameer Patel', 'specialty': 'Cardiologist', 'location': 'City Medical Center'},
            {'name': 'Dr. Nina Roy', 'specialty': 'Dermatologist', 'location': 'Wellness Suite'},
        ]
        for item in doctors:
            Doctor.objects.get_or_create(**item)
        self.stdout.write(self.style.SUCCESS('Seeded doctors successfully.'))
