# Araştırma Soruları ve Kapsam

## 1. Amaç

Bu belge, **LLM Security–Usability Benchmark** projesinin Phase 0 kapsamını tanımlar. Amaç, Büyük Dil Modellerinin (LLM) güvenlik mekanizmalarında güvenlik ile kullanılabilirlik arasındaki dengeyi, tek bir istek üzerinden yapılan risk analizi ile çok turlu ve bağlam farkındalıklı risk analizini karşılaştırarak incelemektir.

Bu bir jailbreak koleksiyonu veya saldırı aracı değildir. Araştırma; güvenlik değerlendirmesi, meşru fakat teknik açıdan hassas kullanımların korunması, yeniden üretilebilirlik ve sorumlu veri yönetimi üzerine kuruludur.

## 2. Birincil araştırma sorusu

> Bağlam farkındalıklı risk analizi, tek-istek değerlendirmesine kıyasla LLM güvenlik mekanizmalarının güvenlik–kullanılabilirlik dengesini iyileştirebilir mi?

Buradaki “iyileştirme” önceden kabul edilmiş bir sonuç değildir. Çalışma; iyileşme, anlamlı bir fark bulunmaması veya olumsuz sonuç olasılıklarını eşit biçimde değerlendirecek şekilde tasarlanmalıdır.

## 3. Destekleyici araştırma soruları

### RQ1 — Model aileleri arasındaki farklar

Farklı LLM aileleri; adversarial değerlendirme örnekleri ve teknik açıdan hassas fakat meşru etkileşimler karşısında güvenlik–kullanılabilirlik dengesinde nasıl farklılaşır?

**Kapsam:** Başlangıçta OpenAI, Anthropic ve bir open-weight model ailesinden temsilî modeller. Kesin model sürümleri her değerlendirme aşamasından önce dondurulmalı ve kayıt altına alınmalıdır.

### RQ2 — Bağlamın katkısı

Multi-Turn Context-Aware Risk Analysis, Single-Prompt Risk Analysis’e kıyasla ölçülebilir bir avantaj sağlar mı?

**Kapsam:** Aynı son isteğin yalnız başına ve önceki konuşma turlarıyla birlikte değerlendirilmesi. Bağlamın yorumu değiştirdiği, meşru kullanım güvenini artırdığı, risk güvenini artırdığı veya çok az etkilediği durumlar ayrı izlenmelidir.

### RQ3 — Hafif savunma katmanının etkisi

Hafif bir Context-Aware Defensive Layer, adversarial başarıyı azaltırken meşru isteklerin gereksiz reddini ve operasyonel gecikme ek yükünü pratik açıdan kabul edilebilir düzeyde tutabilir mi?

**Kapsam:** Başlangıçta üç yapılandırma karşılaştırılmalıdır:

1. **A — Baseline:** İlave savunma katmanı yok.
2. **B — Single-Prompt Defensive Layer:** Yalnızca mevcut isteği analiz eden savunma katmanı.
3. **C — Multi-Turn Context-Aware Defensive Layer:** Mevcut istek, önceki turlar ve bağlamsal sinyalleri birlikte analiz eden savunma katmanı.

Bu aşamada savunma prototipi uygulanmayacaktır; yapılandırmalar yalnızca deney tasarımının kapsamını tanımlar.

### RQ4 — Birleşik optimizasyon ve Pareto sınırı

Güvenlik, kullanılabilirlik ve operasyonel ek yük birlikte değerlendirildiğinde ölçülebilir Pareto-etkin bölgeler ortaya çıkar mı?

**Kapsam:** Tek bir metriği optimize etmek yerine güvenlik, görev başarısı/görev sadakati ve gecikme/hesaplama maliyetleri arasındaki değiş tokuş incelenmelidir.

## 4. Birincil hipotez

> Hafif bir Multi-Turn Context-Aware Defensive Layer, meşru isteklerin gereksiz reddini veya operasyonel gecikmeyi orantısız biçimde artırmadan risk ayrımını iyileştirebilir ve adversarial başarıyı azaltabilir.

Bu hipotez yönlendirici bir araştırma varsayımıdır; beklenen sonucu garanti etmez. Analiz planı, sonucu hipotezi doğrulayacak şekilde seçmemeli veya ölçümleri sonradan değiştirmemelidir.

## 5. Kapsam ve kapsam dışı konular

### Kapsam dahilinde

- Meşru fakat teknik olarak hassas isteklerin gereksiz reddedilmesinin incelenmesi.
- Kontrollü adversarial değerlendirme.
- Tek-istek ve çok-turlu bağlamın karşılaştırılması.
- Model, yapılandırma, veri sürümü, örnek ve değerlendirme tarihinin kaydedilmesi.
- Güvenlik, kullanılabilirlik ve operasyonel ek yükün birlikte raporlanması.
- Hassas içeriğin azaltılması, erişim kontrollü tutulması ve kamuya açık çıktılarda yalnızca güvenli örneklerin kullanılması.

### Kapsam dışında

- Gerçek sistemlere yetkisiz erişim veya saldırı.
- Ham jailbreak içeriklerinin gereksiz biçimde toplanması ya da yayımlanması.
- Savunma prototipinin bu aşamada uygulanması.
- Veri kümesinin bu aşamada oluşturulması.
- Ölçülmemiş model performansı, uzman doğrulaması veya deney sonucu iddiası.

## 6. Pilotun tasarım kısıtları

Pilot, toplam **300 benzersiz örnek** hedeflemektedir:

- 120 benign örnek,
- 100 adversarial değerlendirme örneği,
- 80 multi-turn konuşma.

Yaklaşık 50 örnek ayrıca uzman incelemesine alınabilir. “Uzman incelemesi”, veri kümesi kategorisi değil, anotasyon/doğrulama özelliğidir; örneklerin ana kategorileriyle çakışabilir.

Benign bölüm, özellikle yazılım geliştirme, hata ayıklama, sistem yönetimi, siber güvenlik, tehdit analizi, malware analizi, reverse engineering, ağ, DevOps, güvenlik mühendisliği ve akademik araştırma gibi meşru teknik alanları kapsamalıdır. Örneklerin kaynak dağılımı ayrıca belgelenmelidir.

## 7. Ölçüm çerçevesi

Bu belgede eşik veya beklenen performans hedefi belirlenmemektedir. Önce baseline ölçülmeli, daha sonra göreli farklar ve belirsizlikleri raporlanmalıdır.

### Güvenlik

- **Attack Success Rate (ASR):** Kontrollü adversarial değerlendirmelerde tanımlı başarı ölçütünü karşılayan sonuçların oranı.

ASR’nin kesin karar kuralı; veri etiketleri, değerlendirme protokolü ve güvenli anotasyon yönergeleri belirlendikten sonra yazılmalıdır.

### Kullanılabilirlik

- **Benign Refusal Rate:** Benign olarak etiketlenmiş örneklerdeki reddetme oranı.
- **Over-Refusal Rate:** Meşru ve yanıtlanabilir olarak değerlendirilen örneklerin uygunsuz biçimde reddedilme oranı.
- **Legitimate Task Completion:** Meşru görevin kabul edilebilir biçimde tamamlanma oranı.
- **Task Fidelity:** Yanıtın görevin niyetini ve gereksinimlerini ne ölçüde karşıladığı.

Benign Refusal Rate ile Over-Refusal Rate aynı kavram olarak kullanılmamalıdır; ikincisi, reddin uygun olup olmadığına ilişkin etiketleme kuralını gerektirir.

### Operasyonel performans

- Ortalama, medyan ve P95 gecikme.
- CPU ve bellek kullanımı.
- İlave model çağrısı sayısı.

Donanım, ağ koşulları, önbellek durumu, tekrar sayısı ve zaman ölçüm noktaları kayıt altına alınmadan gecikme karşılaştırmaları yorumlanmamalıdır.

## 8. Kayıt altına alınması gereken alanlar

Her değerlendirme en az şu bilgileri taşımalıdır:

- Model adı ve sürümü.
- Değerlendirme tarihi ve zaman dilimi.
- Yapılandırma (A, B veya C).
- İlgili system instruction ve çalışma ayarları.
- Veri kümesi sürümü.
- Örnek veya konuşma kimliği.
- Model yanıtı ya da güvenli şekilde saklanmış yanıt referansı.
- Gecikme ve ölçüm koşulları.
- Değerlendirme sonucu ve kullanılan karar kuralı.

Hassas ham adversarial içerik, kamuya açık depoya varsayılan olarak yazılmamalıdır. Kamuya açık sürüm; taksonomi, şema, metodoloji, temizlenmiş örnekler, kod ve toplulaştırılmış sonuçlarla sınırlandırılabilir.

## 9. Anotasyon ilkeleri

İlerideki anotasyon çerçevesi en az şu boyutları değerlendirebilecek şekilde tasarlanmalıdır:

- Adversariality.
- Maliciousness.
- Legitimate Plausibility.
- Context Dependence.
- Expected Risk.
- Refusal Appropriateness.
- Confidence.

Ölçekler, puanlayıcı sayısı ve karar eşikleri gerekçelendirilmeden kesinleştirilmemelidir. Anotasyon tasarımı kesinleştiğinde uygun anlaşma ölçütü (ör. Cohen’s Kappa, Fleiss’ Kappa veya Krippendorff’s Alpha) seçilmelidir.

## 10. Metodolojik riskler ve açık sorular

### Riskler

- “Adversarial başarı” ve “uygun reddetme” için karar kuralları farklı yorumlanabilir.
- Teknik olarak hassas benign örneklerle kötüye kullanım amacı taşıyan örnekleri ayırmak anotasyon yanlılığı yaratabilir.
- Multi-turn konuşmalarda bağlam uzunluğu, son istek ve konuşma sırası birbirini etkileyebilir.
- Model sürümü, sistem talimatı, sıcaklık ve servis değişiklikleri tekrarlanabilirliği etkileyebilir.
- Farklı sağlayıcıların güvenlik politikaları doğrudan karşılaştırılabilir olmayabilir.
- Gecikme ve ek model çağrısı sayısı, savunma katmanının gerçek operasyonel maliyetini eksik yansıtabilir.
- Küçük pilot örnekleminde alt gruplar için belirsizlik aralıkları geniş olabilir.
- Uzman incelemesi yapılmadan “uzman doğrulaması” ifadesi kullanılamaz.

### Phase 2 öncesi yanıtlanması gereken sorular

1. Benign, adversarial ve multi-turn kategorilerinin çakışmasına hangi kurallarla izin verilecek?
2. Multi-turn konuşmalarda birim analiz “konuşma” mı, “son tur” mu olacak?
3. ASR, Task Fidelity ve Refusal Appropriateness için güvenli ve tekrarlanabilir karar kuralları nasıl tanımlanacak?
4. Uzman incelemesinde kaç puanlayıcı, hangi yeterlilik ölçütü ve hangi körleme yöntemi kullanılacak?
5. Sağlayıcılar arası model sürümleri ve yapılandırma eşleştirmesi nasıl raporlanacak?
6. Hassas veri için erişim, saklama süresi, redaksiyon ve silme prosedürü ne olacak?
7. Pilotun istatistiksel gücü hangi etki büyüklüğü ve belirsizlik varsayımlarıyla değerlendirilecek?

## 11. Önerilen sonraki adım

Phase 2’ye geçmeden önce bu kapsam ve ilk tehdit taksonomisi onaylanmalıdır. Onaydan sonra önerilen sıra şöyledir:

1. Taksonomi ve etiket sözlüğünü küçük, güvenli örneklerle sınamak.
2. Veri kümesi şemasını ve örnek kimliği kurallarını tasarlamak.
3. Anotasyon yönergelerini ve pilot anotasyon planını yazmak.
4. Veri üretimine başlamadan önce hassas içerik ve sorumlu yayın politikasını kesinleştirmek.

Bu dosya yalnızca araştırma tasarımını tanımlar; veri, ölçülmüş sonuç veya uygulama üretmez.
