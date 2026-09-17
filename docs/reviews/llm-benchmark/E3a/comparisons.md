# E3a — Başlangıç/bitiş karşılaştırması

## Referanslar

- Başlangıç HEAD ve çalışma ağacı: `9dd9d31607b3d97c02fe3ef9b7cfb68b4a3ed50e`, branch `master`,
  tracked dirty: `M .gitignore` + E2a zinciri kod değişikliği (commitlenmedi, ayrı teslimler);
  untracked: brief/plan + `docs/reviews/` + `uv.lock`
  (`logs/01-git-head-status.sh.stdout`, `hashes-start.txt`). E3a dizini iskeletti (logs/).
- Bitiş HEAD ve çalışma ağacı: aynı HEAD; commit/push/branch yok.
- Önceki kabul: `../E0-acceptance.md`. E1/E2 bulguları değiştirilmedi.
- Geçici çalışma: `/tmp/opencode/e3a_scan.py` (salt okunur tarama; repoya yazmadı).

## Dosya ve hash farkları

Beklenen farklar (`E3a` belge teslimi):

- `docs/reviews/llm-benchmark/E3a/` altında 7 belge + `logs/` (7 komut). Untracked oldukları
  için düz `git diff` içinde görünmezler; burada sayıldılar.
- `hashes-start.txt` → `hashes-end.txt`: v1 hash + 50/171 + final-byte + audit prefix
  birebir aynı; yalnız dosya listesi satırı değişti (beklenen).

Beklenmeyen farklar: yok.

- Stimulus v1 baytları, QC/audit kayıtları, kod, testler değişmedi (05 logundaki yazım kontrolü).
- `git diff --check`: temiz. `delivery.diff`: E3a'nın tracked farkı YOKTUR (salt belge işi);
  dosya bu olguyu kaydeder.

## Davranış karşılaştırması

- Tarama deterministik stdlib hesabıdır (tekrar koşusunda aynı JSON); 50/171 sayıları,
  final-byte eşliği ve v1 hash'i başlangıç/bitişte aynı.
- Hedefli `test_phase7f_stimulus.py` salt okunur koştu (04 logu); v1'e yazım yok.
- 19 aday = insan kuyruğu; KEEP/REVISE/REJECT hükmü yok; toplama tahmin yok.

## Açıklanmayan farklar

Yok.
