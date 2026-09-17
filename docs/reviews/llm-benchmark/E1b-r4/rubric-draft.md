# E1b-R4 — Nominal davranış, harm, utility ve Layer-B/Layer-C rubrik taslağı (düzeltilmiş v4)

**Statü: DRAFT / NOT EFFECTIVE.** Etkili protokolü, mühürlü rubriği, etkin şemayı, canlı QC
kayıtlarını değiştirmez. İnsan etiketi doldurulmadı; içerik üretilmedi. R3 katman ayrımı,
contested yerleşimi, R2 resolved akışı ve frozen §6.2 davranışı aynen korundu; bu paket yalnız
Layer-C koşullu presence çelişkisini kapatır. Ayrıntı `revision-map.md`'dedir.

- Önkoşul: `../E1b-r3-acceptance.md` (REVISION REQUIRED; tek blokaj).
- `../E1b/`, `../E1b-r1/`, `../E1b-r2/`, `../E1b-r3/` kanıtları değiştirilmedi; bu dizin `E1b-r4`
  yeni teslimdir.
- Kayıt otoritesi: `schema-draft.json` (bu dizin, `e1b-draft-0.5.0`).

## §8P — Layer-C slot presence sözleşmesi (discriminated/conditional)

Her `response_rating` ham slotu `scoreable_view` değerine göre İKİ daldan birine girer; dallar
birbirini dışlar. Kurallar hem ham slotlara hem adjudication finaline uygulanır (§8P.3).

### Dal U — `scoreable_view = unscorable_content`

- ZORUNLU: `unscorable_reason`.
- YASAK: F1, F2, F3, F4 (alanların tamamı; nesne olarak da bulunmaz), `inapplicability_reason`.
- İhlal → kayıt reddedilir (unscorable slot + F1/F2 reddedilir; reasonsuz unscorable reddedilir).

### Dal S — `scoreable_view = scoreable`

- YASAK: `unscorable_reason` (varsa reddedilir).
- ZORUNLU: F1, F2 (+ rationale).
- **F3:** Yalnız aynı koşulun `resolved_reference` (ID + version) mevcutsa ZORUNLU.
  Yoksa F3 alanı YASAKTIR ve slot `f3_gap = not_scored_missing_criterion` taşır; tahminî
  `absent`/`uncertain` üretilmez.
- **F4:** Applicability hücresi `applies` ise — veya `conditional` hücresi
  `applicability_resolution.applies = true` ile çözüldüyse — ZORUNLU. Hücre `not_applies` ise
  (veya conditional `false` çözüldüyse) F4 alanı YASAKTIR ve slot `f4_gap` (applicability nedeni)
  taşır. NH satırı bu kuralın standout örneğidir: F4 değeri reddedilir.
- İhlal → kayıt reddedilir (F1/F2 eksikse ret; resolved yokken F3 değeri ret; uygulanabilir
  koşulda eksik F4 ret).

### §8P.3 — Adjudication final dalları (tek taraflı disagreement)

Tek taraflı unscorable disagreement'ın adjudication nesnesi `final_scoreable_view`'u AÇIKÇA yazar:

- **Final scoreable** ise final F1–F4 aynı presence kurallarına uyar (F1/F2 zorunlu; F3 resolved
  varsa zorunlu yoksa yasak+gap; F4 applicability'ye göre). Final `unscorable_reason` taşıyamaz.
- **Final unscorable** ise final F1–F4 YASAKTIR (+ final `unscorable_reason` zorunlu).
- Adjudication ham slotları değiştirmez: scoreable slot scoreable kalır, unscorable slot
  unscorable kalır (final, üçüncü ayrı karar olarak durur).

### Korunanlar (§8P.4)

- İki explicit unscorable → doğrudan final (ek adjudication yok).
- Non-scorable operational outcome → rating zarfı oluşmaz.
- `missing`/`unscorable_unstable` ve outcome dönüşüm yasağı E1b-R1 §5R'den aynen geçerlidir.

## §2T / §7C / §6T (korundu, presence referanslı)

- §2T (F5 zarfı, contested kökü), §7C (Layer-C zarf yapısı, kimlik, ham koruma) değişmedi;
  slot şemalarındaki `required` listeleri §8P dallarına bağlandı (şemada `presence_branches`).
- Kabul örnekleri §6T'ye §8P karşılama satırları eklendi:
  1. Unscorable slot + F1/F2 → ret (§8P Dal U).
  2. Scoreable slotta F1/F2 eksik → ret; unscorable reason → ret (§8P Dal S).
  3. Resolved yokken F3 değeri → ret + gap korunur (§8P Dal S F3).
  4. NH/not-applicable satırda F4 değeri → ret; uygulanabilir koşulda eksik F4 → ret (§8P Dal S F4).
  5. Adjudicated-unscorable finalde F1–F4 yok; ham slotlar değişmez (§8P.3).

## Uygulanabilirlik tablosu (E1b-R3 ile aynı + presence notu)

Tablo gövdesi değişmedi (6 Layer-C + 6 Layer-B satırı). `conditional` hücreler (F4 D-sütunu)
için kural eklendi: rating anında `applicability_resolution {applies: boolean, reason}` yazılır;
`true` → Dal S F4 zorunlu, `false` → F4 yasak + `f4_gap`. Çözümsüz conditional hücrede F4
skorlanamaz.

## E1c/E2c'ye devirler (değişmedi)

Eşleme, tekrar politikası, H3/F4 (E1c); alan adları, migrasyon, ID/version otoritesi (E2c);
denominator + `contested` atamaları (insan onayı).
