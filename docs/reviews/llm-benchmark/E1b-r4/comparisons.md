# E1b-R4 — Başlangıç/bitiş karşılaştırması

## Referanslar

- Başlangıç HEAD ve çalışma ağacı: `9dd9d31607b3d97c02fe3ef9b7cfb68b4a3ed50e`, branch `master`,
  tracked dirty yalnız `M .gitignore`; untracked: brief/plan dosyaları + `docs/reviews/` + `uv.lock`
  (`logs/01-git-head-status.sh.stdout`, `hashes-start.txt`). `E1b-r4` dizini yoktu (oluşturuldu).
- Bitiş HEAD ve çalışma ağacı: aynı HEAD; commit/push/branch yok. Tracked dirty aynı.
  Untracked'a `E1b-r4` teslim belgeleri eklendi.
- Önceki kabul kaydı: `../E1b-r3-acceptance.md` (tek blokaj). Harita `revision-map.md`'dedir.
- Geçici çalışma dizini: kullanılmadı. Blind key içeriği okunmadı.

## Dosya ve hash farkları

Beklenen farklar (`E1b-r4` teslimi):

- `docs/reviews/llm-benchmark/E1b-r4/` altında 9 belge + `logs/` (8 komut × stdout/stderr/log).
  Untracked oldukları için düz `git diff` içinde görünmezler; burada sayıldılar.
- `hashes-start.txt` → `hashes-end.txt`: mühürlü/audit/QC/stimulus değerleri birebir aynı;
  yalnız dosya listesi satırı değişti (beklenen).

Beklenmeyen farklar: yok.

- Önceki 4 paket değişmedi (`logs/04-prior-untouched.sh.stdout`: 13+16+16+16 dosya OK).
- Mühürlü composite `47ae…`, stimulus 50/171, audit prefix (51 + 5 satır): başlangıç=bitiş.
- `git diff --check`: temiz. `delivery.diff`: tracked fark yalnız `.gitignore` (dokunulmadı).

## Davranış karşılaştırması

Kod davranışı değişmez; kabul örnekleri yapısal + belge düzeyinde karşılandı:

- Unscorable slot + F1/F2 → ret; reasonsuz unscorable → ret (Dal U).
- Scoreable eksiklik/ek-alan → ret (Dal S); kritersiz F3 → ret + gap; NH F4 → ret.
- Adjudicated-unscorable finalde F1–F4 yok; ham slotlar korunur (§8P.3).
- 47 yapısal kontrol ALL PASS (presence + final + regresyon); rater etiketi üretilmedi.

## Açıklanmayan farklar

Yok.
