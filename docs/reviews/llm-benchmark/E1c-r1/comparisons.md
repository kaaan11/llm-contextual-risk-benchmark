# E1c-R1 — Başlangıç/bitiş karşılaştırması

## Referanslar

- Başlangıç HEAD ve çalışma ağacı: `9dd9d31607b3d97c02fe3ef9b7cfb68b4a3ed50e`, branch `master`,
  tracked dirty yalnız `M .gitignore`; untracked: brief/plan dosyaları + `docs/reviews/` + `uv.lock`
  (`logs/01-git-head-status.sh.stdout`, `hashes-start.txt`). E1c-r1 dizini yoktu (oluşturuldu).
- Bitiş HEAD ve çalışma ağacı: aynı HEAD; commit/push/branch yok. Tracked dirty aynı.
  Untracked'a E1c-r1 teslim belgeleri eklendi.
- Önceki kabul kaydı: `../E1c-acceptance.md` (R1–R5). Harita `revision-map.md`'dedir.
- Geçici çalışma dizini: kullanılmadı (matematik bellek-içi stdlib). Blind key okunmadı.

## Dosya ve hash farkları

Beklenen farklar (`E1c-r1` teslimi):

- `docs/reviews/llm-benchmark/E1c-r1/` altında 9 belge + `logs/` (6 komut × stdout/stderr/log).
  Untracked oldukları için düz `git diff` içinde görünmezler; burada sayıldılar.
- `hashes-start.txt` → `hashes-end.txt`: mühürlü/audit/QC/stimulus değerleri birebir aynı;
  yalnız dosya listesi satırı değişti (beklenen).

Beklenmeyen farklar: yok.

- `../E1c/` kanıtı değişmedi (`logs/03-math-frozen.sh.stdout` içinde manifesto karşılaştırması).
- Mühürlü composite `47ae…`, stimulus 50/171, audit prefix (51 + 5 satır): başlangıç=bitiş.
- `git diff --check`: temiz. `delivery.diff`: tracked fark yalnız `.gitignore` (dokunulmadı).

## Davranış karşılaştırması

Kod davranışı değişmez; kabul maddeleri belge + hesap düzeyinde karşılandı:

- Her endpointte tüm durumlar tek payda davranışında veya seçenekte (§2 tablo).
- Job kimliği model/run boyutlu; retry yeni gözlem değil (§3).
- Strata ekseni zorunlu/ayrı/havuzsuz (§1).
- TBD CI exact sunulmuyor; CP tek-oranda (§5).
- D-A/D-B seçimsiz kural değil (§6).
- Matematik insansız deterministik hesapla geçti (KÖ-1/KÖ-3).

## Açıklanmayan farklar

Yok.
