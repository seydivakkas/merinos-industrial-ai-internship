"""
Merinos Industrial AI Internship - Day 29
Custom NLP Engine & Nano Causal Language Model Architecture.

Implements from first principles:
1. MerinosBPETokenizer: Domain subword tokenizer with specialized textile tokens.
2. RotaryEmbedding (RoPE): Modern rotational positional embeddings.
3. RMSNorm: Root Mean Square Layer Normalization for stability.
4. SwiGLUFFN: Gated Feed-Forward Network with Swish/SiLU.
5. MoEFeedForward: Sparse Mixture of Experts (Mixtral / DeepSeek style with Shared Expert & Aux Loss).
6. CausalSelfAttention: Grouped Query Attention (GQA), KV Caching & Logit Soft-Capping (Gemma-2).
7. TransformerBlock: Pre-RMSNorm residual causal transformer layer with MoE toggle.
8. MerinosCausalLM: End-to-end autoregressive language model engine with KV-cache generation.
"""

from __future__ import annotations
import math
import re
from typing import Dict, List, Optional, Tuple, Union

import torch
import torch.nn as nn
import torch.nn.functional as F

from day29.mini_project.src.models import NanoLLMConfig


# ============================================================================
# 1. Custom Domain BPE / Subword Tokenizer
# ============================================================================

SPECIAL_TOKENS = [
    # 1. Temel Yapay Zeka Belirteçleri (Gerekçe: Dizi başı/sonu ve dolgu yönetimi)
    "[PAD]", "[UNK]", "[BOS]", "[EOS]",
    # 2. Endüstriyel Yapısal Görev Belirteçleri (Gerekçe: Prompt, arıza, çözüm ve bakım bloklarını koşullandırır)
    "[ARIZA]", "[COZUM]", "[BAKIM]", "[PARAMETRE]",
    # 3. Alarm ve Öncelik Belirteçleri (Gerekçe: PLC/SCADA arıza aciliyetini temsil eder)
    "[ONCELIK_KRITIK]", "[ONCELIK_UYARI]", "[ONCELIK_BILGI]",
    # 4. Halı & Tekstil Alt Sistem Belirteçleri (Gerekçe: MoE uzman katmanına doğrudan anlamsal ipucu sağlar)
    "[ATKI]", "[COZGU]", "[JAKAR]", "[RAMOZ]", "[LEVENT]", "[RAPYER]", "[BCF]", "[ILME]", "[TUY]", "[GUCU]",
    # 5. Halı Desen, Çizim & Jakar CAD Belirteçleri (Gerekçe: Desinatörün desen, raport, rölyef ve renk paleti isteklerini koşullandırır)
    "[DESEN]", "[CIZIM]", "[TARAK]", "[RAPORT]", "[ROLYEF]", "[RENK_PALETI]", "[NOKTA_YOGUNLUGU]", "[CAD_EP]",
    # 6. Kalite Kontrol & Akredite Laboratuvar Belirteçleri (Gerekçe: TSE 2104, ISO 4919 tuft-lock, haslık ve GSM testlerini koşullandırır)
    "[KALITE]", "[TEST_LAB]", "[GRAMAJ]", "[HASLIK]", "[TSE_STANDART]",
    # 7. OEE Duruş ve ERP Yedek Parça Belirteçleri (Gerekçe: OEE kaybı, vardiya analizi, MRP kodlama ve kritik stok sorgulamaları)
    "[OEE]", "[DURUS]", "[VARDIYA]", "[YEDEK_PARCA]", "[STOK_MRP]"
]


class MerinosBPETokenizer:
    """
    Subword tokenizer customized for Merinos Carpet manufacturing terminology.
    Combines exact-match domain tokens, byte-level fallback, and subword segmentation.
    Gerekçe: Standart tokenizer'lar Türkçe tekstil terimlerini gereksiz yere 4-5 alt parçaya
    bölerek bellek ve gecikme kaybına yol açar; Merinos tokenizer'ı tek token olarak kodlar.
    """

    def __init__(self, vocab_size: int = 1024):
        self.vocab_size = vocab_size
        self.special_tokens = SPECIAL_TOKENS
        self.token_to_id: Dict[str, int] = {}
        self.id_to_token: Dict[int, str] = {}
        
        self._build_initial_vocab()

    def _build_initial_vocab(self) -> None:
        """Populate initial vocab with special tokens, ASCII/extended chars, and textile morphemes."""
        idx = 0
        # 1. Special tokens
        for st in self.special_tokens:
            self.token_to_id[st] = idx
            self.id_to_token[idx] = st
            idx += 1

        # 2. Textile and Turkish domain root tokens (Gerekçe: Fabrika terimleri tek parça halinde işlenir)
        textile_roots = [
            "dokuma", "tezgah", "iplik", "polipropilen", "polyester", "akrilik",
            "atki", "cozgu", "jakar", "hiz", "devir", "sicaklik", "ramoz",
            "fikse", "apre", "kalite", "hata", "kopma", "tansiyon", "levent",
            "baski", "boya", "bcf", "filament", "denye", "tarak", "mekik",
            "sensör", "titresim", "rulman", "yaglama", "merinos", "gaziantep",
            "üretim", "motor", "akim", "voltaj", "tork", "hava", "basinc",
            "metre", "dakika", "hata_kodu", "durussuz", "verimlilik", "vardiya",
            "otomasyon", "plc", "scada", "telemetri", "alarm", "esik", "ayar",
            "rapyer", "lingo", "gucu", "bicak", "caglik", "bobin", "dtex",
            "neumag", "schonherr", "brueckner", "siemens", "lenze", "bonas",
            "viskozite", "kalsit", "lateks", "oransal", "brulor", "rezistans",
            "profinet", "profibus", "quench", "solenoid", "tuft_lock", "ekstruder",
            # Halı desen ve çizim kökleri (Gerekçe: Desinatör CAD ve jakar terimleri tek token olarak işlenir)
            "desen", "cizim", "raport", "bordur", "gobek", "rolyef", "cokertme",
            "nedgraphics", "texcelle", "designscope", "atki_sikligi", "nokta_sayisi",
            "hav_yuksekligi", "renk_kombini", "armur", "dokuma_en", "caglik_dizilimi",
            # Kalite kontrol, laboratuvar ve standart kökleri (Gerekçe: Laboratuvar ve TSE/ISO analiz terimleri tek token işlenir)
            "kalite_lab", "martindale", "haslik", "tse2104", "oeko_tex", "tuft_lock_kuvveti", "gri_skala",
            # OEE duruş, maliyet ve ERP parça kökleri (Gerekçe: OEE ve ERP stok yönetim terimleri tek parça işlenir)
            "oee_analiz", "durus_kaybi", "yedek_parca", "stok_mrp", "tedarik_gun", "kritik_stok", "emniyet_stok"
        ]
        for root in textile_roots:
            if root not in self.token_to_id and idx < self.vocab_size - 100:
                self.token_to_id[root] = idx
                self.id_to_token[idx] = root
                idx += 1

        # 3. Standard character/byte table (Latin-1, Turkish characters, punctuation, digits)
        base_chars = " abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,:;!?-/_=()[]{}%°+*~<>\"'\nçğıöşüÇĞİÖŞÜ"
        for ch in base_chars:
            if ch not in self.token_to_id and idx < self.vocab_size:
                self.token_to_id[ch] = idx
                self.id_to_token[idx] = ch
                idx += 1

        # 4. Fill remainder with byte hex tokens if needed
        byte_idx = 0
        while idx < self.vocab_size:
            token = f"<0x{byte_idx:02X}>"
            if token not in self.token_to_id:
                self.token_to_id[token] = idx
                self.id_to_token[idx] = token
                idx += 1
            byte_idx += 1

    @property
    def pad_id(self) -> int:
        return self.token_to_id["[PAD]"]

    @property
    def unk_id(self) -> int:
        return self.token_to_id["[UNK]"]

    @property
    def bos_id(self) -> int:
        return self.token_to_id["[BOS]"]

    @property
    def eos_id(self) -> int:
        return self.token_to_id["[EOS]"]

    def encode(self, text: str, add_special_tokens: bool = True) -> List[int]:
        """Encodes text into token IDs using greedy domain matching and character fallback."""
        tokens: List[int] = []
        if add_special_tokens:
            tokens.append(self.bos_id)

        pattern = "|".join(re.escape(st) for st in self.special_tokens)
        parts = re.split(f"({pattern})", text) if pattern else [text]

        for part in parts:
            if not part:
                continue
            if part in self.token_to_id:
                tokens.append(self.token_to_id[part])
            else:
                i = 0
                while i < len(part):
                    matched = False
                    for j in range(min(len(part), i + 15), i, -1):
                        sub = part[i:j].lower()
                        if sub in self.token_to_id:
                            tokens.append(self.token_to_id[sub])
                            i = j
                            matched = True
                            break
                    if not matched:
                        ch = part[i]
                        tokens.append(self.token_to_id.get(ch, self.unk_id))
                        i += 1

        if add_special_tokens:
            tokens.append(self.eos_id)
        return tokens

    def decode(self, token_ids: List[int], skip_special_tokens: bool = True) -> str:
        """Decodes token IDs back to a reconstructed string."""
        pieces: List[str] = []
        for tid in token_ids:
            if tid not in self.id_to_token:
                continue
            token_str = self.id_to_token[tid]
            if skip_special_tokens and token_str in self.special_tokens:
                continue
            pieces.append(token_str)
        return "".join(pieces)


# ============================================================================
# 2. Rotary Position Embeddings (RoPE)
# ============================================================================

class RotaryEmbedding(nn.Module):
    """
    Rotary Positional Embedding (RoPE) based on Su et al. (RoFormer / LLaMA / Qwen).
    Encodes relative position by rotating queries and keys in complex 2D subspaces.
    Supports position offset for KV-cached single-token generation.
    """

    def __init__(self, dim: int, max_position_embeddings: int = 2048, base: float = 10000.0):
        super().__init__()
        self.dim = dim
        self.max_position_embeddings = max_position_embeddings
        self.base = base

        inv_freq = 1.0 / (self.base ** (torch.arange(0, self.dim, 2).float() / self.dim))
        self.register_buffer("inv_freq", inv_freq, persistent=False)
        self._build_cache(max_position_embeddings)

    def _build_cache(self, seq_len: int) -> None:
        t = torch.arange(seq_len, dtype=torch.float32)
        freqs = torch.outer(t, self.inv_freq)  # (seq_len, dim // 2)
        emb = torch.cat((freqs, freqs), dim=-1)  # (seq_len, dim)
        self.register_buffer("cos_cached", emb.cos(), persistent=False)
        self.register_buffer("sin_cached", emb.sin(), persistent=False)

    @staticmethod
    def _rotate_half(x: torch.Tensor) -> torch.Tensor:
        """Rotates half the hidden dimensions: [-x2, x1]."""
        x1 = x[..., : x.shape[-1] // 2]
        x2 = x[..., x.shape[-1] // 2 :]
        return torch.cat((-x2, x1), dim=-1)

    def forward(
        self,
        q: torch.Tensor,
        k: torch.Tensor,
        seq_len: int,
        offset: int = 0
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Applies rotary position embeddings to query and key tensors with optional offset.
        q, k shape: (batch_size, n_heads, seq_len, head_dim)
        """
        end_pos = offset + seq_len
        if end_pos > self.cos_cached.shape[0]:
            self._build_cache(max(end_pos, self.cos_cached.shape[0] * 2))

        cos = self.cos_cached[offset:end_pos, :].unsqueeze(0).unsqueeze(0)  # (1, 1, seq_len, head_dim)
        sin = self.sin_cached[offset:end_pos, :].unsqueeze(0).unsqueeze(0)  # (1, 1, seq_len, head_dim)

        q_rot = (q * cos) + (self._rotate_half(q) * sin)
        k_rot = (k * cos) + (self._rotate_half(k) * sin)
        return q_rot, k_rot


# ============================================================================
# 3. RMSNorm (Root Mean Square Layer Normalization)
# ============================================================================

class RMSNorm(nn.Module):
    """
    Root Mean Square Layer Normalization (Zhang & Sennrich, NeurIPS 2019).
    Scales inputs by the root-mean-square without mean-centering, saving FLOPs.
    """

    def __init__(self, hidden_size: int, eps: float = 1e-6):
        super().__init__()
        self.eps = eps
        self.weight = nn.Parameter(torch.ones(hidden_size))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        variance = x.pow(2).mean(-1, keepdim=True)
        x_norm = x * torch.rsqrt(variance + self.eps)
        return self.weight * x_norm


# ============================================================================
# 4. SwiGLU Feed-Forward Network
# ============================================================================

class SwiGLUFFN(nn.Module):
    """
    SwiGLU Gated Feed-Forward Network (Shazeer, 2020 / PaLM / LLaMA / Mistral / Qwen).
    SwiGLU(x) = (SiLU(x * W_gate) * (x * W_up)) * W_down
    """

    def __init__(self, hidden_size: int, intermediate_size: int):
        super().__init__()
        self.gate_proj = nn.Linear(hidden_size, intermediate_size, bias=False)
        self.up_proj = nn.Linear(hidden_size, intermediate_size, bias=False)
        self.down_proj = nn.Linear(intermediate_size, hidden_size, bias=False)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        gate = F.silu(self.gate_proj(x))
        up = self.up_proj(x)
        return self.down_proj(gate * up)


# ============================================================================
# 5. Sparse Mixture of Experts (MoE) with DeepSeek-Style Shared Expert
# ============================================================================

class MoEFeedForward(nn.Module):
    """
    Sparse Mixture of Experts (MoE) layer with:
    - Top-K Gating Router
    - Auxiliary Load Balancing Loss (Switch Transformer / DeepSeek style)
    - Optional Shared Expert (DeepSeek-V2/V3 style: always active baseline domain knowledge)
    """

    def __init__(self, config: NanoLLMConfig):
        super().__init__()
        self.num_experts = config.num_experts
        self.top_k = min(config.num_experts_per_tok, self.num_experts)
        self.d_model = config.d_model

        # Gating router: projects d_model -> num_experts
        self.gate = nn.Linear(config.d_model, self.num_experts, bias=False)

        # Expert networks (each is an independent SwiGLU FFN)
        expert_dim = config.intermediate_size
        self.experts = nn.ModuleList([
            SwiGLUFFN(config.d_model, expert_dim)
            for _ in range(self.num_experts)
        ])

        # Shared expert: always active to preserve core textile domain knowledge
        self.shared_expert = (
            SwiGLUFFN(config.d_model, expert_dim)
            if config.use_shared_expert else None
        )

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass for MoE:
        Returns:
            output: (batch_size, seq_len, d_model)
            aux_loss: scalar load balancing loss for optimizer regularisation.
        """
        bs, seq_len, d_model = x.shape
        flat_x = x.view(-1, d_model)  # (N, D) where N = bs * seq_len
        num_tokens = flat_x.size(0)

        # 1. Gate logits and probabilities
        gate_logits = self.gate(flat_x)  # (N, num_experts)
        gate_probs = F.softmax(gate_logits, dim=-1)  # (N, num_experts)

        # 2. Select Top-K experts per token
        topk_weights, topk_indices = torch.topk(gate_probs, self.top_k, dim=-1)  # (N, top_k)
        # Renormalize topk weights to sum to 1.0
        topk_weights = topk_weights / (topk_weights.sum(dim=-1, keepdim=True) + 1e-9)

        # 3. Auxiliary Load Balancing Loss:
        # L_aux = N * sum_i (fraction_tokens_to_i * avg_prob_to_i)
        # Fraction of tokens dispatched to each expert
        expert_mask = F.one_hot(topk_indices, num_classes=self.num_experts).float()  # (N, top_k, num_experts)
        fraction_per_expert = expert_mask.sum(dim=(0, 1)) / (num_tokens * self.top_k + 1e-9)  # (num_experts,)
        avg_prob_per_expert = gate_probs.mean(dim=0)  # (num_experts,)
        aux_loss = self.num_experts * torch.sum(fraction_per_expert * avg_prob_per_expert)

        # 4. Dispatch tokens to selected experts
        final_output = torch.zeros_like(flat_x)
        for k_idx in range(self.top_k):
            indices_for_k = topk_indices[:, k_idx]  # (N,)
            weights_for_k = topk_weights[:, k_idx].unsqueeze(-1)  # (N, 1)

            for exp_id, expert in enumerate(self.experts):
                token_mask = (indices_for_k == exp_id)
                if token_mask.any():
                    selected_tokens = flat_x[token_mask]
                    expert_out = expert(selected_tokens)
                    final_output[token_mask] += expert_out * weights_for_k[token_mask]

        # 5. Add Shared Expert contribution if enabled (DeepSeek innovation)
        if self.shared_expert is not None:
            shared_out = self.shared_expert(flat_x)
            final_output = final_output + shared_out

        return final_output.view(bs, seq_len, d_model), aux_loss


# ============================================================================
# 6. Causal Self-Attention with GQA, KV Caching & Logit Soft-Capping
# ============================================================================

class CausalSelfAttention(nn.Module):
    """
    Causal Multi-Head / Grouped Query Attention (GQA) layer with:
    - KV Caching support for fast $O(1)$ token decoding
    - Gemma-2 style Logit Soft-Capping (tanh attention bound)
    - Rotary Position Embeddings (RoPE)
    """

    def __init__(self, config: NanoLLMConfig):
        super().__init__()
        self.d_model = config.d_model
        self.n_heads = config.n_heads
        self.n_kv_heads = config.n_kv_heads or config.n_heads
        self.head_dim = self.d_model // self.n_heads
        self.num_key_value_groups = self.n_heads // self.n_kv_heads
        self.soft_cap = config.attention_logit_soft_capping

        assert self.d_model % self.n_heads == 0, "d_model must be divisible by n_heads"
        assert self.n_heads % self.n_kv_heads == 0, "n_heads must be divisible by n_kv_heads"

        self.q_proj = nn.Linear(self.d_model, self.n_heads * self.head_dim, bias=False)
        self.k_proj = nn.Linear(self.d_model, self.n_kv_heads * self.head_dim, bias=False)
        self.v_proj = nn.Linear(self.d_model, self.n_kv_heads * self.head_dim, bias=False)
        self.out_proj = nn.Linear(self.d_model, self.d_model, bias=False)

        self.rotary_emb = RotaryEmbedding(self.head_dim, max_position_embeddings=config.max_seq_len)
        self.dropout = nn.Dropout(config.dropout)

    def _repeat_kv(self, x: torch.Tensor, n_rep: int) -> torch.Tensor:
        """Repeat KV heads for Grouped Query Attention: (B, n_kv, S, D) -> (B, n_q, S, D)."""
        if n_rep == 1:
            return x
        bs, n_kv, slen, hdim = x.shape
        x = x[:, :, None, :, :].expand(bs, n_kv, n_rep, slen, hdim)
        return x.reshape(bs, n_kv * n_rep, slen, hdim)

    def forward(
        self,
        x: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        past_key_value: Optional[Tuple[torch.Tensor, torch.Tensor]] = None
    ) -> Tuple[torch.Tensor, Optional[Tuple[torch.Tensor, torch.Tensor]]]:
        bs, seq_len, _ = x.shape

        # Projections
        q = self.q_proj(x)
        k = self.k_proj(x)
        v = self.v_proj(x)

        # Reshape to (B, n_heads, S, head_dim)
        q = q.view(bs, seq_len, self.n_heads, self.head_dim).transpose(1, 2)
        k = k.view(bs, seq_len, self.n_kv_heads, self.head_dim).transpose(1, 2)
        v = v.view(bs, seq_len, self.n_kv_heads, self.head_dim).transpose(1, 2)

        # KV cache position offset
        offset = past_key_value[0].shape[2] if past_key_value is not None else 0

        # Apply RoPE
        q, k = self.rotary_emb(q, k, seq_len, offset=offset)

        # Update KV Cache
        if past_key_value is not None:
            past_k, past_v = past_key_value
            k = torch.cat([past_k, k], dim=2)
            v = torch.cat([past_v, v], dim=2)

        present_key_value = (k, v)
        total_k_len = k.shape[2]

        # Expand KV heads for GQA
        k_expanded = self._repeat_kv(k, self.num_key_value_groups)
        v_expanded = self._repeat_kv(v, self.num_key_value_groups)

        # Scaled dot-product attention
        scale = 1.0 / math.sqrt(self.head_dim)
        attn_weights = torch.matmul(q, k_expanded.transpose(-1, -2)) * scale  # (B, n_heads, seq_len, total_k_len)

        # Gemma-2 style Logit Soft-Capping: cap * tanh(weights / cap)
        if self.soft_cap is not None and self.soft_cap > 0:
            attn_weights = self.soft_cap * torch.tanh(attn_weights / self.soft_cap)

        # Apply causal mask: only mask if seq_len > 1 (during full prefill)
        if seq_len > 1:
            causal_mask = torch.triu(
                torch.full((seq_len, total_k_len), float("-inf"), device=x.device),
                diagonal=total_k_len - seq_len + 1
            )
            attn_weights = attn_weights + causal_mask.unsqueeze(0).unsqueeze(0)

        if attention_mask is not None:
            attn_weights = attn_weights + attention_mask

        attn_probs = F.softmax(attn_weights, dim=-1)
        attn_probs = self.dropout(attn_probs)

        # Context output
        context = torch.matmul(attn_probs, v_expanded)  # (B, n_heads, seq_len, head_dim)
        context = context.transpose(1, 2).contiguous().view(bs, seq_len, self.d_model)

        return self.out_proj(context), present_key_value


# ============================================================================
# 7. Transformer Block (Pre-RMSNorm Residual with MoE Toggle)
# ============================================================================

class TransformerBlock(nn.Module):
    """
    Standard causal transformer block with Pre-RMSNorm and either Dense SwiGLU or Sparse MoE.
    """

    def __init__(self, config: NanoLLMConfig):
        super().__init__()
        self.attn_norm = RMSNorm(config.d_model, eps=config.rms_norm_eps)
        self.self_attn = CausalSelfAttention(config)
        self.ffn_norm = RMSNorm(config.d_model, eps=config.rms_norm_eps)

        # Select Dense SwiGLU or Sparse MoE
        self.use_moe = config.use_moe
        if self.use_moe:
            self.ffn = MoEFeedForward(config)
        else:
            self.ffn = SwiGLUFFN(config.d_model, config.intermediate_size)

    def forward(
        self,
        x: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        past_key_value: Optional[Tuple[torch.Tensor, torch.Tensor]] = None
    ) -> Tuple[torch.Tensor, Optional[Tuple[torch.Tensor, torch.Tensor]], torch.Tensor]:
        # Pre-norm Self-Attention + Residual
        attn_in = self.attn_norm(x)
        attn_out, present_kv = self.self_attn(attn_in, attention_mask=attention_mask, past_key_value=past_key_value)
        h = x + attn_out

        # Pre-norm FFN (Dense or MoE) + Residual
        ffn_in = self.ffn_norm(h)
        if self.use_moe:
            ffn_out, aux_loss = self.ffn(ffn_in)
        else:
            ffn_out = self.ffn(ffn_in)
            aux_loss = torch.tensor(0.0, device=x.device)

        out = h + ffn_out
        return out, present_kv, aux_loss


# ============================================================================
# 8. MerinosCausalLM (Full Decoder-Only Engine with MoE & KV Cache)
# ============================================================================

class MerinosCausalLM(nn.Module):
    """
    Custom Causal Language Model designed for Merinos Industrial Edge AI.
    Implements token embedding, decoder layer stack, RMSNorm, MoE, KV Caching,
    and fast autoregressive generation.
    """

    def __init__(self, config: NanoLLMConfig):
        super().__init__()
        self.config = config

        self.tok_embeddings = nn.Embedding(config.vocab_size, config.d_model)
        self.layers = nn.ModuleList([TransformerBlock(config) for _ in range(config.n_layers)])
        self.norm = RMSNorm(config.d_model, eps=config.rms_norm_eps)
        self.lm_head = nn.Linear(config.d_model, config.vocab_size, bias=False)

        # Tie weights between embedding and lm_head (saves memory in SLMs)
        self.lm_head.weight = self.tok_embeddings.weight

        self.apply(self._init_weights)

    def _init_weights(self, module: nn.Module) -> None:
        if isinstance(module, (nn.Linear, nn.Embedding)):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if hasattr(module, "bias") and module.bias is not None:
                nn.init.zeros_(module.bias)

    def count_parameters(self) -> Dict[str, int]:
        """Calculates total, trainable, and active parameter counts."""
        total = sum(p.numel() for p in self.parameters())
        trainable = sum(p.numel() for p in self.parameters() if p.requires_grad)
        
        # In MoE models, active params per token is less than total params
        if self.config.use_moe:
            # Count parameters that are not part of routed sparse experts (shared expert, attention, embeddings, norms)
            base_and_shared_params = sum(p.numel() for name, p in self.named_parameters() if ".experts." not in name)
            # Count params for exactly num_experts_per_tok active experts per layer
            single_expert_params = sum(p.numel() for p in self.layers[0].ffn.experts[0].parameters()) if isinstance(self.layers[0].ffn, MoEFeedForward) else 0
            active_expert_params = self.config.n_layers * self.config.num_experts_per_tok * single_expert_params
            active = base_and_shared_params + active_expert_params
        else:
            active = total

        return {"total": total, "trainable": trainable, "active_per_token": active}

    def forward(
        self,
        input_ids: torch.Tensor,
        targets: Optional[torch.Tensor] = None,
        attention_mask: Optional[torch.Tensor] = None,
        past_key_values: Optional[List[Tuple[torch.Tensor, torch.Tensor]]] = None
    ) -> Tuple[torch.Tensor, Optional[torch.Tensor], Optional[List[Tuple[torch.Tensor, torch.Tensor]]], torch.Tensor]:
        """
        Forward pass of the causal language model.
        Returns:
            logits: (batch_size, seq_len, vocab_size)
            loss: scalar CrossEntropyLoss + MoE aux_loss if targets provided, else None.
            present_key_values: updated KV cache per layer.
            aux_loss: aggregated load balancing loss across all MoE layers.
        """
        bs, seq_len = input_ids.shape
        offset = past_key_values[0][0].shape[2] if past_key_values is not None else 0
        if offset + seq_len > self.config.max_seq_len:
            raise ValueError(f"Total sequence length {offset + seq_len} exceeds max {self.config.max_seq_len}")

        h = self.tok_embeddings(input_ids)
        present_kvs: List[Tuple[torch.Tensor, torch.Tensor]] = []
        total_aux_loss = torch.tensor(0.0, device=input_ids.device)

        for i, layer in enumerate(self.layers):
            layer_past_kv = past_key_values[i] if past_key_values is not None else None
            h, present_kv, layer_aux = layer(h, attention_mask=attention_mask, past_key_value=layer_past_kv)
            if present_kv is not None:
                present_kvs.append(present_kv)
            total_aux_loss = total_aux_loss + layer_aux

        h = self.norm(h)
        logits = self.lm_head(h)

        loss = None
        if targets is not None:
            ce_loss = F.cross_entropy(
                logits.view(-1, self.config.vocab_size),
                targets.view(-1),
                ignore_index=-100
            )
            loss = ce_loss + (self.config.aux_loss_coef * total_aux_loss)

        return logits, loss, present_kvs if present_kvs else None, total_aux_loss

    @torch.no_grad()
    def generate(
        self,
        prompt_tokens: Union[torch.Tensor, List[int]],
        max_new_tokens: int = 30,
        temperature: float = 0.7,
        top_k: int = 20,
        top_p: float = 0.9,
        eos_id: Optional[int] = None,
        use_cache: bool = True
    ) -> List[int]:
        """
        Autoregressive generation loop with optional fast KV caching ($O(1)$ per token step).
        """
        self.eval()
        device = next(self.parameters()).device

        if isinstance(prompt_tokens, list):
            input_ids = torch.tensor([prompt_tokens], dtype=torch.long, device=device)
        else:
            input_ids = prompt_tokens.to(device)
            if input_ids.dim() == 1:
                input_ids = input_ids.unsqueeze(0)

        generated = input_ids[0].tolist()
        past_key_values = None

        if use_cache and self.config.enable_kv_cache:
            # Prefill step: process initial prompt and seed KV cache
            logits, _, past_key_values, _ = self(input_ids, past_key_values=None)
            next_token_logits = logits[:, -1, :]

            for _ in range(max_new_tokens):
                # Sample next token
                if temperature > 0.0:
                    scaled_logits = next_token_logits / temperature
                    if top_k > 0:
                        v, _ = torch.topk(scaled_logits, min(top_k, scaled_logits.size(-1)))
                        scaled_logits[scaled_logits < v[:, [-1]]] = -float("Inf")
                    if 0.0 < top_p < 1.0:
                        sorted_logits, sorted_indices = torch.sort(scaled_logits, descending=True)
                        cumulative_probs = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)
                        sorted_indices_to_remove = cumulative_probs > top_p
                        sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
                        sorted_indices_to_remove[..., 0] = 0
                        indices_to_remove = sorted_indices[sorted_indices_to_remove]
                        scaled_logits[0, indices_to_remove] = -float("Inf")

                    probs = F.softmax(scaled_logits, dim=-1)
                    next_token = torch.multinomial(probs, num_samples=1)
                else:
                    next_token = torch.argmax(next_token_logits, dim=-1, keepdim=True)

                next_token_id = next_token.item()
                generated.append(next_token_id)
                if eos_id is not None and next_token_id == eos_id:
                    break

                # Decoding step: feed only the single new token into the model with cached KV!
                logits, _, past_key_values, _ = self(next_token, past_key_values=past_key_values)
                next_token_logits = logits[:, -1, :]
        else:
            # Fallback un-cached generation
            curr_input_ids = input_ids
            for _ in range(max_new_tokens):
                cond_ids = curr_input_ids if curr_input_ids.size(1) <= self.config.max_seq_len else curr_input_ids[:, -self.config.max_seq_len:]
                logits, _, _, _ = self(cond_ids)
                next_token_logits = logits[:, -1, :]

                if temperature > 0.0:
                    scaled_logits = next_token_logits / temperature
                    if top_k > 0:
                        v, _ = torch.topk(scaled_logits, min(top_k, scaled_logits.size(-1)))
                        scaled_logits[scaled_logits < v[:, [-1]]] = -float("Inf")
                    if 0.0 < top_p < 1.0:
                        sorted_logits, sorted_indices = torch.sort(scaled_logits, descending=True)
                        cumulative_probs = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)
                        sorted_indices_to_remove = cumulative_probs > top_p
                        sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
                        sorted_indices_to_remove[..., 0] = 0
                        indices_to_remove = sorted_indices[sorted_indices_to_remove]
                        scaled_logits[0, indices_to_remove] = -float("Inf")

                    probs = F.softmax(scaled_logits, dim=-1)
                    next_token = torch.multinomial(probs, num_samples=1)
                else:
                    next_token = torch.argmax(next_token_logits, dim=-1, keepdim=True)

                curr_input_ids = torch.cat((curr_input_ids, next_token), dim=1)
                next_token_id = next_token.item()
                generated.append(next_token_id)

                if eos_id is not None and next_token_id == eos_id:
                    break

        return generated
