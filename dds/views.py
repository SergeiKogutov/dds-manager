from django.contrib import messages
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import (
    CashFlowFilterForm,
    CashFlowRecordForm,
    CategoryForm,
    StatusForm,
    SubcategoryForm,
    TransactionTypeForm,
)
from .models import (
    CashFlowRecord,
    Category,
    Status,
    Subcategory,
    TransactionType,
)
from .serializers import CategorySerializer, SubcategorySerializer


class TransactionListView(ListView):
    """Главная страница — список записей ДДС с фильтрами."""

    model = CashFlowRecord
    template_name = 'dds/transaction_list.html'
    context_object_name = 'records'
    paginate_by = 20

    def get_queryset(self):
        queryset = CashFlowRecord.objects.select_related(
            'status',
            'transaction_type',
            'category',
            'subcategory',
        )
        self.filter_form = CashFlowFilterForm(self.request.GET or None)

        if self.filter_form.is_valid():
            data = self.filter_form.cleaned_data
            if data.get('date_from'):
                queryset = queryset.filter(date__gte=data['date_from'])
            if data.get('date_to'):
                queryset = queryset.filter(date__lte=data['date_to'])
            if data.get('status'):
                queryset = queryset.filter(status=data['status'])
            if data.get('transaction_type'):
                queryset = queryset.filter(transaction_type=data['transaction_type'])
            if data.get('category'):
                queryset = queryset.filter(category=data['category'])
            if data.get('subcategory'):
                queryset = queryset.filter(subcategory=data['subcategory'])

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = self.filter_form
        query = self.request.GET.copy()
        query.pop('page', None)
        context['filter_query'] = query.urlencode()
        return context


class TransactionCreateView(CreateView):
    """Создание новой записи ДДС."""

    model = CashFlowRecord
    form_class = CashFlowRecordForm
    template_name = 'dds/transaction_form.html'

    def get_success_url(self):
        messages.success(self.request, 'Запись успешно создана.')
        return reverse('transaction_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Новая запись ДДС'
        context['submit_label'] = 'Создать'
        return context


class TransactionUpdateView(UpdateView):
    """Редактирование записи ДДС."""

    model = CashFlowRecord
    form_class = CashFlowRecordForm
    template_name = 'dds/transaction_form.html'

    def get_success_url(self):
        messages.success(self.request, 'Запись успешно обновлена.')
        return reverse('transaction_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактирование записи ДДС'
        context['submit_label'] = 'Сохранить'
        return context


class TransactionDeleteView(DeleteView):
    """Удаление записи ДДС."""

    model = CashFlowRecord
    template_name = 'dds/transaction_confirm_delete.html'

    def get_success_url(self):
        messages.success(self.request, 'Запись удалена.')
        return reverse('transaction_list')


class CategoryListAPIView(APIView):
    """API: категории по выбранному типу."""

    def get(self, request):
        type_id = request.query_params.get('transaction_type')
        if not type_id:
            return Response([])
        categories = Category.objects.filter(transaction_type_id=type_id)
        return Response(CategorySerializer(categories, many=True).data)


class SubcategoryListAPIView(APIView):
    """API: подкатегории по выбранной категории."""

    def get(self, request):
        category_id = request.query_params.get('category')
        if not category_id:
            return Response([])
        subcategories = Subcategory.objects.filter(category_id=category_id)
        return Response(SubcategorySerializer(subcategories, many=True).data)


class DictionaryView(View):
    """Страница управления справочниками."""

    template_name = 'dds/dictionary.html'

    FORM_MAP = {
        'status': (StatusForm, Status),
        'transaction_type': (TransactionTypeForm, TransactionType),
        'category': (CategoryForm, Category),
        'subcategory': (SubcategoryForm, Subcategory),
    }

    def get(self, request):
        return render(request, self.template_name, self._context())

    def post(self, request):
        action = request.POST.get('action')
        entity = request.POST.get('entity')

        if action == 'create' and entity in self.FORM_MAP:
            return self._handle_create(request, entity)
        if action == 'update' and entity in self.FORM_MAP:
            return self._handle_update(request, entity)
        if action == 'delete' and entity in self.FORM_MAP:
            return self._handle_delete(request, entity)

        messages.error(request, 'Некорректное действие.')
        return redirect('dictionary')

    def _handle_create(self, request, entity):
        form_class, _ = self.FORM_MAP[entity]
        form = form_class(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Элемент справочника добавлен.')
        else:
            messages.error(request, 'Ошибка при добавлении. Проверьте данные.')
        return redirect('dictionary')

    def _handle_update(self, request, entity):
        _, model = self.FORM_MAP[entity]
        form_class, _ = self.FORM_MAP[entity]
        item = get_object_or_404(model, pk=request.POST.get('pk'))
        form = form_class(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Элемент справочника обновлён.')
        else:
            messages.error(request, 'Ошибка при обновлении. Проверьте данные.')
        return redirect('dictionary')

    def _handle_delete(self, request, entity):
        _, model = self.FORM_MAP[entity]
        item = get_object_or_404(model, pk=request.POST.get('pk'))
        try:
            item.delete()
            messages.success(request, 'Элемент справочника удалён.')
        except ProtectedError:
            messages.error(
                request,
                'Невозможно удалить: элемент используется в записях или связанных справочниках.',
            )
        return redirect('dictionary')

    def _context(self):
        return {
            'statuses': Status.objects.all(),
            'transaction_types': TransactionType.objects.prefetch_related('categories'),
            'categories': Category.objects.select_related('transaction_type'),
            'subcategories': Subcategory.objects.select_related('category'),
            'status_form': StatusForm(),
            'transaction_type_form': TransactionTypeForm(),
            'category_form': CategoryForm(),
            'subcategory_form': SubcategoryForm(),
        }
