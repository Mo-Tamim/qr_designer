document.addEventListener("DOMContentLoaded", () => {
  const pageSizeSelect = document.getElementById("layout-page-size");
  pageSizeSelect.addEventListener("change", () => {
    document.getElementById("custom-page-size").classList.toggle("hidden", pageSizeSelect.value !== "custom");
    saveLayoutState();
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
      top_font_size_pt: parseFloat(document.getElementById("top-font-size").value) || 8,
      bottom_font_size_pt: parseFloat(document.getElementById("bottom-font-size").value) || 8,
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

  function buildLayoutFormState() {
    const formState = {};
    document.querySelectorAll("input, select, textarea").forEach((el) => {
      if (!el.id) return;
      if (el.type === "checkbox") {
        formState[el.id] = el.checked;
      } else if (el.type === "file") {
        return;
      } else {
        formState[el.id] = el.value;
      }
    });
    return formState;
  }

  function applyLayoutFormState(formState) {
    Object.entries(formState).forEach(([id, value]) => {
      if (id.startsWith("_")) return;
      const el = document.getElementById(id);
      if (!el) return;
      if (el.type === "checkbox") {
        el.checked = value;
      } else if (el.type !== "file") {
        el.value = value;
      }
    });
    document.getElementById("custom-page-size").classList.toggle("hidden", pageSizeSelect.value !== "custom");
  }

  function saveLayoutState() {
    localStorage.setItem("qr_layout_form_state", JSON.stringify(buildLayoutFormState()));
  }

  function restoreLayoutState() {
    const saved = localStorage.getItem("qr_layout_form_state");
    if (!saved) return false;
    try {
      applyLayoutFormState(JSON.parse(saved));
      return true;
    } catch (e) {
      console.error("Failed to restore layout state:", e);
      return false;
    }
  }

  // Auto-save on any input change
  document.querySelectorAll("input, select, textarea").forEach((el) => {
    if (el.type === "file") return;
    el.addEventListener("input", () => saveLayoutState());
    el.addEventListener("change", () => saveLayoutState());
  });

  // Export settings (both designer + layout)
  document.getElementById("export-settings-btn").addEventListener("click", () => {
    const combined = {
      designer: JSON.parse(localStorage.getItem("qr_designer_form_state") || "{}"),
      layout: buildLayoutFormState(),
    };
    const blob = new Blob([JSON.stringify(combined, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "qr-design-settings.json";
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  });

  // Import settings (both designer + layout)
  document.getElementById("import-settings").addEventListener("change", (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (evt) => {
      try {
        const data = JSON.parse(evt.target.result);
        if (data.layout) {
          applyLayoutFormState(data.layout);
          saveLayoutState();
        } else if (!data.designer) {
          applyLayoutFormState(data);
          saveLayoutState();
        }
        if (data.designer) {
          localStorage.setItem("qr_designer_form_state", JSON.stringify(data.designer));
          localStorage.setItem("qr_designer_style", "");
        }
      } catch (err) {
        console.error("Failed to import settings:", err);
        alert("Invalid settings file.");
      }
    };
    reader.readAsText(file);
    e.target.value = "";
  });

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

  // Export PDF
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

  // --- Interactive layout diagram ---
  const SVG_NS = "http://www.w3.org/2000/svg";
  const diagramSvg = document.getElementById("layout-diagram");

  function svgEl(tag, attrs) {
    const el = document.createElementNS(SVG_NS, tag);
    for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, v);
    return el;
  }

  function drawDimArrow(x1, y1, x2, y2, label, color, side) {
    const g = svgEl("g", {});
    const isH = Math.abs(y2 - y1) < 1;
    const len = isH ? Math.abs(x2 - x1) : Math.abs(y2 - y1);
    if (len < 2) return g;

    g.appendChild(svgEl("line", {
      x1, y1, x2, y2,
      stroke: color, "stroke-width": "1", "stroke-dasharray": "3,2",
    }));

    const capLen = 4;
    if (isH) {
      g.appendChild(svgEl("line", { x1, y1: y1 - capLen, x2: x1, y2: y1 + capLen, stroke: color, "stroke-width": "1" }));
      g.appendChild(svgEl("line", { x1: x2, y1: y2 - capLen, x2: x2, y2: y2 + capLen, stroke: color, "stroke-width": "1" }));
    } else {
      g.appendChild(svgEl("line", { x1: x1 - capLen, y1, x2: x1 + capLen, y2: y1, stroke: color, "stroke-width": "1" }));
      g.appendChild(svgEl("line", { x1: x2 - capLen, y1: y2, x2: x2 + capLen, y2: y2, stroke: color, "stroke-width": "1" }));
    }

    const tx = (x1 + x2) / 2;
    const ty = (y1 + y2) / 2;
    const text = svgEl("text", {
      x: isH ? tx : (side === "left" ? tx - 6 : tx + 6),
      y: isH ? (side === "top" ? ty - 4 : ty + 10) : ty + 3,
      fill: color,
      "font-size": "7",
      "text-anchor": "middle",
      "font-family": "sans-serif",
    });
    text.textContent = label;
    g.appendChild(text);

    return g;
  }

  function renderDiagram() {
    if (!diagramSvg) return;
    diagramSvg.innerHTML = "";

    const PAGE_SIZES = { a4: [210, 297], letter: [216, 279], a3: [297, 420], legal: [216, 356] };

    const psVal = pageSizeSelect.value;
    let pw_mm, ph_mm;
    if (psVal === "custom") {
      pw_mm = parseFloat(document.getElementById("page-width").value) || 210;
      ph_mm = parseFloat(document.getElementById("page-height").value) || 297;
    } else {
      [pw_mm, ph_mm] = PAGE_SIZES[psVal] || [210, 297];
    }

    const ml = parseFloat(document.getElementById("margin-left").value) || 0;
    const mr = parseFloat(document.getElementById("margin-right").value) || 0;
    const mt = parseFloat(document.getElementById("margin-top").value) || 0;
    const mb = parseFloat(document.getElementById("margin-bottom").value) || 0;
    const cw = parseFloat(document.getElementById("cell-width").value) || 40;
    const ch = parseFloat(document.getElementById("cell-height").value) || 50;
    const hs = parseFloat(document.getElementById("h-spacing").value) || 0;
    const vs = parseFloat(document.getElementById("v-spacing").value) || 0;
    const ox = parseFloat(document.getElementById("offset-x").value) || 0;
    const oy = parseFloat(document.getElementById("offset-y").value) || 0;
    const rows = parseInt(document.getElementById("grid-rows").value) || 2;
    const cols = parseInt(document.getElementById("grid-cols").value) || 2;

    const drawCols = Math.min(cols, 3);
    const drawRows = Math.min(rows, 3);

    const svgPad = 20;
    const scaleX = (260 - svgPad * 2) / pw_mm;
    const scaleY = (340 - svgPad * 2) / ph_mm;
    const s = Math.min(scaleX, scaleY);
    const drawW = pw_mm * s;
    const drawH = ph_mm * s;
    const originX = (260 - drawW) / 2;
    const originY = (340 - drawH) / 2;

    diagramSvg.setAttribute("viewBox", `0 0 260 340`);

    diagramSvg.appendChild(svgEl("rect", {
      x: originX, y: originY, width: drawW, height: drawH,
      fill: "#fff", stroke: "#555", "stroke-width": "1", rx: "2",
    }));

    const mls = ml * s, mts = mt * s, mrs = mr * s, mbs = mb * s;
    const cws = cw * s, chs = ch * s, hss = hs * s, vss = vs * s;
    const oxs = ox * s, oys = oy * s;

    // Margin shading
    const marginColor = "rgba(108,114,203,0.10)";
    if (mt > 0) diagramSvg.appendChild(svgEl("rect", { x: originX, y: originY, width: drawW, height: mts, fill: marginColor }));
    if (mb > 0) diagramSvg.appendChild(svgEl("rect", { x: originX, y: originY + drawH - mbs, width: drawW, height: mbs, fill: marginColor }));
    if (ml > 0) diagramSvg.appendChild(svgEl("rect", { x: originX, y: originY + mts, width: mls, height: drawH - mts - mbs, fill: marginColor }));
    if (mr > 0) diagramSvg.appendChild(svgEl("rect", { x: originX + drawW - mrs, y: originY + mts, width: mrs, height: drawH - mts - mbs, fill: marginColor }));

    // Draw cells
    const gridStartX = originX + mls + oxs;
    const gridStartY = originY + mts + oys;

    for (let r = 0; r < drawRows; r++) {
      for (let c = 0; c < drawCols; c++) {
        const cx = gridStartX + c * (cws + hss);
        const cy = gridStartY + r * (chs + vss);
        diagramSvg.appendChild(svgEl("rect", {
          x: cx, y: cy, width: cws, height: chs,
          fill: "rgba(108,114,203,0.15)", stroke: "#6c72cb", "stroke-width": "0.8", rx: "1",
        }));
        const qrPad = cws * 0.15;
        const qrS = Math.min(cws, chs) - qrPad * 2;
        const qx = cx + (cws - qrS) / 2;
        const qy = cy + (chs - qrS) / 2;
        diagramSvg.appendChild(svgEl("rect", {
          x: qx, y: qy, width: qrS, height: qrS,
          fill: "rgba(108,114,203,0.25)", stroke: "none", rx: "1",
        }));
      }
    }

    // Ellipsis indicators
    if (cols > 3) {
      const elX = gridStartX + drawCols * (cws + hss) - hss / 2;
      const elY = gridStartY + chs / 2;
      const dots = svgEl("text", { x: elX + 5, y: elY + 2, fill: "#6c72cb", "font-size": "10", "font-family": "sans-serif" });
      dots.textContent = "...";
      diagramSvg.appendChild(dots);
    }
    if (rows > 3) {
      const elX = gridStartX + cws / 2;
      const elY = gridStartY + drawRows * (chs + vss) - vss / 2;
      const dots = svgEl("text", { x: elX - 3, y: elY + 5, fill: "#6c72cb", "font-size": "10", "font-family": "sans-serif", "text-anchor": "middle" });
      dots.textContent = "...";
      diagramSvg.appendChild(dots);
    }

    // Dimension arrows
    const COLORS = {
      margin: "#ef5350",
      cell: "#4caf50",
      spacing: "#ff9800",
      offset: "#e040fb",
    };

    // Top margin
    if (mt > 0) {
      diagramSvg.appendChild(drawDimArrow(
        originX + drawW + 5, originY, originX + drawW + 5, originY + mts,
        `${mt}`, COLORS.margin, "right"
      ));
      const lbl = svgEl("text", { x: originX + drawW + 15, y: originY + mts / 2 + 3, fill: COLORS.margin, "font-size": "6", "font-family": "sans-serif" });
      lbl.textContent = "margin-top";
      diagramSvg.appendChild(lbl);
    }

    // Left margin
    if (ml > 0) {
      diagramSvg.appendChild(drawDimArrow(
        originX, originY + drawH + 5, originX + mls, originY + drawH + 5,
        `${ml}`, COLORS.margin, "bottom"
      ));
      const lbl = svgEl("text", { x: originX + mls / 2, y: originY + drawH + 16, fill: COLORS.margin, "font-size": "6", "font-family": "sans-serif", "text-anchor": "middle" });
      lbl.textContent = "margin-left";
      diagramSvg.appendChild(lbl);
    }

    // Cell width
    if (drawCols > 0) {
      const cy0 = gridStartY;
      diagramSvg.appendChild(drawDimArrow(
        gridStartX, cy0 - 8, gridStartX + cws, cy0 - 8,
        `${cw}mm`, COLORS.cell, "top"
      ));
    }

    // Cell height
    if (drawRows > 0) {
      const cx0 = gridStartX;
      diagramSvg.appendChild(drawDimArrow(
        cx0 - 8, gridStartY, cx0 - 8, gridStartY + chs,
        `${ch}mm`, COLORS.cell, "left"
      ));
    }

    // Horizontal spacing
    if (drawCols > 1 && hs > 0) {
      const sy = gridStartY + chs + 4;
      const sx1 = gridStartX + cws;
      const sx2 = sx1 + hss;
      diagramSvg.appendChild(drawDimArrow(sx1, sy, sx2, sy, `${hs}`, COLORS.spacing, "bottom"));
      // Shade the gap
      diagramSvg.appendChild(svgEl("rect", {
        x: sx1, y: gridStartY, width: hss, height: chs,
        fill: "rgba(255,152,0,0.10)", stroke: "none",
      }));
    }

    // Vertical spacing
    if (drawRows > 1 && vs > 0) {
      const sx = gridStartX + cws + 4;
      const sy1 = gridStartY + chs;
      const sy2 = sy1 + vss;
      diagramSvg.appendChild(drawDimArrow(sx, sy1, sx, sy2, `${vs}`, COLORS.spacing, "right"));
      diagramSvg.appendChild(svgEl("rect", {
        x: gridStartX, y: sy1, width: cws, height: vss,
        fill: "rgba(255,152,0,0.10)", stroke: "none",
      }));
    }

    // Offset X
    if (ox !== 0) {
      const ocy = gridStartY + chs / 2;
      const baseX = originX + mls;
      diagramSvg.appendChild(drawDimArrow(
        baseX, ocy, baseX + oxs, ocy,
        `x:${ox}`, COLORS.offset, "top"
      ));
    }

    // Offset Y
    if (oy !== 0) {
      const ocx = gridStartX + cws / 2;
      const baseY = originY + mts;
      diagramSvg.appendChild(drawDimArrow(
        ocx, baseY, ocx, baseY + oys,
        `y:${oy}`, COLORS.offset, "left"
      ));
    }

    // Legend
    const legendY = originY + drawH + 24;
    const legendItems = [
      { color: COLORS.margin, label: "Margins" },
      { color: COLORS.cell, label: "Cell size" },
      { color: COLORS.spacing, label: "Spacing" },
      { color: COLORS.offset, label: "Offset" },
    ];
    const legendStartX = originX;
    legendItems.forEach((item, i) => {
      const lx = legendStartX + i * 58;
      diagramSvg.appendChild(svgEl("rect", { x: lx, y: legendY, width: 8, height: 8, fill: item.color, rx: "1" }));
      const t = svgEl("text", { x: lx + 11, y: legendY + 7, fill: "#9598a6", "font-size": "7", "font-family": "sans-serif" });
      t.textContent = item.label;
      diagramSvg.appendChild(t);
    });
  }

  // Re-render diagram on any input change
  document.querySelectorAll("input, select").forEach((el) => {
    if (el.type === "file") return;
    el.addEventListener("input", renderDiagram);
    el.addEventListener("change", renderDiagram);
  });

  restoreLayoutState();
  renderDiagram();
});
