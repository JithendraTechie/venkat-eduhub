from django.db import models
from enrollments.models import Enrollment

class Payment(models.Model):
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    mode = models.CharField(max_length=20, choices=[
        ('cash', 'Cash'),
        ('upi', 'UPI'),
        ('bank', 'Bank Transfer')
    ], default='cash')

    def __str__(self):
        return f"{self.enrollment} - {self.amount}"