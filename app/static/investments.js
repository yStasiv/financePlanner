// investments.js: логіка для сторінки інвестицій

// Функція для завантаження інвестицій з бекенду
async function loadInvestments() {
    const token = localStorage.getItem("access_token");
    const response = await fetch("/finances/investments", {
        headers: {
            "Authorization": "Bearer " + token
        }
    });
    if (response.ok) {
        const data = await response.json();
        // Оновлюємо загальну суму інвестицій
        const totalEl = document.getElementById("total-invested");
        if (totalEl) totalEl.textContent = data.total_invested;
        // Оновлюємо таблицю витрат по категоріях
        const tableEl = document.getElementById("investments-table");
        if (tableEl) {
            tableEl.innerHTML = "";
            data.investments.forEach(inv => {
                const tr = document.createElement("tr");
                tr.innerHTML = `<td>${inv.category}</td><td>${inv.sum}</td>`;
                tableEl.appendChild(tr);
            });
        }
        // Оновлюємо деталі витрат
        const detailsEl = document.getElementById("investments-details");
        if (detailsEl) {
            detailsEl.innerHTML = "";
            data.investments.forEach(inv => {
                const div = document.createElement("div");
                div.innerHTML = `<h4>${inv.category}</h4>`;
                const ul = document.createElement("ul");
                inv.expenses.forEach(e => {
                    ul.innerHTML += `<li>${e.date}: ${e.amount} ${e.description ? "— " + e.description : ""}</li>`;
                });
                div.appendChild(ul);
                detailsEl.appendChild(div);
            });
        }
    } else {
        alert("Не вдалося отримати інвестиції");
    }
}

// Викликаємо при завантаженні сторінки
if (window.location.pathname.includes("investments")) {
    window.addEventListener("DOMContentLoaded", loadInvestments);
}
