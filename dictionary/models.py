from django.db import models
from users.models import User

# Create your models here.

class UserWord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='words')
    word = models.CharField(max_length=100)
    translation = models.CharField(max_length=100)
    usage_count = models.IntegerField(default=0)
    is_saved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'word']
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.word} - {self.user.email}"
