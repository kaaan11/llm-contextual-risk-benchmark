# E1b — Başlangıç/bitiş karşılaştırması

## Referanslar

- Başlangıç HEAD ve çalışma ağacı: `9dd9d31607b3d97c02fe3ef9b7cfb68b4a3ed50e`, branch `master`,
  tracked dirty yalnız `M .gitignore`; untracked: brief/plan dosyaları + `docs/reviews/` + `uv.lock`
  (`logs/01-git-head-status.sh.stdout`, `hashes-start.txt`). E1b dizini yoktu (oluşturuldu).
- Bitiş HEAD ve çalışma ağacı: aynı HEAD; commit/push/branch yok. Tracked dirty aynı
  (`.gitignore` kullanıcı değişikliği korundu). Untracked'a E1b teslim belgeleri eklendi:
  `rubric-draft.md`, `schema-draft.json`, `boundary-cases.md`, `README.md`, `comparisons.md`,
  `commands.jsonl`, `hashes-start/end.txt`, `delivery.diff`, `run-outputs.sha256`, `logs/`.
- Önceki kabul kayıtları: `../E0-acceptance.md` (E0 KABUL), `../E1a-acceptance.md`
  (E1a worker taslağı kabul; insan kararları bekliyor). Bu paket E0/E1a bulgularını değiştirmedi.
- Geçici çalışma dizini: kullanılmadı. Blind key içeriği okunmadı.

## Dosya ve hash farkları

Beklenen farklar (E1b teslimi):

- `docs/reviews/llm-benchmark/E1b/` altında 8 belge + `logs/` (6 komut × stdout/stderr/log) eklendi.
  Untracked oldukları için düz `git diff` içinde görünmezler; burada sayıldılar.
- `hashes-start.txt` → `hashes-end.txt`: mühürlü/audit/QC/stimulus değerleri birebir aynı;
  yalnız E1b dosya listesi satırı değişti (beklenen).

Beklenmeyen farklar: yok.

- Mühürlü 6 protokol dosyası + composite `47ae…`: başlangıç=bitiş (`logs/03-frozen-hashes.sh.stdout`).
- Stimulus v1 hash + 50/171: başlangıç=bitiş. Audit history prefix (51 + 5 satır): aynı; yazım yok.
- `git diff --check`: temiz (`logs/04-diff-check.sh.stdout`).
- `delivery.diff`: tracked fark yalnız başlangıçtaki `.gitignore` değişikliğidir; E1b bu dosyaya dokunmadı.

## Davranış karşılaştırması

E1b kod davranışı değiştirmez; kabul örnekleri belge düzeyindedir:

- Ayrı boyutlar composite'e sıkıştırılmadı: F1 nominal, F3/F4 bağımsız, F5 handling ayrı; yasak listesi
  `schema-draft.json` `prohibitions` alanında makinece de kayıtlı.
- Layer A/C'den Layer B doldurulmasına izin verilmedi: F5/F6 `pre_evaluation` zamanlı, rater körlüğü
  §5'te zorunlu; model görmüş rater Layer B üretemez.
- Aynı output metni B/C beklentisiyle yeniden adlandırılmaz (§3.1 output-merkezlilik).
- Uygulanabilirlik tablosu A/B/C/D × DU/AM/NB/NH için eksiksiz (D'siz 29 maddede D sütunu ○).
- Sınır örnekleri briefin 5 zorunlu tipi + 1 ek tipi kapsar; annotation değildir, corpus kararı vermez.
- Hiçbir hüküm `APPROVED` değil; insan-kararı E1b kabul kaydına aittir.

## Açıklanmayan farklar

Yok.
