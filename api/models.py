from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
import os



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
        try:
            with open(self.file.path,'r', encoding="utf-8") as f:
                content = f.read()
                return content
        except:
            print(f"Error reading file: {Exception}")
            return ""

    def __str__(self):
        return self.title

class Collection(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    documents = models.ManyToManyField(Document, related_name='collections')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def content(self):
        contents = []
        for document in self.documents.all():
            try:
                # Assuming Document model has a 'file' FileField and 'content' property
                contents.append(document.content)
            except Exception as e:
                print(f"Error reading document {document.id}: {str(e)}")
                contents.append("")  # Add empty string if there's an error
        
        return "\n".join(contents)


    def __str__(self):
        return self.name
    
class Statistics(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, null=True, blank=True)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, null=True, blank=True)
    data = models.JSONField() 
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Statistics"
    