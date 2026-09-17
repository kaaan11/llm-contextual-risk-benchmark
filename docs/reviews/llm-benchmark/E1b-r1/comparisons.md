# E1b-R1 — Başlangıç/bitiş karşılaştırması

## Referanslar

- Başlangıç HEAD ve çalışma ağacı: `9dd9d31607b3d97c02fe3ef9b7cfb68b4a3ed50e`, branch `master`,
  tracked dirty yalnız `M .gitignore`; untracked: brief/plan dosyaları + `docs/reviews/` + `uv.lock`
  (`logs/01-git-head-status.sh.stdout`, `hashes-start.txt`). `E1b-r1` dizini yoktu (oluşturuldu);
  `../E1b/` ham kanıtı mevcuttu (üzerine yazılmadı).
- Bitiş HEAD ve çalışma ağacı: aynı HEAD; commit/push/branch yok. Tracked dirty aynı.
  Untracked'a `E1b-r1` teslim belgeleri eklendi (`logs/06-diff-check.sh.stdout`, `hashes-end.txt`).
- Önceki kabul kaydı: `../E1b-acceptance.md` (REVISION REQUIRED, R1–R5). Bu paket R-karşılıklarını
  `revision-map.md`'de verir; kabul kararını vermez.
- Geçici çalışma dizini: kullanılmadı. Blind key içeriği okunmadı.

## Dosya ve hash farkları

Beklenen farklar (`E1b-r1` teslimi):

- `docs/reviews/llm-benchmark/E1b-r1/` altında 9 belge + `logs/` (8 komut × stdout/stderr/log).
  Untracked oldukları için düz `git diff` içinde görünmezler; burada sayıldılar.
- `hashes-start.txt` → `hashes-end.txt`: mühürlü/audit/QC/stimulus değerleri birebir aynı;
  yalnız dosya listesi satırı değişti (beklenen).

Beklenmeyen farklar: yok.

- `../E1b/` dosyaları değişmedi: `run-outputs.sha256` girdileri yeniden hesaplandı, tamamı OK
  (`logs/04-e1b-untouched.sh.stdout`).
- Mühürlü composite `47ae…`, stimulus 50/171, audit prefix (51 + 5 satır): başlangıç=bitiş.
- `git diff --check`: temiz. `delivery.diff`: tracked fark yalnız `.gitignore` (dokunulmadı).

## Davranış karşılaştırması

Kod davranışı değişmez; kabul örnekleri yapısal + belge düzeyinde karşılandı:

- F3 ref → aynı koşul `criterion_id`; eksik/dangling ret (§2R, şema bütünlük kuralı).
- Aynı reviewer ID ret; rol≠kimlik; ham kayıtlar adjudication sonrası korunur (§2R, B-5R).
- `allow_with_safeguards` vs `decline` = disagreement, otomatik contested yok (§2R.1, B-5R).
- İki low-confidence ≠ `unscorable_content` (§4R, B-7R).
- Timeout/error → F1–F4 yasak, missing reason korunur (§5R, B-8R).
- Aynı output B/C'de aynı F1 (§3 korundu).
- 43 yapısal kontrol ALL PASS; rater etiketi üretilmedi.

## Açıklanmayan farklar

Yok.
