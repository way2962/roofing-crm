"""
Twilio IVR webhooks — voice chatbot that routes new vs existing callers.

Twilio calls these endpoints when a call comes in. They return TwiML (XML)
that tells Twilio what to say and what to listen for.

For demo/testing without a real Twilio number, use the Call Simulator
at /call-simulator/ in the CRM.
"""
import os
import logging
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from twilio.twiml.voice_response import VoiceResponse, Gather
from .models import Client, CallLog, Appointment

logger = logging.getLogger(__name__)
COMPANY_NAME = os.getenv('COMPANY_NAME', 'the roofing company')
TWILIO_LANG = 'en-US'


# ─── HELPERS ───────────────────────────────────────────────────────────

def _twiml(resp):
    """Return TwiML as an XML HttpResponse."""
    return HttpResponse(str(resp), content_type='text/xml')


def _say(text):
    """Shortcut: say text and return a voice response."""
    resp = VoiceResponse()
    resp.say(text, language=TWILIO_LANG)
    return resp


def _lookup_client(phone):
    """Try to find a client by phone number."""
    if not phone:
        return None
    # Strip +1 and non-digits for matching
    cleaned = ''.join(c for c in phone if c.isdigit())
    for c in Client.objects.filter(is_active=True):
        c_clean = ''.join(d for d in c.phone if d.isdigit())
        if c_clean and (c_clean == cleaned or c_clean.endswith(cleaned[-7:])):
            return c
    return None


def _log_call(phone, name, client, inquiry_type, is_new, notes='', address=''):
    """Save a call record."""
    return CallLog.objects.create(
        client=client,
        caller_phone=phone,
        caller_name=name,
        call_type='incoming',
        is_new_client=is_new,
        inquiry_type=inquiry_type,
        notes=notes,
        address=address,
        from_ivr=True,
    )


# ─── CALL ENTRY POINT ──────────────────────────────────────────────────

@csrf_exempt
def incoming_call(request):
    """
    Twilio webhook: a call is coming in.
    Looks up the caller's phone number to determine new vs existing.
    """
    caller_phone = request.GET.get('From') or request.POST.get('From', '')
    client = _lookup_client(caller_phone)
    resp = VoiceResponse()

    if client:
        # ─── EXISTING CLIENT ───────────────────────────────────────
        resp.say(
            f"Welcome back to {COMPANY_NAME}, {client.name}. "
            f"How can I help you today?",
            language=TWILIO_LANG
        )
        gather = Gather(
            input='speech dtmf',
            action='/twilio/existing-menu/',
            method='POST',
            speech_timeout='auto',
            language=TWILIO_LANG,
            hints='emergency, general question, service, estimate'
        )
        gather.say(
            "Say emergency for urgent roof leaks or damage. "
            "Say general question for anything else. "
            "Say service request to schedule a repair. "
            "Say estimate to get a quote.",
            language=TWILIO_LANG
        )
        # Pass caller info to next step via <Redirect> hidden — use session-ish via URL params
        resp.append(gather)
        # Timeout fallback
        resp.say("I didn't catch that. Let me transfer you to our team.", language=TWILIO_LANG)
    else:
        # ─── NEW CLIENT ────────────────────────────────────────────
        resp.say(
            f"Thank you for calling {COMPANY_NAME}. "
            f"I see this is your first time reaching out.",
            language=TWILIO_LANG
        )
        gather = Gather(
            input='speech dtmf',
            action='/twilio/new-client-name/',
            method='POST',
            speech_timeout='auto',
            language=TWILIO_LANG,
            hints='name'
        )
        gather.say(
            "Please tell me your full name so I can look up your information.",
            language=TWILIO_LANG
        )
        resp.append(gather)
        resp.say("I didn't catch your name. Please call us back at your convenience.", language=TWILIO_LANG)

    return _twiml(resp)


# ─── NEW CLIENT FLOW ───────────────────────────────────────────────────

@csrf_exempt
def new_client_name(request):
    """Step 1 for new callers: captured their name."""
    caller_phone = request.POST.get('From', '')
    name = request.POST.get('SpeechResult', '') or request.POST.get('Digits', '')
    resp = VoiceResponse()

    if not name:
        gather = Gather(input='speech dtmf', action='/twilio/new-client-name/', method='POST',
                        speech_timeout='auto', language=TWILIO_LANG)
        gather.say("I didn't hear your name. Please say it again.", language=TWILIO_LANG)
        resp.append(gather)
        return _twiml(resp)

    # Store name in URL params for next step — use <Redirect> with query params
    gather = Gather(
        input='speech dtmf',
        action=f'/twilio/new-client-address/?name={name}&phone={caller_phone}',
        method='POST',
        speech_timeout='auto',
        language=TWILIO_LANG,
        hints='address, street, road, lane'
    )
    gather.say(
        f"Thanks, {name}. What is your service address? "
        f"Please say the street address.",
        language=TWILIO_LANG
    )
    resp.append(gather)
    resp.say("I didn't catch the address.", language=TWILIO_LANG)
    return _twiml(resp)


@csrf_exempt
def new_client_address(request):
    """Step 2 for new callers: captured their address."""
    name = request.GET.get('name', 'Caller')
    caller_phone = request.GET.get('phone', request.POST.get('From', ''))
    address = request.POST.get('SpeechResult', '') or request.POST.get('Digits', '')
    resp = VoiceResponse()

    if not address:
        gather = Gather(input='speech dtmf', action=f'/twilio/new-client-address/?name={name}&phone={caller_phone}',
                        method='POST', speech_timeout='auto', language=TWILIO_LANG)
        gather.say("I didn't get the address. Please say it again.", language=TWILIO_LANG)
        resp.append(gather)
        return _twiml(resp)

    # Log the call
    _log_call(
        phone=caller_phone, name=name, client=None,
        inquiry_type='general', is_new=True,
        notes='New caller — gathered info via IVR', address=address
    )

    # Ask what they need
    gather = Gather(
        input='speech dtmf',
        action=f'/twilio/new-client-need/?name={name}&phone={caller_phone}&address={address}',
        method='POST',
        speech_timeout='auto',
        language=TWILIO_LANG,
        hints='emergency, estimate, repair, question'
    )
    gather.say(
        f"Thanks, {name}. What are you calling about today? "
        f"Say emergency for urgent roof leaks. "
        f"Say estimate to get a quote. "
        f"Say repair if you need a service. "
        f"Or say general for anything else.",
        language=TWILIO_LANG
    )
    resp.append(gather)
    return _twiml(resp)


@csrf_exempt
def new_client_need(request):
    """Step 3 for new callers: what they need → book appointment."""
    name = request.GET.get('name', 'Caller')
    phone = request.GET.get('phone', request.POST.get('From', ''))
    address = request.GET.get('address', '')
    need = (request.POST.get('SpeechResult', '') or request.POST.get('Digits', '')).lower()
    resp = VoiceResponse()

    is_emergency = 'emergency' in need
    inquiry_type = 'emergency' if is_emergency else 'estimate' if 'estimate' in need or 'quote' in need else 'service' if 'repair' in need or 'service' in need else 'general'

    # Create the appointment
    Appointment.objects.create(
        client=None,
        caller_name=name,
        caller_phone=phone,
        address=address,
        is_emergency=is_emergency,
        reason=need,
        status='pending',
        from_ivr=True,
    )

    if is_emergency:
        resp.say(
            f"Understood, {name}. This is marked as an emergency. "
            f"Our team has been notified and will call you back shortly at {phone}. "
            f"If this is life-threatening, please hang up and dial 911.",
            language=TWILIO_LANG
        )
    else:
        resp.say(
            f"Thanks, {name}. We've received your {inquiry_type} request for "
            f"{address}. Our team will contact you at {phone} within 24 hours "
            f"to schedule an appointment. Have a great day!",
            language=TWILIO_LANG
        )

    resp.hangup()
    return _twiml(resp)


# ─── EXISTING CLIENT FLOW ──────────────────────────────────────────────

@csrf_exempt
def existing_menu(request):
    """Existing client: routing based on their selection."""
    caller_phone = request.POST.get('From', '')
    choice = (request.POST.get('SpeechResult', '') or request.POST.get('Digits', '')).lower()
    client = _lookup_client(caller_phone)
    resp = VoiceResponse()

    if 'emergency' in choice:
        # Log and create emergency appointment
        _log_call(phone=caller_phone, name=client.name if client else 'Existing Client',
                   client=client, inquiry_type='emergency', is_new=False,
                   notes='Emergency call via IVR')
        Appointment.objects.create(
            client=client,
            caller_name=client.name if client else 'Existing Client',
            caller_phone=caller_phone,
            is_emergency=True,
            reason='Emergency — called via IVR',
            status='pending',
            from_ivr=True,
        )
        resp.say(
            f"We've flagged this as an emergency, {client.name}. "
            f"Someone will call you back shortly. If this is an emergency, "
            f"please hang up and dial 911.",
            language=TWILIO_LANG
        )

    elif 'question' in choice or 'general' in choice:
        _log_call(phone=caller_phone, name=client.name if client else 'Existing Client',
                   client=client, inquiry_type='general', is_new=False,
                   notes='General inquiry via IVR')
        gather = Gather(
            input='speech dtmf',
            action=f'/twilio/existing-question/?name={client.name}&phone={caller_phone}',
            method='POST',
            speech_timeout='auto',
            language=TWILIO_LANG
        )
        gather.say(
            f"What's your question, {client.name}? Please speak after the beep.",
            language=TWILIO_LANG
        )
        resp.append(gather)

    elif 'estimate' in choice or 'quote' in choice:
        _log_call(phone=caller_phone, name=client.name if client else 'Existing Client',
                   client=client, inquiry_type='estimate', is_new=False,
                   notes='Estimate request via IVR')
        Appointment.objects.create(
            client=client,
            caller_name=client.name if client else 'Existing Client',
            caller_phone=caller_phone,
            is_emergency=False,
            reason='Estimate / Quote request via IVR',
            status='pending',
            from_ivr=True,
        )
        resp.say(
            f"We've scheduled an estimate request for you, {client.name}. "
            f"Our team will call to arrange a time within 24 hours.",
            language=TWILIO_LANG
        )

    elif 'service' in choice or 'repair' in choice:
        _log_call(phone=caller_phone, name=client.name if client else 'Existing Client',
                   client=client, inquiry_type='service', is_new=False,
                   notes='Service request via IVR')
        Appointment.objects.create(
            client=client,
            caller_name=client.name if client else 'Existing Client',
            caller_phone=caller_phone,
            is_emergency=False,
            reason='Service / Repair request via IVR',
            status='pending',
            from_ivr=True,
        )
        resp.say(
            f"We've scheduled a service request for you, {client.name}. "
            f"Our team will call to confirm a time.",
            language=TWILIO_LANG
        )

    else:
        gather = Gather(
            input='speech dtmf',
            action='/twilio/existing-menu/',
            method='POST',
            speech_timeout='auto',
            language=TWILIO_LANG,
            hints='emergency, general question, service, estimate'
        )
        gather.say(
            "I didn't understand that. Please say: "
            "emergency, general question, service request, or estimate.",
            language=TWILIO_LANG
        )
        resp.append(gather)

    resp.hangup()
    return _twiml(resp)


@csrf_exempt
def existing_question(request):
    """Existing client: captured their question."""
    name = request.GET.get('name', 'Client')
    phone = request.GET.get('phone', request.POST.get('From', ''))
    question = request.POST.get('SpeechResult', '') or request.POST.get('Digits', '')
    client = _lookup_client(phone)
    resp = VoiceResponse()

    _log_call(phone=phone, name=name, client=client,
               inquiry_type='general', is_new=False,
               notes=f'Question from IVR: {question}')

    resp.say(
        f"Thanks, {name}. We've noted your question and someone will get back to you "
        f"shortly. Have a great day!",
        language=TWILIO_LANG
    )
    resp.hangup()
    return _twiml(resp)


# ─── SIMULATOR API (for in-browser demo) ───────────────────────────────

@csrf_exempt
def simulator_lookup(request):
    """AJAX endpoint: look up a phone number and return the IVR path."""
    phone = request.GET.get('phone', '').strip()
    client = _lookup_client(phone)
    if client:
        return JsonResponse({
            'client_found': True,
            'name': client.name,
            'phone': client.phone,
            'flow': 'existing',
            'message': f'Existing client: {client.name}',
        })
    else:
        return JsonResponse({
            'client_found': False,
            'flow': 'new',
            'message': 'New caller — no matching client found.',
        })


@csrf_exempt
def simulator_submit(request):
    """AJAX endpoint: submit IVR choices from the simulator."""
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        phone = data.get('phone', '')
        name = data.get('name', '')
        flow = data.get('flow', 'new')
        inquiry = data.get('inquiry', 'general')
        address = data.get('address', '')
        question = data.get('question', '')
        client = _lookup_client(phone)

        if flow == 'new':
            _log_call(phone=phone, name=name, client=client,
                       inquiry_type=inquiry, is_new=True,
                       notes=f'Simulated call: {inquiry}', address=address)
            Appointment.objects.create(
                client=client, caller_name=name, caller_phone=phone,
                address=address, is_emergency=(inquiry == 'emergency'),
                reason=question or inquiry, status='pending', from_ivr=True,
            )
        else:
            _log_call(phone=phone, name=name or (client.name if client else ''),
                       client=client, inquiry_type=inquiry, is_new=False,
                       notes=f'Simulated call: {question or inquiry}')
            if inquiry != 'general':
                Appointment.objects.create(
                    client=client, caller_name=name or (client.name if client else ''),
                    caller_phone=phone, is_emergency=(inquiry == 'emergency'),
                    reason=question or inquiry, status='pending', from_ivr=True,
                )

        return JsonResponse({'status': 'ok', 'message': 'Call logged successfully.'})

    return JsonResponse({'status': 'error', 'message': 'POST required.'}, status=400)
