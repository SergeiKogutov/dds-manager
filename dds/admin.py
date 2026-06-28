from django.contrib import admin

from .models import CashFlowRecord, Category, Status, Subcategory, TransactionType


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    search_fields = ['name']


@admin.register(TransactionType)
class TransactionTypeAdmin(admin.ModelAdmin):
    search_fields = ['name']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'transaction_type']
    list_filter = ['transaction_type']
    search_fields = ['name']


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']
    list_filter = ['category']
    search_fields = ['name']


@admin.register(CashFlowRecord)
class CashFlowRecordAdmin(admin.ModelAdmin):
    list_display = [
        'date',
        'status',
        'transaction_type',
        'category',
        'subcategory',
        'amount',
    ]
    list_filter = ['status', 'transaction_type', 'category', 'date']
    search_fields = ['comment']
    date_hierarchy = 'date'
