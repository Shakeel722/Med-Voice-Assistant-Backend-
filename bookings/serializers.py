from rest_framework import serializers
from .models import Specialization, SpecializationSynonym, Doctor, Slot, Appointment


class SpecializationSynonymSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecializationSynonym
        fields = ['id', 'synonym_name']


class SpecializationSerializer(serializers.ModelSerializer):
    synonyms = SpecializationSynonymSerializer(many=True, read_only=True)

    class Meta:
        model = Specialization
        fields = ['id', 'name', 'synonyms']


class DoctorSerializer(serializers.ModelSerializer):
    specialization = SpecializationSerializer(read_only=True)
    specialization_id = serializers.PrimaryKeyRelatedField(queryset=Specialization.objects.all(), source='specialization', write_only=True)

    class Meta:
        model = Doctor
        fields = ['id', 'name', 'fees', 'specialization', 'specialization_id', 'contact_number', 'hospital_address']


class SlotSerializer(serializers.ModelSerializer):
    doctor = DoctorSerializer(read_only=True)
    doctor_id = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all(), source='doctor', write_only=True)

    class Meta:
        model = Slot
        fields = ['id', 'doctor', 'doctor_id', 'slot_time', 'is_booked']


class AppointmentSerializer(serializers.ModelSerializer):
    doctor = DoctorSerializer(read_only=True)
    doctor_id = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all(), source='doctor', write_only=True)

    class Meta:
        model = Appointment
        fields = ['id', 'patient_name', 'patient_phone', 'doctor', 'doctor_id', 'appointment_date', 'appointment_time', 'status', 'created_at']
        read_only_fields = ['status', 'created_at']