# E1c — Ana inceleyici kararı

Tarih: 2026-09-10. İnceleyici: Sol. Durum: **REVISION REQUIRED. E1c KABUL EDİLMEDİ; E1 BİLİMSEL KARAR KAPISI AÇIK KALDI.**

## Doğrulanan güçlü yönler

[E1c briefi](../../llm-benchmark-E1c-task.md), amendment taslağı, estimand sözleşmesi,
legacy haritası ve kanıt paketi incelendi. Teslim şu hedefleri karşılar:

- Frozen ordinal-distance, D-state, modal-effect ve Wilcoxon kurallarını açık amendment konusu
  yapar; eski metinleri sessizce değiştirmez.
- E-act, E-harm ve E-util ayrı; madde-eşit ve kategori bazlı başlangıç önerileri olarak sunulur.
- DU=30, DU-D=14, D-kohortu, AM, NB ve NH örneklem büyütmek için havuzlanmaz.
- Mode ikincil tutulur; McNemar yalnız paired-binary error-asymmetry olarak adlandırılır.
- Missing/error/duplicate/exclusion, zero denominator, multiplicity ve H3/F4 seçenekleri görünürdür.
- Taslak `DRAFT / NOT EFFECTIVE` kalır; insan onayı ve yeni freeze olmadan E5/E6'ya etkin devir yoktur.

Üç karşıörneğin sayıları bağımsız doğrulandı. 30/0 McNemar exact two-sided değer
`1.862645149×10^-9`'dur. Eş dağılımlı modal örnekte 16 D'siz madde için `p=.25` ve 14 D'li
madde için `p=.125`; beklenen pozitif sayı `5.75`, en az altı olasılığı `0.5281675`'tir.

Kanıt paketi de geçti: altı exit-0 komut kaydı, log hedefleri, checksumlar, bağlantılar ve
`git diff --check` doğrulandı. Stimulus ve append-only audit geçmişleri değişmedi; kod, insan
annotation'ı veya API çağrısı yoktur.

## Bloklayıcı eksikler

### R1 — Harm ve utility estimand paydaları kapalı değil

E-harm “harm-present oranı”, E-util “completion oranı” olarak yazılmıştır; fakat E1b'nin
`uncertain`, `partial`, `not_completed`, `not_applicable`, F3 gap ve F4 applicability durumlarının
hangisinin paya, paydaya veya ayrı rapora girdiği tanımlanmamıştır. Bu seçimler sonucu değiştirebilir
ve E6a worker'ına bırakılamaz. Her endpoint için pay, payda, madde-içi oran ve dışlanan/ayrı
raporlanan durumlar formülle veya kapalı tabloyla belirtilmelidir.

### R2 — Duplicate kimliği model/run boyutunu kaybediyor

Duplicate anahtarı yalnız `item × condition × repetition` olarak verilmiştir. Çoklu model veya
ayrı run kayıtlarında aynı bilimsel hücreler meşru olarak tekrar eder. Anahtar en az protocol/data
version, run ID, requested model identity, item, condition ve repetition/seed kapsamını ayırmalı;
aynı logical job'ın yeniden dispatch'i attempt ledger'da kalmalı ve yeni gözlem sayılmamalıdır.
Kesin alan sahipliği E5a/E5c'ye devredilebilir, fakat analizde hangi kimlikle duplicate sayıldığı
şimdiden açık olmalıdır.

### R3 — Zorunlu assistant-stance tabakası yok

AGENTS.md, Phase 8'de asistan turu özdeş AM ile farklı DU/NH gruplarının
`stratified_by_assistant_stance` altında ayrı ele alınmasını zorunlu kılar. Taslak AM/DU/NH
kategorilerini ayrı saysa da bu adla zorunlu strata çıktısı, mapping ve havuzlama yasağı
tanımlamaz. Kategori ve assistant-stance iki ayrı eksen olarak açıkça raporlanmalıdır.

### R4 — CI dili kendi içinde çelişkili

Endpoint sunumu ve amendment “exact CI” vaat ederken §5, eşleşmiş fark ortalamaları için yöntemi
TBD bırakır. Clopper–Pearson yalnız tek oran içindir; madde-eşit eşleşmiş fark vektörünün CI'ı
olarak doğrudan kullanılamaz. İnsan kararı verilene kadar metin “CI yöntemi TBD; exact olduğu
iddia edilmez” demeli veya aday yöntemleri, varsayımları ve küçük-n sınırlarını seçenek olarak
sunmalıdır.

### R5 — Onaysız denominator seçeneği uygulanmış gibi yazılmış

§3, `either_defensible`/`contested` durumlarını hata oranları dışında bırakır; aynı cümle D-A/D-B
onayının beklediğini söyler. E1b'de bu payda davranışı insan kararı olarak açık bırakılmıştır.
Taslak seçenekleri ayrı göstermeli; karar verilmeden tek davranışı sözleşme gibi kullanmamalıdır.

## Karar ve devam

Teslim güçlü bir ilk amendment taslağıdır, ancak E6'nın deterministik uygulayacağı kapalı estimand
sözleşmesi değildir. Ham E1c teslimi değiştirilmeden korunacaktır.
[E1c-R1 briefi](../../llm-benchmark-E1c-r1-task.md) yalnız R1–R5 düzeltmeleriyle sınırlıdır.
E1c-R1 kabulü ve ardından insan bilimsel kararları olmadan E1 kapanmaz; E5/E6 etkinleşmez.

