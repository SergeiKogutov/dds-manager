from django import forms
from django.utils import timezone

from .models import (
    CashFlowRecord,
    Category,
    Status,
    Subcategory,
    TransactionType,
)


class CashFlowRecordForm(forms.ModelForm):
    """Форма создания и редактирования записи ДДС."""

    date = forms.DateField(
        label='Дата',
        widget=forms.DateInput(
            format='%Y-%m-%d',
            attrs={
                'type': 'date',
                'class': 'form-control',
                'required': True,
            },
        ),
        input_formats=['%Y-%m-%d', '%d.%m.%Y'],
    )
    status = forms.ModelChoiceField(
        label='Статус',
        queryset=Status.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select', 'required': True}),
    )
    transaction_type = forms.ModelChoiceField(
        label='Тип',
        queryset=TransactionType.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select', 'required': True}),
    )
    category = forms.ModelChoiceField(
        label='Категория',
        queryset=Category.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select', 'required': True}),
    )
    subcategory = forms.ModelChoiceField(
        label='Подкатегория',
        queryset=Subcategory.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select', 'required': True}),
    )
    amount = forms.DecimalField(
        label='Сумма (руб.)',
        min_value=0.01,
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'required': True,
            }
        ),
    )
    comment = forms.CharField(
        label='Комментарий',
        required=False,
        widget=forms.Textarea(
            attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Необязательно'}
        ),
    )

    class Meta:
        model = CashFlowRecord
        fields = [
            'date',
            'status',
            'transaction_type',
            'category',
            'subcategory',
            'amount',
            'comment',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.instance.pk and not self.data:
            self.initial.setdefault('date', timezone.localdate())

        transaction_type_id = self._get_selected_id('transaction_type')
        category_id = self._get_selected_id('category')

        if transaction_type_id:
            self.fields['category'].queryset = Category.objects.filter(
                transaction_type_id=transaction_type_id
            )
        elif self.instance.pk:
            self.fields['category'].queryset = Category.objects.filter(
                transaction_type=self.instance.transaction_type
            )
        else:
            self.fields['category'].queryset = Category.objects.none()

        if category_id:
            self.fields['subcategory'].queryset = Subcategory.objects.filter(
                category_id=category_id
            )
        elif self.instance.pk:
            self.fields['subcategory'].queryset = Subcategory.objects.filter(
                category=self.instance.category
            )
        else:
            self.fields['subcategory'].queryset = Subcategory.objects.none()

    def _get_selected_id(self, field_name):
        if self.data.get(field_name):
            try:
                return int(self.data[field_name])
            except (TypeError, ValueError):
                return None
        if self.instance.pk:
            return getattr(self.instance, f'{field_name}_id', None)
        return None

    def clean(self):
        cleaned_data = super().clean()
        transaction_type = cleaned_data.get('transaction_type')
        category = cleaned_data.get('category')
        subcategory = cleaned_data.get('subcategory')

        if transaction_type and category:
            if category.transaction_type_id != transaction_type.id:
                self.add_error(
                    'category',
                    'Категория не относится к выбранному типу.',
                )

        if category and subcategory:
            if subcategory.category_id != category.id:
                self.add_error(
                    'subcategory',
                    'Подкатегория не относится к выбранной категории.',
                )

        return cleaned_data


class CashFlowFilterForm(forms.Form):
    """Фильтры для списка записей ДДС."""

    date_from = forms.DateField(
        label='Дата с',
        required=False,
        widget=forms.DateInput(
            format='%Y-%m-%d',
            attrs={'type': 'date', 'class': 'form-control'},
        ),
        input_formats=['%Y-%m-%d', '%d.%m.%Y'],
    )
    date_to = forms.DateField(
        label='Дата по',
        required=False,
        widget=forms.DateInput(
            format='%Y-%m-%d',
            attrs={'type': 'date', 'class': 'form-control'},
        ),
        input_formats=['%Y-%m-%d', '%d.%m.%Y'],
    )
    status = forms.ModelChoiceField(
        label='Статус',
        queryset=Status.objects.all(),
        required=False,
        empty_label='Все',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    transaction_type = forms.ModelChoiceField(
        label='Тип',
        queryset=TransactionType.objects.all(),
        required=False,
        empty_label='Все',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    category = forms.ModelChoiceField(
        label='Категория',
        queryset=Category.objects.all(),
        required=False,
        empty_label='Все',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    subcategory = forms.ModelChoiceField(
        label='Подкатегория',
        queryset=Subcategory.objects.all(),
        required=False,
        empty_label='Все',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )


class StatusForm(forms.ModelForm):
    class Meta:
        model = Status
        fields = ['name']
        widgets = {'name': forms.TextInput(attrs={'class': 'form-control', 'required': True})}


class TransactionTypeForm(forms.ModelForm):
    class Meta:
        model = TransactionType
        fields = ['name']
        widgets = {'name': forms.TextInput(attrs={'class': 'form-control', 'required': True})}


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'transaction_type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'transaction_type': forms.Select(attrs={'class': 'form-select', 'required': True}),
        }


class SubcategoryForm(forms.ModelForm):
    class Meta:
        model = Subcategory
        fields = ['name', 'category']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'category': forms.Select(attrs={'class': 'form-select', 'required': True}),
        }
