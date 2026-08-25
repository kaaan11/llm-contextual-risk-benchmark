# Benchmark framework

Bu paket Phase 5 evaluation framework’ünün ilk modüler sürümüdür. Gerçek model çağrısı yapmadan dataset loader, adapter sözleşmesi, runner, yanıt loglama, latency, refusal detection, metrik ve experiment metadata katmanlarını sağlar.

## Mimari

```text
DatasetLoader
      |
      v
EvaluationCase + ExperimentMetadata
      |
      v
EvaluationRunner ----> ModelAdapter
      |                    |
      |                    +-- MockAdapter
      |                    +-- OpenAIAdapter
      |                    +-- AnthropicAdapter
      |                    +-- OpenWeightAdapter
      |
      +--> Latency measurement
      +--> RefusalDetector
      +--> ResponseLogger (JSONL)
      +--> Metric calculator
```

## Güvenlik

- API anahtarları kaynak koda yazılmaz.
- OpenAI: `OPENAI_API_KEY`
- Anthropic: `ANTHROPIC_API_KEY`
- Open-weight hosted endpoint: isteğe bağlı `OPENWEIGHT_API_KEY` ve zorunlu `OPENWEIGHT_BASE_URL`
- Anahtar değerleri metadata veya response loglarına yazılmaz.
- Gerçek evaluation öncesinde endpoint, model sürümü, veri sürümü ve retention politikasının ayrıca onaylanması gerekir.

## Dry-run

Kök dizinden aşağıdaki komut yalnızca üç kayıt ve `MockAdapter` kullanır:

```text
<bundled-python> -m benchmark.dry_run
```

Çıktılar `benchmark/runs/mock-dry-run/` altında `responses.jsonl`, `experiment_metadata.json` ve `metrics.json` dosyalarıdır. Bu sonuçlar araştırma sonucu değildir.

## Gerçek evaluation için sonraki adımlar

1. Sağlayıcı credential’larını yalnızca runtime ortam değişkenlerine yükle.
2. Model adını ve tam sürüm/snapshot bilgisini `ModelSpec` içinde sabitle.
3. Önce tek model, tek yapılandırma ve çok küçük `limit` ile preflight çalıştır.
4. Yanıt loglarının hassasiyet ve saklama politikasını onayla.
5. Refusal detector’ı insan anotasyonlarıyla kalibre et.
6. Sonra kontrollü, tekrarlı evaluation run’larına geç.

Bu aşamada gerçek provider çağrısı çalıştırılmamıştır.

## Phase 6A smoke test

Phase 6A için `benchmark.smoke_test` 20 kayıtlık deterministik manifesti doğrular, provider/model sürümü/credential preflight'ı yapar, bounded retry ve güvenli hata maskelemesi uygular. Varsayılan çalışma ağa çıkmaz; gerçek çağrı için ayrıca `--live` gerekir:

```text
<bundled-python> -m benchmark.smoke_test --config configs/phase6a_smoke.json
<bundled-python> -m benchmark.smoke_test --config configs/phase6a_smoke.json --live
```

Çıktılar `results/smoke_test/phase6a-real-model-smoke/` altında yerel tutulur ve Git'e alınmaz. Mevcut ortamda gerekli credential/model sürümü yoksa her provider açıkça `not_evaluated` durumuyla raporlanır.
