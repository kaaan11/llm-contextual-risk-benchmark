# E1a — Teslim kanıt paketi

Durum: **TAMAMLANDI (worker taslağı; insan araştırmacı + ana inceleyici kararı bekleniyor).**
Görev: [E1a briefi](../../../llm-benchmark-E1a-task.md).
Üst plan: [değerlendirme ve eylem planı](../../../llm-benchmark-assessment-and-plan.md) §E1a.
Sözleşme: [worker sözleşmesi](../../../llm-benchmark-worker-contract.md).
Önkoşul: `../E0-acceptance.md` (E0 KABUL EDİLDİ, 2026-09-09).

## Sonuç

Mevcut belgelerdeki iddialar dar fixed-history technical pilot construct'ına göre haritalandı.
14 iddia satırı (C-01–C-14): kaynak konumu, mevcut ifade, `koru/daralt/terk et/ertele` önerisi,
önerilen ifade, kanıt, etkilenen hipotez/çıktı ve boş insan-kararı alanı içerir. Briefin zorunlu
kapsamı (whole-history packet, latent intent, pure user evidence, D rolü, AM/NB/NH sınırları,
assistant stance tabakaları, external validity, novelty/"first", calibration, contamination) eksiksiz
kapsandı; ek olarak puanlama (judge), eski RQ kapsamı ve hipotez/güç sayıları eklendi.
Belge drift'i (RQ dokümanı, başlık sorusu, ROADMAP judge, güç/bütçe) görünür kılındı.
En güçlü yayın iddiası taslağı yön/model/etki/basarım doldurmadan verildi.
Bu paket etkili protokolü ve mühürlü belgeleri değiştirmez; metin `DRAFT / NOT EFFECTIVE` kalır.

## Değişen dosyalar (yalnız bu dizin)

- `claim-decisions.md`: karar matrisi + drift notu + yayın iddiası taslağı + hipotez/çıktı özeti + mekanizma kontrol listesi.
- `README.md` (bu dosya), `comparisons.md`, `commands.jsonl`, `hashes-start.txt`, `hashes-end.txt`,
  `delivery.diff`, `run-outputs.sha256`, `logs/`.
- `README.md` ve araştırma belgeleri (`README.md`, `research_questions.md`, `ROADMAP.md`, raporlar)
  bu pakette düzenlenmedi. Mühürlü belgeler, stimulus, audit geçmişi değişmedi.

## Doğrulamalar (gerçek komutlar; çalıştırılmayan yok)

| # | Komut (özet) | Log | Exit |
| --- | --- | --- | --- |
| 01 | `git rev-parse HEAD`, `status`, `branch`, `log -3` | `logs/01-git-head-status.sh.stdout` | 0 |
| 02 | `python3 --version`, `uv --version` | `logs/02-env.sh.stdout` | 0 |
| 03 | Frozen hashler: composite + stimulus 50/171 + audit prefix + iddia konum grepleri | `logs/03-frozen-hashes.sh.stdout` | 0 |
| 04 | `git diff --check` + `status` | `logs/04-diff-check.sh.stdout` | 0 |
| 05 | Teslim içi bağlantı kontrolü (final, PASS) | `logs/05-link-check.sh.stdout` | 0 |
| 06 | `run-outputs.sha256` üretimi (belgeler + log stdout'ları; kendi üretim logu hariç) | `logs/06-run-outputs.sh.stdout` | 0 |

Test gereksizdir (brief §kabul): test çalıştırılmadı. `commands.jsonl` içinde çalıştırılmayan komut
yoktur; boş satır yoktur (E0 kabulündeki kusur #1 tekrarlanmadı). `run-outputs.sha256` kendi üretim
logunu kapsamaz (kusur #2 tekrarlanmadı); kendi hash'i `logs/06-run-outputs.sh.stdout` içindedir.

## Sınırlılıklar

- Dış literatür (L01–L36) bağımsız taranmadı; novelty/ölçüm gerekçeleri raporun haritasını benimser,
  doğrulamaz.
- `verify_contract.py` / `prospective_sensitivity.py` çalıştırılmadı; model/API çağrısı yok.
- Matris önerileri worker taslağıdır; `APPROVED` hükmü yoktur. v1.0.2'nin `rules_changed=false`
  niteliği yeni ölçüme taşınamaz (üst plan E1 kapısı).
- E1b (rubrik) ve E1c (estimand/amendment) bu pakete çekilmedi; C-10/C-14 ilgili teslimlere devreder.

## Devam

E1a burada durur. Sıradaki önkoşul: ana inceleyici + araştırmacının somut kararları
(`../E1a-acceptance.md`, kabul şablonuyla): her satırın `koru/daralt/terk et/ertele` karşılığı ve
yayın iddiası taslağının onayı. Onay yoksa taslak tamamlanmış sayılabilir, bilimsel değişiklik
etkin sayılmaz. Sonraki teslim (E1b) bu kabulü bekler; Phase 7G/8 durumu değişmedi.
