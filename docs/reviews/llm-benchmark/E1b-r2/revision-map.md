# E1b-R2 — Revizyon haritası (revision map)

E1b-R1 acceptance'taki iki kalan blokajın `E1b-r2` karşılığı. `../E1b/` ve `../E1b-r1/`
kanıtları değiştirilmedi. Korunanlar: nominal taxonomy, output-merkezlilik, ayrı harm/utility,
no-composite, iki-rater kimliği, ham kayıtların korunması, disagreement/contested ayrımı,
operational-outcome sınırı, soyut örnek disiplini, `DRAFT / NOT EFFECTIVE`.

| Blokaj | E1b-R1 kusuru | Düzeltme (dosya/bölüm) | Kabul örneği karşılama | İnsan kararı gereken |
| --- | --- | --- | --- | --- |
| R1 resolved criterion | Üçlü yalnız ham slotlarda; agreement'ta hangi metnin record-of-reference olduğu + provenance tanımsız; F3 ID yalnız koşulu buluyor | `rubric-draft.md` §2S (resolved nesne, agreement/disagreement yolu, version, sessiz-seçim yasağı); `schema-draft.json` F5 `resolved_reference` + F3 `binds [criterion_id, criterion_version]` + `integrity`; `boundary-cases-r2.md` B-2S/B-9S | Anlaşan iki reviewer → provenance'lı resolved, F3 yalnız ona; üçlü farklı + adjudication yok → resolved ve F3 ret; adjudication hamı değiştirmez, source gösterir | Criterion içerikleri, ID/version atama otoritesi, re-version politikası (E2c + araştırmacı) |
| R2 frozen §6.2 | İki explicit unscorable'a ek adjudication şartı (mühürlü kurala kapı) | `rubric-draft.md` §4S (frozen alıntı + üç durum); `schema-draft.json` `scoreability_final_states` (both→direct, single→adjudication, low-confidence→yok); `boundary-cases-r2.md` B-7S (A/B/C durumları) | İki explicit → doğrudan final; tek taraflı → adjudication; iki low → unscorable yok | Kural değişikliği istenirse resmi protokol eki (bu taslakta yapılamaz) |

## Korunanlar (yeniden tasarım yok)

- E1b-R1'in tamamı (zarf, kimlik kuralı, enum ayrıklığı, adjudication nesnesi, contested,
  §3, §5R, requires koşulları, yasaklar, uygulanabilirlik gövdesi) — bu paket yalnız yukarıdaki
  iki satırı değiştirir/ekler.
- E1b örnek 1/3/4/6, E1b-R1 B-5R/B-8R geçerli (tekrarlanmadı).
- E1c/E2c devirleri + denominator seçenekleri açık bırakıldı.

## Etkilenen dosyalar

- Değişen (bu dizinde yeni): `rubric-draft.md` (v0.3.0), `schema-draft.json` (v0.3.0),
  `boundary-cases-r2.md` (B-2S güncelleme, B-7S revize, B-9S yeni).
- Değişmeyen: `../E1b/*`, `../E1b-r1/*`, mühürlü belgeler, stimulus, audit/QC, insan rating'leri,
  üretim kodu.
