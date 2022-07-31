from distutils.command.upload import upload
from pyexpat import model
from django.db import models
from sqlalchemy import null

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
    points = models.IntegerField(default=0)
    def __str__(self):
        return self.username

class MaskBase(models.Model):
    name = models.CharField(max_length=20, unique=True, default="none")
    remain = models.IntegerField(default=100)
    total_capacity = models.IntegerField(default=100)
    capability = models.IntegerField(default=1)
    def __str__(self):
        return self.name

class Mask(models.Model):
    mask_image = models.ImageField(upload_to="images/", null=True, blank=True)
    username = models.CharField(max_length=20)
    def __str__(self):
        return self.username