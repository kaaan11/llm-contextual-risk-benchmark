# E1b-R3 — Başlangıç/bitiş karşılaştırması

## Referanslar

- Başlangıç HEAD ve çalışma ağacı: `9dd9d31607b3d97c02fe3ef9b7cfb68b4a3ed50e`, branch `master`,
  tracked dirty yalnız `M .gitignore`; untracked: brief/plan dosyaları + `docs/reviews/` + `uv.lock`
  (`logs/01-git-head-status.sh.stdout`, `hashes-start.txt`). `E1b-r3` dizini yoktu (oluşturuldu).
- Bitiş HEAD ve çalışma ağacı: aynı HEAD; commit/push/branch yok. Tracked dirty aynı.
  Untracked'a `E1b-r3` teslim belgeleri eklendi.
- Önceki kabul kaydı: `../E1b-r2-acceptance.md` (iki yerleşim blokajı). Harita
  `revision-map.md`'dedir; kabul kararı verilmez.
- Geçici çalışma dizini: kullanılmadı. Blind key içeriği okunmadı.

## Dosya ve hash farkları

Beklenen farklar (`E1b-r3` teslimi):

- `docs/reviews/llm-benchmark/E1b-r3/` altında 9 belge + `logs/` (8 komut × stdout/stderr/log).
  Untracked oldukları için düz `git diff` içinde görünmezler; burada sayıldılar.
- `hashes-start.txt` → `hashes-end.txt`: mühürlü/audit/QC/stimulus değerleri birebir aynı;
  yalnız dosya listesi satırı değişti (beklenen).

Beklenmeyen farklar: yok.

- `../E1b/`, `../E1b-r1/`, `../E1b-r2/` dosyaları değişmedi (`logs/04-prior-untouched.sh.stdout`).
- Mühürlü composite `47ae…`, stimulus 50/171, audit prefix (51 + 5 satır): başlangıç=bitiş.
- `git diff --check`: temiz. `delivery.diff`: tracked fark yalnız `.gitignore` (dokunulmadı).

## Davranış karşılaştırması

Kod davranışı değişmez; kabul örnekleri yapısal + belge düzeyinde karşılandı:

- Layer-B slotunda scoreability/F1–F4 reddedilir (şema çapraz-katman yasağı).
- Skorlanabilir response → iki Layer-C ham görüş + provenance; adjudication hamı değiştirmez.
- İki explicit unscorable → ek adjudication olmadan final (uygulama yeri §7C).
- Timeout/error → zarf yok, F1–F4 yasak.
- `resolved_reference=null` + researcher contested geçerli; criterion nesnesinde değil;
  disagreement üretmez.
- 60+ yapısal kontrol ALL PASS; rater etiketi üretilmedi.

## Açıklanmayan farklar

Yok. Not: çalışma sırasında E1b-r2'de oluşan stray 07/08 yeniden-çalışması onarıldı
(README olay notu); `../E1b-r2/commands.jsonl` 8 kayıt, manifestosu PASS.
