# Pilot veri kümesi

## Phase 6B kamu benchmark durumu

Phase 6B incelemesinde yeni public-benchmark manifesti oluşturulmadı. Mevcut `pilot_dataset.json` Phase 3’te üretilen 300 kayıtlı özgün pilot datasetidir ve Phase 6B nedeniyle değiştirilmemiştir. XSTest/JBB-Behaviors/WildGuardMix kaynakları metadata düzeyinde incelendi; JBB birim analizi, WildGuard erişim/lisans/locator politikası, immutable revision ve cross-source overlap kontrolleri sonuçlanmadan final `manifest.json` oluşturulması engellendi.

Ön denetim raporları `results/dataset_audit/`, kaynak kaydı `configs/phase6b_sources.json`, yöntem `docs/pilot_sampling_methodology.md` ve güvenli gate script’i `scripts/build_pilot_manifest.py` altındadır.

Bu dizin Phase 3’te pipeline tarafından üretilen pilot çıktıları içerir.

## Güvenlik durumu

- Toplam 300 benzersiz kayıt vardır.
- 120 benign, 100 adversarial değerlendirme ve 80 multi-turn kayıt bulunur.
- Adversarial kayıtlar canlı jailbreak veya uygulanabilir saldırı talimatı değildir; operasyonel ayrıntıları redakte edilmiş güvenli senaryo temsilleridir.
- `annotations` dizileri bilerek boştur. Uzman incelemesi yapılmamıştır ve yapılmış gibi gösterilmemelidir.
- Model değerlendirmesi henüz yapılmadığından `evaluations`, `evaluation_runs` ve `analysis_runs` boştur.
- Kayıtlarda kişisel veri, gerçek sır, erişim belirteci veya özel şirket bilgisi bulunmamalıdır; üretici bunu hedefler, ancak yayın öncesi insan incelemesi yine gereklidir.

## Dosyalar

- `pilot_dataset.json`: `dataset/schema.json` ile uyumlu canonical dataset manifesti ve 300 record.
- `records.jsonl`: Aynı record’ların ölçeklenebilir JSONL aktarımı.
- `attribution.json`: Public benchmark import durumu ve gelecekteki importlar için zorunlu attribution alanları.

## Kaynak dağılımı

Bu çalıştırmada tüm kayıtlar proje içi deterministic generator tarafından üretildi:

- 200 `research_generated` kayıt: benign ve multi-turn kolları.
- 100 `controlled_evaluation` kayıt: güvenli, redakte edilmiş adversarial senaryo kayıtları.
- 0 public benchmark import.

Public benchmark örneği gelecekte eklenirse özgün proje, URL/DOI, lisans, sürüm, özgün örnek kimliği, erişim tarihi, SHA-256 ve dönüşüm özeti `attribution.json` içinde kaydedilmelidir. Lisans ve yayın izni doğrulanmadan ham metin commit edilmemelidir.

## Yeniden üretim

Kök dizinden:

```text
<bundled-python> dataset/build_pilot.py
```

Üretici deterministiktir ve varsayılan seed metadata olarak kabul edilir. Yeni bir sürümde generator sürümü, dataset sürümü ve değişiklik özeti birlikte artırılmalıdır.
