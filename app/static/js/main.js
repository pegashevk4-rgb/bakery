// ===== CSRF helper: подставляем токен во все fetch-запросы с изменением данных =====
const CSRF_TOKEN = document.querySelector('meta[name="csrf-token"]')?.content;

async function apiFetch(url, body) {
  const res = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": CSRF_TOKEN,
    },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.error || "Что-то пошло не так");
  }
  return res.json();
}

function updateCartBadge(count) {
  const badge = document.getElementById("cart-badge");
  if (badge) badge.textContent = count;
}

// ===== Клиентская фильтрация витрины (без перезагрузки страницы) =====
(function initFilters() {
  const grid = document.getElementById("product-grid");
  if (!grid) return;

  const chips = document.querySelectorAll(".filter-chip");
  const priceRange = document.getElementById("max-price");
  const priceOutput = document.getElementById("max-price-value");
  const cards = Array.from(grid.querySelectorAll(".product-card"));

  let activeCategory = document.querySelector(".filter-chip.is-active")?.dataset.category || "";

  function applyFilters() {
    const maxPrice = parseFloat(priceRange.value);
    let visibleCount = 0;

    cards.forEach((card) => {
      const category = card.dataset.category;
      const price = parseFloat(card.dataset.price);
      const matchesCategory = !activeCategory || category === activeCategory;
      const matchesPrice = price <= maxPrice;
      const visible = matchesCategory && matchesPrice;
      card.style.display = visible ? "" : "none";
      if (visible) visibleCount += 1;
    });

    let emptyMsg = grid.querySelector(".empty-state");
    if (visibleCount === 0 && !emptyMsg) {
      emptyMsg = document.createElement("p");
      emptyMsg.className = "empty-state";
      emptyMsg.textContent = "Товаров по этому фильтру не нашлось.";
      grid.appendChild(emptyMsg);
    } else if (visibleCount > 0 && emptyMsg) {
      emptyMsg.remove();
    }
  }

  chips.forEach((chip) => {
    chip.addEventListener("click", () => {
      chips.forEach((c) => c.classList.remove("is-active"));
      chip.classList.add("is-active");
      activeCategory = chip.dataset.category;
      applyFilters();
    });
  });

  if (priceRange) {
    priceRange.addEventListener("input", () => {
      priceOutput.textContent = `${parseFloat(priceRange.value).toFixed(1)} €`;
      applyFilters();
    });
    priceOutput.textContent = `${parseFloat(priceRange.value).toFixed(1)} €`;
  }

  applyFilters();
})();

// ===== Кнопки количества (+/-) на карточках товара =====
document.querySelectorAll(".product-card, .cart-row").forEach((card) => {
  const input = card.querySelector(".qty-input");
  if (!input) return;
  card.querySelectorAll(".qty-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const delta = btn.dataset.action === "inc" ? 1 : -1;
      const next = Math.max(1, (parseInt(input.value, 10) || 1) + delta);
      input.value = Math.min(99, next);
      input.dispatchEvent(new Event("change", { bubbles: true }));
    });
  });
});

// ===== Добавление в корзину с витрины =====
document.querySelectorAll(".add-to-cart").forEach((btn) => {
  btn.addEventListener("click", async () => {
    const card = btn.closest(".product-card");
    const qtyInput = card.querySelector(".qty-input");
    const quantity = parseInt(qtyInput.value, 10) || 1;

    btn.disabled = true;
    try {
      const data = await apiFetch("/cart/api/add", {
        product_id: btn.dataset.productId,
        quantity,
      });
      updateCartBadge(data.count);
      const originalText = btn.textContent;
      btn.textContent = "Добавлено ✓";
      btn.classList.add("added");
      setTimeout(() => {
        btn.textContent = originalText;
        btn.classList.remove("added");
        btn.disabled = false;
      }, 900);
    } catch (err) {
      alert(err.message);
      btn.disabled = false;
    }
  });
});
