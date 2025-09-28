from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()
    icon_class = serializers.CharField(read_only=True)
    color = serializers.CharField(read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'title', 'text', 'image', 'created_at', 'is_read', 'notification_type', 'icon_class', 'color']

    def get_created_at(self, obj):
        return obj.created_at.strftime('%d.%m.%Y %H:%M') 