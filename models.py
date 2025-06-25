from django.db import models

class Lead(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    status = models.CharField(max_length=50)
    called_at = models.DateTimeField(null=True, blank=True)
    follow_up = models.BooleanField(default=False)
    next_call_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.phone})"

class CallLog(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    transcript = models.TextField()
    response = models.TextField()
    status = models.CharField(max_length=50)

    def __str__(self):
        return f"Call with {self.lead.name} on {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

