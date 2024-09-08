from django.db import models

class Mesin(models.Model):
    category_machine = models.CharField(max_length=255, null=True)
    no_machine = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)  # Status mesin
    status = models.CharField(
        max_length=50,
        default='standby'  # Set a default status if necessary
    )


class DowntimeMesin(models.Model):
    machine = models.ForeignKey(Mesin, on_delete=models.CASCADE)
    # actor = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    # reason = models.CharField(max_length=255, blank=True)
    reason = models.TextField(blank=True, null=True)

    def duration(self):
        """Calculate the duration of the downtime."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None

    def __str__(self):
        return f"Downtime from {self.start_time} to {self.end_time}"
    
class DowntimeRole(models.Model):
    downtime = models.ForeignKey(DowntimeMesin, on_delete=models.CASCADE)
    role = models.CharField(max_length=255)
    # start_time = models.DateTimeField()
    # end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=255)