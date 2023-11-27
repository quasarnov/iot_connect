from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from .forms import CustomUserCreationForm,DeviceForm
from .models import Device,Measurement
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from .serializers import MeasurementSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib import messages
from rest_framework import status
import json


def send_verification_email(request, user):
    current_site = get_current_site(request)
    mail_subject = 'Activate your account.'
    message = render_to_string('iot_device/acc_active_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user),
    })
    to_email = user.email
    email = EmailMessage(mail_subject, message, to=[to_email])
    email.content_subtype = "html" 
    email.send()


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()  # Save the user instance to the database
            send_verification_email(request, user)  # Extracted function for sending email
            messages.success(request, "Please confirm your email address to complete the registration.")
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'iot_device/register.html', {'form': form})

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
        messages.error(request, "Activation link is invalid!")  # Added an error message

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Your account has been activated. You can now log in.")
        return redirect('login')
    else:
        messages.error(request, "Activation link is invalid or has expired.")  # Added an error message
        return render(request, 'iot_device/activation_invalid.html')


@login_required
def home(request):
    user_devices = Device.objects.filter(user=request.user)  # Get devices for the logged-in user

    # Fetch the latest measurement for each device
    for device in user_devices:
        latest_measurement = Measurement.objects.filter(device=device).order_by('-timestamp').first()
        if latest_measurement:
            device.latest_measurement = latest_measurement
        else:
            device.latest_measurement = None

    paginator = Paginator(user_devices, 10)  # Show 10 devices per page
    page_number = request.GET.get('page') 
    page_obj = paginator.get_page(page_number)

    return render(request, 'iot_device/home.html', {'page_obj': page_obj})


@login_required
def create_or_edit_device(request, device_id=None):
    if device_id:
        device = get_object_or_404(Device, id=device_id, user=request.user)  # Get the existing device
        if request.method == 'POST':
            form = DeviceForm(request.POST, instance=device)
            if form.is_valid():
                form.save()
                return redirect('home')  # Redirect after POST
        else:
            form = DeviceForm(instance=device)
    else:
        if request.method == 'POST':
            form = DeviceForm(request.POST)
            if form.is_valid():
                device = form.save(commit=False)
                device.user = request.user
                device.save()
                return redirect('home')  # Redirect after POST
        else:
            form = DeviceForm()  # An unbound form for creating

    return render(request, 'iot_device/create_or_edit_device.html', {'form': form, 'device_id': device_id})

@require_POST  # Ensure this view only accepts POST requests
def delete_device(request, device_id):
    device = get_object_or_404(Device, id=device_id, user=request.user)
    device.delete()
    return redirect('home')  # Redirect after deletion


@login_required
def display_measurements(request, device_id):
    # Ensure the device exists and belongs to the current user
    device = get_object_or_404(Device, id=device_id, user=request.user)

    # Retrieve measurements for the device, ordered from most recent to oldest
    measurements = Measurement.objects.filter(device=device).order_by('-timestamp')

    return render(request, 'iot_device/measurements.html', {'measurements': measurements, 'device': device})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_measurements(request, serial, start_date, end_date):
    # Find the device with the given serial that belongs to the user
    device = get_object_or_404(Device, serial=serial, user=request.user)

    # Filter measurements by date range
    measurements = Measurement.objects.filter(
        device=device,
        timestamp__range=[start_date, end_date]
    )

    # Serialize the data
    serializer = MeasurementSerializer(measurements, many=True)
    return Response(serializer.data)


@login_required
def settings_page(request):
    # Get or create the token for the logged-in user
    token, created = Token.objects.get_or_create(user=request.user)

    return render(request, 'iot_device/settings.html', {'token': token})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def receive_iot_data(request):
    # Extract serial and values from the request
    serial = request.data.get('serial')
    values = request.data.get('values')
    if not serial or values is None:
        return Response({'error': 'Missing serial or values'}, status=status.HTTP_400_BAD_REQUEST)
    # Convert values from string to list if necessary
    if isinstance(values, str):
        try:
            values = json.loads(values)
        except json.JSONDecodeError:
            return Response({'error': 'Invalid format for values'}, status=status.HTTP_400_BAD_REQUEST)
    if not isinstance(values, list):
        return Response({'error': 'Values must be a list'}, status=status.HTTP_400_BAD_REQUEST)
    # Find the device with the given serial and user
    device = get_object_or_404(Device, serial=serial, user=request.user)
    # Create a new measurement
    Measurement.objects.create(device=device, values=values)
    return Response({'success': 'Measurement stored successfully'}, status=status.HTTP_201_CREATED)