# E1b-R4 — Etkilenen sınır örnekleri (revize)

**Statü: DRAFT / NOT EFFECTIVE.** Yalnız E1b-R3 acceptance'taki koşullu-presence blokajından
etkilenen örnek buradadır. E1b örnek 1/3/4/6, E1b-R1 B-5R/B-8R, E1b-R2 B-2S/B-9S, E1b-R3 B-8T
değişmeden geçerlidir (tekrarlanmadı). Annotation değildir; corpus kararı vermez.

## B-7U (revize): Scoreability dalları + presence + adjudicated final

- **Dal U (unscorable slot):** `scoreable_view=unscorable_content` + `unscorable_reason` zorunlu;
  F1/F2/F3/F4'ten herhangi biri varsa kayıt REDDEDİLİR; reason yoksa REDDEDİLİR.
- **Dal S (scoreable slot):** F1 + F2 zorunlu (eksikse RET); `unscorable_reason` varsa RET;
  resolved criterion yokken F3 değeri RET + `f3_gap=not_scored_missing_criterion` korunur;
  NH/not-applicable satırda F3 değil F4 değeri RET + `f4_gap` korunur; uygulanabilir koşulda
  eksik F4 RET.
- **Adjudicated final:** Tek taraflı disagreement sonrası adjudication `final_scoreable_view`'u
  açıkça yazar. Final scoreable → Dal S kuralları (F1/F2 + koşullu F3/F4); final unscorable →
  F1–F4 YOK (+ final reason). Ham scoreable ve unscorable slotlar DEĞİŞMEDEN kalır
  (adjudicated-unscorable finalde bile ham scoreable slot F1/F2'sini korur — final ayrı nesnedir).
- **Korunan:** İki explicit unscorable → doğrudan final; non-scorable outcome → zarf yok.
