from django.db import models

class Student(models.Model):
    name = models.CharField(max_length=100)
    guardian=models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=15)
    photo = models.ImageField(upload_to='students/', null=True, blank=True)

    college = models.CharField(max_length=150, blank=True)
    year = models.CharField(max_length=20, blank=True)

    joined_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name