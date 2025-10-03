const histBtn = document.getElementById("btnHistory");
if (histBtn) {
  histBtn.addEventListener("click", async () => {
    const box = document.getElementById("historyPanel");
    const out = document.getElementById("historyOut");
    box.classList.remove("hidden");
    out.textContent = "Loading…";
    try {
      const res = await fetch("/history");
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      const lines = data.map(
        (r) =>
          `#${r.id} user=${r.user ?? "-"} ip=${r.ip} in=${r.sql_in_len} out=${r.sql_out_len}`
      );
      out.textContent = lines.join("\n");
    } catch (e) {
      out.textContent = "Failed to load history: " + e.message;
    }
  });
}
