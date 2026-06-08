import re
from datetime import datetime
from django.utils import timezone
from django.db import models
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Specialization, SpecializationSynonym, Doctor, Slot, Appointment
from .serializers import DoctorSerializer, SlotSerializer, AppointmentSerializer
from .tts import synthesize_text_to_wav_bytes
import openai
import io
from django.http import HttpResponse


def parse_date_time_from_text(text):
    # date: YYYY-MM-DD
    date_match = re.search(r"(\d{4})-(\d{1,2})-(\d{1,2})", text)
    date = None
    if date_match:
        y, m, d = date_match.groups()
        date = f"{y}-{m.zfill(2)}-{d.zfill(2)}"

    # time HH:MM or H:MM or H(am|pm)
    time_match = re.search(r"(\d{1,2}):(\d{2})\s*(am|pm)?", text, re.IGNORECASE)
    time = None
    if time_match:
        hour, minute = time_match.group(1), time_match.group(2)
        time = f"{hour.zfill(2)}:{minute}"
    else:
        time_match = re.search(r"(\d{1,2})\s*(am|pm)", text, re.IGNORECASE)
        if time_match:
            hour = int(time_match.group(1))
            ampm = time_match.group(2).lower()
            if ampm == 'pm' and hour != 12:
                hour += 12
            time = f"{str(hour).zfill(2)}:00"

    return date, time


@api_view(['GET'])
def doctor_search(request):
    q = request.query_params.get('q', '').strip()
    qs = Doctor.objects.select_related('specialization')
    if q:
        # search in name, specialization name, and synonyms
        qs = qs.filter(
            models.Q(name__icontains=q) |
            models.Q(specialization__name__icontains=q) |
            models.Q(specialization__synonyms__synonym_name__icontains=q)
        ).distinct()
    serializer = DoctorSerializer(qs.order_by('name'), many=True)
    return Response(serializer.data)


@api_view(['GET'])
def doctor_slots(request, pk):
    try:
        doctor = Doctor.objects.get(pk=pk)
    except Doctor.DoesNotExist:
        return Response({'detail': 'Doctor not found'}, status=status.HTTP_404_NOT_FOUND)
    qs = doctor.slots.filter(is_booked=False, slot_time__gte=timezone.now()).order_by('slot_time')
    serializer = SlotSerializer(qs, many=True)
    return Response(serializer.data)


@api_view(['GET', 'POST'])
def appointments_view(request):
    if request.method == 'GET':
        qs = Appointment.objects.select_related('doctor').order_by('appointment_date', 'appointment_time')
        serializer = AppointmentSerializer(qs, many=True)
        return Response(serializer.data)

    # POST - create booking
    serializer = AppointmentSerializer(data=request.data)
    if serializer.is_valid():
        doctor = serializer.validated_data['doctor']
        adate = serializer.validated_data['appointment_date']
        atime = serializer.validated_data['appointment_time']

        # try to find a matching slot and mark booked
        slot_dt = datetime.combine(adate, atime)
        try:
            slot = Slot.objects.get(doctor=doctor, slot_time=slot_dt)
            if slot.is_booked:
                return Response({'detail': 'Slot already booked'}, status=status.HTTP_400_BAD_REQUEST)
            slot.is_booked = True
            slot.save()
        except Slot.DoesNotExist:
            slot = None

        appt = serializer.save()
        out = AppointmentSerializer(appt)
        return Response(out.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def appointment_cancel(request, pk):
    try:
        appt = Appointment.objects.get(pk=pk)
    except Appointment.DoesNotExist:
        return Response({'detail': 'Appointment not found'}, status=status.HTTP_404_NOT_FOUND)

    if appt.status == 'cancelled':
        return Response({'detail': 'Already cancelled'}, status=status.HTTP_400_BAD_REQUEST)

    # free slot if exists
    slot_dt = datetime.combine(appt.appointment_date, appt.appointment_time)
    Slot.objects.filter(doctor=appt.doctor, slot_time=slot_dt, is_booked=True).update(is_booked=False)

    appt.status = 'cancelled'
    appt.save()
    return Response({'detail': 'Cancelled'})


@api_view(['POST'])
def voice_query(request):
    # Accepts: transcript, patient_name, optional doctor_id, date, time
    transcript = request.data.get('transcript', '')
    patient_name = request.data.get('patient_name')
    patient_phone = request.data.get('patient_phone')
    doctor_id = request.data.get('doctor_id')
    date = request.data.get('date')
    time = request.data.get('time')

    if not patient_name or not patient_phone:
        return Response({'detail': 'patient_name and patient_phone are required'}, status=status.HTTP_400_BAD_REQUEST)

    doctor = None
    if doctor_id:
        try:
            doctor = Doctor.objects.get(pk=doctor_id)
        except Doctor.DoesNotExist:
            return Response({'detail': 'Doctor not found'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        q = transcript.strip()
        # try to match by name
        if q:
            d = Doctor.objects.filter(name__icontains=q).first()
            if d:
                doctor = d
        # try specialization
        if not doctor and q:
            d = Doctor.objects.filter(models.Q(specialization__name__icontains=q) | models.Q(specialization__synonyms__synonym_name__icontains=q)).first()
            if d:
                doctor = d

    if not doctor:
        return Response({'detail': 'Unable to determine doctor from transcript'}, status=status.HTTP_400_BAD_REQUEST)

    parsed_date, parsed_time = parse_date_time_from_text(transcript)
    adate = date or parsed_date
    atime = time or parsed_time
    if not adate or not atime:
        return Response({'detail': 'Unable to determine date/time from transcript'}, status=status.HTTP_400_BAD_REQUEST)

    # build serializer
    appt_data = {
        'patient_name': patient_name,
        'patient_phone': patient_phone,
        'doctor_id': doctor.id,
        'appointment_date': adate,
        'appointment_time': atime,
    }
    serializer = AppointmentSerializer(data=appt_data)
    if serializer.is_valid():
        appt = serializer.save()

        # try to book slot
        try:
            slot_dt = datetime.combine(appt.appointment_date, appt.appointment_time)
            slot = Slot.objects.get(doctor=doctor, slot_time=slot_dt)
            slot.is_booked = True
            slot.save()
        except Exception:
            pass

        return Response(AppointmentSerializer(appt).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def voice_reply(request):
    """Generate a dynamic text reply using OpenAI and return speech (mp3) bytes.

    Body params: `prompt` (optional) or `transcript`.
    """
    prompt = request.data.get('prompt') or request.data.get('transcript') or ''
    if not prompt:
        return Response({'detail': 'prompt or transcript required'}, status=status.HTTP_400_BAD_REQUEST)

    # Generate text using OpenAI if key provided, otherwise use local HF model (distilgpt2 by default)
    openai_api_key = os.getenv('OPENAI_API_KEY')
    text = None
    if openai_api_key:
        openai.api_key = openai_api_key
        resp = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[
                {'role': 'system', 'content': 'You are a helpful medical assistant.'},
                {'role': 'user', 'content': prompt},
            ],
            max_tokens=200,
        )
        text = resp['choices'][0]['message']['content'].strip()
    else:
        # Use Hugging Face transformers local model as open-source fallback
        try:
            from transformers import pipeline
        except Exception:
            return Response({'detail': 'No LLM backend available (install transformers or set OPENAI_API_KEY)'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        model_name = os.getenv('HF_MODEL', 'distilgpt2')
        gen = pipeline('text-generation', model=model_name)
        out = gen(prompt, max_length=150, do_sample=True, top_p=0.95, temperature=0.7)
        text = out[0]['generated_text'].strip()

    # Synthesize speech (MP3)
    try:
        audio_bytes = synthesize_text_to_wav_bytes(text)
        return HttpResponse(audio_bytes, content_type='audio/mpeg')
    except Exception as e:
        return Response({'detail': 'TTS failed', 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
