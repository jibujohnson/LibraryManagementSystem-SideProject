from django.contrib import admin
from .models import Category,Book,BorrowRecord,Fine

# Register your models here.

admin.site.register(Category)
admin.site.register(Book)
admin.site.register(BorrowRecord)
admin.site.register(Fine)
