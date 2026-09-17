# E1b-R5 — Teslim kanıt paketi

Durum: **TAMAMLANDI (worker revizyonu; yeniden inceleme bekleniyor).**
Görev: [E1b-R5 briefi](../../../llm-benchmark-E1b-r5-task.md).
Önkoşul: `../E1b-r4-acceptance.md` (REVISION REQUIRED; tek blokaj).
Sözleşme: [worker sözleşmesi](../../../llm-benchmark-worker-contract.md).

## Sonuç

R4 dal mantığı değiştirilmeden slot-scope ref bütünlüğü kapatıldı; taxonomy, bilimsel kurallar,
katmanlar, adjudication akışı ve applicability kararları yeniden tasarlanmadı.

- 8 dal alanı (`F1–F4`, `unscorable_reason`, `f3_gap`, `f4_gap`, `applicability_resolution`)
  slot şemasında açık type/value tanımına sahip; tek presence otoritesi `presence_branches`.
- Nested F1–F4 üst düzey `#/fields/F1..F4` ref'i + kayıpsız şekli taşır (drift yok).
- `f3_gap` tek değerli; `f4_gap` reason'lı; resolution boolean+reason, non-conditional'da yasak.
- Adjudication finallerindeki tüm alanlar aynı scope'ta tanımlı (`final_field_scope`).
- Linter anahtar araması değil gerçek ref-çözümlemedir: dal/final listelerindeki her ad scope
  anahtarlarında bulunur (undeclared=[]); unscorable/scoreable kuralları R4 ile aynı; yanlış-dal
  gap/reason reddedilir; R2/R3 regresyonları geçer; insan etiketi üretilmedi.

## Değişen dosyalar (yalnız bu dizin)

- `schema-draft.json` (v0.6.0: slot tanımlar + makine listeleri + `final_field_scope`).
- `rubric-ref-note.md` (kısa not; R4 §8P metni geçerli).
- `revision-map.md`, `README.md` (bu dosya), `comparisons.md`, `commands.jsonl`,
  `hashes-start.txt`, `hashes-end.txt`, `delivery.diff`, `run-outputs.sha256`, `logs/`.
- Önceki 5 paket değişmedi (komut 04: 13+16+16+16+16 dosya OK). Üretim kodu, mühürlü belgeler,
  stimulus, audit/QC, insan rating'leri değişmedi.

## Doğrulamalar (gerçek komutlar; çalıştırılmayan yok)

| # | Komut (özet) | Log | Exit |
| --- | --- | --- | --- |
| 01 | `git rev-parse HEAD`, `status`, `branch`, `log -3` | `logs/01-git-head-status.sh.stdout` | 0 |
| 02 | `python3 --version`, `uv --version` | `logs/02-env.sh.stdout` | 0 |
| 03 | Ref linter: deklarasyon çözümleme + drift + gap/reason + R4/regression (34 kontrol) | `logs/03-ref-linter.sh.stdout` | 0 |
| 04 | 5 önceki paketin değişmezliği | `logs/04-prior-untouched.sh.stdout` | 0 |
| 05 | Frozen hashler: composite + stimulus 50/171 + audit prefix | `logs/05-frozen-hashes.sh.stdout` | 0 |
| 06 | `git diff --check` + `status` + `delivery.diff` üretimi | `logs/06-diff-check.sh.stdout` | 0 |
| 07 | Teslim içi bağlantı kontrolü (final, PASS) | `logs/07-link-check.sh.stdout` | 0 |
| 08 | `run-outputs.sha256` üretimi (belgeler + log stdout'ları; kendi üretim logu hariç) | `logs/08-run-outputs.sh.stdout` | 0 |

`commands.jsonl` içinde çalıştırılmayan komut yoktur; boş satır yoktur.
`run-outputs.sha256` kendi üretim logunu kapsamaz; kendi hash'i `logs/08-run-outputs.sh.stdout` içindedir.

## Sınırlılıklar

- Eşleme/tekrar/H3-F4 (E1c); migrasyon/ID otoritesi (E2c); `contested`/payda atamaları
  insan onayı bekler (`APPROVED` yok). Dış literatür taranmadı.

## Devam

Teslimden sonra durulur. Sıradaki önkoşul: ana inceleyicinin yeniden incelemesi.
Kabul olmadan E1c/E2c başlamaz; Phase 7G/8 kapalıdır.
