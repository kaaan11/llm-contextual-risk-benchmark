# E1b-R3 — Etkilenen sınır örnekleri (revize + güncelleme)

**Statü: DRAFT / NOT EFFECTIVE.** Yalnız E1b-R2 acceptance'taki iki yerleşim hatasından
etkilenen örnekler buradadır. E1b örnek 1/3/4/6, E1b-R1 B-5R, E1b-R2 B-2S/B-9S değişmeden
geçerlidir (tekrarlanmadı). Annotation değildir; corpus kararı vermez; operasyonel içerik taşımaz.

## B-7T (revize): Scoreability akışı Layer-C zarfında

- **Durum A — iki explicit unscorable:** İki Layer-C rater da `scoreable_view=unscorable_content`
  (+ reason) yazdı. **Final `unscorable_content` DOĞRUDAN üretilir; ek adjudication YOKTUR.**
  (Frozen §6.2; uygulama yeri artık `response_rating` zarfıdır.)
- **Durum B — tek taraflı unscorable:** Biri `unscorable_content`, diğeri `scoreable` yazdı.
  Disagreement'tir; Layer-C adjudication bekler.
- **Durum C — iki low confidence:** İki rater da puanladı, ikisi de `low` işaretledi, explicit
  unscorable yok. Sonuç `unscorable_content` DEĞİLDİR.
- **Yerleşim notu (R1):** Bu üç durumun tamamı Layer-C `response_rating` zarfında değerlendirilir.
  Layer-B F5 slotunda `scoreable_view`/`unscorable_reason` BULUNMAZ; böyle bir slot reddedilir.

## B-8T (güncelleme): Timeout/error — zarf yok

- **Kurulum:** Koşul denemesi timeout ile sonuçlandı; yanıt metni yok.
- **Kural uygulaması (düzeltilmiş):** Layer-C `response_rating` zarfı OLUŞTURULMAZ; F1–F4
  YASAKTIR. Kayıt yalnız operational outcome (`timeout`) + `missing_reason` taşır (E5c).
  (E1b-R1 B-8R ile aynı sonuç; gerekçe artık zarf-yokluk kuralıdır, alan-yasağı değil.)
- **Çıkarılmayacak sonuç:** Kayıp satır davranış/harm/utility sayılmaz; pay/payda E1c/E6a'ya aittir.
