// fetchAPI helper for authorized requests
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
    loadCategories('income');
    loadCategories('expense');
    loadFinancialData();
    document.querySelectorAll('input[type="date"]').forEach(input => {
        input.valueAsDate = new Date();
    });
}


async function addExpense(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData.entries());
    const token = localStorage.getItem("access_token");
    let warning = null;
    let expenseAdded = false;
    try {
        const response = await fetch("/finances/expenses/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + token
            },
            body: JSON.stringify(data)
        });
        if (response.ok) {
            expenseAdded = true;
        } else {
            // Якщо бекенд повертає warning, але не помилку
            const error = await response.json();
            if (error.detail && error.detail.message && error.detail.limit !== undefined) {
                warning = error.detail;
                expenseAdded = true; // все одно додаємо
            } else {
                throw new Error(error.detail || "Failed to add expense");
            }
        }
    } catch (err) {
        alert(err.message);
        return;
    }
    if (expenseAdded) {
        let msg = "Expense added!";
        if (warning) {
            msg += `\n\nПопередження: ${warning.message}\nЛіміт: ${warning.limit}\nСума: ${warning.total}\nПеревищено: ${warning.exceeded}`;
        }
        alert(msg);
        loadFinancialData();
    }
}

async function addIncome(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData.entries());
    const token = localStorage.getItem("access_token");
    const response = await fetch("/finances/incomes/", {
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
async function addCategory(type, event) {
    event.preventDefault();
    const token = localStorage.getItem("access_token");
    const input = document.getElementById(`new-${type}-category-name`);
    const name = input.value;
    let payload = { name };
    if (type === 'expense') {
        const limitInput = document.getElementById('new-expense-category-limit');
        const limit = limitInput.value;
        if (limit) payload.limit = parseFloat(limit);
    }
    if (!name) return;
    await fetchAPI(`/finances/${type}_categories/`, {
        method: 'POST',
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        body: JSON.stringify(payload)
    });
    input.value = '';
    if (type === 'expense') document.getElementById('new-expense-category-limit').value = '';
    loadCategories(type);
}

async function loadCategories(type) {
    const token = localStorage.getItem("access_token");
    // Update category list for categories page
    const list = document.getElementById(`${type}-categories-list`);
    if (list) {
        list.innerHTML = '';
    }
    try {
        const response = await fetch(`/finances/${type}_categories/`, {
            headers: {
                "Authorization": "Bearer " + token
            }
        });
        const categories = await response.json();

        // Update select in add transaction form
        const select = document.querySelector(`form[onsubmit='add${type.charAt(0).toUpperCase() + type.slice(1)}(event)'] select[name='category_id']`);
        if (select) {
            select.innerHTML = '';
            categories.forEach(category => {
                const option = document.createElement('option');
                option.value = category.id;
                option.textContent = category.name;
                select.appendChild(option);
            });
        }

        // Update list for categories page
        if (list) {
            categories.forEach(category => {
                const li = document.createElement('li');
                li.id = `${type}-category-${category.id}`;
                li.value = category.id;
                li.innerHTML = `
                    <span>${category.name}${type === 'expense' && category.limit !== null ? ` (Ліміт: ${category.limit})` : ''}</span>
                    <div class="category-buttons">
                        <button onclick="toggleEditForm('${type}', ${category.id}, '${category.name}', ${type === 'expense' ? category.limit : 'null'})">Edit</button>
                        <button onclick="deleteCategory('${type}', ${category.id})">Delete</button>
                    </div>
                `;
                list.appendChild(li);
            });
        }
    } catch (error) {
        console.error(`Failed to load ${type} categories:`, error);
    }
}

function toggleEditForm(type, id, currentName) {
    const li = document.getElementById(`${type}-category-${id}`);
    const span = li.querySelector('span');
    const buttonsDiv = li.querySelector('.category-buttons');
    const existingEditForm = li.querySelector('.edit-form');
    if (existingEditForm) {
        existingEditForm.remove();
        span.style.display = 'inline';
        buttonsDiv.style.display = 'block';
    } else {
        span.style.display = 'none';
        buttonsDiv.style.display = 'none';
        const editForm = document.createElement('div');
        editForm.className = 'edit-form';
        let limitInput = '';
        if (type === 'expense') {
            limitInput = `<input type="number" id="edit-limit-${type}-${id}" placeholder="Limit (optional)" min="0" step="0.01">`;
        }
        editForm.innerHTML = `
            <input type="text" value="${currentName}" id="edit-input-${type}-${id}">
            ${limitInput}
            <button onclick="updateCategory('${type}', ${id})">Save</button>
            <button onclick="toggleEditForm('${type}', ${id}, '${currentName}', ${arguments.length > 3 ? arguments[3] : 'null'})">Cancel</button>
        `;
        li.appendChild(editForm);
        editForm.querySelector('input[type="text"]').focus();
        if (type === 'expense' && arguments.length > 3 && arguments[3] !== null) {
            editForm.querySelector(`#edit-limit-${type}-${id}`).value = arguments[3];
        }
    }
}

async function updateCategory(type, id) {
    const input = document.getElementById(`edit-input-${type}-${id}`);
    const newName = input.value;
    let payload = { name: newName };
    if (type === 'expense') {
        const limitInput = document.getElementById(`edit-limit-${type}-${id}`);
        if (limitInput && limitInput.value !== '') {
            payload.limit = parseFloat(limitInput.value);
        } else {
            payload.limit = null;
        }
    }
    if (!newName) return;
    await fetchAPI(`/finances/${type}_categories/${id}`, {
        method: 'PUT',
        body: JSON.stringify(payload)
    });
    loadCategories(type);
}

document.addEventListener("DOMContentLoaded", function() {
    if (!token) {
        window.location.href = '/login';
        return;
    }
    loadCategories('expense');
    loadCategories('income');
});

async function deleteTransaction(type, id) 
{
    if (confirm('Are you sure you want to delete this transaction?')) {
        await fetchAPI(`/finances/${type}/${id}`, { method: 'DELETE' });
        loadFinancialData();
    }
}

async function deleteCategory(type, id) {
    if (confirm('Are you sure you want to delete this category? Associated transactions will be moved to "Uncategorized".')) {
        await fetchAPI(`/finances/${type}_categories/${id}`, { method: 'DELETE' });
        loadCategories(type);
    }
}

