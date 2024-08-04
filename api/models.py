from django.db import models

class Location(models.Model):
    address = models.CharField(max_length=255, db_index=True)  # Index for faster lookups
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    formatted_address = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.address
