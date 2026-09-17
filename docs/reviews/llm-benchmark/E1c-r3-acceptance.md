# E1c-R3 — Ana inceleyici kararı

Tarih: 2026-09-10. İnceleyici: Sol. Durum: **ACCEPTED AS WORKER DRAFT; İNSAN BİLİMSEL KARARLARI BEKLİYOR.**

## Kabul edilen kapsam

[E1c-R3 briefindeki](../../llm-benchmark-E1c-r3-task.md) tek blokaj kapatılmıştır.
`estimand-contract.md` artık bütün endpointleri etkileyen response-düzeyi durumları (§3A) ile
yalnız ilgili alanı kullanan endpointi etkileyen eksiklikleri (§3B) ayırır. Global exclusion
listesi kaldırılmıştır.

Kabul örnekleri tek anlamlıdır:

- Resolved F1 + F3 gap + geçerli F4 kaydı E-act ve uygun E-util hesabına girer; E-harm'a
  girmez ve F3 gap oranında sayılır.
- Resolved F1/F3 + F4 `not_applicable` kaydı E-act/E-harm eligibility'sini korur ve E-util NA
  kuralını izler.
- Unresolved response rating hiçbir F1/F3/F4 endpoint gözlemi üretmez.
- Eksik Layer-B/F3 referansı, resolved F1 mevcutsa E-act gözlemini düşürmez.

E1c-R1 ve R2'de doğrulanan resolved observation, canonical job, contested seçenekleri,
standalone error-asymmetry, yardımcı paydalar, CI seçenekleri ve kategori × assistant-stance
kuralları korunmuştur. Bu kabul E1c zincirinin worker taslağını kapatır; seçeneklerin bilimsel
onayı veya amendment yürürlüğü anlamına gelmez.

## Bağımsız kanıt

- Altı komut kaydı exit 0'dır; stdout/stderr/combined hedefleri mevcuttur.
- `run-outputs.sha256`, belge bağlantıları ve `git diff --check` geçti.
- E1c, E1c-R1 ve E1c-R2 paketlerinin manifestolu dosyaları değişmemiştir.
- McNemar değeri `1.862645149230957×10^-9`; KÖ-3 değeri
  `P(X≥6)=0.5281675158588918` olarak yeniden hesaplandı.
- Stimulus SHA-256 değeri `2f78e79e19d844b84b6bc06a0c2bef47e19283cc7c54b91f6ae283e1a74af077`
  olarak kaldı. Audit geçmişleri 51 ve 5 satırla sırasıyla `e145afed…` ve `23755e0f…`
  hashlerinde kaldı. Frozen dosyalara, koda veya insan rating'lerine yazılmadı; API çağrısı yoktur.

## Karar ve sonraki kapı

E1c-R3 için worker revizyonu gerekmiyor. E1a, E1b ve E1c taslaklarındaki açık bilimsel
seçenekler insan araştırmacı tarafından karara bağlanmadan E1 onaylanmış sayılmaz; E5/E6
önkoşulları açılmaz. E0 kabulüne bağlı ve bu kararlardan bağımsız sıradaki worker teslimi
[E2a](../../llm-benchmark-E2a-task.md)'dır.
