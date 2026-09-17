# E1b-R6 — Teslim kanıt paketi

Durum: **TAMAMLANDI (worker revizyonu; yeniden inceleme bekleniyor).**
Görev: [E1b-R6 briefi](../../../llm-benchmark-E1b-r6-task.md).
Önkoşul: `../E1b-r5-acceptance.md` (REVISION REQUIRED; ref blokajı).
Sözleşme: [worker sözleşmesi](../../../llm-benchmark-worker-contract.md).

## Sonuç

R5 alan tanımları ve R4 presence mantığı değiştirilmeden bütün ref'ler gerçekten çözülebilir
hale getirildi; adjudication final payload'ı kapalı şema olarak tanımlandı. Bilimsel kural veya
alan eklenmedi.

- Değer şekillerinin tek canonical otoritesi `$defs` (9 tanım, `def_id`/`def_kind` kimlikli);
  `fields` dizisi + slot/final girdileri `$ref` + presence notudur, şekil kopyası taşımaz.
- `final_payload_schema`: discriminator + 2 dal, tüm final alanları `$defs` `$ref`'li.
- Linter her `$ref`'i kökten token-token traverse eder, hedef kimliğini doğrular;
  `#/fields/F1` türü geçersiz pointer reddedilir; unresolved listesi boş.
- Negatif varyant kanıtı (yalıtılmış bellek kopyaları, canlı dosya değişmedi): bozuk hedef ve
  dizi-içi pointer reddedildi.
- R2–R5 davranış/katman kuralları aynen korundu; insan etiketi üretilmedi.

## Değişen dosyalar (yalnız bu dizin)

- `schema-draft.json` (v0.7.0: `$defs`, `canonical_authority`, `$ref` girdiler,
  `final_payload_schema`, 2 yeni yasak).
- `rubric-ref-note.md` (kısa ref notu; R4/R5 mantığı geçerli).
- `revision-map.md`, `README.md` (bu dosya), `comparisons.md`, `commands.jsonl`,
  `hashes-start.txt`, `hashes-end.txt`, `delivery.diff`, `run-outputs.sha256`, `logs/`.
- Önceki 6 paket değişmedi (komut 04). Üretim kodu, mühürlü belgeler, stimulus, audit/QC,
  insan rating'leri değişmedi.

## Doğrulamalar (gerçek komutlar; çalıştırılmayan yok)

| # | Komut (özet) | Log | Exit |
| --- | --- | --- | --- |
| 01 | `git rev-parse HEAD`, `status`, `branch`, `log -3` | `logs/01-git-head-status.sh.stdout` | 0 |
| 02 | `python3 --version`, `uv --version` | `logs/02-env.sh.stdout` | 0 |
| 03 | Gerçek ref linter: traverse + hedef kimlik + kopya yasağı + final şeması + 2 negatif + regresyon (45 kontrol) | `logs/03-ref-linter.sh.stdout` | 0 |
| 04 | 6 önceki paketin değişmezliği | `logs/04-prior-untouched.sh.stdout` | 0 |
| 05 | Frozen hashler: composite + stimulus 50/171 + audit prefix | `logs/05-frozen-hashes.sh.stdout` | 0 |
| 06 | `git diff --check` + `status` + `delivery.diff` üretimi | `logs/06-diff-check.sh.stdout` | 0 |
| 07 | Teslim içi bağlantı kontrolü (final, PASS) | `logs/07-link-check.sh.stdout` | 0 |
| 08 | `run-outputs.sha256` üretimi (belgeler + log stdout'ları; kendi üretim logu hariç) | `logs/08-run-outputs.sh.stdout` | 0 |

Not: 03 betiği ilk koşuda tırnaksız heredoc nedeniyle bash genişletmesine uğradı (şema değil,
betik hatası); düzeltilmiş koşu kaydedildi, teslim dosyaları hiç değişmedi.
`commands.jsonl` içinde çalıştırılmayan komut yoktur; boş satır yoktur.
`run-outputs.sha256` kendi üretim logunu kapsamaz; kendi hash'i `logs/08-run-outputs.sh.stdout` içindedir.

## Sınırlılıklar

- Eşleme/tekrar/H3-F4 (E1c); migrasyon/ID otoritesi (E2c); `contested`/payda atamaları
  insan onayı bekler (`APPROVED` yok). Dış literatür taranmadı.

## Devam

Teslimden sonra durulur. Sıradaki önkoşul: ana inceleyicinin yeniden incelemesi.
Kabul olmadan E1c/E2c başlamaz; Phase 7G/8 kapalıdır.
