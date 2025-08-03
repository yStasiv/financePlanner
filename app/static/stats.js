// Статистика: логіка для сторінки statistics

// fetchAPI helper для авторизованих запитів
function fetchAPI(url, options = {}) {
    const token = localStorage.getItem('access_token');
    const defaultOptions = {
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    };
    const mergedOptions = { ...defaultOptions, ...options, headers: { ...defaultOptions.headers, ...options.headers } };
    return fetch(url, mergedOptions).then(async response => {
        if (response.status === 401) {
            window.location.href = '/login';
        }
        if (!response.ok && response.status !== 204) {
            const error = await response.json();
            alert(`Error: ${error.detail}`);
            throw new Error(error.detail);
        }
        return response;
    });
}

async function loadFinancialData() {
    const token = localStorage.getItem("access_token");
    // Update filter select (category-filter) for both income and expense categories
    const filterSelect = document.getElementById('category-filter');
    if (filterSelect) {
        // Зберігаємо вибране значення
        const prevValue = filterSelect.value;
        // Очищаємо select через innerHTML
        filterSelect.innerHTML = '<option value="all">All categories</option>';
        try {
            const [incomeRes, expenseRes] = await Promise.all([
                fetch('/finances/income_categories/', { headers: { 'Authorization': 'Bearer ' + token } }),
                fetch('/finances/expense_categories/', { headers: { 'Authorization': 'Bearer ' + token } })
            ]);
            const incomeCategories = incomeRes.ok ? await incomeRes.json() : [];
            const expenseCategories = expenseRes.ok ? await expenseRes.json() : [];

            // Додаємо категорії лише якщо їх value ще не додано у select
            const addedValues = new Set();
            Array.from(filterSelect.options).forEach(opt => addedValues.add(opt.value));
            incomeCategories.forEach(category => {
                const value = `income-${category.id}`;
                if (!addedValues.has(value)) {
                    addedValues.add(value);
                    const option = document.createElement('option');
                    option.value = value;
                    option.textContent = `[Дохід] ${category.name}`;
                    filterSelect.appendChild(option);
                }
            });
            expenseCategories.forEach(category => {
                const value = `expense-${category.id}`;
                if (!addedValues.has(value)) {
                    addedValues.add(value);
                    const option = document.createElement('option');
                    option.value = value;
                    option.textContent = `[Витрата] ${category.name}`;
                    filterSelect.appendChild(option);
                }
            });
            // Відновлюємо вибране значення, якщо воно є серед опцій
            if ([...filterSelect.options].some(opt => opt.value === prevValue)) {
                filterSelect.value = prevValue;
            } else {
                filterSelect.value = 'all';
            }
        } catch (e) {
            // ignore
        }
    }
    const startDateInput = document.getElementById("start_date");
    const endDateInput = document.getElementById("end_date");
    const dateRangeSelect = document.getElementById("date-range");
    const categoryFilter = document.getElementById("category-filter");

    let startDate = startDateInput ? startDateInput.value : null;
    let endDate = endDateInput ? endDateInput.value : null;
    const categoryId = categoryFilter ? categoryFilter.value : null;

    if (dateRangeSelect && dateRangeSelect.value !== "custom") {
        const now = new Date();
        endDate = now.toISOString().split("T")[0];
        switch (dateRangeSelect.value) {
            case "week":
                now.setDate(now.getDate() - 7);
                startDate = now.toISOString().split("T")[0];
                break;
            case "month":
                now.setMonth(now.getMonth() - 1);
                startDate = now.toISOString().split("T")[0];
                break;
            case "year":
                now.setFullYear(now.getFullYear() - 1);
                startDate = now.toISOString().split("T")[0];
                break;
            case "all":
                startDate = null;
                endDate = null;
                break;
            case "custom":
                break;
        }
        if (startDateInput) startDateInput.value = startDate;
        if (endDateInput) endDateInput.value = endDate;
    }

    let url = "/finances/?";
    if (startDate) url += `start_date=${startDate}&`;
    if (endDate) url += `end_date=${endDate}&`;
    // Додаємо категорію до запиту, якщо вибрана
    if (categoryId && categoryId !== "all" && categoryId.includes('-')) {
        const [type, id] = categoryId.split('-');
        url += `category_type=${type}&category_id=${id}&`;
    } else if (categoryId && categoryId !== "all") {
        url += `category_id=${categoryId}&`;
    }
    const response = await fetch(url, {
        headers: {
            "Authorization": "Bearer " + token
        }
    });
    if (response.ok) {
        const data = await response.json();

        // Calculate totals and aggregates
        let totalIncome = 0;
        const incomeByCategory = {};
        data.incomes.forEach(income => {
            totalIncome += income.amount;
            const categoryName = income.category ? income.category.name : "Uncategorized";
            if (!incomeByCategory[categoryName]) {
                incomeByCategory[categoryName] = 0;
            }
            incomeByCategory[categoryName] += income.amount;
        });

        let totalExpenses = 0;
        const expenseByCategory = {};
        data.expenses.forEach(expense => {
            totalExpenses += expense.amount;
            const categoryName = expense.category ? expense.category.name : "Uncategorized";
            if (!expenseByCategory[categoryName]) {
                expenseByCategory[categoryName] = 0;
            }
            expenseByCategory[categoryName] += expense.amount;
        });

        const balance = totalIncome - totalExpenses;

        // Update summary elements
        if (document.getElementById("balance")) {
            document.getElementById("balance").textContent = balance.toFixed(2);
        }
        if (document.getElementById("total-income")) {
            document.getElementById("total-income").textContent = totalIncome.toFixed(2);
        }
        if (document.getElementById("total-expenses")) {
            document.getElementById("total-expenses").textContent = totalExpenses.toFixed(2);
        }

        // Update incomes list
        if (document.getElementById("incomes-list")) {
            const incomesList = document.getElementById("incomes-list");
            incomesList.innerHTML = "";
            data.incomes.forEach(income => {
                const li = document.createElement("li");
                const categoryName = income.category ? income.category.name : "Uncategorized";
                li.textContent = `${income.description} (${categoryName}): ${income.amount}`;
                const deleteButton = document.createElement("button");
                deleteButton.textContent = "Delete";
                deleteButton.onclick = () => deleteTransaction('incomes', income.id);
                li.appendChild(deleteButton);
                incomesList.appendChild(li);
            });
        }

        // Update expenses list
        if (document.getElementById("expenses-list")) {
            const expensesList = document.getElementById("expenses-list");
            expensesList.innerHTML = "";
            data.expenses.forEach(expense => {
                const li = document.createElement("li");
                const categoryName = expense.category ? expense.category.name : "Uncategorized";
                li.textContent = `${expense.description} (${categoryName}): ${expense.amount}`;
                const deleteButton = document.createElement("button");
                deleteButton.textContent = "Delete";
                deleteButton.onclick = () => deleteTransaction('expenses', expense.id);
                li.appendChild(deleteButton);
                expensesList.appendChild(li);
            });
        }

        // Update expense by category list
        if (document.getElementById("expense-by-category-list")) {
            const expenseByCategoryList = document.getElementById("expense-by-category-list");
            expenseByCategoryList.innerHTML = "";
            for (const category in expenseByCategory) {
                const li = document.createElement("li");
                li.textContent = `${category}: ${expenseByCategory[category].toFixed(2)}`;
                expenseByCategoryList.appendChild(li);
            }
        }

        // Update income by category list
        if (document.getElementById("income-by-category-list")) {
            const incomeByCategoryList = document.getElementById("income-by-category-list");
            incomeByCategoryList.innerHTML = "";
            for (const category in incomeByCategory) {
                const li = document.createElement("li");
                li.textContent = `${category}: ${incomeByCategory[category].toFixed(2)}`;
                incomeByCategoryList.appendChild(li);
            }
        }

        // Render combined chart for income and expenses by category
        if (document.getElementById("chart")) {
            const chartEl = document.getElementById("chart");
            chartEl.innerHTML = ""; // Clear previous chart

            const allCategories = [...new Set([...Object.keys(incomeByCategory), ...Object.keys(expenseByCategory)])].sort();

            const incomeData = allCategories.map(cat => incomeByCategory[cat] || 0);
            const expenseData = allCategories.map(cat => expenseByCategory[cat] || 0);

            const options = {
                series: [{
                    name: 'Income',
                    data: incomeData
                }, {
                    name: 'Expenses',
                    data: expenseData
                }],
                chart: {
                    type: 'bar',
                    height: 400,
                    toolbar: {
                        show: false
                    }
                },
                plotOptions: {
                    bar: {
                        horizontal: false,
                        columnWidth: '60%',
                        endingShape: 'rounded'
                    },
                },
                dataLabels: {
                    enabled: false
                },
                stroke: {
                    show: true,
                    width: 2,
                    colors: ['transparent']
                },
                xaxis: {
                    categories: allCategories,
                },
                yaxis: {
                    title: {
                        text: 'Amount'
                    }
                },
                fill: {
                    opacity: 1
                },
                tooltip: {
                    y: {
                        formatter: function (val) {
                            return val.toFixed(2);
                        }
                    }
                },
                title: {
                    text: 'Income vs Expenses by Category',
                    align: 'left'
                },
                legend: {
                    position: 'top',
                },
                responsive: [{
                    breakpoint: 480,
                    options: {
                        chart: {
                            width: '100%'
                        },
                        legend: {
                            position: 'bottom'
                        }
                    }
                }]
            };

            const chart = new ApexCharts(chartEl, options);
            chart.render();
        }
    }
}