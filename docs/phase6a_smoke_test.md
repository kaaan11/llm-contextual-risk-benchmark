# Phase 6A — Gerçek model smoke test

## Kapsam

Phase 6A, Phase 5 benchmark frameworkünün sınırlı gerçek-model hazırlık ve smoke test aşamasıdır. Tam 300 kayıtlık değerlendirme bu aşamada çalıştırılmaz. Smoke manifesti kaynak dataset'i değiştirmeden 20 benzersiz kaydı deterministik olarak seçer:

| Stratum | Kayıt |
|---|---:|
| benign | 6 |
| adversarial | 7 |
| multi_turn | 7 |
| Toplam | 20 |

Seçim manifesti `tests/fixtures/phase6a_smoke_manifest.json` içindedir. Manifest dataset kimliği/sürümü, duplicate ID, stratum üyeliği ve kaynak dosya hash'i ile doğrulanır.

## Güvenlik ve gizlilik

- API anahtarları yalnızca ortam değişkenlerinden okunur; config ve artifact'lere değerleri yazılmaz.
- Model adı ve tam sürüm/snapshot bilgisi canlı çalışma öncesi zorunludur. Sürüm değişkeni eksikse provider `not_evaluated` olarak raporlanır.
- Ham yanıtlar `results/` altında yerel tutulur ve Git'ten hariçtir.
- Prompt metinleri response log'a yazılmaz; request kimliği, turn sayısı ve SHA-256 digest yazılır.
- Hata mesajlarında bilinen bearer/API-key biçimleri maskelenir.
- Adversarial içerik pilot dataset'teki güvenli/redakte edilmiş biçimle sınırlıdır; yeni saldırı materyali üretilmez.

## Çalıştırma kapısı

Varsayılan komut preflight yapar ve ağa çıkmaz:

```text
<bundled-python> -m benchmark.smoke_test --config configs/phase6a_smoke.json
```

Gerekli ortam değişkenleri ve model sürümleri doldurulduktan sonra gerçek çağrı için ayrıca açık kapı gerekir:

```text
<bundled-python> -m benchmark.smoke_test --config configs/phase6a_smoke.json --live
```

Her provider için `configured`, `not_evaluated`, `disabled` veya `completed` durumu summary'ye yazılır. Eksik credential/model/sürüm sessizce atlanmaz.

## Ölçüm ve yorum sınırları

Her sonuçta başlangıç/bitiş UTC zaman damgaları, toplam request yaşam döngüsü `latency_ms`, sağlayıcı çağrısı ve retry/backoff dahil `provider_call_latency_ms`, deneme sayısı, durum, usage ve hata alanları tutulur. Metrics; başarı/durum dağılımı, benign refusal rate, adversarial yanıt/refusal sınıfları, ortalama/medyan/P95 latency ve mevcutsa token toplamlarını üretir.

`heuristic_v2` refusal detector; açık refusal, partial refusal, clarification, safe alternative, compliant answer, ambiguous ve api error sınıflarını verir. Bu kararlar ground truth değildir. İnsan anotasyonu ve hata analizi yapılmadan refusal rate bilimsel sonuç olarak yorumlanmamalıdır. Pilot dataset'te açık attack outcome bulunmadığı için ASR hesaplanmaz.

## Artifact'ler

Canlı çalışma olursa `results/smoke_test/phase6a-real-model-smoke/<provider>/` altında metadata, metrics ve JSONL response log oluşur. Varsayılan olarak `responses.jsonl` içinde model yanıt metinleri saklanmaz (`response_text: null`). Ham yanıt metinlerinin saklanması için `--raw-response-dir DIR` ile `results/` dışındaki bir dizin açıkça belirtilmelidir. Özet dosyası `summary.json` provider durumlarını, 20 kayıt manifestini, kaynak hash'lerini ve maliyet tahminini içerir. Fiyat yapılandırılmadığında maliyet `pricing_not_configured` olarak kalır; token tahmini gerçek usage değildir.

## Phase 6A sonucu

Bu çalışma için canlı provider çağrısı yalnızca credential ve model sürümü mevcutsa yapılabilir. Tam dataset değerlendirmesi, sonuçların bilimsel yorumlanması ve Phase 7 kapsamı bu aşamanın dışındadır; sonraki adım kullanıcı onayıdır.
