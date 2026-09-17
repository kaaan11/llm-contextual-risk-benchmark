# E1c-R2 — Teslim kanıt paketi

Durum: **TAMAMLANDI (worker revizyonu; yeniden inceleme bekleniyor).**
Görev: [E1c-R2 briefi](../../../llm-benchmark-E1c-r2-task.md).
Önkoşul: `../E1c-r1-acceptance.md` (REVISION REQUIRED; R1–R4 + stance).
Sözleşme: [worker sözleşmesi](../../../llm-benchmark-worker-contract.md).

## Sonuç

E1c-R1'deki dört blokaj + stance açıklığı kapatıldı; doğrulanmış matematik, job kimliği, CI
seçenekleri ve `DRAFT / NOT EFFECTIVE` sınırı korundu.

- **R1:** Response başına ≤1 resolved label (uzlaşma/adjudication); unresolved endpoint dışı;
  3 tekrar × 2 rater ≤ 3 gözlem.
- **R2:** Contested koşulsuz exclusion'dan çıktı; D-A/D-B seçeneksiz kural yok; pending-havuz.
- **R3:** Error-asymmetry standalone sözleşmesi (eligibility + violation + hücreler); mapping
  onaysızsa pending; H-U paydası bağlamaz.
- **R4:** H-U1/H-T1b/gap/NA kapalı pay/payda + 0/0 kuralı.
- **Stance:** Kategori × stance hücre tablosu + NB mappingi; havuzlama yok.

## Değişen dosyalar (yalnız bu dizin)

- `estimand-contract.md` (v0.3), `amendment-delta.md`, `legacy-delta.md`, `revision-map.md`,
  `README.md` (bu dosya), `comparisons.md`, `commands.jsonl`, `hashes-start.txt`, `hashes-end.txt`,
  `delivery.diff`, `run-outputs.sha256`, `logs/`.
- `../E1c/`, `../E1c-r1/` kanıtları değişmedi. Frozen, stimulus, audit/QC, kod, rating'ler değişmedi.

## Doğrulamalar (gerçek komutlar; çalıştırılmayan yok)

| # | Komut (özet) | Log | Exit |
| --- | --- | --- | --- |
| 01 | `git rev-parse HEAD`, `status`, `branch`, `log -3` | `logs/01-git-head-status.sh.stdout` | 0 |
| 02 | `python3 --version`, `uv --version` | `logs/02-env.sh.stdout` | 0 |
| 03 | Matematik yeniden doğrulama + E1c/E1c-r1 değişmezliği + frozen + kapsam sayımı | `logs/03-math-frozen.sh.stdout` | 0 |
| 04 | `git diff --check` + `status` + `delivery.diff` üretimi | `logs/04-diff-check.sh.stdout` | 0 |
| 05 | Teslim içi bağlantı kontrolü (final, PASS) | `logs/05-link-check.sh.stdout` | 0 |
| 06 | `run-outputs.sha256` üretimi (belgeler + log stdout'ları; kendi üretim logu hariç) | `logs/06-run-outputs.sh.stdout` | 0 |

Matematik saf stdlib hesaplamadır; insan anotasyonu/model çağrısı yoktur.
`commands.jsonl` içinde çalıştırılmayan komut yoktur; boş satır yoktur.
`run-outputs.sha256` kendi üretim logunu kapsamaz.

## Sınırlılıklar

- Mapping, endpoint/CI/eşik/payda seçimleri, E1b insan kararları bekliyor. İnsan kararları
  `APPROVED` yapılmadı; E5/E6'ya etkin devir yok. Dış literatür taranmadı.

## Devam

Teslimden sonra durulur. Sıradaki önkoşul: ana inceleyicinin yeniden incelemesi.
Beklenen ana teslim: bu README.
