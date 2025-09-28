from django.db import models
from users.models import User
from datetime import datetime

class Folder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='folders')
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subfolders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Module(models.Model):
    MODULE_TYPES = [
        ('public', 'Открытый'),
        ('private', 'Частный'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='modules')
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name='modules', null=True, blank=True)
    name = models.CharField(max_length=100)
    module_type = models.CharField(max_length=10, choices=MODULE_TYPES, default='private')
    is_saved = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.name} - {self.user.email}"

class Card(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='cards')
    term = models.CharField(max_length=200)
    translation = models.CharField(max_length=200)
    image = models.ImageField(upload_to='cards/images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.term} - {self.translation}"

class BubbleGameRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='bubble_records')
    score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'module')

    def __str__(self):
        return f"{self.user.username} - {self.module.name} - Score: {self.score}"

class LearningProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    last_attempt = models.DateTimeField(auto_now=True)
    correct_attempts = models.IntegerField(default=0)
    incorrect_attempts = models.IntegerField(default=0)
    needs_review = models.BooleanField(default=False)
    next_review = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'card', 'module')

    def __str__(self):
        return f"{self.user.username} - {self.card.term}"

    def update_progress(self, is_correct):
        if is_correct:
            self.correct_attempts += 1
            self.incorrect_attempts = 0
            self.needs_review = False
        else:
            self.incorrect_attempts += 1
            self.correct_attempts = 0
            self.needs_review = True
        self.save()

class BalloonGameRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'module')
        verbose_name = 'Рекорд игры "Воздушные шары"'
        verbose_name_plural = 'Рекорды игры "Воздушные шары"'