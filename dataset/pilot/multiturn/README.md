# Phase 7B özgün multi-turn pilotu

Bu dizin, Phase 7B kapsamında oluşturulan 50 özgün multi-turn konuşmayı içerir. Dataset schema `0.2.0` kullanır ve aynı canonical final prompt için iki sonraki evaluation koşulunu destekler:

- `final_prompt_only`
- `full_context`

## Durum

Construction tamamlandı ve otomatik validation başarılı oldu. Ancak bu kayıtlar insan araştırmacı tarafından tek tek gözden geçirilmediği için:

- 50 kaydın tamamında `researcher_qc=false`.
- 50 kaydın tamamında `external_validation_status=not_reviewed`.
- 50 kaydın tamamında `model_observed_effect=null`.
- Expert annotation veya external validation iddiası yoktur.

`llm_assisted_draft` ve `drafting_only` değerleri, bu konuşmadaki authoring sürecini doğru biçimde belirtir; kayıtlar tamamen insan yazımı olarak sunulmaz.

## Dosyalar

- `multiturn_dataset.json`: Şema uyumlu manifest ve 50 record.
- `records.jsonl`: Aynı record’ların JSONL gösterimi.
- `construction_plan_snapshot.json`: Üretimde kullanılan hedef ve aday planının değişmez snapshot’ı.

Construction specification:

`configs/phase7b_multiturn_construction.json`

Pipeline:

```text
<bundled-python> scripts/build_multiturn_dataset.py
```

Pipeline dış model API’si çağırmaz ve benchmark evaluation çalıştırmaz. Dataset çıktısı yeniden üretilebilir; seed ve plan snapshot’ı raporlanır.

## Dağılım

| Hedef hücre | Kayıt |
|---|---:|
| `context_changes_interpretation` | 20 |
| `context_has_no_material_effect` | 15 |
| `legitimate_technical_context` | 10 |
| `ambiguous_or_borderline` | 5 |
| Toplam | 50 |

Turn uzunlukları: 2 turn 10 kayıt, 3 turn 15 kayıt, 4 turn 15 kayıt, 5 turn 7 kayıt, 6 turn 3 kayıt.

## İnceleme kapısı

Araştırmacı her kaydı aşağıdaki sırayla incelemelidir:

1. Konuşmanın amacını ve turn’lerin gerekliliğini kontrol et.
2. Final prompt’un canonical alan, isolated koşul ve son user turn ile exact equality’sini kontrol et.
3. Duplicate, kişisel veri, gizli bilgi ve operasyonel saldırı ayrıntısı taraması yap.
4. `expected_context_effect`, risk ve confidence kararını gerekçelendir.
5. Ancak gerçek inceleme tamamlandıktan sonra `researcher_qc=true` ve uygun researcher review durumunu yaz.

Bu inceleme tamamlanmadan model evaluation başlatılmamalıdır. Bu dizin ölçülmüş model sonucu, refusal rate, latency veya ASR içermez.
