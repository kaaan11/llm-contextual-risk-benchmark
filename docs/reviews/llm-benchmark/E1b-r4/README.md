# E1b-R4 — Teslim kanıt paketi

Durum: **TAMAMLANDI (worker revizyonu; yeniden inceleme bekleniyor).**
Görev: [E1b-R4 briefi](../../../llm-benchmark-E1b-r4-task.md).
Önkoşul: `../E1b-r3-acceptance.md` (REVISION REQUIRED; tek blokaj).
Sözleşme: [worker sözleşmesi](../../../llm-benchmark-worker-contract.md).

## Sonuç

Layer-C koşullu presence çelişkisi kapatıldı; R3 katman ayrımı, contested yerleşimi, R2
resolved akışı ve frozen §6.2 davranışı aynen korundu.

- **Dal U** (`unscorable_content`): `unscorable_reason` zorunlu; F1–F4 yasak.
- **Dal S** (`scoreable`): `unscorable_reason` yasak; F1/F2 zorunlu; F3 yalnız resolved
  ID/version mevcutsa zorunlu (yoksa yasak + `f3_gap=not_scored_missing_criterion`);
  F4 yalnız applicability izin veriyorsa zorunlu (yoksa yasak + `f4_gap` + neden;
  conditional hücre `applicability_resolution` ile çözülür).
- **Adjudication finali:** `final_scoreable_view` açıkça yazılır; final scoreable → Dal S
  kuralları, final unscorable → F1–F4 yasak; ham slotlar değişmez.
- İki explicit unscorable doğrudan final + non-scorable'da zarf yokluğu korundu.
- 5 kabul örneği `rubric-draft.md` §6T'de birebir karşılandı; rater etiketi üretilmedi.

## Değişen dosyalar (yalnız bu dizin)

- `rubric-draft.md` (v0.5.0: §8P dallar + §8P.3 finaller + §6T karşılama).
- `schema-draft.json` (v0.5.0: `presence_branches`, final `requires_conditional` dalları,
  F3 `f3_gap`, F4 trio + `applicability_resolution`, 6 yeni yasak).
- `boundary-cases-r4.md` (yalnız etkilenen: B-7U revize).
- `revision-map.md`, `README.md` (bu dosya), `comparisons.md`, `commands.jsonl`,
  `hashes-start.txt`, `hashes-end.txt`, `delivery.diff`, `run-outputs.sha256`, `logs/`.
- Önceki 4 paket değişmedi (komut 04 ile doğrulandı). Üretim kodu, mühürlü belgeler, stimulus,
  audit/QC, insan rating'leri değişmedi.

## Doğrulamalar (gerçek komutlar; çalıştırılmayan yok)

| # | Komut (özet) | Log | Exit |
| --- | --- | --- | --- |
| 01 | `git rev-parse HEAD`, `status`, `branch`, `log -3` | `logs/01-git-head-status.sh.stdout` | 0 |
| 02 | `python3 --version`, `uv --version` | `logs/02-env.sh.stdout` | 0 |
| 03 | Yapısal kontroller: presence matrisi, final dalları, regresyon, matris (47 kontrol) | `logs/03-structural-checks.sh.stdout` | 0 |
| 04 | 4 önceki paketin değişmezliği | `logs/04-prior-untouched.sh.stdout` | 0 |
| 05 | Frozen hashler: composite + stimulus 50/171 + audit prefix | `logs/05-frozen-hashes.sh.stdout` | 0 |
| 06 | `git diff --check` + `status` + `delivery.diff` üretimi | `logs/06-diff-check.sh.stdout` | 0 |
| 07 | Teslim içi bağlantı kontrolü (final, PASS) | `logs/07-link-check.sh.stdout` | 0 |
| 08 | `run-outputs.sha256` üretimi (belgeler + log stdout'ları; kendi üretim logu hariç) | `logs/08-run-outputs.sh.stdout` | 0 |

`commands.jsonl` içinde çalıştırılmayan komut yoktur; boş satır yoktur.
`run-outputs.sha256` kendi üretim logunu kapsamaz; kendi hash'i `logs/08-run-outputs.sh.stdout` içindedir.

## Sınırlılıklar

- Eşleme, tekrar, H3/F4 (E1c); migrasyon, ID otoritesi (E2c); `contested`/payda atamaları
  insan onayı bekler (`APPROVED` yok). Dış literatür taranmadı.

## Devam

Teslimden sonra durulur. Sıradaki önkoşul: ana inceleyicinin yeniden incelemesi.
Kabul olmadan E1c/E2c başlamaz; Phase 7G/8 kapalıdır.
