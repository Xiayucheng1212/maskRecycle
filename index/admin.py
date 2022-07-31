from django.contrib import admin
from .models import MaskBase, Post,User, Mask
# Register your models here.
admin.site.register(Post)
admin.site.register(User)
admin.site.register(MaskBase)
admin.site.register(Mask)