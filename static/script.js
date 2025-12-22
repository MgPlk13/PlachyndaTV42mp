async function checkQuery() {
    const query = document.getElementById("sqlQuery").value;
    const resultArea = document.getElementById("resultArea");

    resultArea.textContent = "⏳ Перевірка...";

    try {
        const response = await fetch("/check_query", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ query })
        });

        const data = await response.json();

        if (data.result) {
            resultArea.textContent = `${data.result} (score: ${data.score || "-"})`;
        } else if (data.error) {
            resultArea.textContent = `❌ Помилка: ${data.error}`;
        } else {
            resultArea.textContent = "⚠️ Невідома відповідь від сервера.";
        }

    } catch (err) {
        resultArea.textContent = "❌ Сервер недоступний або помилка запиту.";
    }
}

function clearQuery() {
    document.getElementById("sqlQuery").value = "";
    document.getElementById("resultArea").textContent = "";
}