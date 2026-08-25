# Phase 5 Benchmark Framework

## 1. Amaç

Bu belge, dataset ve annotation framework’ten sonra gelen benchmark execution katmanını tanımlar. Amaç OpenAI, Anthropic ve open-weight modelleri aynı deney sözleşmesiyle çalıştırabilen, sonuçları izlenebilir ve daha sonra genişletilebilir bir temel oluşturmaktır.

Phase 5 kapsamında yalnızca unit testler ve mock dry-run çalıştırılmıştır. Gerçek model evaluation yapılmamıştır.

## 2. Katmanlar

### Dataset loader

`benchmark.loader.DatasetLoader`, canonical `pilot_dataset.json` veya JSONL kayıtlarını okur, mevcut dataset doğrulayıcısını çağırır ve `EvaluationCase` nesnelerine dönüştürür. `limit`, `sample_ids` ve membership filtreleri küçük preflight çalıştırmalarını destekler.

### Adapter interface

`benchmark.adapters.base.ModelAdapter` tek bir `GenerationRequest -> AdapterResponse` sözleşmesi tanımlar. Runner sağlayıcı ayrıntılarını bilmez.

Sağlayıcı adapter’ları:

- `OpenAIAdapter`: Responses API biçiminde input ve text response normalizasyonu.
- `AnthropicAdapter`: Messages biçiminde payload ve content block text normalizasyonu.
- `OpenWeightAdapter`: Yerel veya hosted, JSON tabanlı open-weight endpoint’i.
- `MockAdapter`: Ağ ve credential olmadan deterministik test.

HTTP transport dependency injection ile değiştirilebilir. Böylece adapter testleri gerçek ağa ihtiyaç duymaz.

### Evaluation runner

`EvaluationRunner`:

1. Kaydın bağlam moduna göre mesajları seçer.
2. `GenerationRequest` oluşturur.
3. Adapter çağrısını `perf_counter` ile ölçer.
4. Yanıtı refusal detector’a verir.
5. Hata veya yanıtı `EvaluationResult` olarak loglar.
6. Metriklerin hesaplanabilmesi için sonuçları döndürür.

`current_prompt_only` modunda system/developer mesajları korunur ve önceki konuşma turları çıkarılır; son kullanıcı mesajı tutulur. `conversation_context` modunda tüm turn’ler korunur.

### Response logging

`JsonlResponseLogger` her sonucu bir satır olarak yazar. Kayıt; sample/evaluation/run kimliklerini, model metadata’sını, request digest’ini, response text’ini, latency’yi, usage bilgisini, refusal kararını ve hata alanını içerir.

Loglarda prompt metni varsayılan olarak tutulmaz; bunun yerine input turn sayısı ve SHA-256 request digest’i yazılır. Response text’in hassas olabileceği gerçek koşullarda `include_response_text=False` seçeneği kullanılmalıdır.

### Latency

Latency, adapter çağrısı çevresinde monotonic `perf_counter` ile ölçülen duvar saati süresidir ve milisaniye olarak kaydedilir. Sağlayıcının kendi processing time header’ı varsa ileride ayrı metadata olarak eklenebilir; iki ölçüm aynı kavram gibi birleştirilmemelidir.

### Refusal detection

Detector `heuristic_v2` olarak Türkçe ve İngilizce açık reddetme sinyallerini tarar; explicit, partial, clarification, safe alternative, compliant, ambiguous ve api error sınıflarını ayrı tutar. Detector ground truth değildir. Gerçek evaluation öncesi insan anotasyonlarıyla kalibrasyon gerekir.

### Metrics

`calculate_metrics` şu gözlemleri üretir:

- toplam/tamamlanan/hatalı istek sayısı ve durum dağılımı,
- toplam ve membership bazlı refusal rate,
- benign refusal rate ve adversarial yanıt/refusal sınıf dağılımı,
- toplam yaşam döngüsü ile sağlayıcı çağrısı için ortalama, medyan ve P95 latency,
- mevcutsa token kullanım toplamları,
- açık ground-truth outcome varsa ASR.

Pilot kayıtlarında gerçek outcome etiketi bulunmadığı için ASR otomatik olarak hesaplanmaz ve `not_computable_without_ground_truth` olarak raporlanır. Framework ölçülmemiş bir sonucu doldurmaz.

### Experiment metadata

`ExperimentMetadata` run kimliği, dataset/model sürümü, yapılandırma, bağlam modu, generation parametreleri, seed ve runner sürümünü taşır. API key, token veya secret alanı içermez.

## 3. Ortam değişkenleri

| Sağlayıcı | Gerekli değişkenler |
|---|---|
| OpenAI | `OPENAI_API_KEY`; isteğe bağlı `OPENAI_BASE_URL` |
| Anthropic | `ANTHROPIC_API_KEY`; isteğe bağlı `ANTHROPIC_BASE_URL`, `ANTHROPIC_API_VERSION` |
| Open-weight | `OPENWEIGHT_BASE_URL`; hosted ise isteğe bağlı `OPENWEIGHT_API_KEY` |

Anahtarlar kodda hard-code edilmez, experiment metadata’ya yazılmaz ve response loglarına eklenmez.

## 4. Mock dry-run kapsamı

Dry-run, pilot dataset’in ilk üç kaydını MockAdapter ile çalıştırır. Bir benign yanıt, bir genel yanıt ve bir redakte edilmiş adversarial senaryo için güvenli mock yanıtı kullanır. Çalıştırma gerçek provider’a bağlanmaz.

Dry-run çıktıları:

- `responses.jsonl`
- `experiment_metadata.json`
- `metrics.json`

Bu dosyalardaki latency ve refusal sonuçları yalnızca framework smoke testidir; araştırma sonucu veya model karşılaştırması değildir.

## 5. Gerçek evaluation daha sonra nasıl çalıştırılacak?

Approval sonrasında önerilen sıra:

1. Provider credential’larını runtime ortamına koy.
2. Tam model version/snapshot bilgisini `ModelSpec` ile dondur.
3. Dataset version ve experiment configuration metadata’sını üret.
4. `DatasetLoader` ile limitli preflight seç.
5. Adapter endpoint ve response parser’ını küçük çağrıyla doğrula.
6. Response saklama, redaksiyon ve sağlayıcı veri politikalarını kontrol et.
7. Tek model/tek yapılandırmayla küçük kontrollü run gerçekleştir.
8. Sonra A/B/C yapılandırmalarını aynı dataset ve karar kurallarıyla çalıştır.
9. Ham sonuçları değiştirmeden metrics ve analysis pipeline’ına aktar.

Bu aşamada API key eksikliği veya provider adapter kullanımı gerçek çağrı başlatmaz; gerçek run ayrı kullanıcı onayı gerektirir.
