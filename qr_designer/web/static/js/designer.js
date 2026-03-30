document.addEventListener("DOMContentLoaded", () => {
  let logoPath = "";
  let debounceTimer = null;

  // Tab switching
  document.querySelectorAll(".tab").forEach((tab) => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
      document.querySelectorAll(".tab-panel").forEach((p) => p.classList.remove("active"));
      tab.classList.add("active");
      document.getElementById("tab-" + tab.dataset.tab).classList.add("active");
    });
  });

  // Content type switching
  const contentType = document.getElementById("content-type");
  contentType.addEventListener("change", () => {
    document.querySelectorAll(".content-section").forEach((s) => s.classList.add("hidden"));
    const target = document.querySelector(`.content-section[data-type="${contentType.value}"]`);
    if (target) target.classList.remove("hidden");
    schedulePreview();
  });

  // Gradient toggle
  const useGradient = document.getElementById("use-gradient");
  useGradient.addEventListener("change", () => {
    document.getElementById("gradient-controls").classList.toggle("hidden", !useGradient.checked);
    schedulePreview();
  });

  // Gradient angle display
  const gradAngle = document.getElementById("gradient-angle");
  gradAngle.addEventListener("input", () => {
    document.getElementById("gradient-angle-val").textContent = gradAngle.value + "°";
    schedulePreview();
  });

  // Background type switching
  const bgType = document.getElementById("bg-type");
  bgType.addEventListener("change", () => {
    document.getElementById("bg-solid-controls").classList.toggle("hidden", bgType.value !== "solid");
    document.getElementById("bg-gradient-controls").classList.toggle("hidden", bgType.value !== "gradient");
    schedulePreview();
  });

  // Logo upload
  const logoUpload = document.getElementById("logo-upload");
  logoUpload.addEventListener("change", async () => {
    const file = logoUpload.files[0];
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);
    try {
      const res = await fetch("/api/upload-logo", { method: "POST", body: formData });
      const data = await res.json();
      logoPath = data.path;
      document.getElementById("logo-controls").classList.remove("hidden");
      schedulePreview();
    } catch (e) {
      console.error("Logo upload failed:", e);
    }
  });

  // Logo size / padding display
  const logoSize = document.getElementById("logo-size");
  logoSize.addEventListener("input", () => {
    document.getElementById("logo-size-val").textContent = logoSize.value + "%";
    schedulePreview();
  });

  const logoPadding = document.getElementById("logo-padding");
  logoPadding.addEventListener("input", () => {
    document.getElementById("logo-padding-val").textContent = logoPadding.value + "px";
    schedulePreview();
  });

  // Remove logo
  document.getElementById("remove-logo").addEventListener("click", () => {
    logoPath = "";
    logoUpload.value = "";
    document.getElementById("logo-controls").classList.add("hidden");
    schedulePreview();
  });

  // Load presets
  fetch("/api/presets")
    .then((r) => r.json())
    .then((presets) => {
      const sel = document.getElementById("preset-select");
      presets.forEach((p) => {
        const opt = document.createElement("option");
        opt.value = p.name;
        opt.textContent = p.label;
        sel.appendChild(opt);
      });
    });

  // Apply preset
  document.getElementById("preset-select").addEventListener("change", async (e) => {
    const name = e.target.value;
    if (!name) return;
    try {
      const res = await fetch(`/api/presets/${name}`);
      const preset = await res.json();
      applyPreset(preset);
      schedulePreview();
    } catch (e) {
      console.error("Failed to load preset:", e);
    }
  });

  function applyPreset(p) {
    document.getElementById("module-shape").value = p.data_module_shape || "square";
    document.getElementById("qr-shape").value = p.qr_shape || "square";
    document.getElementById("data-color").value = p.data_module_color?.solid || "#000000";
    document.getElementById("finder-outer-shape").value = p.finder_outer_shape || "square";
    document.getElementById("finder-inner-shape").value = p.finder_inner_shape || "square";
    document.getElementById("finder-outer-color").value = p.finder_outer_color?.solid || "#000000";
    document.getElementById("finder-inner-color").value = p.finder_inner_color?.solid || "#000000";

    const useGrad = p.data_module_color?.use_gradient || false;
    document.getElementById("use-gradient").checked = useGrad;
    document.getElementById("gradient-controls").classList.toggle("hidden", !useGrad);
    if (useGrad && p.data_module_color?.gradient) {
      const g = p.data_module_color.gradient;
      document.getElementById("gradient-type").value = g.type || "linear";
      document.getElementById("gradient-angle").value = g.angle || 135;
      document.getElementById("gradient-angle-val").textContent = (g.angle || 135) + "°";
      if (g.stops?.length >= 2) {
        document.getElementById("gradient-color1").value = g.stops[0].color || "#000000";
        document.getElementById("gradient-color2").value = g.stops[g.stops.length - 1].color || "#333333";
      }
    }

    if (p.background) {
      document.getElementById("bg-type").value = p.background.type || "solid";
      document.getElementById("bg-color").value = p.background.color || "#FFFFFF";
      document.getElementById("bg-solid-controls").classList.toggle("hidden", p.background.type !== "solid");
      document.getElementById("bg-gradient-controls").classList.toggle("hidden", p.background.type !== "gradient");
    }
  }

  // Auto-preview on any input change
  document.querySelectorAll("input, select, textarea").forEach((el) => {
    el.addEventListener("input", () => schedulePreview());
    el.addEventListener("change", () => schedulePreview());
  });

  // Export
  document.getElementById("export-btn").addEventListener("click", () => exportQR());

  function schedulePreview() {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(generatePreview, 300);
  }

  function buildStyleConfig() {
    const ct = contentType.value;
    const contentData = getContentData(ct);

    const style = {
      content_type: ct,
      content_data: contentData,
      data_module_shape: document.getElementById("module-shape").value,
      qr_shape: document.getElementById("qr-shape").value,
      error_correction: document.getElementById("error-correction").value,
      size_px: parseInt(document.getElementById("export-size").value) || 800,
      dpi: parseInt(document.getElementById("export-dpi").value) || 300,
      finder_outer_shape: document.getElementById("finder-outer-shape").value,
      finder_inner_shape: document.getElementById("finder-inner-shape").value,
      finder_outer_color: { solid: document.getElementById("finder-outer-color").value },
      finder_inner_color: { solid: document.getElementById("finder-inner-color").value },
      finder_shadow: document.getElementById("finder-shadow").checked,
      alignment_shape: document.getElementById("alignment-shape").value,
      alignment_outer_color: { solid: document.getElementById("alignment-outer-color").value },
      alignment_inner_color: { solid: document.getElementById("alignment-inner-color").value },
      data_module_color: buildModuleColor(),
      background: buildBackground(),
    };

    if (logoPath) {
      style.logo = {
        image_path: logoPath,
        size_ratio: parseInt(logoSize.value) / 100,
        padding: parseInt(logoPadding.value),
        frame_shape: document.getElementById("logo-frame").value,
        frame_color: document.getElementById("logo-frame-color").value,
      };
    }

    return style;
  }

  function getContentData(type) {
    switch (type) {
      case "url":
        return { url: document.getElementById("url-input").value || "https://example.com" };
      case "text":
        return { text: document.getElementById("text-input").value || "Hello" };
      case "wifi":
        return {
          ssid: document.getElementById("wifi-ssid").value || "MyNetwork",
          password: document.getElementById("wifi-password").value || "",
          encryption: document.getElementById("wifi-encryption").value,
        };
      case "vcard":
        return {
          first_name: document.getElementById("vcard-fname").value,
          last_name: document.getElementById("vcard-lname").value,
          phone: document.getElementById("vcard-phone").value,
          email: document.getElementById("vcard-email").value,
          org: document.getElementById("vcard-org").value,
          url: document.getElementById("vcard-url").value,
        };
      case "calendar":
        return {
          summary: document.getElementById("cal-summary").value || "Event",
          start: document.getElementById("cal-start").value,
          end: document.getElementById("cal-end").value,
          location: document.getElementById("cal-location").value,
        };
      case "payment":
        return { url: document.getElementById("payment-url").value || "https://pay.example.com" };
      case "deeplink":
        return { url: document.getElementById("deeplink-url").value || "myapp://home" };
      default:
        return { url: "https://example.com" };
    }
  }

  function buildModuleColor() {
    const col = {
      solid: document.getElementById("data-color").value,
      use_gradient: useGradient.checked,
    };
    if (useGradient.checked) {
      col.gradient = {
        type: document.getElementById("gradient-type").value,
        angle: parseFloat(gradAngle.value),
        stops: [
          { color: document.getElementById("gradient-color1").value, position: 0.0 },
          { color: document.getElementById("gradient-color2").value, position: 1.0 },
        ],
      };
    }
    return col;
  }

  function buildBackground() {
    const type = bgType.value;
    const bg = { type: type };
    if (type === "solid") {
      bg.color = document.getElementById("bg-color").value;
    } else if (type === "gradient") {
      bg.gradient = {
        type: document.getElementById("bg-gradient-type").value,
        angle: 135,
        stops: [
          { color: document.getElementById("bg-gradient-color1").value, position: 0.0 },
          { color: document.getElementById("bg-gradient-color2").value, position: 1.0 },
        ],
      };
    }
    return bg;
  }

  async function generatePreview() {
    const loading = document.getElementById("preview-loading");
    loading.classList.remove("hidden");
    try {
      const style = buildStyleConfig();
      const res = await fetch("/api/preview", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ style: style, preview_size: 400 }),
      });
      const data = await res.json();
      if (data.image) {
        document.getElementById("qr-preview").src = data.image;
      }
    } catch (e) {
      console.error("Preview failed:", e);
    } finally {
      loading.classList.add("hidden");
    }
  }

  async function exportQR() {
    const format = document.getElementById("export-format").value;
    const style = buildStyleConfig();
    try {
      const res = await fetch("/api/export", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ style: style, format: format }),
      });
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `qr_code.${format}`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (e) {
      console.error("Export failed:", e);
    }
  }

  // Initial preview
  generatePreview();
});
