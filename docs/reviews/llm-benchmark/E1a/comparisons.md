# E1a — Başlangıç/bitiş karşılaştırması

## Referanslar

- Başlangıç HEAD ve çalışma ağacı: `9dd9d31607b3d97c02fe3ef9b7cfb68b4a3ed50e`, branch `master`,
  tracked dirty yalnız `M .gitignore`; untracked: brief/plan dosyaları + `docs/reviews/` + `uv.lock`
  (`logs/01-git-head-status.sh.stdout`, `hashes-start.txt`). E1a dizini yoktu (oluşturuldu).
- Bitiş HEAD ve çalışma ağacı: aynı HEAD; commit/push/branch yok. Tracked dirty aynı
  (`.gitignore` kullanıcı değişikliği korundu). Untracked'a E1a teslim belgeleri eklendi:
  `claim-decisions.md`, `README.md`, `comparisons.md`, `commands.jsonl`, `hashes-start/end.txt`,
  `delivery.diff`, `run-outputs.sha256`, `logs/` (`logs/04-diff-check.sh.stdout`, `hashes-end.txt`).
- Önceki kabul kaydı: `../E0-acceptance.md` (E0 KABUL EDİLDİ). Bu paket E0 bulgularını değiştirmedi.
- Geçici çalışma dizini: kullanılmadı. Raporlar salt okunur `/tmp/llm-benchmark-review-20260909`
  ve `/home/kaan/GPT-Pro/reports/LLM_Benchmark` dizinlerinden okundu.

## Dosya ve hash farkları

Beklenen farklar (E1a teslimi):

- `docs/reviews/llm-benchmark/E1a/` altında 7 belge + `logs/` (6 komut × stdout/stderr/log) eklendi.
  Untracked oldukları için düz `git diff` içinde görünmezler; burada sayıldılar.
- `hashes-start.txt` → `hashes-end.txt`: mühürlü/audit/QC/stimulus değerleri birebir aynı;
  yalnız E1a dosya listesi satırı değişti (beklenen).

Beklenmeyen farklar: yok.

- Mühürlü 6 protokol dosyası + composite `47ae…`: başlangıç=bitiş (`logs/03-frozen-hashes.sh.stdout`).
- Stimulus v1 hash + 50/171: başlangıç=bitiş. Audit history prefix (51 + 5 satır): aynı; yazım yok.
- `git diff --check`: temiz (`logs/04-diff-check.sh.stdout`).
- `delivery.diff`: tracked fark yalnız başlangıçtaki `.gitignore` değişikliğidir; E1a bu dosyaya dokunmadı.
- `README.md` ve araştırma belgeleri bu pakette düzenlenmedi (brief yasağı).

## Davranış karşılaştırması

E1a kod davranışı değiştirmez; pozitif/negatif kabul örnekleri belge düzeyindedir:

- Matris belge drift'ini görünür kılar: RQ-300/Pareto/savunma-katmanı (C-13), başlık sorusu + C1–C3 (C-01),
  ROADMAP judge (C-12), güç/bütçe sayıları (C-14) ayrı satırlardadır.
- Mekanizma iddiaları construct'tan ayrıdır: latent intent (C-02) ve pure user evidence (C-03) `terk et`;
  D yokluğu→mekanizma (C-04), AM→DU mekanizması (C-05/C-07), hash→temizlik (C-11) yasakları kontrol
  listesinde kapatıldı.
- Önerilen yayın iddiasında yön/model/etki/başarım doldurulmadı; D yokluğu mekanizma sayılmadı;
  AM DU etkisinin tanımlanması olarak kullanılmadı; hash contamination sayılmadı (brief §20).
- Hiçbir hüküm `APPROVED` değil; insan-kararı sütunu 14 satırda boş.

## Açıklanmayan farklar

Yok.
