(function () {
    'use strict';

    const typeSelect = document.getElementById('id_transaction_type');
    const categorySelect = document.getElementById('id_category');
    const subcategorySelect = document.getElementById('id_subcategory');
    const form = document.getElementById('transaction-form');

    if (!typeSelect || !categorySelect || !subcategorySelect) {
        return;
    }

    const selectedCategory = categorySelect.value;
    const selectedSubcategory = subcategorySelect.value;

    async function fetchOptions(url, params) {
        const query = new URLSearchParams(params).toString();
        const response = await fetch(`${url}?${query}`);
        if (!response.ok) {
            throw new Error('Ошибка загрузки данных');
        }
        return response.json();
    }

    function fillSelect(select, items, placeholder, selectedValue) {
        select.innerHTML = '';
        const emptyOption = document.createElement('option');
        emptyOption.value = '';
        emptyOption.textContent = placeholder;
        select.appendChild(emptyOption);

        items.forEach(function (item) {
            const option = document.createElement('option');
            option.value = item.id;
            option.textContent = item.name;
            if (String(item.id) === String(selectedValue)) {
                option.selected = true;
            }
            select.appendChild(option);
        });
    }

    async function loadCategories(preserveSelection) {
        const typeId = typeSelect.value;
        if (!typeId) {
            fillSelect(categorySelect, [], '— выберите тип —', '');
            fillSelect(subcategorySelect, [], '— выберите категорию —', '');
            return;
        }

        const categories = await fetchOptions(window.DDS_API.categoriesUrl, {
            transaction_type: typeId,
        });
        fillSelect(
            categorySelect,
            categories,
            '— выберите категорию —',
            preserveSelection ? selectedCategory : categorySelect.value
        );
        await loadSubcategories(preserveSelection);
    }

    async function loadSubcategories(preserveSelection) {
        const categoryId = categorySelect.value;
        if (!categoryId) {
            fillSelect(subcategorySelect, [], '— выберите категорию —', '');
            return;
        }

        const subcategories = await fetchOptions(window.DDS_API.subcategoriesUrl, {
            category: categoryId,
        });
        fillSelect(
            subcategorySelect,
            subcategories,
            '— выберите подкатегорию —',
            preserveSelection ? selectedSubcategory : subcategorySelect.value
        );
    }

    typeSelect.addEventListener('change', function () {
        loadCategories(false);
    });

    categorySelect.addEventListener('change', function () {
        loadSubcategories(false);
    });

    if (form) {
        form.addEventListener('submit', function (event) {
            let valid = true;

            [typeSelect, categorySelect, subcategorySelect].forEach(function (select) {
                if (!select.value) {
                    select.classList.add('is-invalid');
                    valid = false;
                } else {
                    select.classList.remove('is-invalid');
                }
            });

            const amountInput = document.getElementById('id_amount');
            if (amountInput && (!amountInput.value || parseFloat(amountInput.value) <= 0)) {
                amountInput.classList.add('is-invalid');
                valid = false;
            } else if (amountInput) {
                amountInput.classList.remove('is-invalid');
            }

            if (!valid) {
                event.preventDefault();
            }
        });
    }

    if (typeSelect.value) {
        loadCategories(true);
    }
})();
