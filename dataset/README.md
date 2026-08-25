# Dataset dizini

Bu dizin, LLM Security–Usability Benchmark veri kümesinin `0.1.0` temel şemasını ve Phase 7’de uygulanan `0.2.0` paired multi-turn uzantısını içerir.

## Durum

Phase 3 pilot dataset’i ve benchmark dry-run çıktıları mevcut olsa da Phase 7 uzantısı kapsamında yeni 50 multi-turn örnek, expert annotation veya model evaluation eklenmemiştir. v0.2.0 kayıtları için `canonical_final_prompt`, iki evaluation condition ve provenance alanları zorunludur; `model_observed_effect` evaluation öncesinde `null` kalır.

## Dosyalar

- `schema.json`: Dataset manifesti ve kayıtları için JSON Schema (Draft 2020-12).
- `../docs/schema_changelog.md`: v0.1.0’dan v0.2.0’a geçiş ve uyumluluk notları.
- `validate.py`: JSON Schema’nın tek başına ifade edemediği benzersizlik ve çapraz kayıt kurallarını denetleyen doğrulayıcı.
- `build_pilot.py`: Güvenli, deterministik pilot kayıtlarını üretmek ve duplicate kontrolü yapmak için pipeline.
- `annotation_schema.json`: Çoklu puanlayıcı anotasyonları için JSON Schema.
- `validate_annotations.py`: Annotation bundle çapraz kurallarını doğrulayan araç.
- `examples/synthetic_annotations.json`: Gerçek pilot anotasyonu olmayan, açıkça işaretlenmiş sentetik örnekler.

## Önerilen depolama biçimi

Küçük örneklerde şemadaki manifest biçimi kullanılabilir. Daha büyük veri kümelerinde ise aynı kayıt nesnelerinin JSON Lines (JSONL) biçiminde tutulması önerilir:

- `manifest.json`: Şema sürümü, veri kümesi sürümü, yayın profili ve run metadata.
- `records/*.jsonl`: Her satır bir `record` nesnesi.
- `annotations/*.jsonl`: Hassas veya ayrı erişim gerektiren anotasyonlar için isteğe bağlı ayrıştırılmış kayıtlar.
- `evaluations/*.jsonl`: Model değerlendirmelerinin ölçeklenebilir saklanması için isteğe bağlı ayrıştırılmış kayıtlar.

Bu ayrıştırma, ham hassas içeriğin kamuya açık temizlenmiş sürümden ayrı tutulmasını ve 3.000+ örneğe ölçeklenmeyi kolaylaştırır. Nihai fiziksel dosya düzeni Phase 3’te veri erişim politikasına göre kesinleştirilmelidir.

## Güvenlik ve gizlilik

- Gerçek API anahtarı, erişim belirteci, parola, kişisel veri veya özel şirket bilgisi eklenmemelidir.
- Hassas prompt ve yanıtlar için `content_ref`, `sha256` ve `redaction_status` alanları kullanılabilir.
- `public_sanitized` profilinde ham adversarial içerik varsayılan olarak tutulmamalıdır.
- `annotator_id` kişisel kimlik değil, takma ad veya güvenli kod olmalıdır.
- Özel erişim gerektiren dosyalar kaynak depoya veya paketlenmiş kamuya açık veri kümesine eklenmemelidir.

## Doğrulama

Kök dizinden şu komut çalıştırılabilir:

```text
<bundled-python> dataset/validate.py <dataset.json>
```

Testler için:

```text
<bundled-python> -m unittest discover -s tests -p "test_*.py"
```

Doğrulayıcı şu kuralları kontrol eder:

- Zorunlu alanlar ve temel türler.
- `sample_id`, `run_id` ve `analysis_id` benzersizliği.
- `dataset_membership` ile `record_type` uyumu.
- Tek turlu kayıtların tam bir tur içermesi.
- Çok turlu kayıtların en az iki tur içermesi.
- Turn sıra numaralarının ardışık olması.
- İçerik veya güvenli içerik referansı bulunması.
- Kayıt değerlendirmelerinin tanımlı bir `evaluation_run` ile eşleşmesi.
- Anotasyon ve sürüm/tarih biçimlerinin temel tutarlılığı.
- v0.2.0 multi-turn kayıtlarında benzersiz `conversation_id`.
- v0.2.0 multi-turn kayıtlarında `source=original` ve record `dataset_version` eşleşmesi.
- Canonical prompt, iki koşul ve son user turn arasında exact equality.
- Canonical prompt SHA-256 bütünlüğü.
- Expected/observed effect ayrımı ve evaluation öncesi `null` observed effect.
- Authoring/provenance, researcher QC ve external validation durumlarının kontrollü değerleri.

## Şema sürümleme

Şema `0.1.0` olarak başlatılmış, Phase 7 paired multi-turn alanları için `0.2.0` sürümüne genişletilmiştir. Eski v0.1.0 kayıtları yeniden yazılmaz; v0.2.0 single-turn kayıtları yeni paired alanlarını gerektirmez, v0.2.0 multi-turn kayıtları ise bu alanları zorunlu olarak taşır. Geriye dönük uyumsuz değişikliklerde major sürüm artırılmalı; yeni uyumlu alanlarda minor sürüm; düzeltmelerde patch sürüm kullanılmalıdır.
