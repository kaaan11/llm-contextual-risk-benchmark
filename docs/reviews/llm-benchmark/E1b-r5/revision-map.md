# E1b-R5 — Revizyon haritası (revision map)

E1b-R4 acceptance'taki tek şema-ref blokajının `E1b-r5` karşılığı. `../E1b/`, `../E1b-r1/`,
`../E1b-r2/`, `../E1b-r3/`, `../E1b-r4/` kanıtları değiştirilmedi. Korunanlar: R4 dal mantığı,
enum'lar, katman/zaman, kimlik/ham-koruma, resolved akışı, contested yerleşimi, §6.2, yasaklar,
uygulanabilirlik gövdesi, B-7U, `DRAFT / NOT EFFECTIVE`.

| Blokaj | E1b-R4 kusuru | Düzeltme (dosya/bölüm) | Kabul örneği karşılama |
| --- | --- | --- | --- |
| Slot-scope refs | 8 dal alanı tanımsızdı (F1–F4, reason, gap'ler, resolution) | `schema-draft.json` slot_schema: 8 açık tanım + `presence` notları; `presence_authority` beyanı; adjudication `final_field_scope` + `final_fields` | Linter undeclared field bulmaz (komut 03 ile hesaplanarak doğrulandı) |
| Nested drift riski | Nested şekil üst düzeyden kopabilirdi | `ref: #/fields/F1..F4` + kayıpsız şekil kopyası; drift kontrolü (nested values/requires == üst düzey) | Nested sözleşme drifti yok (komut 03) |
| Gap/resolution disiplini | Gap değer/reason koşulları metindeydi | `f3_gap` tek-değer enum + presence; `f4_gap` reason'lı nesne; `applicability_resolution` boolean+reason, non-conditional'da yasak | Yanlış-dal gap/reason reddedilir (komut 03 matris kontrolü) |

## Korunanlar (yeniden tasarım yok)

- R4 `presence_branches` dal mantığı (kural metinleri aynen durur; makine listeleri eklendi).
- Adjudication final dalları mantığı (alan listeleri eklendi).
- Rubrik metni: `rubric-ref-note.md` kısa not; `../E1b-r4/rubric-draft.md` §8P geçerli.
- Sınır örnekleri: B-7U (E1b-r4) geçerli; bu turda etkilenen örnek yok.
- E1c/E2c devirleri açık bırakıldı.

## Etkilenen dosyalar

- Değişen (bu dizinde yeni): `schema-draft.json` (v0.6.0), `rubric-ref-note.md`.
- Değişmeyen: önceki 5 paket, mühürlü belgeler, stimulus, audit/QC, insan rating'leri, üretim kodu.
