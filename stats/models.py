from django.db import models
from django.utils import timezone
# Create your models here.

class DailyStats(models.Model):
    date = models.DateField(default=timezone.now)
    total_translations = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
    average_check = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
    total_users = models.IntegerField(default=0)
    users_with_translations = models.IntegerField(default=0)

    def __str__(self):
        return f'Stats for {self.date}'

    class Meta:
        verbose_name="Daily Statistics"
        verbose_name_plural = "Daily Statistics"
