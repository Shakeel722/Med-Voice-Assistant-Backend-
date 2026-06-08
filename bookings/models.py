from django.db import models


class Specialization(models.Model):
    name = models.CharField(max_length=120, unique=True)

    def __str__(self):
        return self.name


class SpecializationSynonym(models.Model):
    synonym_name = models.CharField(max_length=120)
    specialization = models.ForeignKey(Specialization, on_delete=models.CASCADE, related_name='synonyms')

    def __str__(self):
        return f"{self.synonym_name} -> {self.specialization.name}"


class Doctor(models.Model):
    name = models.CharField(max_length=120)
    fees = models.DecimalField(max_digits=10, decimal_places=2)
    specialization = models.ForeignKey(Specialization, on_delete=models.CASCADE, related_name='doctors')
    contact_number = models.CharField(max_length=30, blank=True)
    hospital_address = models.CharField(max_length=250, blank=True)

    def __str__(self):
        return f"{self.name} ({self.specialization.name})"


class Slot(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='slots')
    slot_time = models.DateTimeField()
    is_booked = models.BooleanField(default=False)

    class Meta:
        ordering = ['slot_time']

    def __str__(self):
        return f"{self.doctor.name} - {self.slot_time.isoformat()} ({'booked' if self.is_booked else 'available'})"


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('booked', 'Booked'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    patient_name = models.CharField(max_length=120)
    patient_phone = models.CharField(max_length=30)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='booked')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient_name} with {self.doctor.name} on {self.appointment_date} at {self.appointment_time} [{self.status}]"
