from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


class User(AbstractUser):
    pass


class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def content(self):
        """Чтение содержимого файла"""
        try:
            with self.file.open('r') as f:
                print(f.read().decode("utf-8"))
                return f.read().decode("utf-8")
        except:
            return ""

    def __str__(self):
        return self.title

class Collection(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    documents = models.ManyToManyField(Document, related_name='collections')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
class Statistics(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, null=True, blank=True)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, null=True, blank=True)
    data = models.JSONField() 
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Statistics"