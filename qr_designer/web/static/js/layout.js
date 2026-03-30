document.addEventListener("DOMContentLoaded", () => {
  // Custom page size toggle
  const pageSizeSelect = document.getElementById("layout-page-size");
  pageSizeSelect.addEventListener("change", () => {
    document.getElementById("custom-page-size").classList.toggle("hidden", pageSizeSelect.value !== "custom");
  });

  function buildStyleConfig() {
    const saved = localStorage.getItem("qr_designer_style");
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (e) {
        console.error("Failed to parse saved style:", e);
      }
    }
    return {
      content_type: "url",
      content_data: { url: "https://example.com" },
      error_correction: "H",
      size_px: 800,
      dpi: 300,
    };
  }

  function buildGridConfig() {
    const config = {
      rows: parseInt(document.getElementById("grid-rows").value) || 5,
      cols: parseInt(document.getElementById("grid-cols").value) || 4,
      cell_width_mm: parseFloat(document.getElementById("cell-width").value) || 40,
      cell_height_mm: parseFloat(document.getElementById("cell-height").value) || 50,
      h_spacing_mm: parseFloat(document.getElementById("h-spacing").value) || 5,
      v_spacing_mm: parseFloat(document.getElementById("v-spacing").value) || 5,
      margin_top_mm: parseFloat(document.getElementById("margin-top").value) || 10,
      margin_bottom_mm: parseFloat(document.getElementById("margin-bottom").value) || 10,
      margin_left_mm: parseFloat(document.getElementById("margin-left").value) || 10,
      margin_right_mm: parseFloat(document.getElementById("margin-right").value) || 10,
      offset_x_mm: parseFloat(document.getElementById("offset-x").value) || 0,
      offset_y_mm: parseFloat(document.getElementById("offset-y").value) || 0,
      top_text: document.getElementById("top-text").value,
      bottom_text: document.getElementById("bottom-text").value,
      font_size_pt: parseFloat(document.getElementById("font-size").value) || 8,
      show_guides: document.getElementById("show-guides").checked,
      show_borders: document.getElementById("show-borders").checked,
      page_size: pageSizeSelect.value === "custom" ? "a4" : pageSizeSelect.value,
    };

    if (pageSizeSelect.value === "custom") {
      config.page_width_mm = parseFloat(document.getElementById("page-width").value) || 210;
      config.page_height_mm = parseFloat(document.getElementById("page-height").value) || 297;
    }

    return config;
  }

  const hasDesign = !!localStorage.getItem("qr_designer_style");
  const placeholder = document.getElementById("layout-placeholder");
  if (hasDesign) {
    placeholder.innerHTML = 'Using your design from the <a href="/">Designer</a> page.<br>Click "Preview Layout" to generate a preview.';
  }

  // Preview
  document.getElementById("layout-preview-btn").addEventListener("click", async () => {
    const loading = document.getElementById("layout-loading");
    const placeholder = document.getElementById("layout-placeholder");
    const iframe = document.getElementById("pdf-preview");

    loading.classList.remove("hidden");
    placeholder.classList.add("hidden");

    try {
      const res = await fetch("/api/layout/preview", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          style: buildStyleConfig(),
          grid: buildGridConfig(),
        }),
      });
      const data = await res.json();
      if (data.pdf) {
        iframe.src = data.pdf;
        iframe.classList.remove("hidden");
      }
    } catch (e) {
      console.error("Layout preview failed:", e);
      placeholder.textContent = "Preview generation failed.";
      placeholder.classList.remove("hidden");
    } finally {
      loading.classList.add("hidden");
    }
  });

  // Export
  document.getElementById("layout-export-btn").addEventListener("click", async () => {
    try {
      const res = await fetch("/api/layout/export", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          style: buildStyleConfig(),
          grid: buildGridConfig(),
        }),
      });
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "qr_grid.pdf";
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (e) {
      console.error("Layout export failed:", e);
    }
  });
});
