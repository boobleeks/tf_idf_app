from django.contrib import admin
from api.models import User, Document, Collection, Statistics
# Register your models here.

admin.site.register(User)
admin.site.register(Document)
admin.site.register(Collection)
admin.site.register(Statistics)