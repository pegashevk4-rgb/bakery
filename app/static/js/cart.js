(function () {
  const container = document.getElementById("cart-container");
  if (!container) return;

  function formatEuro(value) {
    return `${value.toFixed(2)} €`;
  }

  function refreshTotals(total, count) {
    const totalEl = container.querySelector(".cart-total-value");
    if (totalEl) totalEl.textContent = formatEuro(total);
    updateCartBadge(count);

    if (count === 0) {
      // Полностью пустая корзина — просто перезагружаем, чтобы увидеть empty-state
      window.location.reload();
    }
  }

  container.addEventListener("click", async (e) => {
    const row = e.target.closest(".cart-row");
    if (!row) return;
    const productId = row.dataset.productId;

    if (e.target.classList.contains("cart-remove")) {
      try {
        const data = await apiFetch("/cart/api/remove", { product_id: productId });
        row.remove();
        refreshTotals(data.total, data.count);
      } catch (err) {
        alert(err.message);
      }
    }
  });

  container.addEventListener("change", async (e) => {
    if (!e.target.classList.contains("cart-qty")) return;
    const row = e.target.closest(".cart-row");
    const productId = row.dataset.productId;
    const quantity = Math.max(1, parseInt(e.target.value, 10) || 1);
    e.target.value = quantity;

    try {
      const data = await apiFetch("/cart/api/update", { product_id: productId, quantity });
      const item = data.items.find((i) => String(i.product_id) === String(productId));
      if (item) {
        row.querySelector(".cart-subtotal").textContent = formatEuro(item.subtotal);
      }
      refreshTotals(data.total, data.count);
    } catch (err) {
      alert(err.message);
    }
  });
})();
