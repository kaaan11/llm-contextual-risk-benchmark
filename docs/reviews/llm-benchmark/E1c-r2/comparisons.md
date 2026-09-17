# E1c-R2 — Başlangıç/bitiş karşılaştırması

## Referanslar

- Başlangıç HEAD ve çalışma ağacı: `9dd9d31607b3d97c02fe3ef9b7cfb68b4a3ed50e`, branch `master`,
  tracked dirty yalnız `M .gitignore`; untracked: brief/plan dosyaları + `docs/reviews/` + `uv.lock`
  (`logs/01-git-head-status.sh.stdout`, `hashes-start.txt`). E1c-r2 dizini yoktu (oluşturuldu).
- Bitiş HEAD ve çalışma ağacı: aynı HEAD; commit/push/branch yok. Tracked dirty aynı.
  Untracked'a E1c-r2 teslim belgeleri eklendi.
- Önceki kabul kaydı: `../E1c-r1-acceptance.md` (R1–R4 + stance). Harita `revision-map.md`'dedir.
- Geçici çalışma dizini: kullanılmadı. Blind key okunmadı.

## Dosya ve hash farkları

Beklenen farklar (`E1c-r2` teslimi):

- `docs/reviews/llm-benchmark/E1c-r2/` altında 9 belge + `logs/` (6 komut × stdout/stderr/log).
  Untracked oldukları için düz `git diff` içinde görünmezler; burada sayıldılar.
- `hashes-start.txt` → `hashes-end.txt`: mühürlü/audit/QC/stimulus değerleri birebir aynı;
  yalnız dosya listesi satırı değişti (beklenen).

Beklenmeyen farklar: yok.

- `../E1c/`, `../E1c-r1/` kanıtları değişmedi (`logs/03-math-frozen.sh.stdout`).
- Mühürlü composite `47ae…`, stimulus 50/171, audit prefix (51 + 5 satır): başlangıç=bitiş.
- `git diff --check`: temiz. `delivery.diff`: tracked fark yalnız `.gitignore` (dokunulmadı).

## Davranış karşılaştırması

Kod davranışı değişmez; kabul maddeleri belge + hesap düzeyinde karşılandı:

- ≤3 resolved gözlem; unresolved girmez (§1R).
- Seçimsiz contested kuralı yok (§3, §6R).
- Error-asymmetry pending-uyumlu standalone sözleşmede (§2E).
- Yardımcı paydalar + 0/0 kapalı (§2H).
- Hücreler izlenebilir, havuzsuz (§1S).

## Açıklanmayan farklar

Yok.
