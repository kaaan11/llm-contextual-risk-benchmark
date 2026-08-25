# İlk Tehdit Taksonomisi

## 1. Amaç ve sınırlar

Bu belge, LLM Security–Usability Benchmark pilotunda kullanılmak üzere başlangıç düzeyinde bir tehdit taksonomisi önerir. Taksonomi, zararlı operasyonel talimatlar yayımlamak için değil; risk türlerini tutarlı biçimde sınıflandırmak, değerlendirme kapsamını dengelemek ve meşru teknik kullanımları gereksiz reddetmeden ayırmak için hazırlanmıştır.

Taksonomi, örneğin “iyi” veya “kötü” olduğuna dair tek bir hüküm değildir. Bir örnek birden fazla kategoriyle etiketlenebilir; kategori, niyet, bağlam, istenen yetenek ve beklenen etki birbirinden ayrı alanlar olarak tutulmalıdır.

## 2. Sınıflandırma ilkeleri

1. **İçerik ile niyet ayrılmalıdır.** Aynı teknik konu meşru savunma veya kötüye kullanım amacıyla sunulabilir.
2. **İstenen eylem ile potansiyel etki ayrılmalıdır.** Bir istek doğrudan zararlı görünmese bile yüksek etkili bir yeteneği etkinleştirebilir.
3. **Bağlam ayrı bir boyuttur.** Multi-turn konuşma, son isteğin yorumunu değiştirebilir; bağlam etkisi ana tehdit kategorisinin yerine geçmez.
4. **Gerekli ayrıntı seviyesi sınırlanmalıdır.** Kamuya açık belgelerde sınıflandırma mantığı ve temizlenmiş örnekler bulunabilir; hassas operasyonel içerik bulunmamalıdır.
5. **Belirsizlik kaydedilmelidir.** Sınır durumlarında güven puanı ve gerekçe saklanmalıdır.
6. **Çoklu etiket desteklenmelidir.** Tek bir örnek hem kimlik bilgisi kötüye kullanımı hem de savunma atlatma niteliği taşıyabilir.

## 3. Önerilen üst düzey kategoriler

### T1 — Yetkisiz erişim ve erişim kontrolünü aşma

Kimlik doğrulama, yetkilendirme, erişim kontrolü veya izole kaynaklara erişim mekanizmalarını atlatmayı amaçlayan istekler.

**Gerekçe:** Bu kategori, doğrudan yetkisiz erişim riskini ve erişim sınırlarının aşılmasını ayrı görünür kılar. Savunma amaçlı erişim denetimi analizi ile gerçek bir erişim elde etmeye yönelik yönlendirme birbirinden ayrılmalıdır.

**Sınır notu:** Yetkili test, politika incelemesi veya erişim kontrolü tasarımı otomatik olarak bu kategoride yüksek risk sayılmamalıdır; niyet ve bağlam ayrıca etiketlenmelidir.

### T2 — Kimlik bilgileri, sırlar ve hassas verilerin kötüye kullanımı

Parola, erişim belirteci, API anahtarı, kişisel veri, özel yapılandırma veya benzeri hassas bilgilerin elde edilmesi, açığa çıkarılması, çıkarılması ya da kötüye kullanılması.

**Gerekçe:** Veri gizliliği ve sırların korunması, siber güvenlik riskinden ayrı bir değerlendirme boyutu gerektirir. Bu kategori, örneklerin veri işleme ve yayınlama kararlarına doğrudan bağlanmasını sağlar.

**Sınır notu:** Gerçek sırlar veya kişisel veriler pilot veri kümesine konulmamalıdır. Gerekiyorsa sentetik ve güvenli temsiller kullanılmalıdır.

### T3 — Kötücül yazılım ve zararlı kod üretimi/değiştirilmesi

Kötücül yazılım geliştirme, işlev ekleme, değiştirme, gizleme veya yayma amacı taşıyan kodlama istekleri.

**Gerekçe:** Zararlı kod üretimi, teknik olarak meşru malware analizi ve tespit çalışmalarıyla aynı araçları kullanabilir. Ayrı kategori, savunma araştırmasını korurken operasyonel kötüye kullanım riskini görünür kılar.

**Sınır notu:** Tespit, sınıflandırma, tersine mühendislik ve güvenli analiz bağlamları ayrıca `legitimate_plausibility` ve `expected_risk` alanlarıyla değerlendirilmelidir.

### T4 — Güvenlik araçlarının, izleme veya savunma mekanizmalarının kötüye kullanımı

Tarama, izleme, güvenlik yönetimi, yönetim araçları veya savunma bileşenlerinin yetkisiz ya da zararlı amaçlarla kullanılması.

**Gerekçe:** Meşru sistem yönetimi ile kötüye kullanım arasındaki sınır, yalnızca kullanılan aracın adına bakılarak belirlenemez. Bu kategori, araçtan bağımsız olarak kullanım amacını ve olası etkisini incelemeye yardımcı olur.

### T5 — Güvenlik mekanizmalarını ve politika uygulamasını atlatma

Model güvenlik politikalarını, filtreleri, denetimleri veya savunma katmanlarını etkisizleştirmeyi ya da yanıltmayı amaçlayan istekler.

**Gerekçe:** Projenin ana araştırma konusu güvenlik–kullanılabilirlik dengesi olduğundan, savunma mekanizmalarının atlatılmasını ayrı izlemek gerekir. Ancak bu kategori, ham jailbreak içeriklerinin yayımlanmasını gerektirmez.

**Sınır notu:** Güvenlik mekanizmasının davranışını ölçen kontrollü, zararsız ve redakte edilmiş değerlendirmeler bu kategoriye girebilir; operasyonel atlatma talimatları kamuya açık veri olarak saklanmamalıdır.

### T6 — Saldırı otomasyonu, ölçeklendirme ve kalıcılık

Bir güvenlik ihlalini çok sayıda hedefe, yüksek sıklıkta veya uzun süreli biçimde uygulamayı; otomasyon, zamanlama, yayılma veya kalıcılık sağlamayı amaçlayan istekler.

**Gerekçe:** Tekil teknik bilgi ile geniş ölçekte uygulanabilir saldırı kapasitesi aynı riskte değildir. Ölçek, otomasyon ve kalıcılık potansiyelinin ayrıca etiketlenmesi, risk ayrımını daha anlamlı kılar.

### T7 — Hizmet engelleme, kaynak tüketimi ve operasyonel bozulma

Sistemlerin erişilebilirliğini, kapasitesini, performansını veya güvenilirliğini bozmayı amaçlayan istekler.

**Gerekçe:** Gizlilik veya bütünlük ihlalinden farklı olarak burada temel etki kullanılabilirlik ve hizmet sürekliliğidir. Ayrıca savunma performansı değerlendirmesinde operasyonel ek yük ile tehdit kaynaklı kaynak tüketimini karıştırmamak için yararlıdır.

### T8 — Veri bütünlüğü, manipülasyon ve güvenilirlik ihlali

Veri, günlük, kayıt, model girdisi/çıktısı veya yapılandırmaların yetkisiz değiştirilmesi, silinmesi, çarpıtılması ya da güvenilmez hâle getirilmesi.

**Gerekçe:** Güvenlik kararları ve araştırma sonuçları, verinin bütünlüğüne bağlıdır. Bu kategori; log manipülasyonu, ölçüm sonuçlarının bozulması ve güvenilirlik kaybı gibi etkileri görünür kılar.

### T9 — Sosyal mühendislik, aldatma ve kimliğe bürünme

Kişileri veya sistemleri yanıltarak bilgi, erişim, işlem veya güven kazanmayı amaçlayan içerikler.

**Gerekçe:** Teknik bir araç kullanılmasa bile aldatma, siber güvenlik riskinin önemli bir kaynağıdır. Meşru farkındalık eğitimi ve simülasyonlarla gerçek kötüye kullanım amaçlarını ayırmak için niyet ve bağlam etiketleri gerekir.

### T10 — Tehlikeli veya yüksek etkili teknik yönlendirme

Doğrudan siber saldırı kategorilerine girmese de fiziksel güvenlik, kritik altyapı, sağlık, finans veya başka yüksek etkili alanlarda ciddi zarar doğurabilecek uygulanabilir yönlendirmeler.

**Gerekçe:** Proje siber güvenlik ve AI safety kesişiminde olduğundan, yalnızca klasik siber tehditlere odaklanmak yüksek etkili komşu riskleri gözden kaçırabilir. Kategori geniş tutulmalı, alt kapsam ve dahil etme kuralları sonraki anotasyon aşamasında netleştirilmelidir.

### T11 — Model ve değerlendirme bütünlüğünü bozma

Benchmark örneklerini sızdırma, değerlendirme sinyallerini manipüle etme, testleri seçici biçimde yürütme veya modelin gerçek davranışını ölçmeyi engelleme girişimleri.

**Gerekçe:** Araştırma sonuçlarının güvenilirliği yalnızca model yanıtına değil, deney sürecinin bütünlüğüne de bağlıdır. Bu kategori, veri sızıntısı ve değerlendirme yanlılığını tehdit modeli içinde tutar.

### T12 — Bağlam manipülasyonu ve belirsizlik istismarı

Önceki konuşma turlarını, rol/kimlik sinyallerini veya eksik bağlamı kullanarak isteğin riskini olduğundan düşük ya da yüksek göstermeyi amaçlayan etkileşimler.

**Gerekçe:** Bu proje özellikle single-prompt ve multi-turn analizini karşılaştırmaktadır. Bağlamın risk değerlendirmesini nasıl değiştirdiğini ayrı kategoride izlemek, temel tehdit türü ile bağlam etkisini karıştırmadan incelemeyi sağlar.

**Sınır notu:** Her bağlam etkisi kötüye kullanım değildir. Bağlamın meşru amacı netleştirdiği örnekler bu kategorinin karşılaştırma kümesinde yer alabilir, fakat otomatik olarak adversarial sayılmamalıdır.

## 4. Benign teknik kullanım için karşılaştırma etiketleri

Tehdit taksonomisi yalnızca riskli içerikleri kapsarsa, projenin kullanılabilirlik boyutu ölçülemez. Bu nedenle aşağıdaki etiketler tehdit kategorilerinden ayrı tutulmalıdır:

- **B1 — Meşru teknik geliştirme ve hata ayıklama:** Yazılım, sistem veya ağ sorunlarını çözme.
- **B2 — Savunma, tespit ve olay müdahalesi:** Tehdit avcılığı, tespit kuralı, log inceleme veya olay analizi.
- **B3 — Malware/reverse engineering analizi:** Zararlı yazılımı anlamaya, sınıflandırmaya veya etkisizleştirmeye yönelik güvenli analiz.
- **B4 — Güvenlik doğrulama ve yetkili test:** Yetkili ortamda yapılandırma, güvenlik testi veya kontrol doğrulama.
- **B5 — Akademik ve metodolojik araştırma:** Kavramsal analiz, ölçüm tasarımı, literatür ve deney planlama.

Bu etiketler “zararsız” sonucunu tek başına vermez. `legitimate_plausibility`, `maliciousness`, `expected_risk` ve `refusal_appropriateness` gibi boyutlarla birlikte kullanılmalıdır.

## 5. Ortak çapraz boyutlar

Her örnekte üst düzey kategoriye ek olarak aşağıdaki alanlar düşünülmelidir:

| Alan | Önerilen amaç |
|---|---|
| `adversariality` | İsteğin değerlendirme sistemini yanıltma veya savunmayı aşma niteliğini belirtmek |
| `maliciousness` | Kötüye kullanım niyeti ve göstergelerini değerlendirmek |
| `legitimate_plausibility` | Meşru kullanım açıklamasının makullüğünü değerlendirmek |
| `context_dependence` | Önceki turlar olmadan yorumun ne ölçüde eksik kaldığını belirtmek |
| `expected_risk` | Gerçekleşmesi hâlinde beklenen zarar ve uygulanabilirliği değerlendirmek |
| `refusal_appropriateness` | Reddin, kısmi yanıtın veya güvenli yönlendirmenin uygunluğunu değerlendirmek |
| `confidence` | Anotasyon kararındaki belirsizliği kaydetmek |
| `sensitivity` | İçeriğin kamuya açık depoda tutulup tutulamayacağını desteklemek |

Kesin ölçekler ve değer kümeleri, anotasyon yönergeleri hazırlanırken gerekçelendirilmelidir. Bu belge, henüz veri şeması veya nihai ölçek tanımlamaz.

## 6. Multi-turn bağlam etki sınıfları

80 multi-turn konuşmanın analizini desteklemek için aşağıdaki ayrı etiket önerilir:

- **C1 — Yorumu değiştiren bağlam:** Önceki turlar son isteğin anlamını belirgin biçimde değiştiriyor.
- **C2 — Meşru kullanım güvenini artıran bağlam:** Önceki turlar yetkili veya savunma amaçlı kullanımı destekliyor.
- **C3 — Risk güvenini artıran bağlam:** Önceki turlar zararlı niyet veya uygulanabilirlik sinyallerini güçlendiriyor.
- **C4 — Etkisi sınırlı bağlam:** Önceki turlar karar üzerinde anlamlı bir değişiklik oluşturmuyor.
- **C5 — Bağlamsız belirsiz son istek:** Son istek tek başına birden fazla makul yoruma açık.

Bu sınıflar T1–T12 kategorilerinin alternatifi değildir; aynı örnekte birlikte bulunabilir.

## 7. Risk sınıflandırması için önerilen karar akışı

1. İsteğin teknik alanını ve istenen çıktıyı belirle.
2. Meşru kullanım olasılığını ve kötüye kullanım sinyallerini ayrı kaydet.
3. T1–T12 arasından bir veya daha fazla tehdit kategorisi seç.
4. Doğrudan zarar, uygulanabilirlik, ölçeklenebilirlik ve geri döndürülemezlik göstergelerini değerlendir.
5. Multi-turn ise bağlam etki sınıfını ekle.
6. Beklenen risk ile reddetme uygunluğunu ayrı değerlendir.
7. Hassasiyet ve yayın kararını içerik ayrıntısından bağımsız olarak kaydet.
8. Belirsizliği ve anotasyon gerekçesini sakla.

Bu akış, güvenli anotasyon için kavramsal bir başlangıçtır; otomatik karar motoru veya savunma prototipi değildir.

## 8. Sınıflandırma gerekçesinin kaydı

Her anotasyon için en az şu bilgiler önerilir:

- Birincil ve ikincil tehdit kategorileri.
- Meşru kullanım etiketi varsa gerekçesi.
- Risk kararını destekleyen gözlemlenebilir sinyaller.
- Bağlamın kararı değiştirip değiştirmediği.
- Belirsizlik ve puanlayıcı notu.
- İçeriğin saklama/yayın hassasiyeti.

Hassas örneklerde gerekçe, operasyonel talimatın kendisini tekrar etmeyecek şekilde soyut yazılmalıdır.

## 9. Metodolojik riskler ve belirsizlikler

### Kategori örtüşmesi

Bir örnek birden fazla kategoriye girebilir. Tek etiket zorunluluğu, risk profilini aşırı basitleştirebilir. Çoklu etiket ve birincil kategori ayrımı kullanılmalıdır.

### Niyetin gözlemlenememesi

Bir model veya anotatör yalnızca metinden gerçek niyeti kesin biçimde çıkaramaz. “Kötücül” etiketi, kesin gerçeklik iddiası değil, gözlemlenebilir göstergelere dayalı değerlendirme olarak tanımlanmalıdır.

### Teknik hassasiyet ile zarar arasındaki fark

Malware analizi, reverse engineering ve güvenlik testi meşru olabilir. Alan adı tek başına reddetme kararı vermemelidir.

### Bağlamın karıştırıcı etkisi

Multi-turn örneklerde konuşma uzunluğu, bilgi miktarı ve son isteğin karmaşıklığı birlikte değişebilir. Bu değişkenler turn-level metadata ile kaydedilmelidir.

### Sağlayıcı politikalarının etkisi

Farklı modellerin politika ve sistem talimatları eşdeğer olmayabilir. Model sürümü, yapılandırma ve sistem talimatı raporlanmadan model aileleri hakkında güçlü sonuç çıkarılmamalıdır.

### Küçük pilot ve nadir kategoriler

300 örneklik pilotta bazı kategoriler az sayıda kalabilir. Alt grup sonuçları için belirsizlik aralıkları raporlanmalı; seyrek kategorilerden genelleme yapılmamalıdır.

### Hassas içerik ve yayın riski

Taksonomi açıkça yayımlanabilir; ancak ham adversarial örnekler, uygulanabilir saldırı adımları ve gerçek sırlar varsayılan olarak yayımlanmamalıdır. Kontrollü erişim, redaksiyon ve saklama süresi Phase 2 öncesinde tanımlanmalıdır.

## 10. Phase 2 öncesi açık kararlar

1. T1–T12’nin hangi kategorileri pilotta zorunlu, hangileri isteğe bağlı olacak?
2. Kategori örtüşmelerinde birincil kategori nasıl seçilecek?
3. “High risk” kararı hangi gözlemlenebilir ölçütlere dayanacak?
4. Benign karşılaştırma etiketleri tehdit kategorileriyle hangi veri modelinde birlikte tutulacak?
5. Bağlam etkisi için anotatörler hangi karşı-olgusal karşılaştırmayı kullanacak?
6. Hassasiyet seviyeleri ve kontrollü erişim kuralları nasıl uygulanacak?
7. Anotatör anlaşmazlıkları nasıl çözülecek ve hangi anlaşma ölçütü kullanılacak?

## 11. Önerilen sonraki adım

Bu ilk taksonomi kullanıcı tarafından onaylandıktan sonra, her kategori için güvenli ve operasyonel ayrıntı içermeyen örnekler hazırlanmalı; dahil etme/dışlama kuralları küçük bir pilot anotasyonla sınanmalıdır. Bu onay ve sınama tamamlanmadan veri kümesi oluşturulmamalı veya benchmark uygulanmamalıdır.
