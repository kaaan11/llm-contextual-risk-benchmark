# E3a-R1 — Teslim kanıt paketi

Durum: **TAMAMLANDI (worker revizyonu; yeniden inceleme bekleniyor).**
Görev: [E3a-R1 briefi](../../../llm-benchmark-E3a-r1-task.md).
Önkoşul: `../E3a-acceptance.md` (REVISION REQUIRED; R1–R3).
Sözleşme: [worker sözleşmesi](../../../llm-benchmark-worker-contract.md).

## Sonuç

E3a'nın yapısal sayımları + karar-değil sınırı korunarak envanter kalıcı artefaktlardan
yeniden üretilebilir hale getirildi; R-REF provenance'ı kapatıldı; otomatik-hüküm dili kalktı.

- `helpers/e3a_scan.py`: parametrik girdi/çıktı, korumalı-yol retli, deterministik stdlib.
  Temp-output ↔ teslim JSON bayt-eşit (03 logu); `/tmp` bağımlılığı yok.
- 6 R-REF satırında tam hash (6/6 bağımsız doğrulandı) + dörtlü açık karar; kanıtlarda
  prompt parçası yok (R-REF2 token adları dahil tutarlı kural).
- Ham eşleşmeler referent kanıtı değil; adaylar REVIEW kuyruğu. Sayı aynı (19), satır
  anahtarları aynı; farklar `revision-map.md`'dedir.

## Değişen dosyalar (yalnız bu dizin)

- `helpers/e3a_scan.py`, `stimulus-issues.md`, `stimulus-issues.json`, `revision-map.md`,
  `README.md` (bu dosya), `comparisons.md`, `commands.jsonl`, `hashes-start.txt`,
  `hashes-end.txt`, `delivery.diff`, `run-outputs.sha256`, `logs/`.
- `../E3a/` teslimi, stimulus v1, content kaynakları, QC/audit, testler, kod değişmedi.

## Doğrulamalar (gerçek komutlar; çalıştırılmayan yok)

| # | Komut (özet) | Log | Exit |
| --- | --- | --- | --- |
| 01 | `git rev-parse HEAD`, `status`, `branch`, `log -3` | `logs/01-git-head-status.sh.stdout` | 0 |
| 02 | `python3 --version`, `.venv pytest --version` | `logs/02-env.sh.stdout` | 0 |
| 03 | Kalıcı helper ile yeniden üretim (temp) + bayt-eşlik + 6 hash bağımsız doğrulama | `logs/03-regenerate.sh.stdout` | 0 |
| 04 | Hedefli salt-okunur testler (`test_phase7f_stimulus.py`) | `logs/04-targeted-tests.sh.stdout` | 0 |
| 05 | `git diff --check` + yazım kontrolü (stimulus/audit/E3a değişmedi) | `logs/05-diff-check.sh.stdout` | 0 |
| 06 | Teslim içi bağlantı kontrolü (final, PASS) | `logs/06-link-check.sh.stdout` | 0 |
| 07 | `run-outputs.sha256` üretimi (belgeler + helper + log stdout'ları; kendi üretim logu hariç) | `logs/07-run-outputs.sh.stdout` | 0 |

`commands.jsonl` içinde çalıştırılmayan komut yoktur; boş satır yoktur.
`run-outputs.sha256` kendi üretim logunu kapsamaz.

## Sınırlılıklar

- Adaylar hüküm değildir; naturalness/safety/E3b kararları insanındır. Tokenizer profili
  yok → tolerans AÇIK. Dış literatür taranmadı.

## Devam

Teslimden sonra durulur; E3b'ye geçilmez. Sıradaki önkoşul: ana inceleyicinin yeniden
incelemesi.
