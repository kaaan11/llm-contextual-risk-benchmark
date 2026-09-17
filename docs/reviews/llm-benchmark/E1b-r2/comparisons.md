# E1b-R2 — Başlangıç/bitiş karşılaştırması

## Referanslar

- Başlangıç HEAD ve çalışma ağacı: `9dd9d31607b3d97c02fe3ef9b7cfb68b4a3ed50e`, branch `master`,
  tracked dirty yalnız `M .gitignore`; untracked: brief/plan dosyaları + `docs/reviews/` + `uv.lock`
  (`logs/01-git-head-status.sh.stdout`, `hashes-start.txt`). `E1b-r2` dizini yoktu (oluşturuldu);
  `../E1b/`, `../E1b-r1/` ham kanıtları mevcuttu (üzerine yazılmadı).
- Bitiş HEAD ve çalışma ağacı: aynı HEAD; commit/push/branch yok. Tracked dirty aynı.
  Untracked'a `E1b-r2` teslim belgeleri eklendi (`logs/06-diff-check.sh.stdout`, `hashes-end.txt`).
- Önceki kabul kaydı: `../E1b-r1-acceptance.md` (iki blokaj). Harita `revision-map.md`'dedir;
  kabul kararı verilmez.
- Geçici çalışma dizini: kullanılmadı. Blind key içeriği okunmadı.

## Dosya ve hash farkları

Beklenen farklar (`E1b-r2` teslimi):

- `docs/reviews/llm-benchmark/E1b-r2/` altında 9 belge + `logs/` (8 komut × stdout/stderr/log).
  Untracked oldukları için düz `git diff` içinde görünmezler; burada sayıldılar.
- `hashes-start.txt` → `hashes-end.txt`: mühürlü/audit/QC/stimulus değerleri birebir aynı;
  yalnız dosya listesi satırı değişti (beklenen).

Beklenmeyen farklar: yok.

- `../E1b/`, `../E1b-r1/` dosyaları değişmedi (`logs/04-prior-untouched.sh.stdout`).
- Mühürlü composite `47ae…`, stimulus 50/171, audit prefix (51 + 5 satır): başlangıç=bitiş.
- `git diff --check`: temiz. `delivery.diff`: tracked fark yalnız `.gitignore` (dokunulmadı).

## Davranış karşılaştırması

Kod davranışı değişmez; kabul örnekleri yapısal + belge düzeyinde karşılandı:

- Anlaşan iki reviewer → provenance'lı resolved, F3 yalnız ona (§2S, B-9S).
- Üçlü farklı + disagree + adjudication yok → resolved ve F3 ret (§2S).
- Adjudication hamı değiştirmez, source gösterir (şema `never_overwrites_raw_slots`).
- İki explicit unscorable → doğrudan final (§4S, B-7S).
- Tek taraflı → adjudication; iki low → unscorable yok (§4S, B-7S).
- 50 yapısal kontrol ALL PASS; rater etiketi üretilmedi.
- 03 betiğindeki iki yazım-düzeltmesi teslim dosyasını değiştirmedi (README'de açıklandı).

## Açıklanmayan farklar

Yok.
