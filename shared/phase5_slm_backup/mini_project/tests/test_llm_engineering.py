"""
Merinos Industrial AI Internship - Day 29
Comprehensive Test Suite for LLM Engineering, Custom NLP Engine & Hardware Profiling.
Covers Transformer Decoder, MoE, Shared Experts, KV Cache, GQA, RoPE, RMSNorm,
Hardware Profiling and Cross-Framework Functional Mechanics.
"""

from pathlib import Path
import pytest
import torch
import torch.nn.functional as F

from day29.mini_project.src.custom_nlp_engine import (
    CausalSelfAttention,
    MerinosBPETokenizer,
    MerinosCausalLM,
    MoEFeedForward,
    RMSNorm,
    RotaryEmbedding,
    SwiGLUFFN,
    TransformerBlock,
)
from day29.mini_project.src.expert_agent import MerinosTextileExpertEngine
from day29.mini_project.src.functional_backend import (
    FRAMEWORK_EQUIVALENCE_CATALOG,
    FunctionalEquivalenceEngine,
)
from day29.mini_project.src.hardware_profiler import HardwareProfiler
from day29.mini_project.src.models import ModelCandidateSpec, NanoLLMConfig


@pytest.fixture
def tokenizer() -> MerinosBPETokenizer:
    return MerinosBPETokenizer(vocab_size=1024)


@pytest.fixture
def nano_config() -> NanoLLMConfig:
    return NanoLLMConfig(
        vocab_size=1024,
        d_model=96,
        n_heads=4,
        n_kv_heads=2,  # GQA 2:1
        n_layers=2,
        intermediate_size=256,
        max_seq_len=128,
        dropout=0.0,
        use_moe=False,
        enable_kv_cache=True
    )


@pytest.fixture
def moe_config() -> NanoLLMConfig:
    return NanoLLMConfig(
        vocab_size=1024,
        d_model=96,
        n_heads=4,
        n_kv_heads=2,
        n_layers=2,
        intermediate_size=256,
        max_seq_len=128,
        dropout=0.0,
        use_moe=True,
        num_experts=4,
        num_experts_per_tok=2,
        use_shared_expert=True,
        aux_loss_coef=0.01,
        attention_logit_soft_capping=30.0
    )


@pytest.fixture
def profiler() -> HardwareProfiler:
    return HardwareProfiler()


# ---------------------------------------------------------------------------
# Test 1: MerinosBPETokenizer Special Tokens and Domain Vocabulary
# ---------------------------------------------------------------------------
def test_merinos_bpe_tokenizer(tokenizer: MerinosBPETokenizer) -> None:
    text = "[ATKI] kopma tespit edildi dokuma tezgah durdu [ARIZA]"
    tokens = tokenizer.encode(text, add_special_tokens=True)

    assert tokens[0] == tokenizer.bos_id
    assert tokens[-1] == tokenizer.eos_id
    assert tokenizer.token_to_id["[ATKI]"] in tokens
    assert tokenizer.token_to_id["[ARIZA]"] in tokens

    decoded = tokenizer.decode(tokens, skip_special_tokens=False)
    assert "[ATKI]" in decoded
    assert "[ARIZA]" in decoded
    assert "kopma" in decoded or "dokuma" in decoded


# ---------------------------------------------------------------------------
# Test 2: Rotary Positional Embedding (RoPE) Mechanics
# ---------------------------------------------------------------------------
def test_rotary_embedding_rope() -> None:
    dim = 32
    seq_len = 16
    batch_size = 2
    n_heads = 4

    rope = RotaryEmbedding(dim=dim, max_position_embeddings=128)
    q = torch.randn(batch_size, n_heads, seq_len, dim)
    k = torch.randn(batch_size, n_heads, seq_len, dim)

    q_rot, k_rot = rope(q, k, seq_len=seq_len)

    assert q_rot.shape == q.shape
    assert k_rot.shape == k.shape
    assert not torch.allclose(q_rot, q)
    assert torch.isfinite(q_rot).all()
    assert torch.isfinite(k_rot).all()


# ---------------------------------------------------------------------------
# Test 3: RMSNorm Output Normalization & Stability
# ---------------------------------------------------------------------------
def test_rms_norm() -> None:
    hidden_size = 64
    norm = RMSNorm(hidden_size=hidden_size)

    x = torch.randn(4, 12, hidden_size) * 5.0 + 2.0
    y = norm(x)

    assert y.shape == x.shape
    rms = torch.sqrt(torch.mean(y ** 2, dim=-1))
    assert torch.allclose(rms, torch.ones_like(rms), atol=1e-2)


# ---------------------------------------------------------------------------
# Test 4: SwiGLU Gated Feed-Forward Network
# ---------------------------------------------------------------------------
def test_swiglu_ffn() -> None:
    hidden_size = 64
    intermediate_size = 128
    ffn = SwiGLUFFN(hidden_size=hidden_size, intermediate_size=intermediate_size)

    x = torch.randn(2, 8, hidden_size)
    out = ffn(x)

    assert out.shape == (2, 8, hidden_size)
    assert torch.isfinite(out).all()


# ---------------------------------------------------------------------------
# Test 5: Causal Self-Attention with GQA & Causal Masking
# ---------------------------------------------------------------------------
def test_causal_self_attention_gqa_mask(nano_config: NanoLLMConfig) -> None:
    attn = CausalSelfAttention(nano_config)
    x = torch.randn(2, 10, nano_config.d_model)

    out, _ = attn(x)
    assert out.shape == (2, 10, nano_config.d_model)

    # Test causality: altering future tokens does not affect past token representations
    x1 = torch.randn(1, 8, nano_config.d_model)
    x2 = x1.clone()
    x2[:, 5:, :] = torch.randn(1, 3, nano_config.d_model)

    attn.eval()
    with torch.no_grad():
        out1, _ = attn(x1)
        out2, _ = attn(x2)

    assert torch.allclose(out1[:, :5, :], out2[:, :5, :], atol=1e-5)


# ---------------------------------------------------------------------------
# Test 6: TransformerBlock Residual Connections and Gradient Flow
# ---------------------------------------------------------------------------
def test_transformer_block_residual(nano_config: NanoLLMConfig) -> None:
    block = TransformerBlock(nano_config)
    x = torch.randn(2, 6, nano_config.d_model, requires_grad=True)

    out, _, aux_loss = block(x)
    assert out.shape == x.shape
    assert aux_loss.item() == 0.0

    loss = out.sum()
    loss.backward()
    assert x.grad is not None
    assert torch.isfinite(x.grad).all()


# ---------------------------------------------------------------------------
# Test 7: MerinosCausalLM Forward Pass & CrossEntropy Loss
# ---------------------------------------------------------------------------
def test_merinos_causal_lm_forward_and_loss(nano_config: NanoLLMConfig) -> None:
    model = MerinosCausalLM(nano_config)
    batch_size = 2
    seq_len = 12

    input_ids = torch.randint(0, nano_config.vocab_size, (batch_size, seq_len))
    targets = torch.randint(0, nano_config.vocab_size, (batch_size, seq_len))

    logits, loss, present_kvs, aux = model(input_ids, targets=targets)

    assert logits.shape == (batch_size, seq_len, nano_config.vocab_size)
    assert loss is not None
    assert loss.item() > 0.0
    assert torch.isfinite(loss)
    assert present_kvs is not None
    assert len(present_kvs) == nano_config.n_layers


# ---------------------------------------------------------------------------
# Test 8: Autoregressive Next-Token Generation Loop (KV Cached)
# ---------------------------------------------------------------------------
def test_merinos_causal_lm_autoregressive_generation(nano_config: NanoLLMConfig) -> None:
    model = MerinosCausalLM(nano_config)
    prompt_ids = [10, 25, 42]
    max_new = 5

    generated = model.generate(
        prompt_tokens=prompt_ids,
        max_new_tokens=max_new,
        temperature=0.0,
        use_cache=True
    )

    assert len(generated) == len(prompt_ids) + max_new
    assert generated[: len(prompt_ids)] == prompt_ids


# ---------------------------------------------------------------------------
# Test 9: Hardware Profiler VRAM Footprint & KV Cache Calculations
# ---------------------------------------------------------------------------
def test_hardware_profiler_vram_and_kv_cache(profiler: HardwareProfiler) -> None:
    params_b = 0.50

    vram_fp32 = profiler.calculate_weights_memory_gb(params_b, "FP32")
    vram_fp16 = profiler.calculate_weights_memory_gb(params_b, "FP16")
    vram_int8 = profiler.calculate_weights_memory_gb(params_b, "INT8")
    vram_int4 = profiler.calculate_weights_memory_gb(params_b, "INT4")

    assert pytest.approx(vram_fp32, rel=1e-2) == 1.862
    assert pytest.approx(vram_fp16, rel=1e-2) == 0.931
    assert pytest.approx(vram_int8, rel=1e-2) == 0.465
    assert pytest.approx(vram_int4, rel=1e-2) == 0.233

    kv_mha = profiler.calculate_kv_cache_memory_mb(
        n_layers=12, n_kv_heads=8, d_model=512, n_heads=8, seq_len=1000, batch_size=1, precision="FP16"
    )
    kv_gqa = profiler.calculate_kv_cache_memory_mb(
        n_layers=12, n_kv_heads=2, d_model=512, n_heads=8, seq_len=1000, batch_size=1, precision="FP16"
    )
    assert pytest.approx(kv_gqa * 4.0, rel=1e-3) == kv_mha


# ---------------------------------------------------------------------------
# Test 10: Roofline Bottleneck Analysis & SLM Benchmark Ranking
# ---------------------------------------------------------------------------
def test_roofline_and_benchmark_ranking(profiler: HardwareProfiler) -> None:
    roofline_decoding = profiler.analyze_roofline("rtx_4060_8gb", operational_intensity=1.5)
    assert roofline_decoding.operational_regime == "memory_bound"

    roofline_training = profiler.analyze_roofline("rtx_4060_8gb", operational_intensity=1200.0)
    assert roofline_training.operational_regime == "compute_bound"

    benchmark = profiler.benchmark_all_candidates(hardware_id="rtx_4060_8gb", preferred_precision="INT4")
    assert "candidates_ranked" in benchmark
    assert len(benchmark["candidates_ranked"]) > 0
    assert benchmark["selected_slm"] is not None

    catalog = FunctionalEquivalenceEngine.get_catalog()
    assert len(catalog) >= 8
    assert all(item.pytorch_syntax != "" for item in catalog)


# ---------------------------------------------------------------------------
# Test 11: Sparse Mixture of Experts (MoE) Routing & Auxiliary Loss
# ---------------------------------------------------------------------------
def test_moe_feedforward_routing_and_aux_loss(moe_config: NanoLLMConfig) -> None:
    moe_layer = MoEFeedForward(moe_config)
    x = torch.randn(2, 8, moe_config.d_model, requires_grad=True)

    out, aux_loss = moe_layer(x)

    assert out.shape == (2, 8, moe_config.d_model)
    assert aux_loss is not None
    assert aux_loss.item() > 0.0
    assert torch.isfinite(aux_loss)

    # Test backprop through MoE router and experts
    total_loss = out.sum() + moe_config.aux_loss_coef * aux_loss
    total_loss.backward()
    assert x.grad is not None
    assert torch.isfinite(x.grad).all()


# ---------------------------------------------------------------------------
# Test 12: Fast KV Cache Generation Equivalence
# ---------------------------------------------------------------------------
def test_kv_cache_generation_equivalence(nano_config: NanoLLMConfig) -> None:
    model = MerinosCausalLM(nano_config)
    model.eval()

    prompt_ids = [5, 12, 33]
    max_new = 6

    # Greedy generation with cache
    torch.manual_seed(42)
    gen_cached = model.generate(prompt_ids, max_new_tokens=max_new, temperature=0.0, use_cache=True)

    # Greedy generation without cache
    torch.manual_seed(42)
    gen_uncached = model.generate(prompt_ids, max_new_tokens=max_new, temperature=0.0, use_cache=False)

    # Both approaches must generate identical tokens
    assert gen_cached == gen_uncached
    assert len(gen_cached) == len(prompt_ids) + max_new


# ---------------------------------------------------------------------------
# Test 13: Attention Logit Soft-Capping (Gemma-2 Style)
# ---------------------------------------------------------------------------
def test_attention_logit_soft_capping(moe_config: NanoLLMConfig) -> None:
    attn = CausalSelfAttention(moe_config)
    assert attn.soft_cap == 30.0

    x = torch.randn(1, 6, moe_config.d_model)
    out, present_kv = attn(x)

    assert out.shape == (1, 6, moe_config.d_model)
    assert present_kv is not None
    assert present_kv[0].shape == (1, moe_config.n_kv_heads, 6, moe_config.d_model // moe_config.n_heads)


# ---------------------------------------------------------------------------
# Test 14: Textile Expert Lexicon & Factory SOP Lookup
# ---------------------------------------------------------------------------
def test_textile_expert_lexicon_and_sop_lookup() -> None:
    engine = MerinosTextileExpertEngine()

    # Terminology lookup
    jakar_def = engine.lookup_term("jakar")
    assert jakar_def is not None
    assert "desen" in jakar_def.lower() or "elektronik" in jakar_def.lower()

    bcf_def = engine.lookup_term("bcf")
    assert bcf_def is not None
    assert "iplik" in bcf_def.lower() or "filament" in bcf_def.lower()

    ramoz_def = engine.lookup_term("ramöz")
    assert ramoz_def is not None
    assert "fırın" in ramoz_def.lower() or "fikse" in ramoz_def.lower()

    # SOP lookup by industrial fault code
    sop_atk = engine.find_sop_by_fault_code("ERR-ATK-01")
    assert sop_atk is not None
    assert "Dokuma" in sop_atk["department"]
    assert "rapyer" in sop_atk["fault"]["maintenance_sop"].lower()

    sop_ram = engine.find_sop_by_fault_code("ERR-RAM-08")
    assert sop_ram is not None
    assert "pt100" in sop_ram["fault"]["maintenance_sop"].lower() or "kalibratör" in sop_ram["fault"]["maintenance_sop"].lower()

    # Non-existent code returns None
    assert engine.find_sop_by_fault_code("ERR-XYZ-999") is None


# ---------------------------------------------------------------------------
# Test 15: Subsystem Expert MoE Routing & Industrial Safety Gate
# ---------------------------------------------------------------------------
def test_expert_routing_and_safety_gate() -> None:
    engine = MerinosTextileExpertEngine()

    # Department to MoE Expert ID mapping
    assert engine.route_to_subsystem_expert("DOKUMA")[0] == 0
    assert engine.route_to_subsystem_expert("IPLIK_BCF")[0] == 1
    assert engine.route_to_subsystem_expert("RAMOZ_TERBIYE")[0] == 2
    assert engine.route_to_subsystem_expert("MEKATRONIK_PLC")[0] == 3

    # Safety Gate Check 1: LOTO (Lockout / Tagout) violation
    unsafe_plan = "Motor milini kontrol et ve zinciri gerdir"
    is_safe, violations = engine.validate_safety(unsafe_plan)
    assert not is_safe
    assert any("enerji" in v.lower() or "durdurma" in v.lower() for v in violations)

    # Safety Gate Check 2: Ramöz over-temperature violation (> 210°C)
    is_safe_temp, violations_temp = engine.validate_safety(
        plan="Tezgahı acil durdurma emniyetine al ve sıcaklığı sabit tut",
        parameters={"temperature_c": 225.0}
    )
    assert not is_safe_temp
    assert any("sıcaklığı" in v.lower() for v in violations_temp)

    # Safety Gate Check 3: Extruder melt over-pressure violation (> 180 bar)
    is_safe_pres, violations_pres = engine.validate_safety(
        plan="Tezgahı acil durdurma emniyetine al ve basıncı düşür",
        parameters={"pressure_bar": 195.0}
    )
    assert not is_safe_pres
    assert any("basıncı" in v.lower() for v in violations_pres)

    # Safety Gate Check 4: Safe, compliant maintenance action
    safe_plan = "Tezgahı acil durdurma butonuna basarak enerjiyi kes. Rapyer kıskacını temizle ve sıfırla."
    is_safe_ok, violations_ok = engine.validate_safety(
        safe_plan,
        parameters={"temperature_c": 170.0, "pressure_bar": 130.0}
    )
    assert is_safe_ok
    assert len(violations_ok) == 0


# ---------------------------------------------------------------------------
# Test 16: Domain Adaptation Training Loop & End-to-End Diagnostic Pipeline
# ---------------------------------------------------------------------------
def test_domain_adaptation_training_and_diagnose() -> None:
    # Use compact config for fast test convergence
    quick_config = NanoLLMConfig(
        vocab_size=1024,
        d_model=64,
        n_heads=4,
        n_kv_heads=2,
        n_layers=2,
        intermediate_size=128,
        max_seq_len=128,
        use_moe=True,
        num_experts=4,
        num_experts_per_tok=2,
        use_shared_expert=True
    )
    engine = MerinosTextileExpertEngine(config=quick_config)

    # Run quick domain adaptation
    train_res = engine.train_domain_adaptation(epochs=3, learning_rate=3e-3)
    assert train_res["epochs"] == 3
    assert train_res["samples_trained"] > 0
    assert train_res["final_loss"] < train_res["initial_loss"]
    assert train_res["loss_reduction_pct"] > 5.0

    # End-to-end diagnostic pipeline with known fault code (grounded SOP)
    res_grounded = engine.diagnose_fault(
        machine="Van de Wiele RCE02",
        symptom="Atkı teli kopması",
        department="DOKUMA",
        fault_code="ERR-ATK-01"
    )
    assert res_grounded["machine"] == "Van de Wiele RCE02"
    assert res_grounded["assigned_expert"]["expert_id"] == 0
    assert res_grounded["confidence_score"] == 0.98
    assert res_grounded["safety_audit"]["passed"] is True
    assert "[ARIZA]" in res_grounded["prompt_formatted"]
    assert "[COZUM]" in res_grounded["prompt_formatted"]

    # End-to-end diagnostic pipeline with safety violation caught
    res_violation = engine.diagnose_fault(
        machine="Brückner Ramöz",
        symptom="Aşırı fırın harareti",
        department="RAMOZ_TERBIYE",
        parameters={"temperature_c": 230.0}
    )
    assert res_violation["assigned_expert"]["expert_id"] == 2
    assert res_violation["safety_audit"]["passed"] is False
    assert len(res_violation["safety_audit"]["violations"]) > 0


# ---------------------------------------------------------------------------
# Test 17: Carpet Pattern Designer Lexicon, SOPs & Design Tokens
# ---------------------------------------------------------------------------
def test_carpet_designer_lexicon_and_sop() -> None:
    engine = MerinosTextileExpertEngine()

    # Pattern design glossary lookup
    raport_def = engine.lookup_term("raport")
    assert raport_def is not None
    assert "tekrar" in raport_def.lower() or "periyodik" in raport_def.lower()

    rolyef_def = engine.lookup_term("rolyef")
    assert rolyef_def is not None
    assert "derinlik" in rolyef_def.lower() or "kabartma" in rolyef_def.lower()

    tarak_def = engine.lookup_term("tarak_sikligi")
    assert tarak_def is not None
    assert "dis" in tarak_def.lower() or "cozgu" in tarak_def.lower() or "metre" in tarak_def.lower()

    ratio_def = engine.lookup_term("aspect_ratio")
    assert ratio_def is not None
    assert "piksel" in ratio_def.lower() or "oran" in ratio_def.lower()

    # Design SOP retrieval by industrial fault code
    sop_creel = engine.find_sop_by_fault_code("ERR-DES-01")
    assert sop_creel is not None
    assert "Desen" in sop_creel["department"]
    assert "stippling" in sop_creel["fault"]["maintenance_sop"].lower() or "palet" in sop_creel["fault"]["maintenance_sop"].lower()

    sop_aspect = engine.find_sop_by_fault_code("ERR-DES-02")
    assert sop_aspect is not None
    assert "aspect ratio" in sop_aspect["fault"]["maintenance_sop"].lower() or "oran" in sop_aspect["fault"]["maintenance_sop"].lower()

    sop_relief = engine.find_sop_by_fault_code("ERR-DES-03")
    assert sop_relief is not None
    assert "armur" in sop_relief["fault"]["maintenance_sop"].lower() or "kilit" in sop_relief["fault"]["maintenance_sop"].lower()

    # Tokenizer encoding of design tokens
    des_tokens = engine.tokenizer.encode("[DESEN] [CIZIM] [TARAK] 700 [ROLYEF] [CAD_EP]", add_special_tokens=False)
    assert engine.tokenizer.token_to_id["[DESEN]"] in des_tokens
    assert engine.tokenizer.token_to_id["[CIZIM]"] in des_tokens
    assert engine.tokenizer.token_to_id["[ROLYEF]"] in des_tokens


# ---------------------------------------------------------------------------
# Test 18: CAD Design Spec Analysis, Aspect Ratio & MoE Expert 4 Routing
# ---------------------------------------------------------------------------
def test_design_spec_analysis_and_expert_routing() -> None:
    engine = MerinosTextileExpertEngine()

    # Subsystem expert routing for design department
    exp_id, exp_title = engine.route_to_subsystem_expert("DESEN_TASARIM")
    assert exp_id == 4
    assert "Desinatörlüğü" in exp_title or "CAD" in exp_title

    # CAD drafting spec calculation: 700 tarak, 1200 atkı, 8 renk
    spec = engine.analyze_design_spec(
        reed_density=700,
        pick_density_per_m=1200,
        colors_count=8,
        width_m=2.0,
        height_m=3.0,
        max_creel_colors=8
    )
    assert spec["point_density_sqm"] == 1680000
    assert spec["pixel_aspect_ratio"] == 1.714
    assert spec["total_points_carpet"] == 10080000
    assert spec["total_reed_dents"] == 1400
    assert spec["total_picks"] == 3600
    assert spec["design_audit"]["passed"] is True

    # CAD drafting rule violation: 10 colors on 8-color creel
    spec_creel_overflow = engine.analyze_design_spec(
        reed_density=700,
        pick_density_per_m=1200,
        colors_count=10,
        max_creel_colors=8
    )
    assert spec_creel_overflow["design_audit"]["passed"] is False
    assert any("cağlık" in w.lower() for w in spec_creel_overflow["design_audit"]["warnings"])

    # CAD drafting rule violation: Excessive 3D relief depth (> 4.5 mm)
    spec_relief_overflow = engine.analyze_design_spec(
        reed_density=700,
        pick_density_per_m=1200,
        colors_count=8,
        is_relief=True,
        relief_depth_mm=5.5
    )
    assert spec_relief_overflow["design_audit"]["passed"] is False
    assert any("rölyef" in w.lower() for w in spec_relief_overflow["design_audit"]["warnings"])

    # Design prompt formatting
    prompt = engine.format_design_prompt("Modern Geometrik", 700, 1200, 8, has_relief=True)
    assert "[DESEN]" in prompt
    assert "[CIZIM]" in prompt
    assert "[TARAK]" in prompt
    assert "[ROLYEF]" in prompt


# ---------------------------------------------------------------------------
# Test 19: Quality Control & Testing Lab Lexicon, SOPs & Standards Tokens
# ---------------------------------------------------------------------------
def test_quality_lab_lexicon_and_sops() -> None:
    engine = MerinosTextileExpertEngine()

    # Quality and testing glossary lookup
    tse_def = engine.lookup_term("tse_2104")
    assert tse_def is not None
    assert "2104" in tse_def
    assert "ağırlığı" in tse_def.lower() or "gramaj" in tse_def.lower() or "mekanik" in tse_def.lower()

    tuft_def = engine.lookup_term("tuft_lock_mukavemeti")
    assert tuft_def is not None
    assert "4919" in tuft_def or "25" in tuft_def or "kuvvet" in tuft_def.lower()

    mart_def = engine.lookup_term("martindale_asinma")
    assert mart_def is not None
    assert "aşınma" in mart_def.lower() or "50.000" in mart_def or "sürtünme" in mart_def.lower()

    oeko_def = engine.lookup_term("oeko_tex")
    assert oeko_def is not None
    assert "standard 100" in oeko_def.lower() or "ekoloji" in oeko_def.lower() or "formaldehit" in oeko_def.lower()

    gsm_def = engine.lookup_term("gsm_gramaj")
    assert gsm_def is not None
    assert "g/m²" in gsm_def or "metrekare" in gsm_def.lower()

    # Quality laboratory SOP retrieval by fault code
    sop_tuft = engine.find_sop_by_fault_code("ERR-KAL-01")
    assert sop_tuft is not None
    assert "Laboratuvar" in sop_tuft["department"] or "Kalite" in sop_tuft["department"]
    assert "165°c" in sop_tuft["fault"]["maintenance_sop"].lower() or "viskozite" in sop_tuft["fault"]["maintenance_sop"].lower()

    sop_gsm = engine.find_sop_by_fault_code("ERR-KAL-02")
    assert sop_gsm is not None
    assert "100 cm²" in sop_gsm["fault"]["maintenance_sop"] or "kesici" in sop_gsm["fault"]["maintenance_sop"]

    sop_fast = engine.find_sop_by_fault_code("ERR-KAL-03")
    assert sop_fast is not None
    assert "d65" in sop_fast["fault"]["maintenance_sop"].lower() or "fikse" in sop_fast["fault"]["maintenance_sop"].lower()

    sop_oeko = engine.find_sop_by_fault_code("ERR-KAL-04")
    assert sop_oeko is not None
    assert "voc" in sop_oeko["fault"]["maintenance_sop"].lower() or "egzoz" in sop_oeko["fault"]["maintenance_sop"].lower()

    # Tokenizer encoding of quality tokens
    qual_tokens = engine.tokenizer.encode("[KALITE] [TEST_LAB] [GRAMAJ] 2400 [HASLIK] [TSE_STANDART]", add_special_tokens=False)
    assert engine.tokenizer.token_to_id["[KALITE]"] in qual_tokens
    assert engine.tokenizer.token_to_id["[TEST_LAB]"] in qual_tokens
    assert engine.tokenizer.token_to_id["[GRAMAJ]"] in qual_tokens
    assert engine.tokenizer.token_to_id["[HASLIK]"] in qual_tokens
    assert engine.tokenizer.token_to_id["[TSE_STANDART]"] in qual_tokens


# ---------------------------------------------------------------------------
# Test 20: Carpet Quality Audit, TSE 2104 Tolerance & Laboratory Verification
# ---------------------------------------------------------------------------
def test_carpet_quality_audit_and_tolerance() -> None:
    engine = MerinosTextileExpertEngine()

    # Routing for KALITE_LABORATUVAR department
    exp_id, exp_title = engine.route_to_subsystem_expert("KALITE_LABORATUVAR")
    assert exp_id == 2
    assert "Kalite" in exp_title or "Laboratuvarı" in exp_title

    # Compliant carpet audit: Target 2400, Actual 2420 (+0.83% within ±5%)
    res_compliant = engine.audit_carpet_quality(
        gsm_actual=2420.0,
        gsm_target=2400.0,
        tuft_lock_newton=28.5,
        rubbing_fastness=4.5,
        light_fastness=6.5,
        martindale_cycles=55000,
        oeko_tex_certified=True
    )
    assert res_compliant["overall_passed"] is True
    assert res_compliant["metrics"]["gsm_deviation_pct"] == 0.83
    assert res_compliant["compliance_flags"]["tse_2104_passed"] is True
    assert res_compliant["compliance_flags"]["iso_4919_passed"] is True
    assert res_compliant["compliance_flags"]["iso_105_rubbing_passed"] is True
    assert res_compliant["compliance_flags"]["iso_105_light_passed"] is True
    assert res_compliant["compliance_flags"]["oeko_tex_passed"] is True
    assert len(res_compliant["violations"]) == 0
    assert "ONAYLANDI" in res_compliant["audit_verdict"]

    # Non-compliant carpet: GSM overflow (+8.33% > 5%)
    res_gsm_overflow = engine.audit_carpet_quality(
        gsm_actual=2600.0,
        gsm_target=2400.0,
        tuft_lock_newton=28.0
    )
    assert res_gsm_overflow["overall_passed"] is False
    assert res_gsm_overflow["compliance_flags"]["tse_2104_passed"] is False
    assert any("tse 2104" in v.lower() for v in res_gsm_overflow["violations"])

    # Non-compliant carpet: Tuft-lock failure (< 25 N)
    res_tuft_fail = engine.audit_carpet_quality(
        gsm_actual=2400.0,
        gsm_target=2400.0,
        tuft_lock_newton=18.5
    )
    assert res_tuft_fail["overall_passed"] is False
    assert res_tuft_fail["compliance_flags"]["iso_4919_passed"] is False
    assert any("iso 4919" in v.lower() for v in res_tuft_fail["violations"])
    assert any("tuft-lock" in ca.lower() for ca in res_tuft_fail["corrective_actions"])

    # Non-compliant carpet: Rubbing fastness failure (< 3.0)
    res_fast_fail = engine.audit_carpet_quality(
        gsm_actual=2400.0,
        gsm_target=2400.0,
        tuft_lock_newton=26.0,
        rubbing_fastness=2.0
    )
    assert res_fast_fail["overall_passed"] is False
    assert res_fast_fail["compliance_flags"]["iso_105_rubbing_passed"] is False
    assert any("iso 105" in v.lower() or "hasl" in v.lower() for v in res_fast_fail["violations"])

    # Non-compliant carpet: OEKO-TEX uncertified
    res_oeko_fail = engine.audit_carpet_quality(
        gsm_actual=2400.0,
        gsm_target=2400.0,
        tuft_lock_newton=26.0,
        oeko_tex_certified=False
    )
    assert res_oeko_fail["overall_passed"] is False
    assert res_oeko_fail["compliance_flags"]["oeko_tex_passed"] is False
    assert any("oeko-tex" in v.lower() for v in res_oeko_fail["violations"])


# ---------------------------------------------------------------------------
# Test 21: OEE & ERP Spare Parts Lexicon, Special Tokens & MRP Lookup
# ---------------------------------------------------------------------------
def test_oee_and_spare_parts_lexicon_lookup() -> None:
    engine = MerinosTextileExpertEngine()

    # 1. Technical glossary terms lookup
    oee_def = engine.lookup_term("oee_kullanilabilirlik")
    assert oee_def is not None
    assert "kullanılabilirlik" in oee_def.lower() or "duruş" in oee_def.lower() or "availability" in oee_def.lower()

    cost_def = engine.lookup_term("durus_maliyeti")
    assert cost_def is not None
    assert "m²" in cost_def or "kayıp" in cost_def.lower() or "genel gider" in cost_def.lower()

    mrp_def = engine.lookup_term("mrp_kodlama")
    assert mrp_def is not None
    assert "mrp" in mrp_def.lower() or "yedek parça" in mrp_def.lower()

    stock_def = engine.lookup_term("kritik_stok_seviyesi")
    assert stock_def is not None
    assert "emniyet" in stock_def.lower() or "tedarik" in stock_def.lower()

    sqm_def = engine.lookup_term("kaybedilen_metrekare")
    assert sqm_def is not None
    assert "çift parça" in sqm_def.lower() or "devir" in sqm_def.lower() or "yüzey alanı" in sqm_def.lower()

    rop_def = engine.lookup_term("reorder_point")
    assert rop_def is not None
    assert "yeniden sipariş" in rop_def.lower() or "rop" in rop_def.lower()

    # 2. Tokenizer encoding of OEE and ERP tokens
    tokens = engine.tokenizer.encode("[OEE] [DURUS] [VARDIYA] 1 [YEDEK_PARCA] [STOK_MRP] MRP-RAP-101", add_special_tokens=False)
    assert engine.tokenizer.token_to_id["[OEE]"] in tokens
    assert engine.tokenizer.token_to_id["[DURUS]"] in tokens
    assert engine.tokenizer.token_to_id["[VARDIYA]"] in tokens
    assert engine.tokenizer.token_to_id["[YEDEK_PARCA]"] in tokens
    assert engine.tokenizer.token_to_id["[STOK_MRP]"] in tokens

    # 3. Department routing & prompt formatting
    exp_id_erp, title_erp = engine.route_to_subsystem_expert("PLANLAMA_ERP")
    assert exp_id_erp == 1
    assert "Planlama" in title_erp or "ERP" in title_erp

    exp_id_bak, title_bak = engine.route_to_subsystem_expert("BAKIM_ONARIM")
    assert exp_id_bak == 0
    assert "Bakım" in title_bak

    prompt_erp = engine.format_fault_prompt(
        symptom="Kritik emniyet stoku tükenmek üzere",
        machine="Ambar Merkez",
        department="PLANLAMA_ERP",
        parameters="MRP-RAP-101",
        priority="CRITICAL"
    )
    assert "[STOK_MRP]" in prompt_erp
    assert "[ONCELIK_KRITIK]" in prompt_erp

    # 4. Spare parts catalog query (MRP-RAP-101, MRP-EXT-412, MRP-RAM-508)
    rapier_part = engine.query_spare_part("MRP-RAP-101")
    assert rapier_part["found"] is True
    assert rapier_part["machine"] == "Van de Wiele RCE02 / VTR23"
    assert rapier_part["current_stock"] == 2
    assert rapier_part["critical_threshold"] == 3
    assert rapier_part["replenishment_status"] == "CRITICAL_LOW_STOCK"
    assert rapier_part["action_code"] == "REORDER_URGENT"
    assert rapier_part["lead_time_days"] == 14
    assert rapier_part["safety_audit"]["passed"] is False
    assert any("kritik stok" in w.lower() for w in rapier_part["safety_audit"]["warnings"])

    filter_part = engine.query_spare_part("MRP-EXT-412")
    assert filter_part["found"] is True
    assert filter_part["machine"] == "Neumag S+ BCF Ekstrüzyon"
    assert filter_part["current_stock"] == 3
    assert filter_part["critical_threshold"] == 4
    assert filter_part["replenishment_status"] == "CRITICAL_LOW_STOCK"

    ramoz_part = engine.query_spare_part("MRP-RAM-508")
    assert ramoz_part["found"] is True
    assert ramoz_part["current_stock"] == 12
    assert ramoz_part["critical_threshold"] == 6
    assert ramoz_part["replenishment_status"] == "OPTIMAL_STOCK"
    assert ramoz_part["safety_audit"]["passed"] is True

    # Non-existent part code
    unknown_part = engine.query_spare_part("MRP-NONEXISTENT-999")
    assert unknown_part["found"] is False
    assert "bulunamadı" in unknown_part["error"]


# ---------------------------------------------------------------------------
# Test 22: OEE Downtime Loss Calculation, Area Loss & Financial Audit
# ---------------------------------------------------------------------------
def test_oee_downtime_calculation_and_stock_alert() -> None:
    engine = MerinosTextileExpertEngine()

    # 1. Baseline 45-minute downtime on double face-to-face loom
    # v = 165 / 1200 = 0.1375 m/min
    # sqm_rate = 0.1375 * 4.0 * 2 = 1.10 m²/min
    # lost_sqm = 1.10 * 45 = 49.50 m²
    # carpet_loss = 49.50 * 450 = 22,275.00 TL
    # overhead = (45 / 60) * 1850 = 1,387.50 TL
    # total = 23,662.50 TL
    # availability = (435 / 480) * 100 = 90.62%
    res = engine.calculate_oee_and_downtime_loss(
        downtime_minutes=45.0,
        loom_speed_rpm=165.0,
        pick_density_per_m=1200,
        fabric_width_m=4.0,
        planned_shift_minutes=480.0,
        carpet_unit_cost_tl_sqm=450.0,
        hourly_overhead_tl=1850.0,
        is_double_piece=True
    )

    assert res["downtime_minutes"] == 45.0
    assert res["planned_shift_minutes"] == 480.0
    assert res["operating_minutes"] == 435.0
    assert res["oee_availability_pct"] == 90.62
    assert res["production_rate"]["linear_speed_m_per_min"] == 0.1375
    assert res["production_rate"]["sqm_per_min"] == 1.10
    assert res["loss_metrics"]["lost_carpet_sqm"] == 49.50
    assert res["loss_metrics"]["carpet_loss_cost_tl"] == 22275.00
    assert res["loss_metrics"]["overhead_cost_tl"] == 1387.50
    assert res["loss_metrics"]["spare_part_cost_tl"] == 0.0
    assert res["loss_metrics"]["total_financial_loss_tl"] == 23662.50
    assert res["audit"]["passed"] is True

    # 2. Downtime with spare part consumption (MRP-RAP-101: 18,500 TL)
    res_with_part = engine.calculate_oee_and_downtime_loss(
        downtime_minutes=45.0,
        spare_part_code="MRP-RAP-101"
    )
    assert res_with_part["loss_metrics"]["spare_part_cost_tl"] == 18500.00
    assert res_with_part["loss_metrics"]["total_financial_loss_tl"] == 42162.50
    assert res_with_part["spare_part_analysis"]["found"] is True
    assert res_with_part["spare_part_analysis"]["part_code"] == "MRP-RAP-101"
    # Because MRP-RAP-101 stock is 2 <= 3, safety audit warns about critical stock
    assert res_with_part["audit"]["passed"] is False
    assert any("kritik stok" in w.lower() for w in res_with_part["audit"]["warnings"])

    # 3. Excessive downtime (120 minutes -> OEE Availability = 75.00% < 85%)
    res_low_oee = engine.calculate_oee_and_downtime_loss(
        downtime_minutes=120.0,
        planned_shift_minutes=480.0
    )
    assert res_low_oee["oee_availability_pct"] == 75.00
    assert res_low_oee["audit"]["passed"] is False
    assert any("oee verimlilik" in w.lower() for w in res_low_oee["audit"]["warnings"])

    # 4. Single piece weaving verification (lost carpet sqm is halved)
    res_single = engine.calculate_oee_and_downtime_loss(
        downtime_minutes=45.0,
        is_double_piece=False
    )
    assert res_single["production_rate"]["sqm_per_min"] == 0.55
    assert res_single["loss_metrics"]["lost_carpet_sqm"] == 24.75
    assert res_single["loss_metrics"]["carpet_loss_cost_tl"] == 11137.50


# ---------------------------------------------------------------------------
# Test 23: Data Lake Web Harvester, 5-Year Synthetic SAP PM & ISO 14224 Reliability
# ---------------------------------------------------------------------------
def test_data_lake_collector_and_iso14224_models() -> None:
    from day29.mini_project.src.data_lake_collector import DataLakeCollectorEngine
    from day29.mini_project.src.models import (
        ISO14224TaxonomyNode,
        ISO14224FailureRecord,
        ReliabilityMetrics,
        MaintenanceDecisionCard
    )

    collector = DataLakeCollectorEngine()

    # 1. Verify Online Technical Sources indexed
    sources = collector.get_open_technical_sources()
    assert len(sources) >= 8
    mfg_set = {s.manufacturer for s in sources}
    assert "Vandewiele" in mfg_set
    assert "Superba" in mfg_set
    assert "Saurer Volkmann" in mfg_set
    assert "Siemens" in mfg_set
    assert "Atlas Copco" in mfg_set

    # 2. Verify 5-Year Synthetic SAP PM Generation
    records = collector.generate_synthetic_sap_pm_history(num_records=120)
    assert len(records) == 120
    first_rec = records[0]
    assert first_rec.order_id.startswith("IW32-")
    assert first_rec.functional_location.startswith("MER-T01-")
    assert first_rec.mtbf_hours > 0
    assert first_rec.mttr_hours > 0
    assert first_rec.loto_required is True
    assert first_rec.teco_status == "TECO_COMPLETED"
    assert len(first_rec.technician_log) > 10

    # 3. Verify Data Lake summary
    summary = collector.build_data_lake_summary()
    assert summary["phase"] == "Faz 1: Veri Gölü ve Sayısallaştırma"
    assert summary["status"] == "DATA_LAKE_ACTIVE"
    assert summary["online_sources_indexed"] >= 8
    assert summary["sap_pm_records_count"] == 120

    # 4. Verify ISO 14224 Taxonomy Node model
    node = ISO14224TaxonomyNode(
        plant_site="MER-T01",
        area_line="LN-W02 Dokuma Salonu 2",
        equipment_unit="VDW-RCE2-14",
        sub_unit="ATK-01 Atkı Atma Grubu",
        maintainable_item="GRP-R01 Sağ Rapyer Kıskacı",
        part="SPR-092 Kıskaç Baskı Yayı"
    )
    assert node.plant_site == "MER-T01"
    assert node.equipment_unit == "VDW-RCE2-14"
    assert node.maintainable_item == "GRP-R01 Sağ Rapyer Kıskacı"

    # 5. Verify ISO 14224 Failure Record & Reliability Calculations
    # Formula: lambda = (n + 0.7) / t
    # For n=2 failures over t=876 operating hours:
    # lambda = (2 + 0.7) / 876 = 0.00308219 -> 0.003082
    # MTBF = 1 / lambda = 324.44 h
    # Availability = (MTBF / (MTBF + MTTR)) * 100 with MTTR = 0.75h -> 99.77%
    fail_rec = ISO14224FailureRecord(
        iso_fault_code="MEC-TRN-BRK",
        failure_mode="Rapyer devir-teslim kaçırması",
        failure_mechanism="Sürtünme ve yay yorulması",
        failure_cause="Aşırı vuruş hızı ve yetersiz yağlama",
        detection_method="Akustik emisyon ve atkı optik sensörü",
        corrective_action="Kıskaç mandal yayı yenilendi, sentil ayarı 0.35 mm yapıldı"
    )
    assert fail_rec.iso_fault_code == "MEC-TRN-BRK"
    assert "sentil" in fail_rec.corrective_action

    rel_metrics = ReliabilityMetrics.calculate(n=2, t=876.0, xi=180.0, mttr_hours=0.75)
    assert rel_metrics.failure_rate_lambda == 0.003082
    assert rel_metrics.mtbf_hours == 324.44
    assert rel_metrics.availability_ao_pct == 99.77
    assert rel_metrics.mctf_cycles == 3504000.0
    assert rel_metrics.mttf_hours == 324.44

    # 6. Verify Mobile Maintenance Ticket generation
    mobile_ticket = collector.create_mobile_ticket(
        loom_id="VDW-RCE-02",
        technician="Ahmet Usta",
        symptom="Atkı verici pençe ray aşınması ve iplik kaçırma",
        sap_notification_id="IW21-889104"
    )
    assert mobile_ticket.ticket_id.startswith("MOB-TKT-")
    assert mobile_ticket.loom_id == "VDW-RCE-02"
    assert mobile_ticket.technician_name == "Ahmet Usta"
    assert "LOTO_ISOLATION_REQUIRED" in mobile_ticket.safety_gate_status




