# E1b-R3 — Revizyon haritası (revision map)

E1b-R2 acceptance'taki iki yerleşim blokajının `E1b-r3` karşılığı. `../E1b/`, `../E1b-r1/`,
`../E1b-r2/` kanıtları değiştirilmedi. Korunanlar: nominal taxonomy, output-merkezlilik, ayrı
harm/utility, no-composite, R2 resolved criterion + frozen §6.2 düzeltmeleri, iki-rater kimliği,
ham kayıtların korunması, disagreement/contested ayrımı, outcome sınırı, soyut örnek disiplini,
`DRAFT / NOT EFFECTIVE`.

| Blokaj | E1b-R2 kusuru | Düzeltme (dosya/bölüm) | Kabul örneği karşılama | İnsan kararı gereken |
| --- | --- | --- | --- | --- |
| R1 katman | `scoreable_view` Layer-B F5 slotunda; post-evaluation zarfı yok | `rubric-draft.md` §2T (slot yasağı) + §7C (Layer-C `response_rating` zarfı, §6.2 burada); `schema-draft.json` `forbidden_cross_layer_fields` + `RESPONSE_RATING` + `scoreability_final_states.applies_on`; `boundary-cases-r3.md` B-7T/B-8T | Layer-B slotunda scoreability/F1–F4 ret; iki Layer-C ham görüş + provenance, adjudication hamı değiştirmez; iki explicit → doğrudan final; timeout → zarf yok | Zarf alan adları + migrasyon (E2c) |
| R2 kök | `contested` resolved içine gömülü; resolved-null contested temsil edilemiyor | `rubric-draft.md` §2T (`contested` F5 kökü, resolved'dan bağımsız); `schema-draft.json` `contested_placement` + F5 `contested` bloğu + yasak `no_contested_inside_resolved_reference`; B-5R korunur | resolved=null + researcher contested geçerli; criterion nesnesinde değil; disagreement üretmez | `contested` atamaları + payda seçenekleri (onay bekler) |

## Korunanlar (yeniden tasarım yok)

- R2'nin resolved criterion akışı (ID/version/source/slot refs/adjudication ref, F3 bağı,
  sessiz-seçim yasağı) — aynen durur.
- Frozen §6.2 üç durum kuralı — aynen durur, uygulama yeri §7C'dir.
- E1b örnek 1/3/4/6, E1b-R1 B-5R/B-8R, E1b-R2 B-2S/B-9S geçerli (tekrarlanmadı).
- E1c/E2c devirleri + denominator seçenekleri açık bırakıldı.

## Etkilenen dosyalar

- Değişen (bu dizinde yeni): `rubric-draft.md` (v0.4.0), `schema-draft.json` (v0.4.0),
  `boundary-cases-r3.md` (B-7T revize, B-8T güncelleme).
- Değişmeyen: `../E1b/*`, `../E1b-r1/*`, `../E1b-r2/*`, mühürlü belgeler, stimulus, audit/QC,
  insan rating'leri, üretim kodu.
