from rest_framework import serializers
from .models import Deadline

class DeadlineSerializer(serializers.ModelSerializer):
    is_overdue = serializers.ReadOnlyField()
    
    class Meta:
        model = Deadline
        fields = [
            'id', 'title', 'description', 'date', 'time', 
            'priority', 'color', 'is_completed', 'is_overdue',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def create(self, validated_data):
        # Автоматически привязываем к текущему пользователю
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class DeadlineCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deadline
        fields = [
            'title', 'description', 'date', 'time', 
            'priority', 'color'
        ]
    
    def create(self, validated_data):
        # Автоматически привязываем к текущему пользователю
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)