from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.db import models
from django.db.models import Count
from django.utils import timezone
from .models import Client, CallLog, Appointment
from .forms import CallLogForm


@login_required
def dashboard(request):
    """Main dashboard — recent calls and client stats."""
    today = timezone.localdate()
    recent_calls = CallLog.objects.select_related('client')[:20]
    pending_appointments = Appointment.objects.filter(status='pending')[:10]
    client_count = Client.objects.count()
    active_client_count = Client.objects.filter(is_active=True).count()
    today_calls = CallLog.objects.filter(created_at__date=today).count()
    new_clients_today = CallLog.objects.filter(
        created_at__date=today, is_new_client=True
    ).count()
    emergency_count = Appointment.objects.filter(is_emergency=True, status='pending').count()

    context = {
        'recent_calls': recent_calls,
        'pending_appointments': pending_appointments,
        'client_count': client_count,
        'active_client_count': active_client_count,
        'today_calls': today_calls,
        'new_clients_today': new_clients_today,
        'emergency_count': emergency_count,
        'page_title': 'Dashboard',
    }
    return render(request, 'crm/dashboard.html', context)


@login_required
def client_list(request):
    """Searchable list of all clients."""
    query = request.GET.get('q', '').strip()
    clients = Client.objects.all()
    if query:
        clients = clients.filter(
            models.Q(name__icontains=query) |
            models.Q(phone__icontains=query) |
            models.Q(email__icontains=query)
        )
    context = {
        'clients': clients,
        'query': query,
        'page_title': 'Clients',
    }
    return render(request, 'crm/client_list.html', context)


@login_required
def client_detail(request, client_id):
    """View a single client with call history."""
    client = get_object_or_404(Client, id=client_id)
    calls = CallLog.objects.filter(client=client)[:50]
    context = {
        'client': client,
        'calls': calls,
        'page_title': client.name,
    }
    return render(request, 'crm/client_detail.html', context)


@login_required
def call_log_create(request):
    """Manually log a phone call — with phone lookup."""
    if request.method == 'POST':
        form = CallLogForm(request.POST)
        if form.is_valid():
            call = form.save(commit=False)
            try:
                client = Client.objects.get(phone=call.caller_phone)
                call.client = client
                call.is_new_client = False
            except Client.DoesNotExist:
                call.is_new_client = True
            call.save()
            return redirect('dashboard')
    else:
        form = CallLogForm()

    context = {
        'form': form,
        'page_title': 'Log a Call',
    }
    return render(request, 'crm/call_log_form.html', context)


@login_required
def lookup_phone(request):
    """HTMX endpoint — look up a phone number and return caller info."""
    phone = request.GET.get('phone', '').strip()
    if not phone:
        return HttpResponse('<div class="text-muted small">Enter a phone number to look up.</div>')

    try:
        client = Client.objects.get(phone=phone)
        return HttpResponse(
            f'<div class="alert alert-success py-1 px-2 mb-0 small">'
            f'✅ Existing client: <strong>{client.name}</strong></div>'
        )
    except Client.DoesNotExist:
        return HttpResponse(
            '<div class="alert alert-warning py-1 px-2 mb-0 small">'
            '🆕 New caller — will be marked as new client.</div>'
        )


@login_required
def call_simulator(request):
    """In-browser IVR call simulator for demos."""
    recent_sim_calls = CallLog.objects.filter(from_ivr=True)[:10]
    context = {
        'page_title': 'Call Simulator',
        'recent_sim_calls': recent_sim_calls,
    }
    return render(request, 'crm/call_simulator.html', context)


@login_required
def appointment_list(request):
    """List all appointments."""
    appointments = Appointment.objects.all()
    context = {
        'appointments': appointments,
        'page_title': 'Appointments',
    }
    return render(request, 'crm/appointment_list.html', context)


@login_required
def appointment_detail(request, appointment_id):
    """View a single appointment."""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    context = {
        'appointment': appointment,
        'page_title': f'Appointment — {appointment.caller_name}',
    }
    return render(request, 'crm/appointment_detail.html', context)
