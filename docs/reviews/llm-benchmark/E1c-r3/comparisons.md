# E1c-R3 — Başlangıç/bitiş karşılaştırması

## Referanslar

- Başlangıç HEAD ve çalışma ağacı: `9dd9d31607b3d97c02fe3ef9b7cfb68b4a3ed50e`, branch `master`,
  tracked dirty yalnız `M .gitignore`; untracked: brief/plan dosyaları + `docs/reviews/` + `uv.lock`
  (`logs/01-git-head-status.sh.stdout`, `hashes-start.txt`). E1c-r3 dizini yoktu (oluşturuldu).
- Bitiş HEAD ve çalışma ağacı: aynı HEAD; commit/push/branch yok. Tracked dirty aynı.
  Untracked'a E1c-r3 teslim belgeleri eklendi.
- Önceki kabul kaydı: `../E1c-r2-acceptance.md` (tek çelişki). Harita `revision-map.md`'dedir.
- Geçici çalışma dizini: kullanılmadı. Blind key okunmadı.

## Dosya ve hash farkları

Beklenen farklar (`E1c-r3` teslimi):

- `docs/reviews/llm-benchmark/E1c-r3/` altında 9 belge + `logs/` (6 komut × stdout/stderr/log).
  Untracked oldukları için düz `git diff` içinde görünmezler; burada sayıldılar.
- `hashes-start.txt` → `hashes-end.txt`: mühürlü/audit/QC/stimulus değerleri birebir aynı;
  yalnız dosya listesi satırı değişti (beklenen).

Beklenmeyen farklar: yok.

- Önceki 3 paket değişmedi (`logs/03-math-frozen.sh.stdout`).
- Mühürlü composite `47ae…`, stimulus 50/171, audit prefix (51 + 5 satır): başlangıç=bitiş.
- `git diff --check`: temiz. `delivery.diff`: tracked fark yalnız `.gitignore` (dokunulmadı).

## Davranış karşılaştırması

Kod davranışı değişmez; kabul örnekleri belge + hesap düzeyinde karşılandı:

- F3-gap kaydı E-act + E-util'de, E-harm dışı, gap oranında (§3B + örnek 1).
- F4-NA kaydı E-act/E-harm'de, E-util NA kuralında (örnek 2).
- Unresolved hiçbir pay/paydada yok (örnek 3).
- Aynı kayıtta çelişki yok (örnek 4; §3A/§3B ayrımı).

## Açıklanmayan farklar

Yok.
