from django.db import models
from django.contrib.auth.models import User

class SensorRecord(models.Model):
    ipfs_cid = models.CharField(
        max_length=255,
        help_text="CID returned by IPFS",
        unique=True
    )

    blockchain_tx = models.CharField(
        max_length=255,
        help_text="Transaction hash where CID was stored"
    )

    blockchain_account = models.CharField(
        max_length=255,
        help_text="Blockchain account that stored the CID"
    )

    storage_time_taken = models.FloatField(
        help_text="Time taken to store data on blockchain (in seconds)"
    )

    transaction_per_second = models.FloatField(
        help_text="Transactions per second achieved during storage"
    )

    access_time_taken = models.FloatField(
        help_text="Time taken to access/verify data from blockchain (in seconds)",
        null=True,
        blank=True        
    )

    hash_matched = models.BooleanField(
        help_text="Whether the hash matched during verification",
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ipfs_cid[:10]}..."
