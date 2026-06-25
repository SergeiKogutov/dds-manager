from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Status(models.Model):
    """Справочник статусов (Бизнес, Личное, Налог и др.)."""

    name = models.CharField('Название', max_length=100, unique=True)

    class Meta:
        verbose_name = 'Статус'
        verbose_name_plural = 'Статусы'
        ordering = ['name']

    def __str__(self):
        return self.name


class TransactionType(models.Model):
    """Справочник типов операций (Пополнение, Списание и др.)."""

    name = models.CharField('Название', max_length=100, unique=True)

    class Meta:
        verbose_name = 'Тип'
        verbose_name_plural = 'Типы'
        ordering = ['name']

    def __str__(self):
        return self.name


class Category(models.Model):
    """Категория, привязанная к типу операции."""

    name = models.CharField('Название', max_length=100)
    transaction_type = models.ForeignKey(
        TransactionType,
        on_delete=models.PROTECT,
        related_name='categories',
        verbose_name='Тип',
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['transaction_type__name', 'name']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'transaction_type'],
                name='unique_category_per_type',
            ),
        ]

    def __str__(self):
        return f'{self.name} ({self.transaction_type})'


class Subcategory(models.Model):
    """Подкатегория, привязанная к категории."""

    name = models.CharField('Название', max_length=100)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='subcategories',
        verbose_name='Категория',
    )

    class Meta:
        verbose_name = 'Подкатегория'
        verbose_name_plural = 'Подкатегории'
        ordering = ['category__name', 'name']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'category'],
                name='unique_subcategory_per_category',
            ),
        ]

    def __str__(self):
        return f'{self.name} ({self.category})'


class CashFlowRecord(models.Model):
    """Запись о движении денежных средств."""

    date = models.DateField('Дата', default=timezone.localdate)
    status = models.ForeignKey(
        Status,
        on_delete=models.PROTECT,
        verbose_name='Статус',
    )
    transaction_type = models.ForeignKey(
        TransactionType,
        on_delete=models.PROTECT,
        verbose_name='Тип',
        related_name='records',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        verbose_name='Категория',
        related_name='records',
    )
    subcategory = models.ForeignKey(
        Subcategory,
        on_delete=models.PROTECT,
        verbose_name='Подкатегория',
        related_name='records',
    )
    amount = models.DecimalField('Сумма', max_digits=12, decimal_places=2)
    comment = models.TextField('Комментарий', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Запись ДДС'
        verbose_name_plural = 'Записи ДДС'
        ordering = ['-date', '-id']

    def __str__(self):
        return f'{self.date} — {self.amount} р.'

    def clean(self):
        errors = {}

        if self.transaction_type_id and self.category_id:
            if self.category.transaction_type_id != self.transaction_type_id:
                errors['category'] = (
                    'Выбранная категория не относится к указанному типу.'
                )

        if self.category_id and self.subcategory_id:
            if self.subcategory.category_id != self.category_id:
                errors['subcategory'] = (
                    'Выбранная подкатегория не относится к указанной категории.'
                )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
