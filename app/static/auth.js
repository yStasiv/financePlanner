document.addEventListener("DOMContentLoaded", function() {
    const token = localStorage.getItem("access_token");
    if (token) {
        showApp();
    } else {
        showAuth();
    }
});

function showAuth() {
    document.getElementById("auth-container").style.display = "block";
    document.getElementById("app-container").style.display = "none";
}

function showApp() {
    document.getElementById("auth-container").style.display = "none";
    document.getElementById("app-container").style.display = "block";
    loadExpenseCategories();
    loadIncomeCategories();
    loadFinancialData();
    document.querySelectorAll('input[type="date"]').forEach(input => {
        input.valueAsDate = new Date();
    });
}

async function login(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const response = await fetch("/token", {
        method: "POST",
        body: formData
    });
    if (response.ok) {
        const data = await response.json();
        localStorage.setItem("access_token", data.access_token);
        showApp();
    } else {
        alert("Login failed");
    }
}

async function register(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const response = await fetch("/users/", {
        method: "POST",
        body: formData
    });
    if (response.ok) {
        alert("Registration successful! Please log in.");
        // You might want to automatically log in the user here
    } else {
        alert("Registration failed");
    }
}

function logout() {
    localStorage.removeItem("access_token");
    showAuth();
}

async function addExpense(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData.entries());
    const token = localStorage.getItem("access_token");
    const response = await fetch("/expenses/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        body: JSON.stringify(data)
    });
    if (response.ok) {
        alert("Expense added!");
        loadFinancialData();
    } else {
        alert("Failed to add expense");
    }
}

async function addIncome(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData.entries());
    const token = localStorage.getItem("access_token");
    const response = await fetch("/incomes/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        body: JSON.stringify(data)
    });
    if (response.ok) {
        alert("Income added!");
        loadFinancialData();
    } else {
        alert("Failed to add income");
    }
}

async function addExpenseCategory(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData.entries());
    const token = localStorage.getItem("access_token");
    const response = await fetch("/expense_categories/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        body: JSON.stringify(data)
    });
    if (response.ok) {
        alert("Expense category added!");
        loadExpenseCategories();
    } else {
        alert("Failed to add expense category");
    }
}

async function addIncomeCategory(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData.entries());
    const token = localStorage.getItem("access_token");
    const response = await fetch("/income_categories/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        body: JSON.stringify(data)
    });
    if (response.ok) {
        alert("Income category added!");
        loadIncomeCategories();
    } else {
        alert("Failed to add income category");
    }
}

async function loadExpenseCategories() {
    const token = localStorage.getItem("access_token");
    const response = await fetch("/expense_categories/", {
        headers: {
            "Authorization": "Bearer " + token
        }
    });
    if (response.ok) {
        const categories = await response.json();
        const select = document.querySelector("form[onsubmit='addExpense(event)'] select[name='category_id']");
        select.innerHTML = "";
        categories.forEach(category => {
            const option = document.createElement("option");
            option.value = category.id;
            option.textContent = category.name;
            select.appendChild(option);
        });
    }

    if (document.getElementById("expense-categories-list")) {
        const expenseCategoriesList = document.getElementById("expense-categories-list");
        expenseCategoriesList.innerHTML = "";
        categories.forEach(category => {
            const li = document.createElement("li");
            li.textContent = category.name;
            const deleteButton = document.createElement("button");
            deleteButton.textContent = "Delete";
            deleteButton.onclick = () => deleteExpenseCategory(category.id);
            li.appendChild(deleteButton);
            expenseCategoriesList.appendChild(li);
        });
    }
}

async function loadIncomeCategories() {
    const token = localStorage.getItem("access_token");
    const response = await fetch("/income_categories/", {
        headers: {
            "Authorization": "Bearer " + token
        }
    });
    if (response.ok) {
        const categories = await response.json();
        const select = document.querySelector("form[onsubmit='addIncome(event)'] select[name='category_id']");
        select.innerHTML = "";
        categories.forEach(category => {
            const option = document.createElement("option");
            option.value = category.id;
            option.textContent = category.name;
            select.appendChild(option);
        });
    }

    if (document.getElementById("income-categories-list")) {
        const incomeCategoriesList = document.getElementById("income-categories-list");
        incomeCategoriesList.innerHTML = "";
        categories.forEach(category => {
            const li = document.createElement("li");
            li.textContent = category.name;
            const deleteButton = document.createElement("button");
            deleteButton.textContent = "Delete";
            deleteButton.onclick = () => deleteIncomeCategory(category.id);
            li.appendChild(deleteButton);
            incomeCategoriesList.appendChild(li);
        });
    }
}

async function loadFinancialData() {
    const token = localStorage.getItem("access_token");
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
        }
        if (startDateInput) startDateInput.value = startDate;
        if (endDateInput) endDateInput.value = endDate;
    }

    let url = "/finances/?";
    if (startDate) url += `start_date=${startDate}&`;
    if (endDate) url += `end_date=${endDate}&`;
    if (categoryId && categoryId !== "all") url += `category_id=${categoryId}&`;
    const response = await fetch(url, {
        headers: {
            "Authorization": "Bearer " + token
        }
    });
    if (response.ok) {
        const data = await response.json();
        let totalIncome = 0;
        let totalExpenses = 0;

        data.incomes.forEach(income => {
            totalIncome += income.amount;
        });

        data.expenses.forEach(expense => {
            totalExpenses += expense.amount;
        });

        const balance = totalIncome - totalExpenses;

        if (document.getElementById("balance")) {
            document.getElementById("balance").textContent = balance.toFixed(2);
        }
        if (document.getElementById("total-income")) {
            document.getElementById("total-income").textContent = totalIncome.toFixed(2);
        }
        if (document.getElementById("total-expenses")) {
            document.getElementById("total-expenses").textContent = totalExpenses.toFixed(2);
        }

        if (document.getElementById("incomes-list")) {
            const incomesList = document.getElementById("incomes-list");
            incomesList.innerHTML = "";
            data.incomes.forEach(income => {
                const li = document.createElement("li");
                li.textContent = `${income.description} (${income.category.name}): ${income.amount}`;
                const deleteButton = document.createElement("button");
                deleteButton.textContent = "Delete";
                deleteButton.onclick = () => deleteIncome(income.id);
                li.appendChild(deleteButton);
                incomesList.appendChild(li);
            });
        }

        if (document.getElementById("expenses-list")) {
            const expensesList = document.getElementById("expenses-list");
            expensesList.innerHTML = "";
            const expenseByCategory = {};
            data.expenses.forEach(expense => {
                const li = document.createElement("li");
                li.textContent = `${expense.description} (${expense.category.name}): ${expense.amount}`;
                const deleteButton = document.createElement("button");
                deleteButton.textContent = "Delete";
                deleteButton.onclick = () => deleteExpense(expense.id);
                li.appendChild(deleteButton);
                expensesList.appendChild(li);

                if (!expenseByCategory[expense.category.name]) {
                    expenseByCategory[expense.category.name] = 0;
                }
                expenseByCategory[expense.category.name] += expense.amount;
            });

            const expenseByCategoryList = document.getElementById("expense-by-category-list");
            if (expenseByCategoryList) {
                expenseByCategoryList.innerHTML = "";
                for (const category in expenseByCategory) {
                    const li = document.createElement("li");
                    li.textContent = `${category}: ${expenseByCategory[category].toFixed(2)}`;
                    expenseByCategoryList.appendChild(li);
                }
    
                if (document.getElementById("chart")) {
                    const options = {
                        series: Object.values(expenseByCategory),
                        chart: {
                            type: 'pie',
                        },
                        labels: Object.keys(expenseByCategory),
                        responsive: [{
                            breakpoint: 480,
                            options: {
                                chart: {
                                    width: 200
                                },
                                legend: {
                                    position: 'bottom'
                                }
                            }
                        }]
                    };
    
                    const chart = new ApexCharts(document.querySelector("#chart"), options);
                    chart.render();
                }
            }
        }

        if (document.getElementById("income-by-category-list")) {
            const incomeByCategory = {};
            data.incomes.forEach(income => {
                if (!incomeByCategory[income.category.name]) {
                    incomeByCategory[income.category.name] = 0;
                }
                incomeByCategory[income.category.name] += income.amount;
            });

            const incomeByCategoryList = document.getElementById("income-by-category-list");
            incomeByCategoryList.innerHTML = "";
            for (const category in incomeByCategory) {
                const li = document.createElement("li");
                li.textContent = `${category}: ${incomeByCategory[category].toFixed(2)}`;
                incomeByCategoryList.appendChild(li);
            }
        }
    }
}

async function deleteIncome(id) {
    const token = localStorage.getItem("access_token");
    await fetch(`/incomes/${id}`, {
        method: "DELETE",
        headers: {
            "Authorization": "Bearer " + token
        }
    });
    loadFinancialData();
}

async function deleteExpense(id) {
    const token = localStorage.getItem("access_token");
    await fetch(`/expenses/${id}`, {
        method: "DELETE",
        headers: {
            "Authorization": "Bearer " + token
        }
    });
    loadFinancialData();
}

async function deleteExpenseCategory(id) {
    const token = localStorage.getItem("access_token");
    await fetch(`/expense_categories/${id}`, {
        method: "DELETE",
        headers: {
            "Authorization": "Bearer " + token
        }
    });
    loadExpenseCategories();
}

async function deleteIncomeCategory(id) {
    const token = localStorage.getItem("access_token");
    await fetch(`/income_categories/${id}`, {
        method: "DELETE",
        headers: {
            "Authorization": "Bearer " + token
        }
    });
    loadIncomeCategories();
}