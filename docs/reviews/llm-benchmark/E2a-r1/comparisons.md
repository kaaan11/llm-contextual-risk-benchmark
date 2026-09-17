# E2a-R1 — Başlangıç/bitiş karşılaştırması

## Referanslar

- Başlangıç HEAD ve çalışma ağacı: `9dd9d31607b3d97c02fe3ef9b7cfb68b4a3ed50e`, branch `master`,
  tracked dirty yalnız `M .gitignore` + E2a kod değişikliği (henüz commitlenmedi — E2a kanıtı
  ayrı dizinde); untracked: brief/plan + `docs/reviews/` + `uv.lock` + yeni test dosyası
  (`logs/01-git-head-status.sh.stdout`, `hashes-start.txt`). E2a-r1 dizini yoktu (oluşturuldu).
- Bitiş HEAD ve çalışma ağacı: aynı HEAD; commit/push/branch yok.
- Önceki kabul kaydı: `../E2a-acceptance.md` (R1–R4). Harita `revision-map.md`'dedir.
- Geçici çalışma dizini: kullanılmadı (testler bellek-içi deepcopy).

## Dosya ve hash farkları

Beklenen farklar (`E2a-r1` kod + kanıt teslimi):

- Kod: 4 scriptte kanıt kapıları (ölü status-only helper kaldırıldı) + `tests/test_phase7g_gates.py`
  31 test. `delivery.diff` tracked farkı gösterir (E2a + E2a-R1 değişiklikleri birlikte; E2a
  acceptance sonrası ek commit olmadığı için diff kümülatiftir — ayrım `revision-map.md` §9
  dosya listesinde ve aşağıda açıklanır).
- Kanıt: `docs/reviews/llm-benchmark/E2a-r1/` altında 8 belge + `logs/` (8 komut). Untracked
  oldukları için düz `git diff` içinde görünmezler; burada sayıldılar.

Beklenmeyen farklar: yok.

- `../E2a/` kanıtı değişmedi (aşağıdaki değişmezlik kontrolü).
- Mühürlü composite `47ae…`, stimulus 50/171, audit prefix (51 + 5 satır): başlangıç=bitiş;
  test koşuları audit dosyalarına yazmadı.
- `git diff --check`: temiz.

## Davranış karşılaştırması

- 5 karşıörnek grubu: boş-slot el-status / aynı-ID / PARTIAL+COMPLETE / gate-uyuşmazlıkları /
  batch-atomicity — writer ret, validator hata, CLI gizler (log 03).
- Hedefli + tam suite yeşil (log 03/04); validator CLI'ları VALID (log 05).
- E2a davranışları (PARTIAL-ret, FAIL-ret, atomicity) korundu — regresyon yok.

## Açıklanmayan farklar

Yok.
