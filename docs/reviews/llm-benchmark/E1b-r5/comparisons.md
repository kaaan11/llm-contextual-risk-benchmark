# E1b-R5 — Başlangıç/bitiş karşılaştırması

## Referanslar

- Başlangıç HEAD ve çalışma ağacı: `9dd9d31607b3d97c02fe3ef9b7cfb68b4a3ed50e`, branch `master`,
  tracked dirty yalnız `M .gitignore`; untracked: brief/plan dosyaları + `docs/reviews/` + `uv.lock`
  (`logs/01-git-head-status.sh.stdout`, `hashes-start.txt`). `E1b-r5` dizini yoktu (oluşturuldu).
- Bitiş HEAD ve çalışma ağacı: aynı HEAD; commit/push/branch yok. Tracked dirty aynı.
  Untracked'a `E1b-r5` teslim belgeleri eklendi.
- Önceki kabul kaydı: `../E1b-r4-acceptance.md` (tek blokaj). Harita `revision-map.md`'dedir.
- Geçici çalışma dizini: kullanılmadı. Blind key içeriği okunmadı.

## Dosya ve hash farkları

Beklenen farklar (`E1b-r5` teslimi):

- `docs/reviews/llm-benchmark/E1b-r5/` altında 8 belge + `logs/` (8 komut × stdout/stderr/log).
  Untracked oldukları için düz `git diff` içinde görünmezler; burada sayıldılar.
- `hashes-start.txt` → `hashes-end.txt`: mühürlü/audit/QC/stimulus değerleri birebir aynı;
  yalnız dosya listesi satırı değişti (beklenen).

Beklenmeyen farklar: yok.

- Önceki 5 paket değişmedi (`logs/04-prior-untouched.sh.stdout`).
- Mühürlü composite `47ae…`, stimulus 50/171, audit prefix (51 + 5 satır): başlangıç=bitiş.
- `git diff --check`: temiz. `delivery.diff`: tracked fark yalnız `.gitignore` (dokunulmadı).

## Davranış karşılaştırması

Kod davranışı değişmez; kabul örnekleri hesaplanarak karşılandı:

- Linter undeclared field bulmadı (branch + final listeleri scope'ta çözüldü).
- Dal kuralları R4 ile aynı (matris kontrolü); yanlış-dal gap/reason reddedilir.
- Nested enum/değer sözleşmeleri üst düzeyle eşit (drift yok).
- R2/R3 regresyonları geçer; insan etiketi üretilmedi.
- 34 kontrol ALL PASS.

## Açıklanmayan farklar

Yok.
