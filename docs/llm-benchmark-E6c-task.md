# E6c — Offline uçtan uca bütünleşik prova

Durum: E5a–E5d ile E6a/E6b kabulünü bekliyor. Sahip: küçük worker.  
Ortak kurallar: [worker sözleşmesi](llm-benchmark-worker-contract.md).

## Hedef

Schedule → captured mock payload → attempt/outcome ledger → tamamlanma manifestosu → sürümlü analiz → rapor zincirini yeni `/tmp` run'ında sıfır ağ erişimiyle doğrula. Mock politikanın sonuçları bilimsel benchmark bulgusu değildir.

## Prova matrisi

En az iki aynı başarılı koşu, retry sonrası başarı, kalıcı timeout, provider filter, truncation, not-run budget, beklenen missing, duplicate/resume, yarım writer kesintisi ve stale hash senaryoları. Başarı koşusunda deterministik data/provenance eşdeğerliği; failure koşullarında doğru farklılık ve fail-closed reader beklenir.

Gerçek QC tamamlanmamışsa sahte KEEP/Layer-B üretme. Pipeline'ın pre-QC engelini kanıtla; full success entegrasyonu E4b'nin gerçek dondurulmuş girdisini bekleyen ayrı profil olabilir. Mevcut `benchmark/runs/mock-dry-run` üzerine yazma; yeni geçici dizin kullan.

## Kabul

- Hiçbir gerçek adapter/credential/network kullanılmaz; captured transport sayısı schedule/attempt ledger ile uzlaşır.
- Aynı sabit girdide açıklanmayan analiz veya bundle farkı yoktur; değişken timestamp gibi alan politikası önceden yazılıdır.
- Missing/duplicate/error hiçbir karar metriğine sessizce girmez; coverage ve technical completion ayrıdır.
- Frozen hashler, stimulus v1 ve audit prefix'i değişmez.

Teslim: `integration-matrix.md`, run hash envanterleri, karşılaştırma helper'ı gerekiyorsa kaynak ve tüm gerçek loglarla standart paket. E7 veya canlı run başlatma.

