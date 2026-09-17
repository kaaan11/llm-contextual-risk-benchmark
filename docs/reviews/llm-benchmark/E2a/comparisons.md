# E2a — Başlangıç/bitiş karşılaştırması

## Referanslar

- Başlangıç HEAD ve çalışma ağacı: `9dd9d31607b3d97c02fe3ef9b7cfb68b4a3ed50e`, branch `master`,
  tracked dirty yalnız `M .gitignore`; untracked: brief/plan dosyaları + `docs/reviews/` + `uv.lock`
  (`logs/01-git-head-status.sh.stdout`, `hashes-start.txt`). E2a dizini yoktu (oluşturuldu).
- Bitiş HEAD ve çalışma ağacı: aynı HEAD; commit/push/branch yok. Tracked dirty aynı
  (`.gitignore` kullanıcı değişikliği korundu).
- Önceki kabul kaydı: `../E0-acceptance.md`. E1a/E1b/E1c bulguları değiştirilmedi.
- Geçici çalışma dizini: kullanılmadı (testler bellek-içi deepcopy; `/tmp` yazımı yok).

## Dosya ve hash farkları

Beklenen farklar (E2a kod teslimi):

- Kod: 4 script (`apply_phase7g_annotations`, `validate_phase7g_review`, `review_context`,
  `decide_phase7g`) + 2 mevcut test dosyasında 3 test güncellemesi + 1 yeni test dosyası.
  `delivery.diff` tracked farkı gösterir (aşağıda özet).
- Kanıt: `docs/reviews/llm-benchmark/E2a/` altında 7 belge + `logs/` (8 komut).
  Untracked oldukları için düz `git diff` içinde görünmezler; burada sayıldılar.

Beklenmeyen farklar: yok.

- Mühürlü 6 protokol dosyası + composite `47ae…`: başlangıç=bitiş.
- Stimulus v1 hash + 50/171: başlangıç=bitiş. Audit history prefix (51 + 5 satır, hash'ler):
  başlangıç=bitiş; test koşuları audit dosyalarına yazmadı (`logs/05-validators-diff.sh.stdout`
  içinde `git status` kanıtı).
- `git diff --check`: temiz.
- Davranış farkı (beklenen, brief): PARTIAL/disagreement sonrası context artık RET;
  FAIL-gate KEEP writer + validator + CLI'da RET. Gevşek davranışı kodlayan 3 test güncellendi;
  geri kalan 350 test değişmeden geçer.

## Davranış karşılaştırması

- Kabul testleri: 22 yeni gates testi + güncellenmiş 3 test geçer; hedefli 132 + tam 372 yeşil.
- Negatif yollar (PENDING/partial/FAIL/eksik) ret üretir; writer-ret ⟺ validator-hata tutarlı;
  ret mutation yapmaz (derin-eşitlik); CLI liste/teklif aynı sınırı uygular.
- Pozitif iki-rater geçişi (gerçek provenance) inceleyici kabul örneği olarak açık bırakıldı.

## Açıklanmayan farklar

Yok.
