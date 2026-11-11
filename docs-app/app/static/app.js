(function () {
  const NUMBER_DEFAULTS = {
    line_quantity: "1",
    line_unit_price: "0.00",
    line_vat_rate: "21",
  };

  function money(n) {
    return (Math.round((n + Number.EPSILON) * 100) / 100).toFixed(2);
  }

  function formatVatRate(value) {
    const text = String(value ?? "").trim();
    if (text === "") return "";
    const n = Number(text);
    if (!Number.isFinite(n)) return text;
    let out = String(n);
    if (/e/i.test(out)) {
      out = n.toFixed(6).replace(/\.?0+$/, "");
    }
    return out;
  }

  function formatPrice(value) {
    const text = String(value ?? "").trim();
    if (text === "") return "0.00";
    const n = Number(text);
    if (!Number.isFinite(n)) return text;
    return money(n);
  }

  function displayValue(input, value) {
    const name = input.getAttribute("name");
    if (name === "line_unit_price") return formatPrice(value);
    if (name === "line_vat_rate") return formatVatRate(value);
    return String(value ?? "").trim();
  }

  function fieldDefault(input) {
    if (!input || input.type !== "number") return null;
    if (input.dataset.default != null && input.dataset.default !== "") {
      return displayValue(input, input.dataset.default);
    }
    const name = input.getAttribute("name");
    return name && Object.prototype.hasOwnProperty.call(NUMBER_DEFAULTS, name)
      ? NUMBER_DEFAULTS[name]
      : null;
  }

  function sameNumber(a, b) {
    const na = Number(String(a ?? "").trim());
    const nb = Number(String(b ?? "").trim());
    if (!Number.isFinite(na) || !Number.isFinite(nb)) {
      return String(a ?? "").trim() === String(b ?? "").trim();
    }
    return Math.abs(na - nb) < 1e-9;
  }

  function wireNumberField(input) {
    if (!input || input.type !== "number" || input.dataset.defaultWired === "1") return;
    const def = fieldDefault(input);
    if (def == null) return;
    input.dataset.default = def;
    input.dataset.defaultWired = "1";
    if (String(input.value).trim() !== "") {
      input.value = displayValue(input, input.value);
    }
  }

  function wireAllNumberFields(root) {
    (root || document).querySelectorAll('#lines-body input[type="number"]').forEach(wireNumberField);
  }

  function recalc() {
    const rows = document.querySelectorAll("#lines-body tr");
    let subtotal = 0;
    let vatTotal = 0;
    rows.forEach((row) => {
      const qty = parseFloat(row.querySelector('[name="line_quantity"]').value) || 0;
      const price = parseFloat(row.querySelector('[name="line_unit_price"]').value) || 0;
      const vat = parseFloat(row.querySelector('[name="line_vat_rate"]').value) || 0;
      const lineSub = qty * price;
      const lineVat = lineSub * vat / 100;
      subtotal += lineSub;
      vatTotal += lineVat;
      const cell = row.querySelector(".line-sum");
      if (cell) cell.textContent = money(lineSub);
    });
    const elSub = document.getElementById("total-sub");
    const elVat = document.getElementById("total-vat");
    const elAll = document.getElementById("total-all");
    if (elSub) elSub.textContent = money(subtotal);
    if (elVat) elVat.textContent = money(vatTotal);
    if (elAll) elAll.textContent = money(subtotal + vatTotal);
  }

  function addLine(data) {
    const body = document.getElementById("lines-body");
    if (!body) return;
    const qty = data.quantity ?? 1;
    const price = formatPrice(data.unit_price ?? 0);
    const vat = formatVatRate(data.vat_rate ?? 21);
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><input name="line_description" required value="${data.description || ""}" placeholder="Prece / pakalpojums"></td>
      <td><input name="line_unit" value="${data.unit || "gab."}"></td>
      <td><input name="line_quantity" type="number" step="0.001" min="0" value="${qty}" data-default="1"></td>
      <td><input name="line_unit_price" type="number" step="0.01" min="0" value="${price}" data-default="0.00"></td>
      <td><input name="line_vat_rate" type="number" step="0.01" min="0" value="${vat}" data-default="21"></td>
      <td class="line-sum">0.00</td>
      <td><button type="button" class="btn btn-ghost remove-line" title="Dzēst">×</button></td>
    `;
    body.appendChild(tr);
    wireAllNumberFields(tr);
    recalc();
  }

  document.addEventListener("input", (e) => {
    if (e.target.closest("#lines-body")) recalc();
  });

  document.addEventListener("focusin", (e) => {
    const input = e.target;
    if (!input.matches || !input.matches('#lines-body input[type="number"]')) return;
    wireNumberField(input);
    const def = fieldDefault(input);
    if (def == null) return;
    if (sameNumber(input.value, def)) {
      input.value = "";
    }
  });

  document.addEventListener("focusout", (e) => {
    const input = e.target;
    if (!input.matches || !input.matches('#lines-body input[type="number"]')) return;
    wireNumberField(input);
    const def = fieldDefault(input);
    if (def == null) return;
    if (String(input.value).trim() === "") {
      input.value = def;
      recalc();
      return;
    }
    input.value = displayValue(input, input.value);
    recalc();
  });

  document.addEventListener("click", (e) => {
    if (e.target.matches("#add-line")) {
      addLine({ description: "", unit: "gab.", quantity: 1, unit_price: 0, vat_rate: 21 });
    }
    if (e.target.matches(".remove-line")) {
      const body = document.getElementById("lines-body");
      if (body && body.querySelectorAll("tr").length > 1) {
        e.target.closest("tr").remove();
        recalc();
      }
    }
  });

  const productSelect = document.getElementById("product-pick");
  if (productSelect) {
    productSelect.addEventListener("change", () => {
      const opt = productSelect.selectedOptions[0];
      if (!opt || !opt.value) return;
      addLine({
        description: opt.dataset.name,
        unit: opt.dataset.unit,
        quantity: 1,
        unit_price: opt.dataset.price,
        vat_rate: opt.dataset.vat,
      });
      productSelect.value = "";
    });
  }

  // Buyer search
  const buyerSearch = document.getElementById("buyer-search");
  const buyerResults = document.getElementById("buyer-results");
  let searchTimer = null;

  function fillBuyer(b) {
    document.getElementById("buyer_id").value = b.id || "";
    document.getElementById("buyer_name").value = b.name || "";
    document.getElementById("buyer_reg_nr").value = b.reg_nr || "";
    document.getElementById("buyer_vat_nr").value = b.vat_nr || "";
    document.getElementById("buyer_address").value = b.address || "";
    document.getElementById("buyer_phone").value = b.phone || "";
    document.getElementById("buyer_email").value = b.email || "";
    if (buyerResults) buyerResults.classList.remove("open");
  }

  if (buyerSearch && buyerResults) {
    buyerSearch.addEventListener("input", () => {
      clearTimeout(searchTimer);
      const q = buyerSearch.value.trim();
      searchTimer = setTimeout(async () => {
        const res = await fetch("/api/buyers?q=" + encodeURIComponent(q));
        if (!res.ok) return;
        const items = await res.json();
        buyerResults.innerHTML = "";
        items.forEach((b) => {
          const li = document.createElement("li");
          const btn = document.createElement("button");
          btn.type = "button";
          btn.textContent = `${b.name}${b.reg_nr ? " · " + b.reg_nr : ""}`;
          btn.addEventListener("click", () => fillBuyer(b));
          li.appendChild(btn);
          buyerResults.appendChild(li);
        });
        buyerResults.classList.toggle("open", items.length > 0);
      }, 200);
    });
  }

  // Ensure at least one empty line on form
  if (document.getElementById("lines-body") && !document.querySelector("#lines-body tr")) {
    addLine({ description: "", unit: "gab.", quantity: 1, unit_price: 0, vat_rate: 21 });
  } else {
    wireAllNumberFields();
    recalc();
  }
})();
