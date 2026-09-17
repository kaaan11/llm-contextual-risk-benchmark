# E1c-R1 — Ana inceleyici kararı

Tarih: 2026-09-10. İnceleyici: Sol. Durum: **REVISION REQUIRED. E1c-R1 KABUL EDİLMEDİ; E1 BİLİMSEL KARAR KAPISI AÇIK KALDI.**

## Doğrulanan düzeltmeler

[E1c-R1 briefi](../../llm-benchmark-E1c-r1-task.md) ile teslimdeki amendment, estimand
sözleşmesi, legacy delta, revision map ve kanıt paketi karşılaştırıldı. Endpoint durumları için
pay/payda seçenekleri, model/run boyutlarını koruyan canonical logical-job kimliği,
`stratified_by_assistant_stance` çıktısı, CI seçenekleri ve D-A/D-B insan kararları görünür hale
getirilmiştir. Taslak `DRAFT / NOT EFFECTIVE` kalmış; frozen dosya, insan annotation'ı, kod veya
API çağrısı üretilmemiştir.

Altı kayıtlı komutun exit kodları ve logları, checksum manifestosu, belge bağlantıları ve
`git diff --check` bağımsız kontrol edildi. Stimulus ile append-only audit geçmişleri değişmedi.
30/0 McNemar exact two-sided sonucu `1.862645149230957×10^-9`; KÖ-3 için beklenen değer `5.75`
ve `P(X≥6)=0.5281675158588919` olarak yeniden hesaplandı.

## Bloklayıcı eksikler

### R1 — Endpoint gözlemi için tek resolved label-of-record tanımlı değil

Analiz `valid(i,c)` ve “F1 görüşleri” üzerinden tarif ediliyor. E1b ise her yanıt için iki ham
rater görüşü ve gerektiğinde adjudication üretir. Ham rater görüşleri model tekrarı değildir ve
iki kez sayılamaz. Her logical response en fazla bir `resolved_response_rating` üretmeli: rater
uzlaşması veya tamamlanmış adjudication bu kaydın kaynağı olmalı; unresolved kayıt hiçbir
F1/F3/F4 endpoint gözlemi üretmemelidir. Üç provider tekrarı, iki rater olsa da en fazla üç analiz
gözlemidir.

### R2 — Contested davranışı kapalı exclusion listesiyle çelişiyor

`estimand-contract.md` §3, `contested handling` durumunu koşulsuz dışlama listesine alırken §6
D-A/D-B seçiminin henüz yapılmadığını söyler. İnsan seçimi yapılana kadar contested davranışı
etkin bir exclusion kuralı değildir; iki seçenek ayrı ve sonuç üretmeyen taslaklar olarak kalmalıdır.

### R3 — Legacy error-asymmetry yanlış endpoint paydasına bağlanmış

`legacy-delta.md` L-05, error-asymmetry paydasını E-harm ve harm-uncertain seçeneklerine bağlar.
Bu ölçümün kendi sözleşmesi gerekir: uygun B/C çifti, resolved koşul-uygunluk referansı ve resolved
yanıt eyleminden türetilen ikili violation sonucu, ardından discordant hücreler. E1b handling
etiketlerinin frozen üçlü karara eşlenmesi insan kararı bekliyorsa sonuç da pending kalmalıdır;
E-harm uncertain seçimi bu ölçümün paydasını belirlememelidir.

### R4 — Yardımcı uncertain ve partial oranlarının paydaları belirtilmemiş

H-U1 “ayrı uncertain rate”, H-T1b “ayrı partial rate” ister; fakat bu oranların pay ve paydası
yazılmamıştır. Her seçenek için hangi resolved yanıtların paydaya girdiği, payın hangi label olduğu
ve sıfır payda davranışı açık olmalıdır.

Assistant-stance mappingi veriyle uyumludur: AM'de yedi özdeş; DU=30, NB=7 ve NH=6 kayıtta
assistant turu farklıdır. Revizyonda kategori × stance hücreleri korunmalı ve bu eksenler arasında
sonradan örtük havuzlama yapılmamalıdır.

## Karar ve devam

Teslim önceki beş blokajın ana kısmını kapattı, ancak E6a'nın rater görüşlerini gözlem gibi sayma
veya payda kararı icat etme olasılığı sürüyor. Ham E1c-R1 teslimi korunacaktır.
[E1c-R2 briefi](../../llm-benchmark-E1c-r2-task.md) yalnız yukarıdaki dört blokajı ve stance
hücresi açıklığını kapsar. E1c-R2 kabulü ve insan bilimsel kararları olmadan E1 kapanmaz; E5/E6
etkinleşmez.
