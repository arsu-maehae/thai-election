from django.db import models

# Create your models here.

class Candidate(models.Model):
    name = models.TextField(default='')
    party = models.TextField(default='')