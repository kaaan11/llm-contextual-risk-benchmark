# E3a-R2 — Teslim kanıt paketi

Durum: **TAMAMLANDI (worker revizyonu; yeniden inceleme bekleniyor).**
Görev: [E3a-R2 briefi](../../../llm-benchmark-E3a-r2-task.md).
Önkoşul: `../E3a-r1-acceptance.md` (REVISION REQUIRED; R1–R2).
Sözleşme: [worker sözleşmesi](../../../llm-benchmark-worker-contract.md).

## Sonuç

E3a-R1'deki iki helper sorunu kapatıldı; R-REF provenance'ı, karar-değil dili, 19 aday
kuyruğu ve salt-okunur sınır korundu.

- `assistant_shared_bc` exact tur-metni eşliğidir (sıralı rol+UTF-8 bayt); Jaccard ayrı
  betimleyici ölçümdür. Exact 7/43 yeniden üretildi (tümü AM); ayrım unit örneği logdadır.
- Output fail-closed: input==output ret; repo-içi allowlist yalnız bu teslim JSON'u;
  frozen docs + başka repo dosyası retleri içerik değiştirmeden doğrulandı.
- R-REF 6/6 hash, dört açık karar, 19 REVIEW, frozen/audit hashleri korunur.

## Değişen dosyalar (yalnız bu dizin)

- `helpers/e3a_scan.py`, `stimulus-issues.md`, `stimulus-issues.json`, `revision-map.md`,
  `README.md` (bu dosya), `comparisons.md`, `commands.jsonl`, `hashes-start.txt`,
  `hashes-end.txt`, `delivery.diff`, `run-outputs.sha256`, `logs/`.
- `../E3a/`, `../E3a-r1/` teslimleri, stimulus/content, QC/audit, testler, kod değişmedi.

## Doğrulamalar (gerçek komutlar; çalıştırılmayan yok)

| # | Komut (özet) | Log | Exit |
| --- | --- | --- | --- |
| 01 | `git rev-parse HEAD`, `status`, `branch`, `log -3` | `logs/01-git-head-status.sh.stdout` | 0 |
| 02 | `python3 --version`, `.venv pytest --version` | `logs/02-env.sh.stdout` | 0 |
| 03 | Kalıcı helper ile yeniden üretim (temp) + bayt-eşlik | `logs/03-regenerate.sh.stdout` | 0 |
| 04 | Exact 7/43 + ayrım unit örneği (helper fonksiyonları, anotasyonsuz) | `logs/04-exact-stance.sh.stdout` | 0 |
| 05 | Refusal kanıtları (input==output, frozen docs, başka repo dosyası; içerik değişmedi) | `logs/05-refusals.sh.stdout/.stderr` | 0 |
| 06 | Hedefli salt-okunur testler (`test_phase7f_stimulus.py`) | `logs/06-targeted-tests.sh.stdout` | 0 |
| 07 | `git diff --check` + yazım kontrolü (stimulus/audit/E3a/E3a-r1 değişmedi) | `logs/07-diff-check.sh.stdout` | 0 |
| 08 | Teslim içi bağlantı kontrolü (final, PASS) | `logs/08-link-check.sh.stdout` | 0 |
| 09 | `run-outputs.sha256` üretimi (belgeler + helper + log stdout'ları; kendi üretim logu hariç) | `logs/09-run-outputs.sh.stdout` | 0 |

`commands.jsonl` içinde çalıştırılmayan komut yoktur; boş satır yoktur.
`run-outputs.sha256` kendi üretim logunu kapsamaz.

## Sınırlılıklar

- Adaylar hüküm değildir; naturalness/safety/E3b kararları insanındır. Tokenizer profili
  yok → tolerans AÇIK. Dış literatür taranmadı.

## Devam

Teslimden sonra durulur; E3b'ye geçilmez. Sıradaki önkoşul: ana inceleyicinin yeniden
incelemesi.
