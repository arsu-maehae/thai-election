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


class Election(models.Model):
    name = models.CharField(max_length=200, default='การเลือกตั้ง')
    is_open = models.BooleanField(default=False)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({'เปิด' if self.is_open else 'ปิด'})"

    @classmethod
    def is_voting_open(cls):
        return cls.objects.filter(is_open=True).exists()

class Voter(models.Model):
    national_id = models.CharField(max_length=13, unique=True)
    name = models.CharField(max_length=200)
    has_voted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.national_id})"

    @classmethod
    def is_valid_id(cls, national_id):
        return national_id.isdigit() and len(national_id) == 13