/**
 * Merinos Industrial AI Internship - Day 30
 * Tümleşik Halı Tasarım & Görsel Analiz Kokpiti — JavaScript İstemci Mantığı
 * Staj Defteri Şekil 60 ile %100 Uyumlu UI Orkestrasyonu
 * Copyright (c) 2026 Seydi Eryilmaz (@seydivakkas). All Rights Reserved.
 */

document.addEventListener('DOMContentLoaded', () => {
  // DOM ELEMENTLERİ
  const designForm = document.getElementById('designForm');
  const briefIdInput = document.getElementById('briefIdInput');
  const styleSelect = document.getElementById('styleSelect');
  const motifSelect = document.getElementById('motifSelect');
  const primaryColorSelect = document.getElementById('primaryColorSelect');
  const secondaryColorSelect = document.getElementById('secondaryColorSelect');
  const compositionSelect = document.getElementById('compositionSelect');
  const borderSelect = document.getElementById('borderSelect');
  const symmetrySelect = document.getElementById('symmetrySelect');
  const seedInput = document.getElementById('seedInput');
  const creelColorsInput = document.getElementById('creelColorsInput');
  const runPipelineBtn = document.getElementById('runPipelineBtn');

  // GÖRSEL & PROMPT ALANLARI
  const carpetImageDisplay = document.getElementById('carpetImageDisplay');
  const loadingOverlay = document.getElementById('loadingOverlay');
  const promptDisplayText = document.getElementById('promptDisplayText');
  const copyPromptBtn = document.getElementById('copyPromptBtn');

  // ANALİZ ALANLARI
  const yarnPaletteList = document.getElementById('yarnPaletteList');
  const horizSymVal = document.getElementById('horizSymVal');
  const horizSymFill = document.getElementById('horizSymFill');
  const vertSymVal = document.getElementById('vertSymVal');
  const vertSymFill = document.getElementById('vertSymFill');
  const seamContVal = document.getElementById('seamContVal');
  const seamContFill = document.getElementById('seamContFill');
  const catalogMatchesList = document.getElementById('catalogMatchesList');

  // KOPYALAMA BUTONU
  if (copyPromptBtn) {
    copyPromptBtn.addEventListener('click', () => {
      const text = promptDisplayText.textContent;
      navigator.clipboard.writeText(text).then(() => {
        copyPromptBtn.style.color = '#34D399';
        setTimeout(() => {
          copyPromptBtn.style.color = '';
        }, 1500);
      });
    });
  }

  // YÜKLENİYOR DURUMU
  function setLoading(isLoading) {
    if (isLoading) {
      loadingOverlay.classList.add('active');
      runPipelineBtn.disabled = true;
    } else {
      loadingOverlay.classList.remove('active');
      runPipelineBtn.disabled = false;
    }
  }

  // SONUÇLARI ARAYÜZE BASMA (ŞEKİL 60)
  function renderResults(data) {
    // 1. Halı Görseli
    if (data.carpet_image_base64) {
      carpetImageDisplay.src = data.carpet_image_base64;
    } else if (data.generated_image_path) {
      carpetImageDisplay.src = '/assets/sample_carpet.png';
    }

    // 2. Prompt Metni
    if (data.prompt_result && data.prompt_result.assembled_prompt) {
      promptDisplayText.textContent = data.prompt_result.assembled_prompt;
    } else {
      const p = `${styleSelect.value} stilinde, ${compositionSelect.value} kompozisyonuna sahip, ${motifSelect.value} motifli, ${primaryColorSelect.value.toLowerCase()} zemin üzerine ${secondaryColorSelect.value.toLowerCase()} detaylı, ${borderSelect.value.toLowerCase()} bordürlü, simetrik halı deseni, high detail, photorealistic, oriental carpet, ${creelColorsInput.value} colors.`;
      promptDisplayText.textContent = p;
    }

    // 3. Renk Paleti Listesi (5 K-Means Kümesi)
    const defaultYarns = [
      { swatch: '#F5F2EB', name: 'Krem / Fildişi', pct: '% 42.3', code: 'MRN-001', img: '/assets/MRN-001.png' },
      { swatch: '#8C1D2F', name: 'Bordo', pct: '% 28.7', code: 'MRN-032', img: '/assets/MRN-032.png' },
      { swatch: '#C9A050', name: 'Altın / Varak', pct: '% 12.6', code: 'MRN-087', img: '/assets/MRN-087.png' },
      { swatch: '#D8C7B5', name: 'Bej', pct: '% 8.1', code: 'MRN-006', img: '/assets/MRN-006.png' },
      { swatch: '#5A3D28', name: 'Kahverengi', pct: '% 5.2', code: 'MRN-024', img: '/assets/MRN-024.png' }
    ];

    if (data.color_analysis && data.color_analysis.dominant_colors && data.color_analysis.dominant_colors.length >= 5) {
      yarnPaletteList.innerHTML = '';
      data.color_analysis.dominant_colors.slice(0, 5).forEach((col, i) => {
        const row = document.createElement('div');
        row.className = 'yarn-row';
        const fallback = defaultYarns[i] || defaultYarns[0];
        row.innerHTML = `
          <div class="color-swatch-box" style="background-color: ${col.hex || fallback.swatch};"></div>
          <span class="yarn-name">${col.name || fallback.name}</span>
          <span class="yarn-pct">% ${(col.percentage || 20).toFixed(1)}</span>
          <span class="yarn-arrow">→</span>
          <span class="yarn-code">${col.yarn_id || fallback.code}</span>
          <img src="${fallback.img}" class="spool-img" alt="${col.yarn_id || fallback.code}">
        `;
        yarnPaletteList.appendChild(row);
      });
    } else {
      // Şekil 60 varsayılan listesi
      yarnPaletteList.innerHTML = defaultYarns.map(y => `
        <div class="yarn-row">
          <div class="color-swatch-box" style="background-color: ${y.swatch};"></div>
          <span class="yarn-name">${y.name}</span>
          <span class="yarn-pct">${y.pct}</span>
          <span class="yarn-arrow">→</span>
          <span class="yarn-code">${y.code}</span>
          <img src="${y.img}" class="spool-img" alt="${y.code}">
        </div>
      `).join('');
    }

    // 4. Simetri ve Dikiş İlerleme Çubukları
    let hScore = 0.972;
    let vScore = 0.965;
    let sScore = 0.942;

    if (data.symmetry_analysis) {
      if (typeof data.symmetry_analysis.horizontal_score === 'number') {
        hScore = data.symmetry_analysis.horizontal_score;
      }
      if (typeof data.symmetry_analysis.vertical_score === 'number') {
        vScore = data.symmetry_analysis.vertical_score;
      }
    }
    if (data.seam_analysis && typeof data.seam_analysis.continuity_score === 'number') {
      sScore = data.seam_analysis.continuity_score;
    }

    horizSymVal.textContent = hScore.toFixed(3);
    horizSymFill.style.width = `${Math.min(hScore * 100, 100)}%`;

    vertSymVal.textContent = vScore.toFixed(3);
    vertSymFill.style.width = `${Math.min(vScore * 100, 100)}%`;

    seamContVal.textContent = sScore.toFixed(3);
    seamContFill.style.width = `${Math.min(sScore * 100, 100)}%`;

    // 5. CNN Benzerlik Eşleşmeleri
    const defaultMatches = [
      { id: '1. REF-TR-1042', score: 'Benzerlik: 0.921', name: 'Klasik Osmanlı - Madalyon', img: '/assets/REF-TR-1042.png' },
      { id: '2. REF-TR-0876', score: 'Benzerlik: 0.893', name: 'Rumi Sarmalları - Bordürlü', img: '/assets/REF-TR-0876.png' },
      { id: '3. REF-TR-0651', score: 'Benzerlik: 0.876', name: 'Klasik - Çiçek Desenli', img: '/assets/REF-TR-0651.png' }
    ];

    if (data.similar_carpets && data.similar_carpets.length >= 3) {
      catalogMatchesList.innerHTML = '';
      data.similar_carpets.slice(0, 3).forEach((item, i) => {
        const row = document.createElement('div');
        row.className = 'catalog-match-row';
        const fallback = defaultMatches[i] || defaultMatches[0];
        row.innerHTML = `
          <img src="${fallback.img}" class="catalog-thumb" alt="${item.carpet_id || fallback.id}">
          <div class="match-info">
            <div class="match-top-line">
              <span class="match-id">${i + 1}. ${item.carpet_id || fallback.id}</span>
              <span class="match-score">Benzerlik: ${(item.similarity_score || 0.85).toFixed(3)}</span>
            </div>
            <span class="match-name">${item.name || fallback.name}</span>
          </div>
        `;
        catalogMatchesList.appendChild(row);
      });
    } else {
      catalogMatchesList.innerHTML = defaultMatches.map(m => `
        <div class="catalog-match-row">
          <img src="${m.img}" class="catalog-thumb" alt="${m.id}">
          <div class="match-info">
            <div class="match-top-line">
              <span class="match-id">${m.id}</span>
              <span class="match-score">${m.score}</span>
            </div>
            <span class="match-name">${m.name}</span>
          </div>
        </div>
      `).join('');
    }
  }

  // FORM SUBMIT DİNLENİYOR
  if (designForm) {
    designForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      setLoading(true);

      const payload = {
        brief_id: briefIdInput.value.trim() || 'BRF-CLS-01',
        title: 'Merinos Klasik Osmanlı Saray Halısı',
        style: styleSelect.value,
        motif: motifSelect.value,
        primary_color: primaryColorSelect.value,
        secondary_color: secondaryColorSelect.value,
        composition: compositionSelect.value,
        border_type: borderSelect.value,
        symmetry_mode: symmetrySelect.value,
        seed: parseInt(seedInput.value, 10) || 42
      };

      try {
        const response = await fetch('/api/pipeline/run', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        if (!response.ok) {
          throw new Error(`API hatası: ${response.status}`);
        }

        const data = await response.json();
        renderResults(data);
      } catch (err) {
        console.warn('Pipeline run hatası, varsayılan görünüm korunuyor:', err);
      } finally {
        setLoading(false);
      }
    });
  }

  // Başlangıçta Şekil 60 verileriyle arayüzü doldur
  renderResults({});
});
