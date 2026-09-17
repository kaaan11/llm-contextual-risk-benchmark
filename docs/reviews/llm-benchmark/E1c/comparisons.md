# E1c — Başlangıç/bitiş karşılaştırması

## Referanslar

- Başlangıç HEAD ve çalışma ağacı: `9dd9d31607b3d97c02fe3ef9b7cfb68b4a3ed50e`, branch `master`,
  tracked dirty yalnız `M .gitignore`; untracked: brief/plan dosyaları + `docs/reviews/` + `uv.lock`
  (`logs/01-git-head-status.sh.stdout`, `hashes-start.txt`). E1c dizini yoktu (oluşturuldu).
- Bitiş HEAD ve çalışma ağacı: aynı HEAD; commit/push/branch yok. Tracked dirty aynı.
  Untracked'a E1c teslim belgeleri eklendi.
- Önceki kabuller: E0 (kabul), E1a (worker-kabul, insan kararları bekliyor), E1b-r6 (worker-tamam,
  insan bilimsel kararı bekliyor). Bu paket bulguları değiştirmedi.
- Geçici çalışma dizini: kullanılmadı. Blind key içeriği okunmadı.

## Dosya ve hash farkları

Beklenen farklar (`E1c` teslimi):

- `docs/reviews/llm-benchmark/E1c/` altında 8 belge + `logs/` (6 komut × stdout/stderr/log).
  Untracked oldukları için düz `git diff` içinde görünmezler; burada sayıldılar.
- `hashes-start.txt` → `hashes-end.txt`: mühürlü/audit/QC/stimulus değerleri birebir aynı;
  yalnız dosya listesi satırı değişti (beklenen).

Beklenmeyen farklar: yok.

- Mühürlü composite `47ae…`, stimulus 50/171, audit prefix (51 + 5 satır): başlangıç=bitiş.
- `git diff --check`: temiz. `delivery.diff`: tracked fark yalnız `.gitignore` (dokunulmadı).

## Davranış karşılaştırması

Kod davranışı değişmez; brief maddeleri belge düzeyinde karşılandı:

- Primary/secondary, birim, ağırlık, tekrarlar, missing/duplicate/error/exclusion,
  applicability/sıfır-payda, test/CI, multiplicity tanımlı; DU=30/DU-D=14/kontroller havuzlanmadı.
- Başlangıç önerisi: madde-eşit B/C + harm/utility; mode ikincil; McNemar error-asymmetry adlı.
- Ordinal/D-flag/Wilcoxon statüleri + H3/F4/eşik seçenekleri açık.
- 3 karşıörnek beklenen sonuçla yer alır (KÖ-1/2/3).
- Endpoint/alfa/eşik onaylanmış gibi seçilmedi; E5/E6'ya etkin devir yok.

## Açıklanmayan farklar

Yok.
