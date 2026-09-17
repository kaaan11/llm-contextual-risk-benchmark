# E0 — Teslim kanıt paketi

Durum: **TAMAMLANDI (worker teslimi; ana inceleyici kabulü bekleniyor).**
Görev: [E0 briefi](../../../llm-benchmark-E0-task.md).
Üst plan: [değerlendirme ve eylem planı](../../../llm-benchmark-assessment-and-plan.md) §1–4 (E0).
Sözleşme: [worker sözleşmesi](../../../llm-benchmark-worker-contract.md).
Şablon: [comparisons](../_templates/comparisons.md).

## Sonuç

Rapor bulgularını güncel çalışma ağacına bağlayan kalıcı başlangıç paketi üretildi.
Kod düzeltmesi, protokol amendment'ı, insan QC görevi yapılmadı. Phase 7G / Phase 8 durumu değişmedi.

- HEAD `9dd9d31` üzerinde mühürlü composite, stimulus 50/171, QC sayıları ve audit prefix'i
  başlangıç/bitişte aynı (korundu).
- P01–P15 + S01/S02 matrisi üretildi: kodu/mektubu yerelde görülenler `yerelde doğrulandı`,
  sentetik/simülasyon/dış-koşu iddiaları `rapor kanıtı`, hüküm gerektirenler `açık` bırakıldı;
  `çürütüldü` yok.
- Testler ağ/gerçek-yazım/sentetik-rater açısından sınıflandırıldı; güvenli hedefli komutlar önerildi,
  riskli komut çalıştırılmadı. Blind key yalnız varlık olarak kaydedildi.
- Hash/commit/lisans/overlap/contamination iddiaları ayrı tutuldu.

## Değişen dosyalar (yalnız bu dizin)

- `baseline.md`: HEAD/dirty/env, rapor hash'leri, mühür/stimulus/QC/audit envanteri, okunan/yazılan/çalıştırılmayan listesi.
- `findings.md`: P01–P15 + S01/S02 matrisi (dosya/satır, yöntem, kanıt sınırı, sahip).
- `test-safety.md`: 18 test dosyası + 2 rapor script'i sınıflandırması; güvenli öneriler; yasaklılar.
- `provenance-scope.md`: hash / commit / lisans / overlap / contamination ayrımı + blind-key kapsamı.
- `comparisons.md`: başlangıç/bitiş referansları, beklenen farklar, davranış karşılaştırması.
- `hashes-start.txt`, `hashes-end.txt`: mühürlü değerler aynı; E0 dosya listesi farklı (beklenen).
- `commands.jsonl`: 1 şema notu + 11 gerçek komut kaydı (aşağıda).
- `logs/`: 11 komutun stdout/stderr/log çıktısı.
- `delivery.diff`, `run-outputs.sha256`: ek kanıtlar (bu dosyanın altında anlatıldı).

Üretim kodu, config, test, audit, veri dosyası değişmedi. `git diff --check` temiz.
Untracked E0 dosyaları düz `git diff` içinde görünmez; burada sayıldılar.

## Doğrulamalar (gerçek komutlar; çalıştırılmayan yok)

| # | Komut (özet) | Log | Exit |
| --- | --- | --- | --- |
| 01 | `git rev-parse HEAD`, `status`, `branch`, `log -5` | `logs/01-git-head-status.sh.stdout` | 0 |
| 02 | `python3 --version`, `uv --version`, `pyproject` özeti | `logs/02-env.sh.stdout` | 0 |
| 03 | ZIP/Sohbet/`/tmp` 7 dosya hash + manifesto doğrulama (7/7 OK) | `logs/03-manifest.sh.stdout` | 0 |
| 04 | 6 protokol dosyası + composite yeniden üretimi (eşleşti) | `logs/04-composite.sh.stdout` | 0 |
| 05 | Stimulus hash + 50/171 + final-byte 50/50 | `logs/05-stimulus.sh.stdout` | 0 |
| 06 | QC sayıları + blind-key varlığı + history satır/hash | `logs/06-qc-audit.sh.stdout` | 0 |
| 07 | Rapor alıntı hash'lerinin güncelliği (17 dosya) | `logs/07-cited-hashes.sh.stdout` | 0 |
| 08 | Assistant strata 43/7 + D bayt-kısalığı 17/21 | `logs/08-assistant-strata.sh.stdout` | 0 |
| 09 | `rg` kontrolleri (H3/F4, max_tokens, system_instruction, neutral_filler, blind kapısı, n_expected, latency) | `logs/09-rg-checks.sh.stdout` | 0 |
| 10 | `git diff --check` + `diff --stat` + `status` | `logs/10-diff-check.sh.stdout` | 0 |
| 11 | Teslim içi bağlantı kontrolü (ara) | `logs/11-link-check.sh.stdout` | 0 |
| 12 | `delivery.diff` üretimi (tracked) + E0 untracked sayımı | `logs/12-delivery-diff.sh.stdout` | 0 |
| 13 | `run-outputs.sha256` üretimi (belgeler + log stdout'ları) | `logs/13-run-outputs.sh.stdout` | 0 |
| 14 | Teslim içi bağlantı kontrolü (final, PASS) | `logs/14-link-check-final.sh.stdout` | 0 |
| 15 | `run-outputs.sha256` yenilemesi (tüm loglar dahil) | `logs/15-run-outputs-final.sh.stdout` | 0 |

Tam suite, `verify_contract.py`, `prospective_sensitivity.py`, model/API çağrısı, audit/QC yazımı
çalıştırılmadı (`test-safety.md` §3–4). `commands.jsonl` içinde çalıştırılmayan komut yoktur.

## Sınırlılıklar

- Dinamik yeniden üretim yok: P14 sentetik negatif-testleri ve P15/S01 matematiksel karşıörnekleri
  kod şekli/premise düzeyinde doğrulandı; bağımsız koşu/hesap E2/E6'nındır.
- Dış literatür (L01–L36), yenilik hükmü, GitHub/commit authentication, contamination yokluğu
  bu pakette ispatlanmadı; açık bırakıldı.
- `pytest` kurulu değil; bu yokluk test sonucu değildir.
- Blind key içeriği/hash/mapping pakete taşınmadı; Sohbet'in ek PDF/ZIP'leri görülmedi.

## Devam

E0 burada durur. Sıradaki önkoşul: ana inceleyicinin diff'i, kritik kabul örneklerini, korunan
hash'leri ve audit prefix'ini bağımsız doğrulayıp `docs/reviews/llm-benchmark/E0-acceptance.md`
dosyasını [kabul şablonuyla](../_templates/acceptance.md) yazması. Kabul olmadan E1a–E1c/E2a/E3a
başlatılmaz. Bilimsel kararlar (H3/F4, non-trivial, ölçüm/estimand, FAIL yorumu, judge/bütçe,
stimulus hükmü) bu teslimde verilmedi; sahipleri `findings.md` matrisindedir.
