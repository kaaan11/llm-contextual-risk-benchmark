# Phase 6B — Kaynak taksonomisi eşleme

Mevcut [tehdit taksonomisi](threat_taxonomy.md) değiştirilmemiştir. Dış benchmark etiketleri proje etiketleriyle aynı kavramlar değildir; eşleme bir yorum katmanı olarak tutulmalıdır.

## Eşleme ilkesi

`original_label → mapped_label → research_interpretation` zinciri korunur. `harmful`, `unsafe`, `adversarial` ve `jailbreak` birbirinin eş anlamlısı değildir. Kaynağın ölçtüğü kavram, araştırma içi metrikten ayrı alanlarda saklanmalıdır.

## XSTest

| Original | İç eşleme | Yorum |
|---|---|---|
| `safe` | `benign` / `safe_sensitive_prompt` | Güvenli prompt; beklenen davranış genellikle compliance. Over-refusal için karşılaştırma örneğidir. |
| `unsafe` | `unsafe_contrast` | Unsafe contrast; otomatik olarak jailbreak veya adversarial attack değildir. |
| `type` / `focus` | `taxonomy_category` için aday sinyal | Örneğin context/technical sensitivity, mevcut T1–T12 kategorisine ancak gerekçeyle bağlanır. |
| `label` eksik/çelişkili | `unknown` | Birincil değerlendirmeye alınmaz; ambiguity raporlanır. |

Safe XSTest örnekleri gerektiğinde B1/B2/B4/B5 karşılaştırma etiketleriyle ilişkilendirilebilir, fakat bu etiketler source label’dan otomatik çıkarılmaz. Unsafe contrast örnekleri için T kategorisi `focus` ve prompt amacı incelenmeden icat edilmez.

## JBB-Behaviors

| Original | İç eşleme | Yorum |
|---|---|---|
| `harmful` behavior/goal | `harmful_behavior_goal` | Kötüye kullanım hedefi; jailbreak yöntemi değildir. |
| `benign` behavior/goal | `matched_benign_behavior` | Tematik benign karşılaştırma; modelin over-refusal davranışı için kullanılabilir. |
| `Category` | T1–T12 aday kategorisi | Örn. Malware/Hacking → T3/T4; Privacy → T2; Fraud/Deception → T9. Birden fazla kategori ve gerekçe tutulur. |
| `Source` | upstream provenance | `Original`, `AdvBench`, `TDC/HarmBench` ayrımı korunur; bağımsız örnek sayımı buna göre düzeltilir. |
| `judge_comparison` human/LLM labels | `source_outcome_label` | Judge agreement/karşılaştırmasıdır; refusal veya jailbreak ground truth’u olarak doğrudan kullanılmaz. |

## WildGuardMix

| Original | İç eşleme | Yorum |
|---|---|---|
| `adversarial=true/false` | `source_adversarial_flag` | Kaynak flag’i; bizim adversariality anotasyonumuz değildir. |
| `prompt_harm_label` | `source_prompt_harmfulness` | Prompt zararı; maliciousness/expected risk için kanıt alanıdır, eşdeğer skor değildir. |
| `response_harm_label` | `source_response_harmfulness` | Kaynak response etiketi; model evaluation yanıtı değildir. |
| `response_refusal_label` | `source_refusal_label` | Kaynak response refusal/compliance etiketi; bizim heuristik detector ground truth’uyla karıştırılmaz. |
| `subcategory` | `taxonomy_category` aday sinyali | T kategorisi eşlemesi için gerekçe ve confidence gerekir. |
| agreement fields | `source_annotation_agreement` | Anotasyon kalitesini ve ambiguity handling’i destekler. |

## Açık belirsizlikler

1. JBB harmful goal örneklerinin “jailbreak evaluation” diye adlandırılması geçerli değildir; araştırma sorusu veya kaynak birimi değişmelidir.
2. WildGuard’ın harmful/adversarial ayrımı, jailbreak kategorisi olarak yeniden etiketlenemez.
3. XSTest–JBB `judge_comparison` overlap’i nedeniyle bu split bağımsız örnek havuzu değildir.
4. WildGuard native sample ID’si yoksa türetilmiş locator açıkça işaretlenmeden source provenance tamamlanamaz.

Final mapping ancak immutable source snapshotları ve row-level audit sonrasında onaylanmalıdır.
