# Phase 3 Pilot Örnekleme ve Yayın Planı

## 1. Amaç

Bu belge, 300 benzersiz kayıttan oluşan pilot veri kümesinin nasıl üretildiğini ve hangi kayıtların güvenli biçimde sürümlenebileceğini açıklar. Pipeline, gerçek model değerlendirmesi veya uzman incelemesi yapmaz; yalnızca veri yapısını ve güvenli pilot girdilerini üretir.

## 2. Örnekleme stratejisi

Pilot üç ayrık kola bölünmüştür:

| Kol | Kayıt sayısı | Yapı | İçerik yaklaşımı |
|---|---:|---|---|
| Benign | 120 | Tek turlu | Teknik açıdan hassas fakat meşru, savunma ve araştırma odaklı istekler |
| Adversarial değerlendirme | 100 | Tek turlu | Operasyonel ayrıntıları çıkarılmış güvenli tehdit senaryoları |
| Multi-turn | 80 | En az dört turlu | Bağlam etkisini ölçmek için C1–C5 senaryoları |

Toplam 300 kaydın `sample_id` değerleri benzersizdir. Bu pilotta kol üyelikleri inşa aşamasında ayrık tutulmuştur; schema yine de gelecekteki örtüşen alt kümeleri destekler.

### 2.1 Benign dağılımı

120 kayıt, 12 teknik alan arasında eşit dağıtılmıştır; her alanda 10 kayıt vardır:

- Yazılım geliştirme
- Hata ayıklama
- Sistem yönetimi
- Savunmacı siber güvenlik
- Tehdit analizi
- Malware analizi
- Reverse engineering
- Ağ ve networking
- DevOps
- Güvenlik mühendisliği
- Akademik araştırma
- AI safety değerlendirmesi

Bu alanlar, projenin “trivial everyday prompts” yerine teknik açıdan anlamlı benign kullanım hedefiyle uyumludur. Benign kayıtlar gerçek kullanıcı verisinden değil, araştırma amaçlı ve sentetik olarak yazılmış güvenli görevlerden oluşur.

### 2.2 Adversarial dağılımı

100 kayıt, başlangıç taksonomisinin T1–T10 kategorilerine 10’ar kayıt olarak dağıtılmıştır. Her kategori için 10 farklı değerlendirme baskısı/çerçevesi kullanılmıştır; ancak hiçbirinde gerçek hedef, kimlik bilgisi, komut, kod, kaçınma tekniği veya uygulanabilir saldırı adımı bulunmaz.

Bu kol canlı jailbreak koleksiyonu değildir. Kayıtlar, “redakte edilmiş güvenli senaryo” temsilleridir ve değerlendirme metodolojisini belgelemek için uygundur. Gerçek kontrollü adversarial materyal ileride gerekirse özel veya erişim kontrollü ortamda ayrıca tutulmalıdır.

### 2.3 Multi-turn dağılımı

80 konuşma, aşağıdaki beş bağlam etkisine 16’şar kayıt olarak dağıtılmıştır:

- **C1:** Bağlam son isteğin yorumunu değiştiriyor.
- **C2:** Bağlam meşru kullanım güvenini artırıyor.
- **C3:** Bağlam risk güvenini artırıyor.
- **C4:** Bağlamın etkisi sınırlı.
- **C5:** Son istek önceki turlar olmadan belirsiz.

Her konuşmada önceki turlar korunur ve final turu ayrı bir bağlam sinyaliyle işaretlenir. Bu yapı ileride `current_prompt_only` ile `conversation_context` koşullarının eşleştirilmesini sağlar.

## 3. Üretim ve provenance

Kayıtlar `dataset/build_pilot.py` tarafından deterministik şablonlardan üretilmiştir. Üretim sürümü, dataset sürümü ve kaynak türü her kayda metadata olarak eklenir.

Bu çalıştırmanın kaynak dağılımı:

- 120 benign + 80 multi-turn = 200 `research_generated` kayıt.
- 100 adversarial = 100 `controlled_evaluation` kayıt.
- Public benchmark import = 0.

Expert annotation veya expert review yapılmamıştır. Her kaydın `annotations` dizisi boştur.

## 4. Duplicate tespit stratejisi

Pipeline iki seviyeli kontrol uygular:

1. Metin Unicode NFKC ile normalize edilir, büyük/küçük harf ve whitespace farkları giderilir.
2. Normalleştirilmiş turn içeriğinden SHA-256 kaydı parmak izi üretilir; aynı parmak izi exact duplicate sayılır.
3. Üçlü token shingles üzerinden Jaccard benzerliği hesaplanır; eşik üzerindeki fakat aynı olmayan kayıtlar near duplicate olarak işaretlenir.
4. Duplicate bulunduğunda pipeline dataset yazmadan hata verir.

`sample_id` benzersizliği ayrıca dataset doğrulayıcısı tarafından kontrol edilir. Bu yöntem semantik eşdeğerliği tamamen garanti etmez; insan incelemesi ve sonraki veri kürasyonu yine gereklidir.

## 5. Dataset contamination azaltma

Contamination tamamen ölçülebilir veya garanti edilebilir bir özellik değildir; modelin geçmiş eğitim verisi bilinmeyebilir. Pilot için şu önlemler alınmıştır:

- Dış benchmark örnekleri bu çalıştırmada içe aktarılmadı.
- Benign kayıtlar yeniden üretilebilir, proje içi ve sentetik olarak yazıldı.
- Adversarial kayıtlar kamuya açık saldırı metni kopyalamak yerine redakte edilmiş senaryo özetleri olarak üretildi.
- Her kayıt generator sürümü, dataset sürümü, kaynak tipi ve template kimliği taşır.
- Değerlendirme yapılırken model sürümü ve system configuration dondurulmalıdır.
- Sonuç analizi, üretim şablonları ile evaluation kayıtlarını birbirinden ayrı sürümlemelidir.
- Gelecekte train/evaluation ayrımı yapılırsa aynı aileden template’lerin farklı split’lere sızması ayrıca denetlenmelidir.

Bu önlemler public web veya model pretraining contamination’ını ortadan kaldırmaz; yalnızca araştırma veri üretiminden kaynaklanan sızıntıyı azaltır.

## 6. Public benchmark attribution

Phase 3 çıktısında public benchmark kaydı yoktur. Bu nedenle herhangi bir dış projeye ait örnek için kaynak veya lisans iddiasında bulunulmamıştır.

Gelecekte import yapılırsa her kayıt veya kayıt grubu için en az şu alanlar saklanmalıdır:

- yayıncı veya proje adı,
- URL veya DOI,
- lisans,
- kaynak sürümü/release,
- özgün örnek kimliği,
- erişim tarihi,
- özgün içerik veya alınan içerik için SHA-256,
- uygulanan redaksiyon/çeviri/dönüşüm özeti.

Lisans ve yeniden dağıtım izni doğrulanmayan ham public benchmark metni GitHub’a commit edilmemelidir. Gerekirse yalnızca özgün kimlik, kaynak metadata’sı ve temizlenmiş türev tutulmalıdır.

## 7. GitHub’a güvenle commit edilebilecek içerik

Bu pilotun yayın profili `public_sanitized` olarak işaretlenmiştir. İnsan sorumlu yayın incelemesinden sonra şu içerikler commit edilebilir:

- `dataset/schema.json`
- üretim ve doğrulama kodu
- metodoloji, örnekleme planı ve veri sözlüğü
- sentetik benign örnekler
- operasyonel ayrıntıları çıkarılmış adversarial senaryo temsilleri
- toplulaştırılmış sayımlar ve veri kalite raporları
- attribution metadata’sı

Şu içerikler commit edilmemelidir:

- ham veya uygulanabilir jailbreak/saldırı talimatları,
- gerçek sırlar, parolalar, tokenlar ve API anahtarları,
- kişisel veri,
- özel şirket veya erişim kontrollü içerik,
- uzmanların kişisel kimlik bilgileri,
- henüz yayın izni doğrulanmamış dış benchmark metinleri,
- model yanıtlarında oluşabilecek hassas içerik.

## 8. Sonraki aşama için sınırlar

Bu pipeline dataset construction aşamasında durur. Model çağrısı, benchmark evaluation, uzman anotasyonu, ASR hesabı, latency ölçümü veya istatistiksel sonuç üretmez. Model değerlendirmesine geçmeden önce dataset ve yayın politikası yeniden gözden geçirilmelidir.
