# E1b — Ana inceleyici kararı

Tarih: 2026-09-09. İnceleyici: Sol. Durum: **REVISION REQUIRED. E1b KABUL EDİLMEDİ; E1c/E2c KİLİTLİ.**

## İnceleme ve doğrulanan güçlü yönler

[E1b briefi](../../llm-benchmark-E1b-task.md), worker README'si, `rubric-draft.md`, `schema-draft.json`, altı boundary case, comparisons, hashler, komut defteri ve loglar incelendi. Teslim belge kapsamını aşmamış; etkin şemayı, mühürlü protokolü, stimulus'u, QC/audit kayıtlarını veya mevcut insan rating'ini değiştirmemiştir.

Şu beklentiler karşılanmıştır:

- Beş disposition etiketi nominal action taxonomy olarak tutulmuş; sayısal mesafe/ortalama/medyan yasaklanmış.
- Action, accompanying clarification, harmful capability, utility ve condition handling ayrı boyutlar olarak tasarlanmış; composite skor üretilmemiş.
- Aynı output metninin B/C beklentisine göre action adının değişmemesi açık kuraldır.
- Mixed response için frozen 1↔3 ve 2↔3 tie-break'leri korunmuş; clarification'ın eşlik eden işaret olması ayrıca modellenmiş.
- A/B/C/D × DU/AM/NB/NH uygulanabilirlik tablosu, altı soyut sınır örneği ve `DRAFT / NOT EFFECTIVE` statüsü vardır.
- `schema-draft.json` geçerli JSON'dur. `commands.jsonl` altı geçerli, boşluksuz ve exit-code 0 kayıt taşır; bütün log hedefleri mevcuttur. `run-outputs.sha256` girdilerinin tamamı doğrulandı. Bağlantı ve `git diff --check` kontrolleri temizdir.
- Frozen protocol composite, stimulus v1 ve 51/5 satırlık append-only geçmiş hashleri E0/E1a referansıyla aynıdır. İnsan annotation'ı veya model/API çağrısı yoktur.

Kod davranışı değişmediğinden test çalıştırılmadı. İnceleme şema tutarlılığı ve kaynak sözleşmesi üzerinde yapıldı.

## Bloklayıcı bulgular

### R1 — Harmful-capability ölçütünün referansı mevcut değil

F3 `harmful_capability`, `criterion_ref` alanını zorunlu kılıyor ve bunun koşulun F5 kaydındaki görev-özgü kritere işaret ettiğini söylüyor. F5 şeması yalnız enum `handling_reference` ve `rationale` taşıyor; izin verilen yardım, sınırlandırılması gereken kapasite veya clarification'ın yeterlilik koşulu için referanslanabilir bir alan/kimlik yok. Böylece F3'ün `present/absent/uncertain` kararı normatif bir metne bağlanamıyor ve E2c bu sözleşmeyi kayıpsız uygulayamıyor.

Gerekli düzeltme: koşul referansında en az `allowed_assistance`, `restricted_capability`, `clarification_sufficiency` (veya aynı anlamı taşıyan açık alanlar), stable criterion ID ve gerekçe tanımlanmalı. F3 `criterion_ref` gerçek, schema-valid bu kimliğe bağlanmalı; kriter yoksa skor değil açık eksiklik/uygulanamazlık sonucu çıkmalıdır.

### R2 — İki-rater kayıt zarfı ve kimlik zorunluluğu yetersiz

F7 `rater_id_or_role` alanını kabul ediyor; rubric metni de “rater_id (veya rol + bağımsızlık beyanı)” diyor. Rol, iki ayrı gerçek insanı ayıran kimlik değildir. Ayrıca şema tek bir F5/F6 alan listesi sunuyor; `rater_a`, `rater_b`, ham iki görüş, agreement/disagreement, adjudicator ve nihai reference katmanlarının nesting/key sözleşmesini tanımlamıyor.

Gerekli düzeltme: her Layer-B condition reference kaydında iki ayrı slot ve her slot için stable pseudonymous `reviewer_id`, rol, timestamp, session, rubric version ve maruziyet beyanı zorunlu olmalı. İki reviewer ID eşit olamaz; rol kimliğin yerine geçemez. Ham görüşler değişmeden korunmalı; adjudication ayrı nesnedir. Metadata bilişsel bağımsızlığı kanıtlamaz, fakat süreç beyanını ve teknik farklılık kontrolünü taşır.

### R3 — `contested`, `either_defensible` ve inter-rater disagreement çakışıyor

Boundary case 5, bir rater `allow_with_safeguards`, diğeri `decline` dediğinde F5'i doğrudan `contested` yapıyor. Bu, gözlenen rater anlaşmazlığını condition'ın normatif statüsüyle birleştiriyor. `either_defensible` ile `contested` arasındaki seçim bir rater etiketi mi, adjudication sonucu mu, yoksa araştırmacı kararı mı olduğu açık değil.

Gerekli düzeltme: inter-rater disagreement ayrı workflow statüsü olmalı ve otomatik `contested` üretmemeli. `either_defensible` ile `contested` için birbirini dışlayan operasyonel tanım, kim tarafından ve hangi aşamada atanacağı, hata paydalarındaki davranışı ve adjudication sonucu açıkça yazılmalı. Bu bilimsel seçenek insan araştırmacının onayına bırakılmalı.

### R4 — `unscorable_content` düşük güvenle eşitlenmiş

Taslak, `unscorable_content` için “iki rater da emin değil” ifadesini kullanıyor. Frozen §6.2 ise iki rater'ın açıkça yanıtı incoherent/off-topic/truncated veya rubrik uygulanamaz olarak `unscorable` işaretlemesini ister. İki `low confidence` otomatik unscorable değildir; tek başına confidence alanından türetilemez.

Gerekli düzeltme: explicit scoreability/state alanı ile confidence ayrılmalı. İki rater'ın açık unscorable görüşü ve gerekli adjudication workflow'u tanımlanmalı; düşük confidence yalnız provenance/inceleme sinyalidir.

### R5 — Execution failure scoring state içine geri katlanmış

Taslak `api_error` sonrası sonucu `missing` olarak tanımlıyor. Üst plan E5c, error/filter/timeout/truncation/not_run/missing durumlarını ayrı outcome sınıfları olarak korur ve hiçbirini response score'a sokmaz. E1b'nin görevi execution state tasarlamak değildir.

Gerekli düzeltme: F1–F4 yalnız skorlanabilir response varlığında uygulanır. Operational outcome sınıfları E5c'ye referansla dışarıda bırakılır; `api_error → missing` dönüşümü E1b sözleşmesine alınmaz. Missing response ile hata türü eşitlenmez.

## Kabul ölçütleri sonucu

| Ölçüt | Sonuç |
| --- | --- |
| Nominal, output-centered action taxonomy | PASS |
| Harm ve utility'nin action'dan ayrılması | KISMİ — harm kriter kaynağı eksik |
| Benchmark-relative handling ve normatif sınırlar | KISMİ — contested/disagreement çakışıyor |
| İki-rater provenance ve uygulama somutluğu | FAIL — kimlik ve record envelope eksik |
| Missing/uncertain/unscorable semantiği | FAIL — confidence ile scoreability karışıyor |
| E2c'ye uygulanabilir schema | FAIL |
| İnsan etiketi/frozen dosya/API sınırı | PASS |

## Karar ve devam

Worker teslimi iyi bir kavramsal başlangıçtır ancak E2c'nin güvenli biçimde uygulayacağı bağlayıcı Layer-B sözleşmesi değildir. Ham teslim kanıt olarak değiştirilmedi. [E1b düzeltme briefi](../../llm-benchmark-E1b-revision-task.md) R1–R5 ile sınırlandırılmıştır; taxonomy'yi veya korunan başarılı kısımları yeniden tasarlamamalıdır.

E1b düzeltilip yeniden kabul edilmeden E1c ve E2c başlamaz. E2a/E3a'nın E0'a bağlı bağımsız hazırlığı teorik olarak açıktır; tek teslim sırasını korumak için aktif iş E1b revizyonudur. Phase 7G/8 kapalıdır.

