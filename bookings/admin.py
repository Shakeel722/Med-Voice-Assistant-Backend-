from django.contrib import admin
from .models import Doctor, Appointment


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialization', 'hospital_address', 'fees')
    search_fields = ('name', 'specialization__name')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient_name', 'patient_phone', 'doctor', 'appointment_date', 'appointment_time', 'status', 'created_at')
    list_filter = ('appointment_date', 'doctor', 'status')
    search_fields = ('patient_name', 'patient_phone', 'doctor__name')
