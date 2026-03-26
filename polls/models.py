from django.db import models

# Create your models here.

class Candidate(models.Model):
    name = models.CharField(max_length=200)
    party = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.name} ({self.party})"
    

class Vote(models.Model):
    candidate = models.ForeignKey(
        Candidate, on_delete=models.CASCADE, related_name='votes'
    )
    created_at = models.DateTimeField(auto_now_add=True)