from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.dateparse import parse_date
from .models import Deadline
from .serializers import DeadlineSerializer, DeadlineCreateSerializer

class DeadlineViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления дедлайнами
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Deadline.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DeadlineCreateSerializer
        return DeadlineSerializer
    
    @action(detail=False, methods=['get'])
    def by_date(self, request):
        """
        Получить дедлайны по конкретной дате
        Параметр: date (YYYY-MM-DD)
        """
        date_str = request.query_params.get('date')
        if not date_str:
            return Response({'error': 'Параметр date обязателен'}, status=status.HTTP_400_BAD_REQUEST)
        
        date = parse_date(date_str)
        if not date:
            return Response({'error': 'Неверный формат даты. Используйте YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)
        
        deadlines = self.get_queryset().filter(date=date)
        serializer = self.get_serializer(deadlines, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_month(self, request):
        """
        Получить дедлайны по месяцу
        Параметры: year, month
        """
        year = request.query_params.get('year')
        month = request.query_params.get('month')
        
        if not year or not month:
            return Response({'error': 'Параметры year и month обязательны'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            year = int(year)
            month = int(month)
        except ValueError:
            return Response({'error': 'Параметры year и month должны быть цифрами'}, status=status.HTTP_400_BAD_REQUEST)
        
        deadlines = self.get_queryset().filter(date__year=year, date__month=month)
        serializer = self.get_serializer(deadlines, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def toggle_complete(self, request, pk=None):
        """
        Переключить статус выполнения дедлайна
        """
        deadline = self.get_object()
        deadline.is_completed = not deadline.is_completed
        deadline.save()
        serializer = self.get_serializer(deadline)
        return Response(serializer.data)
