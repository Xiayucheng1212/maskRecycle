from pyexpat import model
from django.db import models

# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField(blank=True)
    photo = models.URLField(blank=True)
    location = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.title

class User(models.Model):
    username=models.CharField(max_length=30, blank=False)
    password = models.CharField(max_length=20, blank=False)
    points = models.IntegerField()
    def __str__(self):
        return self.username

class MaskBase(models.Model):
    name = models.CharField(max_length=20, unique=True)
    remain = models.IntegerField()
    total_capacity = models.IntegerField()
    capability = models.IntegerField()
    def __str__(self):
        return self.name