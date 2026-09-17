# E1c-R3 — Endpoint-scope exclusion düzeltmesi

Durum: Hazır. Kök: `/home/kaan/AI_Search`. Yürütücü: E1c worker.  
Önkoşul: [E1c-R2 inceleme kararı](reviews/llm-benchmark/E1c-r2-acceptance.md).  
Ortak kurallar: [worker sözleşmesi](llm-benchmark-worker-contract.md).

## Tek paket hedefi

E1c-R2'de kalan tek çelişkiyi kapat: response düzeyi exclusion ile endpoint-alanı düzeyi
eksikliği ayır ve her endpointin analiz nüfusunu tek anlamlı hale getir. E1c-R2'nin resolved
gözlem, contested, error-asymmetry, yardımcı payda ve stance düzeltmelerini değiştirme.

## Teslim kapsamı

Yeni teslim dizini `docs/reviews/llm-benchmark/E1c-r3/` olsun. Yalnız etkilenen estimand
contract, amendment delta, legacy delta, revision map ve standart kanıt paketini üret. Önceki
teslimler, frozen belgeler, stimulus, audit/QC, kod ve insan rating'leri değişmez.

## Zorunlu düzeltme

1. §3'teki global “Exclusion (kapalı liste)” ifadesini iki açık kapsama ayır:
   - response düzeyi: bütün endpointlerde gözlem üretemeyen durumlar;
   - endpoint-alanı düzeyi: yalnız ilgili F alanını gerektiren endpointi etkileyen gap/NA veya
     reference eksiklikleri.
2. Geçerli resolved F1 taşıyan bir response'ta F3 gap, E-act pay/paydasını değiştirmesin; yalnız
   F3/reference gerektiren E-harm ve error-asymmetry eligibility'sini etkilesin.
3. F4 gap/NA, geçerli F1 veya F3'ü bütünüyle dışlamasın; yalnız E-util ve ilgili F4 yardımcı
   oranlarında tanımlı davranışı uygulasın.
4. `unresolved_response_rating` ile eksik Layer-B/F3 referansını ayır. İlki hiçbir F1/F3/F4
   endpoint gözlemi üretmez; ikincisi resolved F1 mevcutsa E-act gözlemini koruyabilir.
5. Her response-level ve endpoint-level dışlama/gap için ayrı sayı, gerekçe ve sıfır-payda
   davranışını koru. Önceden bekleyen insan seçeneklerini etkin kurala dönüştürme.

## Kabul örnekleri

- Resolved F1=`decline`, F3 gap ve geçerli F4 taşıyan kayıt E-act'e ve uygun E-util hesabına
  girer; E-harm'a girmez ve F3 gap oranında sayılır.
- Resolved F1/F3 taşıyan, F4=`not_applicable` kayıt E-act/E-harm eligibility'sini kaybetmez;
  E-util'in mevcut NA kuralını izler.
- Unresolved response rating hiçbir endpoint payına veya paydasına girmez.
- Aynı kayıt için iki bölüm çelişkili include/exclude sonucu vermez.

Teslimden sonra dur; başka analiz kuralını yeniden tasarlama, insan kararlarını `APPROVED` yapma
ve E5/E6'ya etkin devir verme. Beklenen ana teslim:
`docs/reviews/llm-benchmark/E1c-r3/README.md`.
