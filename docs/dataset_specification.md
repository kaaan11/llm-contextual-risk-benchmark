# Dataset Şartnamesi

## 1. Amaç

Bu belge, LLM Security–Usability Benchmark için Phase 2’de tasarlanan ve Phase 7’de `0.2.0` paired multi-turn alanlarıyla genişletilen veri modelini tanımlar. Şema; benign örnekleri, adversarial değerlendirmeleri, multi-turn konuşmaları, uzman anotasyonlarını, model çıktısını, gecikme ölçümlerini ve istatistiksel analiz metadata’sını aynı araştırma kaydına bağlayacak şekilde tasarlanmıştır.

Phase 7 uzantısı uygulanmış olsa da bu uzantı kapsamında yeni 50 örnek, ölçülmüş sonuç veya uzman doğrulaması oluşturulmamıştır. Şema, veri üretimi ve benchmark uygulaması için sözleşme niteliğindedir; beklenen tasarım metadata’sı model sonucu veya expert annotation değildir.

## 2. Tasarım ilkeleri

### 2.1 Kategori üyeliği ile kayıt türünün ayrılması

`dataset_membership` alanı `benign`, `adversarial` ve `multi_turn` üyeliklerini dizi olarak tutar. Bu alanlar zorunlu olarak birbirini dışlamaz; böylece multi-turn bir kayıt aynı zamanda benign veya adversarial değerlendirme kümesine ait olabilir.

`record_type` ise veri yapısını belirtir:

- `single_turn`: tam olarak bir turn içerir.
- `multi_turn`: en az iki turn içerir.

Bu ayrım, “uzman incelemesi”nin kategori değil bir anotasyon özelliği olması ilkesini de korur.

### 2.2 Tekil ve sürümlü kimlikler

Her kaydın değişmez `sample_id` değeri vardır. Kayıt içindeki turn, anotasyon, evaluation, evaluation run ve analysis run nesneleri de ayrı kimlik taşır. Her kayıt ayrıca `record_version` ile sürümlenir.

Bu yapı; tekrar çalıştırma, kısmi veri aktarımı, hata ayıklama ve 3.000+ örneğe ölçeklenme için gereklidir. JSON Schema benzersizliği tüm kayıtlar arasında tek başına garanti edemediğinden, ek doğrulayıcı bunu ayrıca kontrol eder.

### 2.3 Hassas içeriğin ayrıştırılması

`turn.content` ve `evaluation.response` alanları doğrudan metin (`text`) veya güvenli bir referans (`content_ref`) taşıyabilir. Her ikisi de `redaction_status` ile birlikte saklanır; isteğe bağlı SHA-256 özeti içerik bütünlüğünü kontrol etmeye yardımcı olur.

Bu tasarım, kamuya açık temizlenmiş veri ile kontrollü veya özel ham verinin aynı kimliklendirme sisteminde tutulmasını sağlar. Gerçek sırlar, kişisel veriler ve operasyonel zararlı talimatlar bu şema aracılığıyla otomatik olarak güvenli hâle gelmez; veri işleme politikası ayrıca uygulanmalıdır.

### 2.4 Anotasyonların çoklu ve sürümlü olması

Bir kaydın sıfır, bir veya birden çok anotasyonu olabilir. Her anotasyon:

- anonimleştirilmiş `annotator_id` veya kimliksiz bırakılmış puanlayıcı türünü,
- `guideline_version` değerini,
- anotasyon zamanını,
- etiketleri,
- isteğe bağlı soyut gerekçeyi

taşır. `expert_reviewed` ve `adjudicated` durumları, uzman incelemesini normal anotasyondan ayırır; gerçek uzman incelemesi yapılmadan bu değerler kullanılmamalıdır.

Etiket alanları, Phase 1’de tanımlanan boyutları destekler: `adversariality`, `maliciousness`, `legitimate_plausibility`, `context_dependence`, `expected_risk`, `refusal_appropriateness` ve `confidence`. Tehdit ve benign kategori kodları da ayrı listeler olarak tutulur.

### 2.5 Model değerlendirmesinin run tabanlı izlenebilirliği

`evaluation_runs` dizisi bir değerlendirme koşusunun sabit metadata’sını tutar: model sağlayıcısı, adı, sürümü, benchmark yapılandırması, bağlam modu, veri sürümü ve ortam referansı.

Kayıt içindeki `evaluations` dizisi ise o örneğin belirli run içindeki sonucunu tutar. Her evaluation, `run_id` ile bir run’a bağlanır. Böylece model sürümü veya system configuration değiştiğinde sonuçlar birbirine karıştırılmaz.

Başlangıçtaki üç yapılandırma:

| Kod | Anlam |
|---|---|
| `baseline` | İlave savunma katmanı yok |
| `single_prompt_defense` | Yalnızca mevcut isteği analiz eden katman |
| `multi_turn_context_defense` | Mevcut istek ve konuşma bağlamını analiz eden katman |

`context_mode` ayrıca `current_prompt_only` veya `conversation_context` olarak tutulur. Bu iki alanın birlikte saklanması, yapılandırma ile gerçek giriş bağlamının birbirine karıştırılmasını önler.

### 2.6 Sonuçlar ile analiz çıktılarının ayrılması

Model evaluation kaydı, örnek seviyesindeki gözlemi tutar: yanıt referansı, latency, kaynak kullanımı ve temel outcome etiketleri. `analysis_runs` ise bu gözlemlerden türetilen istatistikleri tutar.

Bir `analysis_run` şu bilgileri taşır:

- analiz türü,
- giriş dataset sürümü,
- analiz kodu sürümü,
- filtreler,
- metrik tahmini,
- örneklem büyüklüğü,
- yöntem,
- varsa güven aralığı, etki büyüklüğü, p-değeri ve artifact referansı.

Bu ayrım, ham gözlem ile sonradan üretilen istatistiksel özeti ayırır ve sonuçların yeniden hesaplanmasını kolaylaştırır.

## 3. Kök dataset manifesti

Kök nesnenin zorunlu alanları:

| Alan | Açıklama |
|---|---|
| `schema_version` | Kullanılan JSON Schema sürümü; mevcut sürüm `0.2.0`, eski `0.1.0` kayıtları desteklenir |
| `dataset_id` | Veri kümesinin stabil kimliği |
| `dataset_version` | Veri içeriğinin sürümü |
| `release_profile` | `private`, `controlled` veya `public_sanitized` |
| `records` | Örnek/kayıt nesneleri dizisi; şu an boş olabilir |

İsteğe bağlı `evaluation_runs`, `analysis_runs` ve `provenance` alanları metadata’yı kökte toplar.

`records` dizisinin boş olmasına izin verilmesinin nedeni, Phase 2’de yalnızca şemanın teslim edilmesi ve gerçek örneklerin sonraki onaydan sonra üretilmesidir.

## 4. Record modeli

Bir record en az şu alanları taşır:

- `sample_id`
- `record_version`
- `dataset_membership`
- `record_type`
- `split`
- `sensitivity`
- `turns`
- `annotations`
- `evaluations`

### 4.1 Turn modeli

Her turn; `turn_id`, sıfırdan başlayan `sequence`, `role` ve içerik nesnesinden oluşur. Roller `system`, `developer`, `user`, `assistant` veya `tool` olabilir.

Turn-level metadata, bağlam sinyallerini, zaman bilgisini ve kaynak kodunu taşıyabilir. Multi-turn çalışmanın amacı gereği, önceki turlar son turdan silinmemeli; analiz sırasında `current_prompt_only` ve `conversation_context` koşulları ayrı üretilebilmelidir.

`task_metadata` içindeki `sampling_cell`, `template_id`, `threat_categories` ve `benign_categories` alanları örnekleme hücresini ve üretim ailesini izlemek için kullanılır. Bunlar uzman anotasyonu değildir; veri üretim/provenance metadata’sıdır.

### 4.2 Hassasiyet profili

Her kayıt şu profillerden birini alır:

- `public_sanitized`: kamuya açık, temizlenmiş içerik.
- `controlled`: erişimi sınırlı, araştırma koşullarında kullanılan içerik.
- `private`: yalnızca iç araştırma ortamında bulunan içerik.
- `restricted`: özel güvenlik prosedürü gerektiren içerik.

Bu alan yayın izni değildir; yayın kararı, sorumlu release politikasındaki ayrı inceleme sonucunda verilmelidir.

### 4.3 Phase 7 paired multi-turn modeli

`schema_version: "0.2.0"` ve `record_type: "multi_turn"` kayıtları, aynı canonical final prompt’un iki ayrı değerlendirme koşulunda kullanılabilmesini sağlayan alanları taşır. `canonical_final_prompt` authoritative kaynaktır; `evaluation_conditions.final_prompt_only.prompt` ve full-context içindeki son user turn metni bununla exact string equality kullanılarak eşleştirilir. Proje tarafından açıkça tanımlanmış bir normalizasyon kuralı bulunmadığı için trim, case-fold veya Unicode normalizasyonu uygulanmaz.

`evaluation_conditions.final_prompt_only`, yalnızca canonical final prompt’u; `evaluation_conditions.full_context` ise record’daki tüm turn kimliklerini ve son prompt turn’ünü temsil eder. `full_context.turn_ids` turn sırasıyla birebir aynı olmalıdır. Böylece tekil prompt koşulu ile tam konuşma koşulu aynı örnek kimliği ve aynı final prompt üzerinden karşılaştırılabilir.

`expected_context_effect`, `expected_risk_profile`, `expected_interpretation` ve gerekçe tasarım aşamasındaki researcher metadata’sıdır. `model_observed_effect` evaluation öncesinde `null` kalır; ileride gözlenen sonuç bu alana yazılırken expected alanları değiştirilmez. `researcher_qc` yalnızca gerçek QC tamamlandıktan sonra `true` yapılabilir. `external_validation_status` gerçek süreç kanıtı olmadan `expert_reviewed` veya `externally_validated` olamaz.

Tek-turn kayıtları aynı dataset içinde tutulabilir ve paired alanlarını gerektirmez. Eski `0.1.0` kayıtları yeniden yazılmadan doğrulanır; v0.2.0 uzantısı yeni multi-turn kayıtlarının açık sözleşmesidir.

Phase 7B özgün kayıtları ayrıca `source: "original"`, record-level `dataset_version: "0.2.0"` ve `source_seed: null` taşır. Public benchmark kavramından esinlenilen ancak dönüştürülen bir kayıt için `source` ve `source_seed` açık provenance ile belirtilmelidir; bu pilotta böyle bir kayıt yoktur.

## 5. Anotasyon ve uzman incelemesi

### 5.1 Ölçek gerekçesi

Şemadaki ortak düzeyler `none`, `low`, `medium`, `high`, `critical` ve `unknown` değerleridir. Bunlar ölçüm sonucu değil, farklı anotasyon boyutlarında kullanılabilecek sıralı kategorilerdir. `unknown`, puanlayıcının yeterli bilgiye sahip olmadığı durumu temsil eder; eksik değerle aynı anlama gelmez.

`refusal_appropriateness` için düzey yerine karar durumu kullanılır: `appropriate`, `inappropriate`, `partial_or_conditional`, `uncertain` veya `not_applicable`. Bu ayrım, reddin risk seviyesinden farklı bir karar olduğunu açık tutar.

`confidence` düşük/orta/yüksek olarak tutulur. Bu alan, etiketin doğruluğu değil, puanlayıcının kendi karar güvenidir.

Kesin tanımlar, örnekler ve puanlayıcı eğitim materyali Phase 3’teki annotation guidelines belgesinde yazılmalıdır.

### 5.2 Uzmanlık iddiasının sınırı

`annotator_type: expert` veya `review_state: adjudicated` yalnızca süreçte gerçekten yetkilendirilmiş inceleme yapıldığında kullanılmalıdır. Şema bu iddiayı doğrulayamaz; süreç kayıtları ve uzman yeterlilik planı ayrıca tutulmalıdır.

Phase 4 itibarıyla anotasyonların kanonik biçimi `dataset/annotation_schema.json` içindeki structured label modelidir. Kayıt içine gömülü `annotations` alanı kullanılırsa aynı model uygulanmalıdır; büyük veya erişim ayrımı gereken veri kümelerinde `sample_id` ile eşlenen sidecar annotation bundle tercih edilir. Mevcut pilot kayıtlarında bu alanlar bilerek boştur.

## 6. Model çıktısı ve metrik girdileri

Evaluation kaydı aşağıdaki gözlemleri destekler:

### Güvenlik

`outcome.attack_success` değerleri `success`, `failure`, `not_applicable` veya `unknown` olabilir. ASR, bu tekil sonuçlardan analiz aşamasında hesaplanmalıdır; şema ASR sonucu uydurmaz.

### Kullanılabilirlik

- `outcome.refusal`: modelin yanıt davranışı.
- `outcome.legitimate_task_completion`: meşru görevin tamamlanma durumu.
- `outcome.task_fidelity`: 0–1 aralığında, `scale_id` ile tanımlanmış skor.

Bu alanlar, benign refusal rate, over-refusal rate, legitimate task completion ve task fidelity hesaplarının girdileridir. Karar kuralları `decision_rule_id` ile sürümlenmelidir.

### Performans

`latency` en az `total_ms` ve `measurement_method` taşır; ayrıştırılabiliyorsa `defense_ms`, `model_ms` ve `queue_ms` de kaydedilir. `resource_usage` CPU zamanı, tepe bellek ve ilave model çağrılarını destekler.

Şema belirli bir gecikme hedefi koymaz. Baseline ve savunma koşullarındaki ölçümler aynı zamanlama protokolüyle toplanmalı; ortalama, medyan ve P95 analiz aşamasında hesaplanmalıdır.

## 7. İstatistiksel analiz modeli

`analysis_result` şu alanları destekler:

- `metric_id` ve `metric_name`,
- `estimate` ve `unit`,
- `sample_size`,
- `group_by`,
- isteğe bağlı güven aralığı,
- isteğe bağlı etki büyüklüğü ve p-değeri,
- kullanılan `method`,
- grafik veya tabloya referans.

Bu esneklik, veri şemasını belirli bir test yöntemine kilitlemez. Uygun yöntem; değişkenin türü, deney tasarımı, puanlayıcı yapısı ve dağılım varsayımları incelendikten sonra seçilmelidir. Uzman anotasyonları için Cohen’s Kappa, Fleiss’ Kappa veya Krippendorff’s Alpha arasından seçim, gerçek anotatör tasarımına bağlıdır.

## 8. Doğrulama kuralları

JSON Schema temel alan, tür, enum ve biçim kısıtlarını ifade eder. `dataset/validate.py` ise şu ilişkisel kuralları ekler:

1. Kök zorunlu alanları ve `schema_version` değerini kontrol eder.
2. `sample_id`, `turn_id`, `annotation_id`, `evaluation_id`, `run_id` ve `analysis_id` tekrarlarını kontrol eder.
3. Multi-turn üyeliği ile `record_type` uyumunu kontrol eder.
4. Tek turlu kaydın bir, multi-turn kaydın en az iki turn içermesini kontrol eder.
5. Turn sıra numaralarının 0’dan başlayıp ardışık olmasını kontrol eder.
6. Turn ve model yanıtında doğrudan metin veya güvenli referans olmasını kontrol eder.
7. Her evaluation’ın kökte tanımlı bir `evaluation_run`a bağlanmasını kontrol eder.
8. Evaluation ve anotasyon tarihleri ile sürüm biçimlerini temel düzeyde kontrol eder.
9. Analysis run’ların giriş dataset sürümünün kök sürümle eşleşmesini kontrol eder.
10. v0.2.0 multi-turn kayıtlarında `conversation_id` ve `sample_id` benzersizliğini kontrol eder.
11. Canonical prompt hash’ini, final-prompt-only kopyasını ve full-context son turn eşitliğini kontrol eder.
12. Full-context turn kimliklerinin record turn sırasıyla eşleşmesini kontrol eder.
13. Expected effect ile model observed effect alanlarını ayırır ve evaluation öncesinde observed effect’in `null` olmasını zorunlu kılar.
14. Authoring, generation assistance, source seed, researcher QC ve external validation değerlerini kontrollü kümelerle sınırlar.

Doğrulayıcı yalnızca hata raporlar; veri içeriğini düzeltmez, redakte etmez veya değiştirmez.

## 9. Bilinen sınırlamalar

- `jsonschema` bağımlılığı olmadan çalışan doğrulayıcı, JSON Schema’nın tüm `enum`, `additionalProperties` ve biçim kurallarını yeniden uygulamaz; üretim hattında bir JSON Schema uyumlu doğrulayıcı da çalıştırılmalıdır.
- Şema, hassas içeriğin gerçekten güvenli olup olmadığını veya `content_ref` hedefinin erişim kontrolünü doğrulayamaz.
- `sample_id` tekrarını kontrol etmek için tüm kayıtların aynı doğrulama kapsamına alınması gerekir.
- Model sağlayıcısı, system configuration ve ortam referansları metadata olarak kaydedilir; içeriklerinin doğruluğu dış süreç gerektirir.
- `task_fidelity` skorunun anlamı `scale_id`ye bağlıdır; ölçek tanımı olmadan sayısal skor karşılaştırılamaz.
- Toplu sonuçlar şemada saklanabilir, ancak istatistiksel uygunluk ve veri sızıntısı riski analizci sorumluluğundadır.
- Henüz veri ayrıştırma, erişim kontrolü, şifreleme ve saklama süresi için operasyonel araç oluşturulmamıştır.

## 10. Önerilen sonraki adım

Şema `0.2.0` uzantısıyla uygulanmış ve test edilmiştir; yeni Phase 7 örnekleri için ayrıca onay beklenmektedir. Sonraki aşamada:

1. Bu uzantı için kullanıcı onayı alınmalı.
2. Onay sonrasında güvenli, operasyonel ayrıntı içermeyen 50 multi-turn örnek hazırlanmalı.
3. Her örnek için researcher QC ve provenance alanları gerçek süreçle doldurulmalı.
4. Model evaluation ve observed effect alanları ayrı bir onaydan sonra üretilmeli.
