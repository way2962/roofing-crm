from django.db import models


class Client(models.Model):
    """A roofing client — synced from QuickBooks or created manually."""
    phone = models.CharField("Phone Number", max_length=20, db_index=True)
    name = models.CharField("Full Name", max_length=200)
    email = models.EmailField("Email", blank=True)
    address = models.TextField("Address", blank=True)
    qbo_id = models.CharField("QuickBooks ID", max_length=100, blank=True, null=True)
    is_active = models.BooleanField("Active", default=True)
    notes = models.TextField("Notes", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Client"
        verbose_name_plural = "Clients"

    def __str__(self):
        return f"{self.name} — {self.phone}"


class CallLog(models.Model):
    """Record of a phone call — incoming, outgoing, or manually entered."""
    CALL_TYPES = [
        ('incoming', 'Incoming'),
        ('outgoing', 'Outgoing'),
        ('manual', 'Manual Entry'),
    ]

    client = models.ForeignKey(
        Client, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name="Matched Client"
    )
    caller_phone = models.CharField("Phone Number", max_length=20, db_index=True)
    caller_name = models.CharField("Caller Name", max_length=200, blank=True)
    call_type = models.CharField("Call Type", max_length=20, choices=CALL_TYPES, default='incoming')
    is_new_client = models.BooleanField("New Client?", default=False)
    notes = models.TextField("Notes", blank=True)
    duration_seconds = models.IntegerField("Duration (sec)", default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Call Log"
        verbose_name_plural = "Call Logs"

    def __str__(self):
        return f"{self.caller_name or 'Unknown'} ({self.caller_phone}) — {self.get_call_type_display()}"
