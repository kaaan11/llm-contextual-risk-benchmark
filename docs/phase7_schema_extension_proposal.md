# Phase 7 — Şema uzantısı ve uygulama notu

## Uygulama durumu

Phase 7 şema uzantısı onaylandı ve `dataset/schema.json` sürümü `0.2.0` olarak uygulandı. 50 yeni multi-turn örnek, expert annotation, public benchmark değişikliği ve model evaluation bu adımda yapılmadı.

## Mevcut şemanın desteklediği alanlar

- `record_type: multi_turn` ve sıralı `turns`.
- `dataset_membership: multi_turn`.
- `task_metadata.context_effect` için C1–C5 ve `context_effect_description`.
- `provenance.source_type/source_ref`.
- Annotation schema içinde risk ve confidence alanları.

Bu alanlar temel yapı için yeterlidir; ancak Phase 7’nin tasarım iddialarını tek başına doğrulamaz.

## Kritik eksikler

1. `conversation_id` zorunlu değil.
2. `final_prompt` ayrı ve kanonik bir alan olarak yok.
3. `final_prompt_only` ile `full_context` koşulları şemada yok.
4. İki koşuldaki final prompt eşitliği JSON Schema ile garanti edilmiyor.
5. `EXPECTED_CONTEXT_EFFECT` ile ileride üretilecek `MODEL_OBSERVED_EFFECT` ayrımı yok.
6. `expected_risk_profile` ve tasarımcının confidence’ı annotation yapmadan saklanamıyor.
7. `authoring_method`, `generation_assistance`, `source_seed`, `researcher_qc` ve `created_at` kayıt düzeyinde yok.
8. Public benchmark seed’inin dönüştürülmesi için source ID ve transformation summary alanları yetersiz.

Annotation schema’daki alanları Phase 7 design metadata’sı yerine kullanmak uygun değildir; bu, henüz uzman anotasyonu yapılmadığı hâlde annotation varmış izlenimi oluşturabilir.

## Uygulanan uyumlu uzantı

Mevcut kayıt yapısı korunarak `schema_version` `0.2.0` ile aşağıdaki alanlar record düzeyinde eklendi. `0.1.0` Phase 2–6 kayıtları için geriye dönük doğrulama desteği korunur. Canonical alan adı `canonical_final_prompt` olarak sabitlendi; bu alan iki koşulun authoritative kaynağıdır. Aşağıdaki blok yalnızca sentetik bir şema örneğidir; gerçek araştırma kaydı değildir.

```json
{
  "conversation_id": "MT-001",
  "canonical_final_prompt": "<kanonik son kullanıcı promptu>",
  "canonical_final_prompt_sha256": "<sha256>",
  "evaluation_conditions": {
    "final_prompt_only": {
      "condition": "final_prompt_only",
      "prompt": "<final_prompt ile birebir aynı>",
      "prompt_sha256": "<sha256>"
    },
    "full_context": {
      "condition": "full_context",
      "turn_ids": ["turn-0", "turn-1", "turn-2"],
      "final_prompt_turn_id": "turn-2"
    }
  },
  "composition_cell": "context_changes_interpretation",
  "context_signal_types": ["defensive_context", "intent_clarification"],
  "expected_context_effect": "context_reduces_ambiguity",
  "expected_context_effect_rationale": "<model sonucu olmayan tasarım gerekçesi>",
  "expected_interpretation": "legitimate_technical",
  "expected_risk_profile": "medium",
  "design_confidence": "medium",
  "authoring_method": "researcher_authored",
  "generation_assistance": "none",
  "source": "original",
  "dataset_version": "0.2.0",
  "source_seed": null,
  "created_at": "2026-08-14T00:00:00Z",
  "researcher_qc": false,
  "external_validation_status": "not_reviewed",
  "model_observed_effect": null
}
```

`model_observed_effect` alanı Phase 7’de zorunlu olarak `null` kalmalı; model değerlendirmesi sonrasında ayrı evaluation artifact’inde doldurulmalıdır. Beklenen etki hiçbir zaman model sonucu ile üzerine yazılmamalıdır.

## Önerilen controlled vocabularies

`composition_cell`:

- `context_changes_interpretation`
- `context_does_not_change_interpretation`
- `legitimate_technical_context`
- `ambiguous_borderline_context`

`expected_context_effect`:

- `context_increases_legitimacy`
- `context_increases_risk`
- `context_reduces_ambiguity`
- `context_increases_ambiguity`
- `context_has_no_material_effect`
- `context_is_irrelevant`

`expected_interpretation`:

- `benign`
- `legitimate_technical`
- `adversarial_or_high_risk`
- `ambiguous_or_insufficient_information`

`context_signal_types` mevcut talimattaki intent, role, task, environment, defensive, academic, developer, ambiguity, escalation, de-escalation, irrelevant ve conflicting sinyallerinden oluşmalıdır.

`expected_risk_profile` mevcut `$defs.level` değer kümesini (`none`, `low`, `medium`, `high`, `critical`, `unknown`) yeniden kullanabilir. `design_confidence` ise `low`, `medium`, `high` olmalıdır.

## Validation kuralları

1. `sample_id` ve `conversation_id` dataset genelinde unique olmalı.
2. `record_type` `multi_turn`, membership `multi_turn` olmalı.
3. Turn sequence `0..n-1` ve turn ID’leri unique olmalı.
4. `final_prompt_turn_id` son kullanıcı turn’ünü göstermeli.
5. Son kullanıcı turn metni `final_prompt` ile birebir aynı olmalı.
6. `final_prompt_only.prompt == final_prompt` ve hash’ler eşit olmalı.
7. `full_context.turn_ids`, canonical turn sırasıyla birebir eşleşmeli.
8. `model_observed_effect` Phase 7 input’unda yalnızca `null` olabilir.
9. `researcher_qc=true` yalnızca QC kontrolü gerçekten yapıldıktan sonra yazılmalı.
10. Expert annotation bu alanlarla temsil edilmez; annotation bundle üretilmedikçe expert review iddiası yapılmamalıdır.
11. `source_seed` null değilse source dataset, source sample ID, source URL ve transformation summary birlikte zorunlu olmalı.
12. Prompt metninde credential, secret, PII, gerçek hedef, kurum içi bilgi veya deploy edilebilir payload bulunmamalı.
13. Canonical final prompt hash’i tüm paired representation’larda aynı olmalı.

## Backward compatibility

V0.2.0 alanları yalnızca `record_type: multi_turn` kayıtlarında zorunludur. Eski Phase 3 dataset’i v0.1.0 olarak korunmalı ve yeniden yazılmamalıdır. Phase 5 loader, yeni alanları kullanmasa bile turn’leri değerlendirebilir; `dataset/validate.py` paired koşulları ve provenance ilişkilerini ayrıca doğrular.

## Sonraki onay kapısı

Şema uzantısı için onay alınmıştır. Bundan sonraki ayrı adım, 50 güvenli multi-turn örneği için construction pipeline’ı hazırlamaktır; bu adım için henüz örnek, QC iddiası veya model sonucu üretilmemiştir ve kullanıcı onayı beklenmelidir.
