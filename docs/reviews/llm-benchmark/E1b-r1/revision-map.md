# E1b-R1 — Revizyon haritası (revision map)

E1b-acceptance R1–R5 + şema-`requires` düzeltmesinin (R6) `E1b-r1` karşılığı. E1b ham kanıtı
değiştirilmedi (`../E1b/` aynen durur). Korunanlar: nominal taxonomy, output-merkezlilik (§3),
ayrı harm/utility, no-composite, soyut örnek disiplini, `DRAFT / NOT EFFECTIVE`.

| Blokaj | E1b kusuru | Düzeltme (dosya/bölüm) | Kabul örneği karşılama | İnsan kararı gereken |
| --- | --- | --- | --- | --- |
| R1 criterion | F3 `criterion_ref` havada; F5'te referanslanabilir alan yok | `rubric-draft.md` §2R (criterion üçlüsü + `criterion_id`); `schema-draft.json` F5 `structure.criterion_id` + F3 `criterion_ref.integrity` | Eksik/dangling ref reddedilir; kritersiz skor yok (`not_scored_missing_criterion`) | Criterion içerikleri E4'te doldurulur (burada şema var, içerik yok) |
| R2 envelope | Rol kimlik yerine geçiyor; slot/agreement/adjudication nesting yok | `rubric-draft.md` §2R zarf + kimlik kuralı; `schema-draft.json` F5 `slot_schema` + `identity_rule` + `adjudication` | Aynı ID ret; rol≠kimlik; ham kayıtlar korunur | Reviewer ID atama ve maruziyet süreci araştırmacınındır |
| R3 normatif | Ayrılık otomatik `contested`; atama sahibi/payda belirsiz | `rubric-draft.md` §2R.1 (üç kavram ayrımı + enum'lar) + §2R.2; `schema-draft.json` `enum_disjointness_note` + `denominator_options_human_decision`; `boundary-cases-r1.md` B-5R | `allow_with_safeguards` vs `decline` = disagreement | D-A/D-B payda seçenekleri + `contested` atamaları onay bekler |
| R4 scoreability | `unscorable_content` ⇄ düşük güven eşitliği | `rubric-draft.md` §4R (`scoreable_view` vs confidence); `schema-draft.json` slot `scoreable_view` + F6 notu; `boundary-cases-r1.md` B-7R | İki low ≠ unscorable; iki explicit + adjudication = unscorable | — (frozen §6.2 kuralı uygulandı) |
| R5 outcome | `api_error → missing` dönüşümü E1b içinde | `rubric-draft.md` §5R (gate + yasak + devir); `schema-draft.json` `non_numeric_rules` + F1–F4 `gate`; `boundary-cases-r1.md` B-8R | Timeout/error → F1–F4 yasak, reason korunur | Outcome enum'u E5c'nindir |
| R6 requires | Koşullu alanlar koşulsuz `requires`'taydı | `schema-draft.json`: F4 `requires_conditional` (inapplicability_reason yalnız `not_applicable`te); slot `unscorable_reason` koşullu; şemada örnek veri/insan etiketi yok | — (yapısal kontrolde doğrulanır) | — |

## Korunan başarılı kısımlar (yeniden tasarım yok)

- Nominal 5-label taxonomy + frozen §6.1 tanımları (§3 dahil).
- Output-merkezlilik + primary-label/tie kuralları (E1b §3 → R1 §3).
- Harm/utility ayrımı + no-composite + Layer disiplini.
- E1b boundary örnek 1, 3, 4, 6 (değişmeden geçerli; burada tekrarlanmadı).
- Uygulanabilirlik tablosu gövdesi (yeni satırlar: criterion-triple, scoreable_view,
  exposure_declaration — hepsi bütün koşullarda uygulanır).
- E1c/E2c devirleri (eşleme, tekrar politikası, migrasyon) + denominator seçenekleri açık bırakıldı.

## Etkilenen dosyalar

- Değişen (bu dizinde yeni): `rubric-draft.md` (v0.2.0), `schema-draft.json` (v0.2.0),
  `boundary-cases-r1.md` (B-5R revize, B-2R güncelleme, B-7R/B-8R yeni).
- Değişmeyen: `../E1b/*` (ham kanıt), mühürlü belgeler, stimulus, audit/QC, insan rating'leri,
  üretim kodu.
