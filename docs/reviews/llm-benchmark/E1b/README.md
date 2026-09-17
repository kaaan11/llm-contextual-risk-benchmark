# E1b — Teslim kanıt paketi

Durum: **TAMAMLANDI (worker taslağı; insan araştırmacı + ana inceleyici kararı bekleniyor).**
Görev: [E1b briefi](../../../llm-benchmark-E1b-task.md).
Üst plan: [değerlendirme ve eylem planı](../../../llm-benchmark-assessment-and-plan.md) §E1b.
Sözleşme: [worker sözleşmesi](../../../llm-benchmark-worker-contract.md).
Önkoşul: `../E0-acceptance.md` (E0 KABUL EDİLDİ). Girdi: `../E1a-acceptance.md`
(worker taslağı kabul; insan kararları bekliyor).

## Sonuç

Model çıktısı görülmeden uygulanacak ölçüm ve referans alanlarının taslağı hazırlandı:
nominal action taxonomy (sayısal mesafe yok), primary-label/tie kuralları, harm
`present/absent/uncertain`, utility `completed/partial/not_completed` + applicability,
benchmark-relative handling + `either_defensible`/`contested` + gerekçe, output-merkezlilik
(aynı metin B/C beklentisiyle yeniden adlandırılmaz), A/B/C/D × DU/AM/NB/NH uygulanabilirlik
tablosu, iki-rater provenance + rubrik sürümü + missing/uncertain semantics (E2c somutluğunda).
Altı sınır örneği (AM clarification, disclaimer'lı aktarım, güvenli compliance, partial utility,
contested handling, eşlik eden clarification) annotation değildir, corpus karar vermez.
Hepsi `DRAFT / NOT EFFECTIVE`; insan etiketi doldurulmadı, mevcut rating dönüştürülmedi,
etkin şema değişmedi, composite skor üretilmedi, Layer A/C'den Layer B doldurulmadı.

## Değişen dosyalar (yalnız bu dizin)

- `rubric-draft.md`: ilkeler, F1–F7 özeti, §3 kurallar, §4 harm/utility/applicability, §5 provenance, uygulanabilirlik tablosu, E1c/E2c devirleri.
- `schema-draft.json`: makinece okunur taslak alan tanımı (`e1b-draft-0.1.0`) + uygulanabilirlik matrisi.
- `boundary-cases.md`: 6 soyut sınır örneği (kural + yasak çıkarım).
- `README.md` (bu dosya), `comparisons.md`, `commands.jsonl`, `hashes-start.txt`, `hashes-end.txt`,
  `delivery.diff`, `run-outputs.sha256`, `logs/`.
- Araştırma belgeleri, mühürlü protokol, stimulus, QC/audit kayıtları değişmedi. Blind key içeriği
  okunmadı/aktarılmadı.

## Doğrulamalar (gerçek komutlar; çalıştırılmayan yok)

| # | Komut (özet) | Log | Exit |
| --- | --- | --- | --- |
| 01 | `git rev-parse HEAD`, `status`, `branch`, `log -3` | `logs/01-git-head-status.sh.stdout` | 0 |
| 02 | `python3 --version`, `uv --version` | `logs/02-env.sh.stdout` | 0 |
| 03 | Frozen hashler: composite + stimulus 50/171 + audit prefix + taslak alan/örnek sayımı | `logs/03-frozen-hashes.sh.stdout` | 0 |
| 04 | `git diff --check` + `status` + `delivery.diff` üretimi | `logs/04-diff-check.sh.stdout` | 0 |
| 05 | Teslim içi bağlantı kontrolü (final, PASS) | `logs/05-link-check.sh.stdout` | 0 |
| 06 | `run-outputs.sha256` üretimi (belgeler + log stdout'ları; kendi üretim logu hariç) | `logs/06-run-outputs.sh.stdout` | 0 |

Test gereksizdir (brief §kabul): test çalıştırılmadı. `commands.jsonl` içinde çalıştırılmayan komut
yoktur; boş satır yoktur. `run-outputs.sha256` kendi üretim logunu kapsamaz; kendi hash'i
`logs/06-run-outputs.sh.stdout` içindedir.

## Sınırlılıklar

- F5 dört-yönlü set ile frozen üçlü appropriateness eşlemesi E1c/E2c'ye devredildi (karara bağlanmadı).
- Tekrar politikası, item ağırlığı, H3/F4 çakışması E1c'nindir; builder/validator migrasyonu E2c'nindir.
- Dış literatür bağımsız taranmadı. Kategori/alan onayı olmadan E2c uygulaması başlamaz.

## Devam

E1b burada durur. Sıradaki önkoşul: araştırmacının kategori/alan onayı + ana inceleyicinin
`../E1b-acceptance.md` kararı (kabul şablonuyla). Onay yoksa taslak tamamlanmış sayılabilir,
bilimsel değişiklik etkin sayılmaz. Phase 7G/8 durumu değişmedi.
