# E1b-R6 — Revizyon haritası (revision map)

E1b-R5 acceptance'taki ref-çözülebilirlik blokajının `E1b-r6` karşılığı. Önceki 6 paket
(`E1b` … `E1b-r5`), kod, frozen dosyalar, stimulus, audit/QC ve insan rating'leri değişmedi.
Korunanlar: R4/R5 dal mantığı, enum'lar, katman/zaman, kimlik/ham-koruma, resolved akışı,
contested yerleşimi, §6.2, uygulanabilirlik gövdesi, B-7U, `DRAFT / NOT EFFECTIVE`.

| Blokaj | E1b-R5 kusuru | Düzeltme (dosya/bölüm) | Kabul karşılama |
| --- | --- | --- | --- |
| Çözülemez `$ref` | `#/fields/F1..F4` dizi-içi geçersiz pointer; linter traverse etmiyordu | `$defs` canonical harita + tüm nested/final girdilerde gerçek `$ref`; linter token-token traverse + hedef `def_id`/`def_kind` doğrulaması | Bütün ref'ler doğru hedefe ulaşır; unresolved listesi boş (komut 03) |
| Serbest-metin final scope | `final_field_scope` metni; final payload şemasızdı | `final_payload_schema` (discriminator + 2 dal + `$ref` alanlar); adjudication `final_payload.$ref` ile bağlanır | Final payload kapalı ve refli; tahmine yer yok (komut 03) |
| Kopya-drift riski | Nested şekil kopyaları üst düzeyden kopabilirdi | Kopyalar kaldırıldı (`$ref` + presence notu); linter şekil-anahtar yasağını denetler | Drift imkânsız (tek kaynak); kontrolde doğrulandı |

## Korunanlar (yeniden tasarım yok)

- Dal/final mantığı metinleri (R4/R5 ile aynı anlam; mekanizma değişmedi).
- Sınır örnekleri: B-7U geçerli; bu turda etkilenen örnek yok.
- E1c/E2c devirleri açık bırakıldı.

## Etkilenen dosyalar

- Değişen (bu dizinde yeni): `schema-draft.json` (v0.7.0), `rubric-ref-note.md`.
- Değişmeyen: önceki 6 paket, mühürlü belgeler, stimulus, audit/QC, insan rating'leri, üretim kodu.
