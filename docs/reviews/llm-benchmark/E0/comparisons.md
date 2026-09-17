# E0 — Başlangıç/bitiş karşılaştırması

## Referanslar

- Başlangıç HEAD ve çalışma ağacı: `9dd9d31607b3d97c02fe3ef9b7cfb68b4a3ed50e`, branch `master`,
  tracked dirty yalnız `M .gitignore`; untracked: 20 brief/plan dosyası + `docs/reviews/` + `uv.lock`
  (`logs/01-git-head-status.sh.stdout`, `hashes-start.txt`). E0 dizini iskelet
  (`README.md`, `commands.jsonl`, `comparisons.md`, `NOT_STARTED`).
- Bitiş HEAD ve çalışma ağacı: aynı HEAD; commit/push/branch yok. Tracked dirty aynı
  (`.gitignore` kullanıcı değişikliği korundu). Untracked'a E0 teslim belgeleri eklendi:
  `baseline.md`, `findings.md`, `test-safety.md`, `provenance-scope.md`, `hashes-start/end.txt`,
  `delivery.diff`, `run-outputs.sha256`, `logs/` (`logs/10-diff-check.sh.stdout`, `hashes-end.txt`).
- Önceki kabul kaydı: yok (ilk teslim E0; `E0-acceptance.md` ana inceleyici tarafından yazılacak).
- Geçici çalışma dizini: kullanılmadı (rapor ZIP'i kalıcı repoya açılmadı).
  Raporlar salt okunur `/home/kaan/GPT-Pro/reports/LLM_Benchmark` ve
  `/tmp/llm-benchmark-review-20260909` dizinlerinden okundu. Test çıktısı `/tmp` önerisi
  `test-safety.md` §2'dedir; E0'da test çalıştırılmadı.

## Dosya ve hash farkları

Beklenen farklar (E0 teslimi):

- `docs/reviews/llm-benchmark/E0/` altında 8 yeni belge + `logs/` (11 komut × stdout/stderr/log) eklendi.
  Untracked oldukları için düz `git diff` içinde görünmezler; burada sayıldılar.
- `hashes-start.txt` → `hashes-end.txt`: mühürlü/audit/QC/stimulus/rapor değerleri birebir aynı;
  yalnız `E0_SKELETON_AT_START` → `E0_DELIVERY_FILES` satırı değişti (beklenen).

Beklenmeyen farklar: yok.

- Mühürlü 6 protokol dosyası + composite: başlangıç=bitiş (`logs/04-composite.sh.stdout`).
- Stimulus v1 hash + 50/171 + final-byte 50/50: başlangıç=bitiş (`logs/05-stimulus.log`).
- QC sayıları (49 PENDING + 1 PARTIAL, rater_a 1/50, rater_b 0/50, kararlar 50 PENDING): aynı.
- Audit history prefix (51 + 5 satır, hash'ler aynı): aynı; yazım yok.
- `git diff --check`: temiz (`logs/10-diff-check.sh.stdout`).
- `delivery.diff`: tracked fark yalnız başlangıçtaki `.gitignore` değişikliğidir; E0 bu dosyaya dokunmadı.

## Davranış karşılaştırması

E0 kod davranışı değiştirmez; pozitif/negatif kabul örnekleri belge/kanıt düzeyindedir:

- Başlangıç kullanıcı değişiklikleri korundu: `M .gitignore` bitişte aynı; untracked `uv.lock` + briefler duruyor.
- Mühürlü dosyalar korundu: per-file + composite eşleşti (başlangıç/bitiş).
- Çalıştırılmayan test / bulunmayan dış artefakt görülmüş/geçmiş sayılmadı:
  tam suite, `verify_contract.py`, `prospective_sensitivity.py`, model/API çağrısı çalıştırılmadı;
  Sohbet'in işaret ettiği ek PDF/ZIP'ler yok sayıldı (`baseline.md` §3, `findings.md` açık liste).
- Kaynaklar tek kanıt gibi birleştirilmedi: ZIP manifestosu (7/7 OK), Sohbet (S01/S02), tarihsel `350 passed`
  ve dış `300/50` koşusu ayrı satırlarda tutuldu.
- Örnek vaka toplam etki diye sunulmadı: AM002/DU004 örüntüleri metin gözlemidir, hüküm E3/insan QC'nindir.

## Açıklanmayan farklar

Yok.
