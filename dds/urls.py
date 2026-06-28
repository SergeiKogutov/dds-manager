from django.urls import path

from .views import (
    CategoryListAPIView,
    DictionaryView,
    SubcategoryListAPIView,
    TransactionCreateView,
    TransactionDeleteView,
    TransactionListView,
    TransactionUpdateView,
)

urlpatterns = [
    path('', TransactionListView.as_view(), name='transaction_list'),
    path('create/', TransactionCreateView.as_view(), name='transaction_create'),
    path('<int:pk>/edit/', TransactionUpdateView.as_view(), name='transaction_edit'),
    path('<int:pk>/delete/', TransactionDeleteView.as_view(), name='transaction_delete'),
    path('dictionaries/', DictionaryView.as_view(), name='dictionary'),
    path('api/categories/', CategoryListAPIView.as_view(), name='api_categories'),
    path('api/subcategories/', SubcategoryListAPIView.as_view(), name='api_subcategories'),
]
