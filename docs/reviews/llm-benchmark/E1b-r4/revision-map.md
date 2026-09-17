# E1b-R4 — Revizyon haritası (revision map)

E1b-R3 acceptance'taki tek koşullu-presence blokajının `E1b-r4` karşılığı. `../E1b/`,
`../E1b-r1/`, `../E1b-r2/`, `../E1b-r3/` kanıtları değiştirilmedi. Korunanlar: R3 katman ayrımı,
contested yerleşimi, R2 resolved akışı, frozen §6.2 davranışı, nominal taxonomy,
output-merkezlilik, ayrı harm/utility, no-composite, kimlik/ham-koruma kuralları,
`DRAFT / NOT EFFECTIVE`.

| Blokaj | E1b-R3 kusuru | Düzeltme (dosya/bölüm) | Kabul örneği karşılama |
| --- | --- | --- | --- |
| Koşullu presence | Dal U'da F1–F4 koşulsuz zorunluydu; F3/F4 presence koşulsuzdu; adjudication final dalları tanımsızdı | `rubric-draft.md` §8P (Dal U/S + §8P.3 final dalları + §8P.4 korunanlar + §6T karşılama); `schema-draft.json` `presence_branches`, adjudication `requires_conditional` finalleri, F3 `f3_gap`, F4 `f4_gap` + `applicability_resolution`, 6 yeni yasak; `boundary-cases-r4.md` B-7U | 5 kabul örneği §6T'de birebir karşılandı (unscorable+F1/F2 ret; scoreable eksiklik/ek-alan ret; kritersiz F3 ret+gap; NH F4 ret + uygulanabilir eksik ret; adjudicated-unscorable finalde F1–F4 yok, ham korunur) |

## Korunanlar (yeniden tasarım yok)

- R3 zarf yapısı, katman/zaman, çapraz-katman yasakları, kimlik kuralları.
- R2 resolved ID/version bağı, provenance akışı, sessiz-seçim yasağı.
- Frozen §6.2 üç durum davranışı (uygulama yeri §7C zarfı).
- Contested kökü + enum ayrıklığı + D-A/D-B onaysızlığı.
- E1b örnek 1/3/4/6, E1b-R1 B-5R/B-8R, E1b-R2 B-2S/B-9S, E1b-R3 B-7T/B-8T geçerli.
- E1c/E2c devirleri açık bırakıldı.

## Etkilenen dosyalar

- Değişen (bu dizinde yeni): `rubric-draft.md` (v0.5.0), `schema-draft.json` (v0.5.0),
  `boundary-cases-r4.md` (B-7U revize).
- Değişmeyen: önceki 4 paket, mühürlü belgeler, stimulus, audit/QC, insan rating'leri, üretim kodu.
