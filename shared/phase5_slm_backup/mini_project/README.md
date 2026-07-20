# Merinos Mini-Proje: Minimal SLM Seçimi, Özel Nano-LLM Motoru & Donanım Kuantalama Profillemesi

Bu mini-proje, **Merinos Halı Sanayi ve Ticaret A.Ş. (Gaziantep 4. OSB)** üretim tesislerinde endüstriyel dil modellerinin uç cihazlarda (NVIDIA RTX 4060 8GB / RTX 3060 12GB ve fabrika sunucusu A10G 24GB) sıfır bellek aşımı (OOM) ve yüksek verimlilikle çalıştırılabilmesi amacıyla geliştirilmiş mimari analiz, özel Causal LM motoru ve kuantalama laboratuvarıdır.

---

## 🏛️ Mimari ve Bileşenler

1. **`custom_nlp_engine.py`**:
   - `MerinosBPETokenizer`: Halı dokuma ve tekstil terminolojisine (`[ATKI]`, `[COZGU]`, `[RAMOZ]`, `[LEVENT]`, `[ARIZA]`) duyarlı özel altkelime tokenlaştırıcı.
   - `RotaryEmbedding` (RoPE): Pozisyon bilgisini Query ve Key tensörlerine dönme matrisleriyle katan modern rotasyonel gömme (offset destekli).
   - `RMSNorm`: Root Mean Square Layer Normalization katmanı.
   - `SwiGLUFFN`: LLaMA / Qwen mimarilerindeki kapılı Swish/SiLU ileri besleme katmanı.
   - `MoEFeedForward`: Sparse Mixture of Experts (Top-K Gating Router, Load Balancing Aux Loss, DeepSeek tarzı daimi aktif Shared Expert).
   - `CausalSelfAttention`: Üçgen alt-matris maskelemeli, Grouped Query Attention (GQA), adım-adım KV önbellekleme ve Gemma-2 logit soft-capping destekli nedensel dikkat katmanı.
   - `MerinosCausalLM`: Uçtan uca otoregresif dil modeli ve $O(1)$ KV-önbellekli üretim döngüsü (`generate(..., use_cache=True)`).

2. **`expert_agent.py` (`MerinosTextileExpertEngine`)**:
   - Fabrika dokuma, BCF ekstrüzyon, terbiye, otomasyon, CAD desinatörlük, akredite kalite kontrol, OEE duruş kaybı ve ERP yedek parça yönetim uzman sistemi.
   - `calculate_oee_and_downtime_loss`: Vardiya bazlı OEE kullanılabilirlik (Availability), kaybedilen halı metrekare hesabı ($v = \text{rpm}/\text{atkı}$, $A_{\text{rate}} = v \times \text{En} \times 2$), sabit fabrika genel gideri ve toplam duruş maliyeti hesaplama motoru.
   - `query_spare_part`: Merinos parça kodları (`MRP-*`) ile entegre ERP stok sorgulama, kritik emniyet eşiği denetimi, tedarik teslim süresi (lead time) ve acil ikmal (`REORDER_URGENT`) alarm mekanizması.
   - `analyze_design_spec`: Tarak/atkı piksel aspect ratio ($1.0 : 1.714$), nokta yoğunluğu ($Tarak \times Atkı \times 2$) ve 3D rölyef emniyet hesaplayıcısı.
   - `audit_carpet_quality`: TSE 2104 metrekare ağırlık toleransı ($\pm 5\%$), ISO 4919 tuft-lock çekme mukavemeti ($\ge 25\text{ N}$), ISO 105 haslıkları ve OEKO-TEX Standard 100 ekolojik denetim motoru.
   - `validate_safety`: LOTO enerji izolasyonu, sıcaklık, basınç, cağlık renk limiti, kalite test standartları, OEE hedef eşiği (%85) ve ERP kritik emniyet stoku doğrulama kapısı.

3. **`functional_backend.py`**:
   - PyTorch ve TensorFlow derin öğrenme çatılarının fonksiyonel, tensörel ve matematiksel eşdeğerlik kataloğu (`FRAMEWORK_EQUIVALENCE_CATALOG`).
   - Einstein Toplamı (`torch.einsum`) ile çok başlı dikkat hesaplaması.
   - Etiket yumuşatmalı Cross-Entropy (`label_smoothing`) kaybı ve Warmup + Cosine Annealing öğrenme oranı zamanlayıcısı.

4. **`hardware_profiler.py`**:
   - FP32 (4B), FP16 (2B), INT8 (1B), INT4 (0.5B) formatlarında ağırlık ve KV önbellek bellek hesaplayıcısı.
   - Donanım Roofline Modeli analizi: Aritmetik Yoğunluk (FLOPs/Byte) ve Diz Darboğaz Noktası ($I_{knee}$) ile Bellek-Bant-Genişliği Bağımlı vs. Hesaplama Bağımlı rejim tespiti.
   - 6 aday SLM (Qwen2.5-0.5B, SmolLM2-360M, TinyLlama-1.1B, Qwen2.5-1.5B, Llama-3.2-1B, MerinosNanoLLM-32M) kıyaslama ve skorlama matrisi.

5. **`visualizer.py`**:
   - 300 DPI 2x2 Master Teşhis Paneli (`llm_profiling_diagnostic_panel.png`).

---

## 🚀 CLI Kullanımı

### 1. OEE Duruş Maliyeti & Kaybedilen Metrekare Hesabı
```bash
python -m day29.mini_project.src.cli oee-calc --downtime 45 --spare-code MRP-RAP-101
```

### 2. ERP Yedek Parça & Kritik Stok Sorgulama (MRP-*)
```bash
python -m day29.mini_project.src.cli spare-part --code MRP-EXT-412
```

### 3. Halı Desinatörü CAD Çizim & Reçete Hesaplama
```bash
python -m day29.mini_project.src.cli design-calc --reed 700 --pick 1200 --colors 8 --relief --relief-depth 3.5
```

### 4. Akredite Kalite Kontrol & Laboratuvar TSE/ISO Denetimi
```bash
python -m day29.mini_project.src.cli quality-audit --gsm-actual 2420 --gsm-target 2400 --tuft-lock 28.5 --rubbing 4.5 --light 6.5
```

### 5. Aday SLM Kıyaslama ve Raporlama (Grafikli)
```bash
python -m day29.mini_project.src.cli benchmark --hardware rtx_4060_8gb --precision INT4 --plot
```

### 4. Tekil Model Donanım Profillemesi
```bash
python -m day29.mini_project.src.cli profile --hardware rtx_4060_8gb --model-id qwen2.5-0.5b
```

### 5. Özel Nano-LLM ile Otoregresif Üretim
```bash
python -m day29.mini_project.src.cli generate --prompt "[ATKI] kopma sensoru alarm verdi" --max-new-tokens 20
```

### 6. Çatılar Arası Eşdeğerlik Kataloğu
```bash
python -m day29.mini_project.src.cli compare-backends
```

---

## 🧪 Testleri Çalıştırma

```bash
pytest day29/mini_project/tests/test_llm_engineering.py -v
```

---

## 📄 Lisans
Bu modül, Merinos Halı Sanayi ve Ticaret A.Ş. staj müfredatı kapsamında geliştirilmiştir. Tüm hakları saklıdır (All Rights Reserved).
Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas).
