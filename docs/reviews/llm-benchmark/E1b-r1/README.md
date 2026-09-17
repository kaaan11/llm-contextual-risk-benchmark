# E1b-R1 — Teslim kanıt paketi

Durum: **TAMAMLANDI (worker revizyonu; yeniden inceleme bekleniyor).**
Görev: [E1b revizyon briefi](../../../llm-benchmark-E1b-revision-task.md).
Önkoşul: `../E1b-acceptance.md` (REVISION REQUIRED; R1–R5).
Sözleşme: [worker sözleşmesi](../../../llm-benchmark-worker-contract.md).

## Sonuç

E1b'deki R1–R5 blokajları kapatıldı; E2c'nin uygulayabileceği tutarlı Layer-B record ve rubric
sözleşmesi üretildi. Kabul edilmiş nominal taxonomy, output-merkezlilik, ayrı harm/utility,
no-composite, soyut sınır örnekleri ve `DRAFT / NOT EFFECTIVE` sınırları korundu.

- **R1:** F5 zarfında `criterion_id` + `allowed_assistance` / `restricted_capability` /
  `clarification_sufficiency`; F3 `criterion_ref` aynı koşulun ID'sine çözülür, eksik/dangling
  ref reddedilir, kritersiz skor üretilmez.
- **R2:** Koşul başına `rater_a`/`rater_b` ham slotları; stable farklı `reviewer_id` zorunlu
  (rol kimlik yerine geçmez); rol/timestamp/session/sürüm/maruziyet beyanı slot başına;
  agreement + ayrı adjudication nesnesi; ham kayıtlar korunur.
- **R3:** `either_defensible` (görüş) / disagreement (workflow) / `contested` (yalnız araştırmacı)
  ayrıştı; rater ve adjudication enum'larında `contested` yok; `allow_with_safeguards` vs
  `decline` = disagreement; payda seçenekleri (D-A/D-B) onaysız seçenek olarak işaretli.
- **R4:** Explicit `scoreable_view` confidence'tan ayrı; iki low ≠ unscorable; iki explicit +
  adjudication = unscorable (frozen §6.2).
- **R5:** F1–F4 yalnız skorlanabilir response'ta; outcome sınıfları E5c'ye devredildi, dönüşüm yok.
- **R6:** `requires` koşulluları doğru anlatıyor (`inapplicability_reason` yalnız `not_applicable`te);
  şemada örnek veri/insan etiketi yok.
- Kabul örnekleri §6'sı (`rubric-draft.md`): 6 örnek ↔ kural eşleşmesi yazılı.

## Değişen dosyalar (yalnız bu dizin)

- `rubric-draft.md` (v0.2.0 metni: §2R zarf, §2R.1 enum'lar, §2R.2 adjudication, §4R, §5R, §6 harita).
- `schema-draft.json` (v0.2.0: envelope, enum ayrıklığı, koşullu requires, yasaklar, uygulanabilirlik).
- `boundary-cases-r1.md` (yalnız etkilenenler: B-5R revize, B-2R güncelleme, B-7R/B-8R yeni;
  E1b örnek 1/3/4/6 geçerli, tekrarlanmadı).
- `revision-map.md` (R1–R6 ↔ düzeltme ↔ kabul örneği ↔ korunanlar).
- `README.md` (bu dosya), `comparisons.md`, `commands.jsonl`, `hashes-start.txt`, `hashes-end.txt`,
  `delivery.diff`, `run-outputs.sha256`, `logs/`.
- `../E1b/` ham kanıtı değişmedi (yapısal kontrol 04 ile doğrulandı). Üretim kodu, frozen belgeler,
  stimulus, audit/QC, insan rating'leri değişmedi. Blind key içeriği okunmadı/aktarılmadı.

## Doğrulamalar (gerçek komutlar; çalıştırılmayan yok)

| # | Komut (özet) | Log | Exit |
| --- | --- | --- | --- |
| 01 | `git rev-parse HEAD`, `status`, `branch`, `log -3` | `logs/01-git-head-status.sh.stdout` | 0 |
| 02 | `python3 --version`, `uv --version` | `logs/02-env.sh.stdout` | 0 |
| 03 | Yapısal kontroller: parse/enum-ayrıklığı/requires/applicability/yasak/içerik-tarama (43 kontrol) | `logs/03-structural-checks.sh.stdout` | 0 |
| 04 | E1b ham kanıtı değişmezliği (`run-outputs.sha256` karşılaştırması) | `logs/04-e1b-untouched.sh.stdout` | 0 |
| 05 | Frozen hashler: composite + stimulus 50/171 + audit prefix | `logs/05-frozen-hashes.sh.stdout` | 0 |
| 06 | `git diff --check` + `status` + `delivery.diff` üretimi | `logs/06-diff-check.sh.stdout` | 0 |
| 07 | Teslim içi bağlantı kontrolü (final, PASS) | `logs/07-link-check.sh.stdout` | 0 |
| 08 | `run-outputs.sha256` üretimi (belgeler + log stdout'ları; kendi üretim logu hariç) | `logs/08-run-outputs.sh.stdout` | 0 |

Kontroller rater etiketi üretmez (şema-yapı assertion'ları + hash/alan sayımları).
`commands.jsonl` içinde çalıştırılmayan komut yoktur; boş satır yoktur.
`run-outputs.sha256` kendi üretim logunu kapsamaz; kendi hash'i `logs/08-run-outputs.sh.stdout` içindedir.

## Sınırlılıklar

- İnsan karar seçenekleri (`contested` atamaları, D-A/D-B paydası, criterion içerikleri, reviewer
  ID süreci) `APPROVED` yapılmadı.
- F5 handling ↔ frozen üçlü eşleme, tekrar politikası (E1c); builder/validator migrasyonu (E2c).
- Dış literatür bağımsız taranmadı.

## Devam

Teslimden sonra durulur. Sıradaki önkoşul: ana inceleyicinin yeniden incelemesi
(`../E1b-r1-acceptance.md` veya E1b kabul güncellemesi). Kabul olmadan E1c/E2c başlamaz.
Phase 7G/8 kapalıdır.
