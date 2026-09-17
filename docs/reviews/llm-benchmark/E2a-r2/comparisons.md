# E2a-R2 — Başlangıç/bitiş karşılaştırması

## Referanslar

- Başlangıç HEAD ve çalışma ağacı: `9dd9d31607b3d97c02fe3ef9b7cfb68b4a3ed50e`, branch `master`,
  tracked dirty yalnız `M .gitignore` + E2a/E2a-R1 kod değişikliği (commitlenmedi);
  untracked: brief/plan + `docs/reviews/` + `uv.lock` + yeni test dosyası
  (`logs/01-git-head-status.sh.stdout`, `hashes-start.txt`). E2a-r2 dizini yoktu (oluşturuldu).
- Bitiş HEAD ve çalışma ağacı: aynı HEAD; commit/push/branch yok.
- Önceki kabul kayıtları: `../E2a-acceptance.md`, `../E2a-r1-acceptance.md`.
  Harita `revision-map.md`'dedir.
- Geçici çalışma dizini: kullanılmadı (testler bellek-içi deepcopy; stub'lar bellek-içi).

## Dosya ve hash farkları

Beklenen farklar (`E2a-r2` kod + kanıt teslimi):

- Kod: `scripts/validate_phase7g_review.py` (R1 kontrolleri) + 2 test dosyası.
  `delivery.diff` tracked farkı gösterir (E2a → E2a-R2 kümülatif; tur ayrımı §9 dosya
  listesinde).
- Kanıt: `docs/reviews/llm-benchmark/E2a-r2/` altında 8 belge + `logs/` (8 komut). Untracked
  oldukları için düz `git diff` içinde görünmezler; burada sayıldılar.

Beklenmeyen farklar: yok.

- `../E2a/`, `../E2a-r1/` kanıtları değişmedi (06 logundaki değişmezlik kontrolü;
  E2a `delivery.diff` hariç — kümülatif tracked diff, gerekçesi README'de).
- Mühürlü composite `47ae…`, stimulus 50/171, audit prefix (51 + 5 satır): başlangıç=bitiş;
  test koşuları audit dosyalarına yazmadı.
- `git diff --check`: temiz.

## Davranış karşılaştırması

- Zorunlu karşıörnek: blind + completion hataları üretir (valence/ID eklenmedi).
- Yasak-pozitif taraması: yeni testlerde sentetik pozitif helper/kayıt yok (06 logu).
- Hedefli + tam suite yeşil; validator CLI'ları VALID.
- E2a-R1 davranışları korundu — regresyon yok (tam suite).

## Açıklanmayan farklar

Yok.
