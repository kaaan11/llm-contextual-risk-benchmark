# E5d — Canonical preflight, bütçe ve run bütünlüğü

Durum: E4b ve E5a–E5c kabulünü bekliyor. Sahip: küçük worker.  
Ortak kurallar: [worker sözleşmesi](llm-benchmark-worker-contract.md).

## Hedef

Gerçek Phase 8 giriş noktasında insan-QC, bilimsel sözleşme, schedule, payload, bütçe ve output bütünlüğünü tek fail-closed preflight zincirinde zorunlu kıl. Bu görev canlı evaluation çalıştırmaz.

## Kapsam

Canonical runner/script girişini, `benchmark/preflight.py`, schedule/outcome/artifact writer-reader'ı ve config'i değiştir. Mock yolunun canlıya fallback yapmadığını koru. Yeni genel depolama framework'ü kurma; küçük completion manifest ve atomik yayın sınırı yeterliyse kullan.

## Kapılar

- E4b accepted population ve Layer-B referans hash'i; etkin protocol/amendment; dataset/stimulus sürümü; exact run config/payload contract; schedule hash'i eksiksiz olmalı.
- Strict preflight kanonik yolda opsiyonel olamaz ve ilk dispatch'ten önce tamamlanır.
- İnsan tarafından seçilen physical attempt/maliyet cap'i her dispatch öncesi tek sahipte rezerve edilir. Tam v1 r=3: 513 logical job; max_attempts=3 üst sınırı 1.539 physical attempt. Yetmeyen cap kapsam eksikliği üretir, sessiz artmaz.
- Yarım, stale, karışık-hash, duplicate veya expected schedule ile uyuşmayan run analiz için complete görünmez. Technical completion ile scientific coverage ayrı alanlardır.
- Resume/restart aynı job'ı sessizce yeniden göndermemeli; açık politika ve idempotency kaydı olmalı.

## Kabul

Injected no-network dispatcher ile her eksik kapının sıfır dispatch ürettiğini; cap sınırını; kesinti/yarım bundle/stale hash/duplicate/resume yollarını doğrula. Başarı fixture'ı gerçek E4b hashlerini salt okunur kullanabilir fakat annotation üretmez/değiştirmez. `canonical-run-contract.md`, completion schema ve standart kanıt paketi teslim et. Phase 8'i başlatma.

