from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=[('income', 'Income'), ('expense', 'Expense')])
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255, blank=True)
    date = models.DateField(default=timezone.now)
    transaction_type = models.CharField(max_length=10, choices=[('income', 'Income'), ('expense', 'Expense')])

    def __str__(self):
        return f"{self.transaction_type} - {self.amount} - {self.category}"
