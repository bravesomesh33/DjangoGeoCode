from django.contrib.postgres.indexes import GinIndex
from django.db import models

class Location(models.Model):
    address = models.CharField(max_length=255, db_index=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    formatted_address = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['address']),
            models.Index(fields=['latitude', 'longitude']),
            GinIndex(fields=['formatted_address'], name='gin_trgm_idx', opclasses=['gin_trgm_ops']),
        ]

    def __str__(self):
        return self.address

