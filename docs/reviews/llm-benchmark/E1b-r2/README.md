# E1b-R2 — Teslim kanıt paketi

Durum: **TAMAMLANDI (worker revizyonu; yeniden inceleme bekleniyor).**
Görev: [E1b-R2 briefi](../../../llm-benchmark-E1b-r2-task.md).
Önkoşul: `../E1b-r1-acceptance.md` (REVISION REQUIRED; iki blokaj).
Sözleşme: [worker sözleşmesi](../../../llm-benchmark-worker-contract.md).

## Sonuç

E1b-R1'de kalan iki blokaj kapatıldı; taxonomy, iki-rater kimliği, ham kayıtların korunması,
disagreement/contested ayrımı, operational-outcome sınırı ve no-composite kararları yeniden
tasarlanmadı.

- **R1:** `resolved_reference` nesnesi (stable ID + version + çözülmüş üçlü + source +
  slot referansları + adjudication referansı + kayıt provenance'ı); agreement yolunda verbatim
  kopya + operatör kaydı (sessiz canonical seçim yasak); disagreement'ta resolved yok, F3 ret;
  F3 yalnız resolved ID/version'a bağlanır, aksi halde `not_scored_missing_criterion`.
- **R2:** Frozen §6.2 birebir — iki explicit unscorable doğrudan final üretir (ek adjudication
  yok); tek taraflı disagreement adjudication'a gider; iki low confidence unscorable üretmez.
- Kabul örnekleri 6 maddesi `rubric-draft.md` §6S'de karşılandı; şema kuralları koşullu ve
  makinece uygulanabilir; örnek insan etiketi / gerçek criterion içeriği üretilmedi.

## Değişen dosyalar (yalnız bu dizin)

- `rubric-draft.md` (v0.3.0: §2S, §4S, §6S).
- `schema-draft.json` (v0.3.0: `resolved_reference`, F3 ID+version bağı, `scoreability_final_states`).
- `boundary-cases-r2.md` (yalnız etkilenenler: B-2S güncelleme, B-7S revize, B-9S yeni).
- `revision-map.md` (R1/R2 ↔ düzeltme ↔ kabul örneği ↔ korunanlar).
- `README.md` (bu dosya), `comparisons.md`, `commands.jsonl`, `hashes-start.txt`, `hashes-end.txt`,
  `delivery.diff`, `run-outputs.sha256`, `logs/`.
- `../E1b/`, `../E1b-r1/` kanıtları değişmedi (komut 04 ile doğrulandı). Üretim kodu, mühürlü
  belgeler, stimulus, audit/QC, insan rating'leri değişmedi. Blind key içeriği okunmadı/aktarılmadı.

## Doğrulamalar (gerçek komutlar; çalıştırılmayan yok)

| # | Komut (özet) | Log | Exit |
| --- | --- | --- | --- |
| 01 | `git rev-parse HEAD`, `status`, `branch`, `log -3` | `logs/01-git-head-status.sh.stdout` | 0 |
| 02 | `python3 --version`, `uv --version` | `logs/02-env.sh.stdout` | 0 |
| 03 | Yapısal kontroller: parse/ref-version/geçiş-matrisi/immutability/§6.2/içerik-tarama (50 kontrol) | `logs/03-structural-checks.sh.stdout` | 0 |
| 04 | E1b + E1b-r1 ham kanıtı değişmezliği | `logs/04-prior-untouched.sh.stdout` | 0 |
| 05 | Frozen hashler: composite + stimulus 50/171 + audit prefix | `logs/05-frozen-hashes.sh.stdout` | 0 |
| 06 | `git diff --check` + `status` + `delivery.diff` üretimi | `logs/06-diff-check.sh.stdout` | 0 |
| 07 | Teslim içi bağlantı kontrolü (final, PASS) | `logs/07-link-check.sh.stdout` | 0 |
| 08 | `run-outputs.sha256` üretimi (belgeler + log stdout'ları; kendi üretim logu hariç) | `logs/08-run-outputs.sh.stdout` | 0 |

Kontroller rater etiketi üretmez. Not: 03 kontrol betiği, teslim dosyaları hiç değişmeden,
iki kez betik-içi yazım hatası (tam-eşleşme vs alt-dize; ASCII-G vs Ğ) nedeniyle düzeltildi;
`commands.jsonl` final geçen koşuyu kaydeder. `commands.jsonl` içinde çalıştırılmayan komut
yoktur; boş satır yoktur. `run-outputs.sha256` kendi üretim logunu kapsamaz; kendi hash'i
`logs/08-run-outputs.sh.stdout` içindedir.

## Sınırlılıklar

- Criterion içerikleri, ID/version atama otoritesi, re-version politikası, `contested`
  atamaları, denominator seçenekleri insan onayı bekler (`APPROVED` yok).
- F5 handling ↔ frozen üçlü eşleme, tekrar politikası (E1c); migrasyon (E2c).
- Dış literatür bağımsız taranmadı.

## Devam

Teslimden sonra durulur. Sıradaki önkoşul: ana inceleyicinin yeniden incelemesi.
Kabul olmadan E1c/E2c başlamaz; Phase 7G/8 kapalıdır.
