from django.db import models
from django.conf import settings

# Create your models here.

class Category(models.Model):
    category_name=models.CharField(max_length=100,unique=True)
    description=models.TextField(blank=True,null=True)

    def __str__(self):
        return self.category_name

class Book(models.Model):
    title=models.CharField(max_length=200)
    author=models.CharField(max_length=150)
    isbn=models.CharField(max_length=17,unique=True)
    # ISBN short for International Standard Book Number.
    category=models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='books'
    )
    publisher=models.CharField(max_length=150,blank=True,null=True)
    published_date=models.DateField(blank=True,null=True)
    total_copies=models.PositiveIntegerField(default=1)
    available_copies=models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.title

class BorrowRecord(models.Model):
    BORROWED='BORROWED'
    RETURNED='RETURNED'

    STATUS_CHOICES=[
        (BORROWED,'Borrowed'),
        (RETURNED,'Returned')
    ]

    user=models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='borrow_records'
    )

    book=models.ForeignKey(
        Book,
        on_delete=models.PROTECT,
        related_name='borrow_records'
    )

    borrow_date=models.DateField(auto_now_add=True)
    due_date=models.DateField()
    return_date=models.DateField(blank=True,null=True)

    status=models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=BORROWED
    )

    def __str__(self):
        return f"{self.user} - {self.book}"

class Fine(models.Model):
    borrow_record=models.OneToOneField(
        BorrowRecord,
        on_delete=models.CASCADE,
        related_name='fine'
    )

    fine_amount=models.DecimalField(
        max_digits=8,
        decimal_places=2
    )

    is_paid=models.BooleanField(default=False)
    paid_date=models.DateField(blank=True,null=True)

    def __str__(self):
        return f"Fine:{self.fine_amount}"




