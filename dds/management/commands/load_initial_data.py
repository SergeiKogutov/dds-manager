from django.core.management.base import BaseCommand

from dds.models import Category, Status, Subcategory, TransactionType


class Command(BaseCommand):
    help = 'Загружает начальные данные справочников'

    def handle(self, *args, **options):
        statuses = ['Бизнес', 'Личное', 'Налог']
        for name in statuses:
            Status.objects.get_or_create(name=name)

        types = ['Пополнение', 'Списание']
        type_objects = {}
        for name in types:
            type_objects[name], _ = TransactionType.objects.get_or_create(name=name)

        categories_data = {
            'Списание': {
                'Инфраструктура': ['VPS', 'Proxy'],
                'Маркетинг': ['Farpost', 'Avito'],
            },
            'Пополнение': {
                'Доход': ['Продажи', 'Возврат'],
            },
        }

        for type_name, categories in categories_data.items():
            transaction_type = type_objects[type_name]
            for category_name, subcategories in categories.items():
                category, _ = Category.objects.get_or_create(
                    name=category_name,
                    transaction_type=transaction_type,
                )
                for subcategory_name in subcategories:
                    Subcategory.objects.get_or_create(
                        name=subcategory_name,
                        category=category,
                    )

        self.stdout.write(self.style.SUCCESS('Начальные данные успешно загружены.'))
