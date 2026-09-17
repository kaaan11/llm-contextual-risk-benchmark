# LLM Benchmark — Bilimsel ve mühendislik değerlendirmesi, eylem planı

Tarih: 2026-09-09  
Durum: **2026-09-10 tarihinde kullanıcı kararıyla donduruldu.** E0, E2a ve E3a kabul edildi; E1a, E1b ve E1c worker taslakları insan bilimsel kararlarını bekliyor. İki bağımsız gerçek rater mevcut değil; aktif worker briefi yok, E2b/E3b ve Phase 8 kilitli. [Dondurma ve yeniden başlatma kaydı](reviews/llm-benchmark/PROJECT-FROZEN-2026-09-10.md).  
İnceleme HEAD'i: `9dd9d31607b3d97c02fe3ef9b7cfb68b4a3ed50e`.  
Biçim referansı: `/home/kaan/sloplab/docs/issue-05-engineering-assessment-and-plan.md`.

Uygulama briefleri: [worker brief dizini](llm-benchmark-worker-index.md).  
Teslim kuralları: [worker teslim ve kanıt sözleşmesi](llm-benchmark-worker-contract.md).  
İnceleme kayıtları: [reviews/llm-benchmark](reviews/llm-benchmark/README.md).

## 1. Sonuç ve kanıt sınırı

Proje sürdürülebilir; önce ölçüm sözleşmesi ile QC'nin fiilen uyguladığı kuralların düzeltilmesi gerekiyor. Önerilen yön, İngilizce teknik görevlerde sabit son isteme sunulan farklı senaryolaştırılmış konuşma geçmişlerinin yanıt davranışına etkisini inceleyen dar bir pilot. Gerçek niyet tanıma, saf kullanıcı risk kanıtının etkisi veya genel güvenlik sıralaması bu tasarımdan çıkarılmamalı.

Mevcut ölçümü daha çok model, daha çok tekrar veya otomatik judge ile büyütmek ilk iş olmamalı. Ordinal kod farklarının bilimsel kararı değiştirmesi, modal oynaklığın etki gibi etiketlenmesi ve koşula göre değişen uygunluk referansının davranış değişimiyle karıştırılması önce çözülecek. Bunlar kod refactor'ından ayrı, insan araştırmacı tarafından onaylanacak gerçek protokol değişiklikleridir.

### Güncel durum ve devam kaydı

| Paket | Durum | Sonraki somut sonuç |
| --- | --- | --- |
| Bu değerlendirme | Tamamlandı | Kaynak ayrımı, yerel kontroller, aşağıdaki teslim planı |
| [E0](reviews/llm-benchmark/E0-acceptance.md) | Kabul | Referans envanteri, bulgu matrisi ve güvenli test sınırı bağımsız doğrulandı |
| [E1a](reviews/llm-benchmark/E1a-acceptance.md) | Worker taslağı kabul; insan kararı bekliyor | 14 iddialık karar matrisi; iki zorunlu ifade düzeltmesi kayıtlı |
| [E1b](reviews/llm-benchmark/E1b-r6-acceptance.md) | Worker taslağı kabul; insan kararı bekliyor | R1–R6 zincirinden sonra Layer-B/C, ref, provenance ve scoreability sözleşmesi tamamlandı |
| [E1b-R1](reviews/llm-benchmark/E1b-r1-acceptance.md) | Düzeltme gerekli | İlk beş blokajın çoğu kapandı; resolved criterion ve frozen unscorable akışı eksik |
| [E1b-R2](reviews/llm-benchmark/E1b-r2-acceptance.md) | Düzeltme gerekli | İki hedef kapandı; Layer-C scoreability zarfı ve contested yerleşimi hatalı |
| [E1b-R3](reviews/llm-benchmark/E1b-r3-acceptance.md) | Düzeltme gerekli | Katman yerleşimi düzeldi; Layer-C koşullu alanları çelişkili |
| [E1b-R4](reviews/llm-benchmark/E1b-r4-acceptance.md) | Düzeltme gerekli | Presence mantığı düzeldi; nested slot alanları tanımsız |
| [E1b-R5](reviews/llm-benchmark/E1b-r5-acceptance.md) | Düzeltme gerekli | Alanlar tanımlı; JSON Pointer ref'leri çözülemiyor |
| [E1b-R6](reviews/llm-benchmark/E1b-r6-acceptance.md) | Kabul | Gerçek ref çözümleme ve adjudication final şeması doğrulandı |
| [E1c](reviews/llm-benchmark/E1c-acceptance.md) | Düzeltme gerekli | Endpoint paydaları, duplicate kimliği, assistant strata, CI ve onaysız payda davranışı eksik |
| [E1c-R1](reviews/llm-benchmark/E1c-r1-acceptance.md) | Düzeltme gerekli | Resolved analiz kaydı ve bağımsız endpoint paydaları eksik |
| [E1c-R2](reviews/llm-benchmark/E1c-r2-acceptance.md) | Düzeltme gerekli | Dört hedef kapandı; endpoint-scope exclusion çelişkisi kaldı |
| [E1c-R3](reviews/llm-benchmark/E1c-r3-acceptance.md) | Worker taslağı kabul; insan kararı bekliyor | Endpoint-scope exclusion ayrımı doğrulandı; E1c worker zinciri kapandı |
| [E2a](reviews/llm-benchmark/E2a-acceptance.md) | Düzeltme gerekli | FAIL→KEEP kapandı; status-forgery, kimlik, validator ordering ve gate bütünlüğü eksik |
| [E2a-R1](reviews/llm-benchmark/E2a-r1-acceptance.md) | Düzeltme gerekli | Context/KEEP kapıları kapandı; phase completion ve sentetik pozitif fixture sorunu kaldı |
| [E2a-R2](reviews/llm-benchmark/E2a-r2-acceptance.md) | Kabul | Phase completion iki-rater kanıtına bağlandı; pozitif sentetik fixture'lar kaldırıldı |
| E2b–E2c | Bekliyor | Eksiksiz B/C/D incelemesi ve Layer-B kayıt desteği |
| [E3a](reviews/llm-benchmark/E3a-acceptance.md) | Düzeltme gerekli | Yapısal sayımlar geçti; kalıcı helper, R-REF hashleri ve karar-değil dili eksik |
| [E3a-R1](reviews/llm-benchmark/E3a-r1-acceptance.md) | Düzeltme gerekli | Provenance ve üretilebilirlik kapandı; exact stance ve output allowlist eksik |
| [E3a-R2](reviews/llm-benchmark/E3a-r2-acceptance.md) | Kabul | Exact stance eşliği, güvenli helper ve 19 adaylık karar kuyruğu doğrulandı |
| E3b | Koşullu | İnsan kararı sonrası sürüm yolu |
| E4a–E4b | İnsan girdisine bağlı | Bağımsız QC, referanslar ve kabul edilmiş veri sürümü |
| E5a–E5d | Bekliyor | Çizelge, gerçek girdi bağı, outcome ve çalıştırma kapısı |
| E6a–E6c | Bekliyor | Sürümlü madde analizi, duyarlılık ve offline bütünleşik prova |
| E7 | Koşullu | Kanıtlı GO/NO-GO dosyası; ardından ayrı canlı yürütüm |

Buradaki E numaraları iyileştirme teslimleridir; deponun Phase 7G/8 adlarını değiştirmez. Bir planın onaylanması, mühürlü dosya değişikliğinin veya canlı değerlendirme başlangıcının onayı yerine geçmez.

### Kaynaklar ve kaynaklar arası fark

Asıl kaynak dizini: `/home/kaan/GPT-Pro/reports/LLM_Benchmark`.

| Kaynak | SHA-256 | Kullanım |
| --- | --- | --- |
| `LCRB_Hakem_Incelemesi_Tam_Paket.zip` | `1c7c12ed51c2a23b2d4d7fd2bcd831338854e15c55303fc5ff5cb9c2ea4af917` | Rapor, kanıt eki, hesaplar ve teslim manifestosu |
| ZIP: `LCRB_Bilimsel_Hakem_Raporu.md` | `530f451010607379bb05b2355d1589f4d8137e0268aec0ee27b737255371c7ab` | 16 bölümlü ana değerlendirme |
| ZIP: `LCRB_Kanit_Eki.md` | `343448ce3ed0e47686955301678e9a7f9f11824b869d1446c622533b149caecf` | P01–P15 dosya/satır ve hesap kanıtları |
| `Sohbet.md` | `4d687615f941d8dc2af722cb023ad70e982b57eebc5444ac922d274353676332` | Ek değerlendirme ve farklı yeniden üretim kaydı |

ZIP teslim manifestosundaki yedi dosyanın boyut/hash eşleşmesi bu turda doğrulandı. ZIP yalnız okumak için `/tmp/llm-benchmark-review-20260909` altına açıldı; bu dizin kalıcı arşiv değildir. Kaynak raporlar değiştirilmedi.

Sohbet tek bir raporun aynısı değil. Son bölümünde ayrıca sabit model davranışı / değişen uygunluk referansı McNemar karşıörneği ve `300 passed / 50 failed` dış paket koşusu anlatılıyor. ZIP'in OKU_BENI dosyası ise bütün test suite'inin çalıştırılmadığını söylüyor. Bu kayıtlar tek bir koşu gibi birleştirilmeyecek. Sohbetin işaret ettiği ek PDF/ZIP dosyaları verilen dizinde yok; içerikleri görülmüş sayılmıyor. Aşağıda **S01**, sohbetin yaklaşık 478–497. satırlarındaki McNemar örneğini; **S02**, yaklaşık 580–586. satırlardaki eksik blind-key/test kaydını ifade eder.

Raporlardaki PROJECT-VERIFIED etiketleri rapor yazarına aittir. Bu turda tam test suite'i, hakem QC negatif-test script'i, model/API çağrısı veya güç simülasyonu çalıştırılmadı. Dış literatür bağımsız taranmadı; raporun yenilik ve literatür hükümleri bu planda doğrulanmış yayın gerçeği olarak benimsenmiyor. Plan yerel rapor değerlendirmesidir; yeni bir sistematik derleme değildir.

### Bu turda bağımsız kontrol edilenler

- Protokol manifestosundaki dosya hash'leri ve composite eşleşiyor: `47ae3fed4117639ef2575135a6ca63f000f4fcc8c052c629355f6ccf4bbcfc6f`.
- `stimulus_dataset_v1.json` SHA-256: `2f78e79e19d844b84b6bc06a0c2bef47e19283cc7c54b91f6ae283e1a74af077`. 50 madde / 171 koşul var; her maddenin koşulları arasında son kullanıcı metni UTF-8 baytları eşit.
- Gruplar: DU 30, AM 7, NB 7, NH 6. D gerçek anahtarla 21 maddede; sihirbazın kullandığı anahtarla sıfır maddede bulunuyor.
- QC JSON'larında `rater_a=1`, `rater_b=0`, 49 `PENDING` + 1 `PARTIAL_ONE_RATER`; nihai kararların 50'si de `PENDING`.
- Yerelde `phase7g_blind_key.json` mevcut. S02'deki paket eksikliği yerelde dosyanın bulunmadığı anlamına gelmiyor; anahtarın içerikleri bu belgeye taşınmadı.
- Başlangıç çalışma ağacında `.gitignore` değişikliği ve untracked `uv.lock` var. Kullanıcı çalışması olarak korunuyor. HEAD eşleşmesi bütün çalışma ağacının hakem snapshot'ıyla aynı olduğunu kanıtlamaz.

## 2. Bulgulara ilişkin değerlendirme

| Bulgu / kaynak | Değerlendirme ve yerel kanıt sınırı | Sahibi |
| --- | --- | --- |
| Ordinal uzaklıkla D kararı; P03/P15 | Ön kayıtta uzaklık ve sıralı kod kullanımı mevcut. Rapordaki recoding karşıörneği bağımsız analiz kabul testine dönüştürülmeli. | E1b, E6a |
| Modal `context_effect_observed`; P03/P15 | Sıfır dağılım etkisinde beklenen 5,75/30 pozitif raporun matematiksel örneği; gerçek model sonucu veya genel test yanlış-pozitif oranı değil. | E1c, E6a/E6b |
| Uygunluk hatası ≠ davranış değişimi; S01 | Ön kayıt McNemar'ı B/C uygunluk ihlaline bağlıyor. Aynı ret / farklı referans örneği bu testin farklı bir estimand ölçtüğünü gösteriyor. | E1c, E6a |
| FAIL→KEEP; P07/P14 | `record_decision` ve validator'da ADJUDICATED kontrolü var; kör `gate_result` kontrolü yok. Frozen protokol §2.4 FAIL için istisna tanımıyor. Dinamik yeniden üretim yapılmadı. | E2a |
| Tek rater sonrası context; P07/P14 | `_blind_submitted_for` yalnız PENDING olmamasına bakıyor; CLI ve `record_context` bunu kullanıyor. | E2a |
| D görünmüyor / eksik alanlar COMPLETE; P07/P14 | `review_context.py` yanlış `neutral_filler` anahtarını kullanıyor. `record_context` kısmi payload sonrasında doğrudan COMPLETE yazıyor. | E2b |
| Çok boyutlu yanıt ve Layer B; P05/P12 | Uygunluk, yardım, clarification ve harm ayrılmalı. Alanların bulunması insan referanslarının tamamlandığını göstermez. | E1b, E2c, E4 |
| Assistant ve D yorumu; P06/P13 | Mevcut clarification zaten whole-history yönünde daraltma içeriyor. AM ortak assistant tabakası DU'nun mekanizmasını tanımlamaz. | E1a |
| AM002 coherence, referent, DU004 D priming; P13 | Maddeye özgü insan incelemesi gerektiren rapor bulguları. Otomatik metin onarımı yetkisi doğurmaz. Byte uzunluğu token ihlali sayılmaz. | E3 |
| Power ve roadmap drift; P08, S02 | Birincil örneklem DU=30; DU-D=14. 350 tarihsel test ile dış paket koşusu farklı kanıtlar. Tekrar ve iki-insan bütçesi geri bağlanmalı. | E0, E1c, E6b, E7 |
| Tekrar/schedule; P09–P11 | Mock builder her koşulu bir kez çıkarıyor. Runner seçilen listeyi yürütüyor; bu giriş yolunda r=3 genişletme yok. `n_expected=len(rows)` kayıp çağrıyı bulamaz. | E5a, E6a |
| Config/payload/model; P09/P10 | Config `max_tokens`, preflight `max_output_tokens` bekliyor. Strict mod opsiyonel; runner `system_instruction=None` veriyor; adapter response modeli request'ten alıyor. | E5b, E5d |
| Gecikme; P09/P11 | Runner toplam provider-call süresinden yalnız backoff'u çıkarıyor. Kalan değer ağ ve başarısız attempt sürelerini de içerebilir. | E5c |
| Kapsam/overlap/yenilik; P13, rapor §14–15 | Mevcut provenance/overlap kayıtları incelenecek. Contamination yokluğu ve “ilk benchmark” sonucu çıkarılmayacak. | E0, E1a; geniş araştırma ertelendi |

Öncelik, yeni bir framework kurmak değil mevcut giriş noktalarının aynı bilimsel sözleşmeyi uygulamasıdır. Yazıcı, validator, CLI ve çalıştırma preflight'ı ayrı ayrı aynı eksikliği taşımamalı. Bunun için küçük ortak doğrulama işlevleri yeterliyse orada durulacak.

## 3. Çalışma sınırları ve karar sahipliği

- [AGENTS.md](../AGENTS.md) bağlayıcıdır. Mühürlü belgeler, manifestoya dahil diğer dosyalar, stimulus metinleri ve tarihsel çıktılar bu planla değiştirilemez. Mevcut clarification da hash manifestosundadır.
- Ölçüm/analiz değişiklikleri önce ayrı **DRAFT / NOT EFFECTIVE** amendment taslağında hazırlanır. Araştırmacı somut farkları onaylayıp resmi ek sürecini tamamlamadan yeni sözleşme etkinleştirilmez; hash yeniden üretilerek eski mühür sessizce değiştirilmez.
- Stimulus v1 korunur. Yeni metin veya v2 üretimi ancak açık insan onayı ve gerekli protokol ekiyle ayrı iş olur. Sorun envanteri hazırlamak metin değişikliği değildir.
- `results/dataset_audit/*.jsonl` geçmişi append-only kalır. Mevcut tek insan rating'i silinmez, başka ratere mal edilmez, yeni rubriğe sessizce çevrilmez.
- Ajan insan rater adına annotation, referans, adjudication veya KEEP üretmez. Hakem paketindeki sentetik blind-label script'i bu turda çalıştırılmadı. Test ihtiyacı bu kuralı geçersiz kılmaz: durum/eksiklik kontrolleri insan etiketi uydurmadan sınanır; sentetik rater verisi gerektiren ayrı test kapsamı açık insan talimatı olmadan yürütülmez.
- Zararsız mock transport ve sayısal analiz örnekleri açıkça test verisidir; insan-QC dosyalarına veya ampirik sonuç dizinine yazılamaz. Testlerin yazma hedefi geçici dizin olmalı; mevcut builder'lar yetkili kayıtları yenilemek için çağrılmamalı.
- Phase 7G iki bağımsız rater ve insan QC kapısı kapanmadan hiçbir gerçek model değerlendirmesi/API çağrısı yoktur. E5/E6'nın offline hazırlanması bu kilidi açmaz.
- AM ile assistant'ı farklı DU/NH tabakaları `stratified_by_assistant_stance` altında korunur; NB'nin farklı-assistant üyeliği de açık tutulur. Dört araştırma grubu ayrıca raporlanır; tabaka etiketi grupları birleştirerek örneklem büyütme izni değildir.

## 4. Fazlar ve küçük worker teslimleri

Ana sıra: **E0 → E1 → E2/E3 → insan-QC hazırlık kabulü → E4 → E7**. E5 ve E6'nın offline işleri E1'de ilgili sözleşme onaylandıktan sonra E4'ten bağımsız hazırlanabilir; gerçek kabul listesiyle entegrasyon E4b'yi bekler. E2a'nın mevcut frozen kuralları uygulayan kısmı E0'dan sonra başlayabilir.

Yaklaşık 16 teknik/belgesel alt teslim (koşullu E3b dahil), 2 insan-QC teslimi ve 1 son kapı vardır. Bu sayı süre taahhüdü değildir. Her alt iş ayrı inceleme birimidir; tek PR olma zorunluluğu yoktur. Aynı dosyayı değiştiren işler sırayla yürütülür.

### E0 — Referans, kanıt matrisi ve yeniden üretim sınırı

Bağ: P01–P15, S01/S02. Öncelik: P0. Sahip: küçük worker; kabul ana inceleyicide.

- [ ] HEAD, dirty dosyalar, Python/dependency ortamı, mevcut hash manifestoları ve audit geçmişlerinin boyut/hash envanterini kalıcı inceleme dosyasına kaydet.
- [ ] Her bulguyu `yerelde doğrulandı / rapor kanıtı / açık / çürütüldü` olarak sınıflandır; ilgili dosya ve satırı, doğrulama türünü ekle.
- [ ] Testlerin canlı ağ, gerçek QC yazımı veya sahte rater üretimi yapıp yapmadığını incele; güvenli çalıştırılabilir hedefli alt kümeyi belirle. Blind key'in paketleme/erişim kapsamını anahtarı açığa çıkarmadan yaz.
- [ ] Mevcut source/overlap raporlarını envanterle; hash bütünlüğü, kaynak lisansı, commit bağı ve contamination iddiasını ayrı tut.

Okuma: bu plan, raporların ilgili bölümleri, `pyproject.toml`, hash manifestosu, ilgili scripts/tests ve durum belgeleri. Yazma: `docs/reviews/llm-benchmark/E0-baseline.md` ve gerekli küçük envanter dosyası. Üretim kodu veya audit dosyası değişmez.

Kabul: kaynaklar birbirine karışmaz; bütün başlangıç hash'leri kayıtlıdır; eksik ortam başarısız test mantığı diye etiketlenmez; hangi doğrulamanın yapılmadığı açıkça listelenir. Bu turdaki sınırlı kontroller E0'ın tamamlandığı anlamına gelmez.

### E1 — Araştırma iddiası, ölçüm ve analiz sözleşmesi

Bağ: P02–P06/P08/P15, S01. Öncelik: P0; araştırmacı kararları zorunlu.

| Alt iş | Dar kapsam ve dosyalar | Teslim / kabul |
| --- | --- | --- |
| E1a — İddia ve karar matrisi | README, research_questions, mevcut clarification ve raporun construct/control bölümleri yalnız okunur. | `E1a-claim-decisions.md`: mevcut hüküm → öneri → gerekçe → etkilenen iddia. Whole-history kapsamı, D'nin sınırlı rolü, AM/NB/NH ayrı yorumları ve ertelenen iddialar eksiksiz. |
| E1b — Rubrik ve referans taslağı | Annotation protocol, mevcut QC şemaları ve P05. | Ayrı taslakta nominal action, karma yanıt/clarification kuralı, harm `present/absent/uncertain`, mevcut utility ve uygulanabilirlik; benchmark-relative handling, `either_defensible` ve gerekçe alanları. Aynı yanıtın action etiketi koşul beklentisiyle değişmiyor; uygunluk ayrı alan. İnsan etiketi doldurulmaz. |
| E1c — Estimand ve amendment taslağı | Preregistration §7–16, power belgesi, P15/S01. | Sürümlü DRAFT ek: primary/secondary kontrastlar, item ağırlığı, tüm tekrarlar, missingness, exclusions, test/CI varsayımları, multiplicity ve hipotez sınırları. Eski→yeni karar farkı açık; H3/F4 sıfır çakışması giderilecek öneri var. |

Önerilen başlangıç: kategori başına madde-eşit B/C olasılık farkları; ayrı harm ve utility kontrastları. Mod ancak ikincil betimleme olabilir. Uygunluk ihlali McNemar analizi korunacaksa yalnız açıkça tanımlanmış paired-binary error-asymmetry endpoint'i olarak kullanılır. Bunun seçimi worker'a bırakılmaz; yeni tek bileşik güvenlik puanı icat edilmez.

E1 kabul kapısı: insan araştırmacı somut amendment farklarını ve hangi endpoint'in birincil olduğunu kayda geçirir. Onay yoksa taslaklar tamamlanmış sayılabilir, bilimsel değişiklik etkin sayılmaz. Mevcut v1.0.2'nin `rules_changed=false` niteliği yeni ölçüm değişikliğine taşınamaz.

### E2 — QC sözleşmesinin kodda uygulanması

Bağ: P05/P07/P12/P14. Öncelik: P0. E2a E0'a; E2b/E2c ilgili E1 alan sözleşmesine bağlı.

| Alt iş | Kod kapsamı | Alt işler ve kabul |
| --- | --- | --- |
| E2a — Kapı ve durum geçişleri | `apply_phase7g_annotations.py`, `validate_phase7g_review.py`, CLI ortak uygunluk kontrolleri | İki gerçek bağımsız rating ve gerekli uyuşmazlık çözümü olmadan context erişimini reddet; frozen FAIL→KEEP yasağını yazıcı ve validator'a bağla; status alanına güvenmek yerine gerekli dayanakları doğrula. PENDING/tek-rater/eksik kimlik/çözülmemiş uyuşmazlık ve FAIL yolları kapalı. Ret yolunda veri değişimi yok. |
| E2b — B/C/D görünürlüğü ve tamlık | `review_context.py`, QC builder/validator'ın ilgili alanları | Gerçek `neutral_filler_control` anahtarını kullan; mevcut 21 D'nin hepsi görüntülenebilir. B/C yön, relevance/resolution/leakage, naturalness/safety ve D contamination/length alanları onaylı uygulanabilirlik tablosuna göre istenir. D'siz madde missing D diye başarısız olmaz; D'li madde D incelenmeden tamamlanmaz. Kısmi kayıt COMPLETE olamaz. |
| E2c — Layer-B ve provenance | Onaylı referans şeması, annotation/import/export ve blind araçları | Koşul bazlı iki insan referansı, rater kimliği/zamanı/rubrik sürümü ve gerekçe yakalanır. Rater B, A'nın yanıtını görmez; author expectation/model output referans doldurmaz. Eski annotation korunur; sürüm uyumsuzluğu görünürdür. |

Teslim başına ilgili hedefli test ve kısa kabul kaydı gerekir. Rater davranışının bilişsel bağımsızlığı salt farklı kimlik string'leriyle kanıtlanamaz; kod kontrolleri ve insan maruziyet beyanı ayrı kanıtlardır. Tam test tasarımı AGENTS.md'nin sentetik anotasyon yasağıyla uyumlu olmalı; worker bu sınırı kendiliğinden gevşetemez.

E2 sonunda yalnız araçların hazır olduğu söylenebilir; gerçek referansların veya Phase 7G'nin tamamlandığı söylenemez.

### E3 — Yerel stimulus sorunları ve korunan sürüm yolu

Bağ: P06/P13, rapor §9/14. Öncelik: P0. E3a E0 sonrasında; E3b koşullu.

- [ ] **E3a — Kusur envanteri:** AM002'nin karşı koşuldan bilgi kullanımı, eksik referent/risk ambiguity ayrımı, DU004 ve diğer D'lerde görev çözümünü etkileyen ipuçları için madde/koşul/kanıt/sorun türü tablosu hazırla. Tur ve son-byte eşitliği ile metinsel coherence ayrı denetlensin. Token toleransı ancak belirtilmiş tokenizer/profil altında ölçülsün; profil yoksa sonuç açık kalsın.
- [ ] **E3b — İnsan kararı sonrası sürümleme:** Her sorun için gerekçeli koruma, REVISE veya REJECT insan tarafından seçilir. Yeni stimulus gerekiyorsa açık yetki + resmi ek sonrası v1'i koruyan yeni sürüm, kaynak bağı ve yeniden-QC kapsamı hazırlanır. Yetki verilmemişse yalnız değişiklik önerisi teslim edilir; metin üretilmez/değiştirilmez.

Dosyalar: v1 ve stimulus kaynak modülleri yalnız okunur; `docs/reviews/llm-benchmark/E3-stimulus-issues.md` yazılır. Onaylı sürüm işinin yazma kapsamı ayrıca belirlenir.

Kabul: etkilenen madde sayısı örneklerden tahmin edilmez; v1 baytları sabit kalır; onaylı yeni sürümde koşullar arası final-byte eşitliği tekrar doğrulanır. Final prompt değişirse yeni kör inceleme gerekir. Önceki bağlam maruziyeti yeni oturum açılarak silinmiş kabul edilmez. Korpusun tamamı otomatik yeniden yazılmaz.

### E4 — İnsan QC ve değerlendirme popülasyonunun dondurulması

Bağ: E1 onayı + E2 kabulü + E3 sorunlarının kararı. Sahip: gerçek insan rater'lar ve araştırmacı; worker yalnız araç/aktarım desteği.

- [ ] **E4a — İnsan oturumları:** Bağımsız isolated-prompt incelemeleri, uyuşmazlık çözümü, ardından context incelemesi ve koşul referansları. Rater eğitiminde analiz korpusundan bağımsız materyal ve maruziyet kaydı kullanılır. Mevcut tek rating'in yeni süreçte kullanılabilirliği insan tarafından belirlenir; gerekirse yalnız tarihsel/yardımcı kalır.
- [ ] **E4b — Kabul manifestosu:** Gerçek KEEP/REVISE/REJECT kararları, referans tamlığı, sürüm/hash bağları, ham rater anlaşmazlıkları, grup bazlı attrition ve son kabul listesi kaydedilir. “50/50 KEEP” başarı hedefi yapılmaz. Tüm kararların tamamlanması ile değerlendirmeye uygun yeterli örneklem ayrı kapılardır.

Kabul: her kabul edilmiş madde iki-rater/gate/context/safety/reference koşullarını sağlar. Dışlama veya revizyon sonrası örneklem ve çıkarım kapsamı onaylı protokolle uyumludur. Eksik insan girdisi worker tarafından tamamlanmaz. Kabul manifestosu ve Layer B, ilk model yanıtından önce dondurulur.

Tam v1 üzerinden başlangıç iş yükü 100 isolated rating ve 342 koşul-rater referans değerlendirmesidir; bunlar rater zamanı ölçümü değildir. Model başına 1.026 yanıt puanlaması daha sonra ayrıca gelir. Kabul edilen koşul sayısı değişirse bütün bütçeler yeniden hesaplanır.

### E5 — Çalıştırma çizelgesi, provenance ve gerçek değerlendirme kilidi

Bağ: P09–P11. Öncelik: P1; offline hazırlık E1 sonrası, nihai veri bağı E4b sonrası.

| Alt iş | Dosya/sözleşme kapsamı | Teslim ve kabul |
| --- | --- | --- |
| E5a — Beklenen çizelge | Phase 8 case builder, `benchmark/types.py`, metadata; ayrı schedule üreticisi gerekiyorsa küçük modül | `item × condition × repetition × model` tekil anahtarı, önceden beklenen iş listesi, r=3, açık seed/sıra/block politikası. Tam v1 için model başına 513 iş; D'siz maddelere D yaratılmaz. Üç tekrar üç bağımsız madde sayılmaz. Sıra ve fresh history, zararsız mock ile doğrulanır. |
| E5b — Uygulanan girdi kimliği | `preflight.py`, `metadata.py`, `adapters/providers.py`, config | `max_tokens/max_output_tokens` ve provider parametre uyumu; çözülmüş system text/hash; exact istenen model ile dönen model/fingerprint/finish reason ayrımı; adapter dönüşümü sonrası payload provenance. Desteklenmeyen parametre sessiz atılmaz. Alias + version metadata pinleme diye sunulmaz; ağ kullanmadan transport-capture kontrolü yapılır. |
| E5c — Outcome, retry ve gecikme | `runner.py`, `retry.py`, `logging.py`, `latency.py`, result alanları | Planlanan iş ile fiziksel attempt ayrılır; success/error/filter/timeout/truncation/missing durumları ve yeniden başlatmada duplicate politikası açık olur. Backoff, başarılı/başarısız attempt duvar süreleri ve toplam süre ayrılır. `pure_inference_latency_ms` yalnız gerçekten ölçülebiliyorsa değer alır; aksi halde null + neden, client süreleri ayrı adla verilir. |
| E5d — Canonical preflight ve kayıt bütünlüğü | Canlı giriş noktası, ortak preflight, artifact writer/reader | Eksik insan-QC, referans, protokol/veri hash'i veya run freeze ile dispatch engellenir. Strict kontrol canonical yolda zorunlu; mock yolu canlıya fallback yapmaz. Yarım/karmış run, hash uyuşmazlığı ve yinelenen iş kimliği bilimsel analize sessiz geçmez. En küçük completion manifestosu yeterliyse yeni depolama framework'ü kurulmaz. |

E5b sağlayıcı seçimi/güncel endpoint doğrulaması zamanı geldiğinde resmi sağlayıcı belgeleriyle yapılacak ayrı kontroldür; config'teki tarihsel adayların bugün kullanılabilir olduğu bu planda varsayılmıyor.

E5c bütçe kabulü: tam v1, tek model, r=3 için 513 mantıksal iş vardır. `max_attempts=3` ile teorik üst sınır 1.539 fiziksel attempt'tir; iki ek retry ayrı tekrar değildir. İnsan tarafından seçilmiş fiziksel çağrı/maliyet cap'i dispatch öncesi denetlenir. Cap yetmezse kapsam eksikliği raporlanır; cap sessizce artırılmaz. Para maliyeti provider fiyatı doğrulanmadan hesaplanmaz.

### E6 — Sürümlü analiz, duyarlılık ve offline bütünleşik prova

Bağ: P03–P05/P08/P11/P15, S01. Öncelik: P0/P1. E6a/E6b onaylı E1c'ye; E6c ayrıca E5'e bağlı.

| Alt iş | Dar görev | Kabul ölçütü |
| --- | --- | --- |
| E6a — Analiz uygulaması | Generic row metrikleriyle ayrı, onaylı item/condition/repetition analizi; analysis version ve input hash bağı | Tüm geçerli tekrarlar saklanır; modal anlaşmazlık unscorable diye atılmaz. Expected schedule'a göre missing/duplicate/coverage raporlanır. DU/AM/NB/NH, DU-D=14 başlangıç altkümesi ve assistant tabakaları ayrı. Pay/payda, applicability/uncertain/either_defensible ve eksik-tekrar politikası açık. |
| E6b — Prospective sensitivity | Onaylı endpoint için sabit seed ve senaryo tablosuyla bağımsız hesap | Null dağılım, madde heterojenliği, floor/ceiling, block bağımlılığı, r=3/5/10, %10/20/30 attrition ve hata/truncation duyarlılığı. Rater belirsizliği gerekiyorsa yalnız matematiksel hata parametreleri kullanılır; sahte rater kayıtları üretilmez. Gerçek model gücü gibi sunulmaz; test/CI varsayımları ve küçük-hücre frozen kısıtları korunur veya açık amendment ile değişir. |
| E6c — Offline uçtan uca kanıt | Yeni geçici run'da schedule → captured mock payload → ledger → analysis → report | Önceden seçilmiş kayıp/duplicate/retry/truncation ve kesinti durumları doğru raporlanır; sıfır ağ çağrısı. Aynı sabit girdilerde açıklanmayan deterministik analiz farkı yok. Mock politika çıktıları bilimsel etki kanıtı sayılmaz. Gerçek QC'yi tamamlanmış gösteren fixture kullanılmaz; başarı kapısı E4 gerçek verisini bekleyebilir. |

E6a'nın bağımsız kabul örnekleri:

1. Aynı response-action dağılımı B ve C'de aynıysa davranış kontrastı sıfırdır. Koşula göre uygunluk referansı değişirse error-asymmetry ayrı değişebilir; bu context effect diye adlandırılmaz (S01).
2. Kategori kimliklerinin yeniden kodlanması nominal sonuçları değiştirmez. Eski ordinal D kuralının değiştiği örnek arşivsel karakterizasyonda açık kalır (P15).
3. Eş dağılımlı stokastik koşullarda gözlenen örnek farkı her koşuda sıfır olmak zorunda değildir. Yeni analiz bu farkı kesin item-level etki diye etiketlemez; inferans varsa null davranışı seçilmiş hata düzeyine göre sınanır (P15).
4. Aynı item kontrastları fakat farklı geçerli tekrar sayıları, onaylı madde ağırlığını sessizce row ağırlığına dönüştürmez. Eksik tekrarları tam kapsam gibi göstermeden politika uygular.
5. AM'de uygun clarification'ın korunması başarısız bağlam duyarlılığı diye kodlanmaz. Harm ve utility, action/refusal kelimelerinden türetilmez; referans alanı yoksa skor üretilemez.

E6 kapsamı yeni büyük istatistik framework'ü değildir. Ana endpoint ve varsayımları hazır değilse worker bir test seçerek boşluğu doldurmaz; bağımsız hesap ve kontrat testlerini hazırlar, bilimsel seçimi araştırmacıya bırakır.

### E7 — Son kapı, belge uyumu ve canlı yürütüme devir

Bağ: E0–E6 kabul kayıtları. Sahip: ana inceleyici + araştırmacı.

- [ ] README, PROJECT_STATUS, CURRENT_STATE_AND_NEXT_STEPS, ROADMAP ve power belgesini onaylı son sözleşmeyle uzlaştır; mühürlü belgeler için yalnız onaylı ek/sürüm yolunu kullan.
- [ ] Tekrar, fiziksel attempt ve iki-insan puanlama bütçesini seçilmiş model sayısı ve gerçek kabul manifestosundan türet. Roadmap'te otomatik judge + %20 insanı primary iki-insan planının yerine bırakma.
- [ ] Bütünleşik gerekli testleri ve hash/append-only kontrollerini ana inceleyici yeniden doğrulasın. Her açık madde için GO'yu engelliyor mu, yalnız iddia sınırı mı, ertelenmiş özellik mi açık olsun.
- [ ] `E7-go-no-go.md`: etkin protokol/veri/reference/run-config kimlikleri, accepted item sayıları, coverage hedefi, endpoint/analysis sürümü, insan onayları, bütçe ve başlatılacak somut komut.

Kabul: E4 gerçek insan kapısı + E5 execution + E6 analiz/prova birlikte kapanmış olmalı. Bu aşamada canlı yürütüm ayrıca yetkilendirilirse başlanır; plan yazımı canlı çağrı yetkisi değildir. Sağlayıcı sürümü değişirse sessiz model ikamesi yapılmaz; yeni deney sürümü ve uygun preflight gerekir. Model çıktısı sonrası iki insanla puanlama, dondurulmuş analiz ve raporlama aynı protokole bağlı ayrı uygulama işleri olarak sürer.

## 5. Bilimsel kararlar ve kapılar

| Karar | Önerilen yön | Karar sahibi / son tarih |
| --- | --- | --- |
| Construct ve kapsam | Seçilmiş İngilizce teknik fixed-history pilot; mekanizma/latent intent iddiası yok | Araştırmacı, E1 kabulü |
| Birincil ölçüm | Nominal davranış ve ayrı harm/utility; referans uygunluğu ayrı | Araştırmacı, E1b/E1c |
| Estimand ve inferans | Item-eşit kontrastlar; tüm tekrarlar; CI/test ve multiplicity açık | Araştırmacı, E6 uygulamasından önce |
| FAIL override | Mevcut frozen “never waived” uygulanır | E2a; değiştirme isteği varsa ayrı gerçek amendment |
| Yerel stimulus sorunları | İnsan incelemesi; v1 sabit, gerekiyorsa açık onaylı yeni sürüm | Araştırmacı, E3b/E4 öncesi |
| Önceki rater maruziyeti | İnsan beyanı ve provenance; bağımsızlık şüphesinde yeni uygun rater | Araştırmacı, E4a |
| Attrition ve minimum kapsam | Tüm maddeleri KEEP'e zorlamadan kabul listesi; azalan örnekleme göre yorum | Araştırmacı, E4b/E7 |
| Gecikme alanı | Backoff ayrılır; ölçülemeyen server inference null + neden | E5c; anlam değişikliği analiz/şema sürümünde |
| Tekrar/model/bütçe | r=3 başlangıcı korunur; değişiklik varsa gerekçeli ek; güncel modeller sonradan doğrulanır | Araştırmacı, E5/E7 |

İnsan-QC'ye dönüş kapısı: E1'in ilgili bilimsel kararları onaylı, E2 araçları kabul edilmiş ve E3 sorunları için uygulanabilir karar/sürüm hazır. Nihai Layer-B etiketleri bu kapıdan önce doldurulmuş olmak zorunda değildir; E4 içinde gerçek insanlarla üretilecektir.

Canlı Phase 8 kapısı: bunlara ek olarak E4b kabul manifestosu, E5, E6 ve E7 kaydı tamamlanmış olmalı. İnsan onayı bekleyen tek iş bütün bağımsız offline işleri durdurmaz; ancak o onaya bağımlı değişiklik etkinleştirilmez.

## 6. Worker çalışma ve kabul protokolü

Küçük worker'a bütün depo ve rapor paketi verilmez. Her görev, bir alt teslim ID'si ve yaklaşık 2–5 ilgili uygulama dosyasıyla başlar; gerekli ortak sözleşmeler ayrıca salt okunur verilir. Kapsam büyürse ana inceleyici yeniden böler. Model adı veya bütçesi bu planda sabitlenmiyor; kullanıcı seçimine göre küçük worker kullanılabilir.

Her görev kartı şu alanları taşımalı:

```text
Görev: E2b gibi tek bir teslim
Amaç ve bağlı bulgular:
Önkoşullar: kabul dosyaları ve etkin sözleşme sürümü
Okunacak dosyalar / rapor bölümleri:
Yazılabilecek dosyalar:
Yasak kapsam: frozen metin, audit geçmişi, insan etiketi, canlı API
Alt işler:
Beklenen teslim ve bağımsız kabul örnekleri:
Doğrulama komutları ve geçici çıktı dizini:
Durma koşulu: bilimsel karar, kapsam çatışması, eksik insan girdisi
Devam kaydı: kalan açık madde ve sıradaki teslim
```

Worker teslimi, bulgu hakkında kısa sonuç, dosya değişiklikleri, çalıştırılan kontroller ve sınırlılıkları içermeli. Ana inceleyici diff'i, korunacak hash'leri, audit geçmişinin eski prefix'ini ve kritik kabul örneğini yeniden kontrol eder; worker'ın “testler geçti” beyanı tek başına kabul değildir. Düşük etkili belge işine gereksiz test yazılmaz; QC/gate ve analiz değişikliğinde anlamlı davranış doğrulaması gerekir.

Her kabul `docs/reviews/llm-benchmark/<ID>-acceptance.md` dosyasına kaydedilir; HEAD yanında dirty/untracked değişiklikleri tanımlayan diff/hash kanıtı bulunur. Bu belgenin durum tablosu güncellenir. Yeni oturum için bu tablo, son kabul kaydı ve aktif görev kartı yeterli olmalı; uzun geçmiş logları tekrar okutulmaz.

Bağımsız yürütülebilir işler: E0 sonrası E2a ile E3a; E1 onayı sonrası E5 hazırlığı ile E6b ve insan E4 süreci. Aynı QC yazıcı/validator dosyalarını değiştiren E2a–E2c sırayla alınır. Ana inceleyici entegrasyonu sahiplenir. Bu turda alt ajan çalıştırılmadı; burada sonraki uygulama için iş bölümü tanımlanıyor.

## 7. Ertelenen işler ve ilk uygulama kapsamı

Pilot kapısı için zorunlu olmayanlar: shared-assistant factorial tasarım, çoklu yeni placebo aileleri, çok dil/domain genişlemesi, büyük model leaderboard'u, otomatik primary judge, IRT/latent model, zorunlu 10+ tekrar, genel contamination araştırması ve performans worker havuzu. Bunlar ayrı araştırma sorusu, veri sürümü veya ölçülmüş ihtiyaçla yeniden ele alınır.

E0, [E2a](reviews/llm-benchmark/E2a-r2-acceptance.md) ve [E3a](reviews/llm-benchmark/E3a-r2-acceptance.md) kabul edildi. E1a, [E1b](reviews/llm-benchmark/E1b-r6-acceptance.md) ve [E1c](reviews/llm-benchmark/E1c-r3-acceptance.md) worker taslakları insan bilimsel kararlarını bekliyor. İki bağımsız gerçek rater bulunmadığından proje **2026-09-10 tarihinde donduruldu**; aktif worker briefi yoktur. E2b, E3b, E4 ve Phase 8 kapalıdır. Devam koşulları ve dondurma anı hashleri [kalıcı dondurma kaydında](reviews/llm-benchmark/PROJECT-FROZEN-2026-09-10.md) bulunur.
