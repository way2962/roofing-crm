from django.urls import path
from . import twilio_views

urlpatterns = [
    # Twilio webhooks
    path('voice/', twilio_views.incoming_call, name='twilio_incoming'),
    path('new-client-name/', twilio_views.new_client_name, name='twilio_new_name'),
    path('new-client-address/', twilio_views.new_client_address, name='twilio_new_address'),
    path('new-client-need/', twilio_views.new_client_need, name='twilio_new_need'),
    path('existing-menu/', twilio_views.existing_menu, name='twilio_existing_menu'),
    path('existing-question/', twilio_views.existing_question, name='twilio_existing_question'),

    # Simulator AJAX
    path('sim-lookup/', twilio_views.simulator_lookup, name='twilio_sim_lookup'),
    path('sim-submit/', twilio_views.simulator_submit, name='twilio_sim_submit'),
]
