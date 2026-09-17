# E0 — Başlangıç referans envanteri (baseline)

Durum: E0 worker başlangıç kaydı. Kök: `/home/kaan/AI_Search`. HEAD: `9dd9d31607b3d97c02fe3ef9b7cfb68b4a3ed50e`.
Tarih (UTC): 2026-09-09. Yürütücü: küçük worker (E0 briefi + worker sözleşmesi kapsamında, salt okunur doğrulama + belge yazımı).

Bu belge kod düzeltmesi, protokol amendment'ı veya insan QC görevi değildir.
Rapor yazarının `PROJECT-VERIFIED` etiketleri yerel yeniden doğrulama yerine kullanılmamıştır;
her satırda yöntem ve kanıt sınırı ayrı yazılmıştır.

## 1. Başlangıç HEAD ve çalışma ağacı

- HEAD: `9dd9d31607b3d97c02fe3ef9b7cfb68b4a3ed50e` (`git rev-parse HEAD`, log: `logs/01-git-head-status.log`).
- Branch: `master`.
- Tracked dirty: yalnız `M .gitignore` (4 satır ek: `gptpro-bundles/`, `gptpro/` local handoff yoksayma).
  Kullanıcı çalışması olarak korunur; sahiplenilmez, düzeltilmez.
- Untracked (başlangıçta, `git status --short`):
  - `docs/llm-benchmark-E0-task.md`, `docs/llm-benchmark-E1a-task.md`, `docs/llm-benchmark-E1b-task.md`,
    `docs/llm-benchmark-E1c-task.md`, `docs/llm-benchmark-E2a-task.md`, `docs/llm-benchmark-E2b-task.md`,
    `docs/llm-benchmark-E2c-task.md`, `docs/llm-benchmark-E3a-task.md`, `docs/llm-benchmark-E3b-task.md`,
    `docs/llm-benchmark-E4a-human-task.md`, `docs/llm-benchmark-E4b-human-task.md`,
    `docs/llm-benchmark-E5a-task.md`, `docs/llm-benchmark-E5b-task.md`, `docs/llm-benchmark-E5c-task.md`,
    `docs/llm-benchmark-E5d-task.md`, `docs/llm-benchmark-E6a-task.md`, `docs/llm-benchmark-E6b-task.md`,
    `docs/llm-benchmark-E6c-task.md`, `docs/llm-benchmark-E7-review-task.md`,
    `docs/llm-benchmark-assessment-and-plan.md`, `docs/llm-benchmark-worker-contract.md`,
    `docs/llm-benchmark-worker-index.md`, `docs/reviews/`, `uv.lock`.
  - `docs/reviews/llm-benchmark/E0/` başlangıçta iskelet (`README.md`, `commands.jsonl`, `comparisons.md`,
    durum `NOT_STARTED`); üzerine yazılmadan genişletildi.
- Bitiş HEAD: değişmedi (commit/push/branch yok). Bitiş dirty: başlangıçla aynı + yeni E0 teslim dosyaları
  (untracked). Mühürlü dosya, audit geçmişi, üretim kodu/config/test/veri değişikliği yok.
  Kanıt: `hashes-start.txt`, `hashes-end.txt`, `comparisons.md`, `delivery.diff`.

## 2. Python ve bağımlılık ortamı

- `python3 --version`: Python 3.14.4 (`logs/02-env.log`).
- `uv --version`: uv 0.12.5.
- `pip` / `pytest` PATH'te yok; `pyproject.toml` (`name=llm-security-usability-benchmark`, `version=0.2.0`,
  `requires-python>=3.10`, `dev: pytest>=8.0.0`, `providers: openai>=1.0.0, anthropic>=0.18.0`).
- Bu E0 paketinde bağımlılık kurulmadı, yükseltilmedi, test suite çalıştırılmadı.
  Eksik `pytest` ortamı test başarısızlığı diye raporlanmadı (`test-safety.md` §4).
- Ağ çağrısı yok; model/API çağrısı yok; provider anahtarı okunmadı/kopyalanmadı.

## 3. Rapor kaynak hashleri (salt okunur, repo dışından okundu)

Asıl kaynak dizini: `/home/kaan/GPT-Pro/reports/LLM_Benchmark`. Kalıcı repo içine ZIP açılmadı.

| Kaynak | SHA-256 | Boyut | Durum |
| --- | --- | --- | --- |
| `LCRB_Hakem_Incelemesi_Tam_Paket.zip` | `1c7c12ed51c2a23b2d4d7fd2bcd831338854e15c55303fc5ff5cb9c2ea4af917` | 85428 | Eşleşti |
| `Sohbet.md` | `4d687615f941d8dc2af722cb023ad70e982b57eebc5444ac922d274353676332` | 66243 | Eşleşti |

Salt okunur geçici dizin: `/tmp/llm-benchmark-review-20260909` (yedi dosya; `TESLIM_MANIFEST.json`
içindeki yedi kaydın boyut/hash eşleşmesi bu turda yeniden doğrulandı, `logs/03-manifest.log`):

| Dosya | SHA-256 | Boyut |
| --- | --- | --- |
| `LCRB_Bilimsel_Hakem_Raporu.md` | `530f451010607379bb05b2355d1589f4d8137e0268aec0ee27b737255371c7ab` | 61937 |
| `LCRB_Kanit_Eki.md` | `343448ce3ed0e47686955301678e9a7f9f11824b869d1446c622533b149caecf` | 152107 |
| `OKU_BENI.md` | `9c117226ac83a21af576dd46a2010ced5daac422d98206737bb72f24d7699e42` | 1982 |
| `contract_negative_tests.json` | `5d8d4cc93acb781d29b94b6372e7a8c572a0fd026946693c6d5c153e4ef746e4` | 1222 |
| `prospective_sensitivity.json` | `b524097c27268e73578cfafd3556da5c3cb2b6311d09cb2d417152a574a7d08c` | 8820 |
| `prospective_sensitivity.py` | `6aa701f3546f7b1981cf76c2925ea2f673c56414f1f878fd1a2b72e21e538cce` | 3842 |
| `verify_contract.py` | `203e8eb4fe02a1f5f6e1243a3a36ac10fb24155394cdc438d5522de37267a840` | 3943 |

Sohbet, ZIP'teki raporun kopyası değildir: ek McNemar karşıörneği (S01) ve
`300 passed / 50 failed` dış paket koşusu kaydı (S02) içerir; ZIP'in `OKU_BENI.md` dosyası ise
bütün test suite'inin çalıştırılmadığını söyler. Bu kayıtlar tek koşu gibi birleştirilmedi.
Sohbetin işaret ettiği ek PDF/ZIP dosyaları verilen dizinde yok; içerikleri görülmüş sayılmıyor.

## 4. Mühürlü protokol ve stimulus (başlangıç; bitişte tekrar edildi)

- Protokol manifestosu: `results/dataset_audit/phase7e_preregistration_hash.json`
  (`protocol_version=1.0.2`, `composite_protocol_hash=47ae3fed...bbcfc6f`).
- Altı `protocol_files` per-file hash'i yeniden hesaplandı, hepsi eşleşti; composite yeniden üretildi,
  eşleşti (`logs/04-composite.log`). Yöntem: sorted `relative_path:sha256` satırlarının `\n` ile
  birleştirilmiş UTF-8 baytlarının SHA-256'sı (manifestodaki `composite_method`).
- Stimulus: `dataset/pilot/multiturn/stimulus_dataset_v1.json`
  SHA-256 `2f78e79e19d844b84b6bc06a0c2bef47e19283cc7c54b91f6ae283e1a74af077`;
  `record_count=50`, `len(records)=50`; toplam koşul `171` (`3 koşullu 29` + `4 koşullu 21`);
  kategori `dual_use_nonnull=30`, `persistent_ambiguity=7`, `null_benign=7`, `null_highrisk=6`;
  her 50 maddede koşullar arası final kullanıcı metni UTF-8 baytları eşit (50/50)
  (`logs/05-stimulus.log`).
- D kapsamı: `neutral_filler_control` 21 maddede mevcut. Sihirbazın aradığı `neutral_filler`
  anahtarıyla sıfır maddede bulunuyor (`scripts/review_context.py:98`; ayrıntı `findings.md` P07).
- QC sayıları (canlı dosyalardan okundu, değiştirilmedi):
  `phase7g_blind_review.json`: 50 madde, `PENDING=49` + `PARTIAL_ONE_RATER=1`,
  `rater_a` dolu=1, `rater_b` dolu=0, `adjudicated=0`;
  `phase7g_human_qc.json` counts: `total=50, pending=50, keep=0, revise=0, reject=0, researcher_qc_true=0`
  (`logs/06-qc-audit.log`).
- Audit history prefix (append-only, hash + satır sayısı; içerik taşınmadı):
  `phase7e_review_history.jsonl`: 51 satır, SHA-256 `e145afed...cf3b866c` (manifestodaki kayıtla aynı);
  `phase7g_review_history.jsonl`: 5 satır, SHA-256 `23755e0f...a550a15` (`logs/06-qc-audit.log`).
  Geçmişe yazılmadı, silinmedi, yeniden yazılmadı.

## 5. Rapor alıntılarının güncelliği (farklı koşu beyanları birleştirilmedi)

- `LCRB_Kanit_Eki.md` içindeki P01–P12 dosya/satır alıntılarının SHA-256 değerleri güncel ağaçla
  karşılaştırıldı: `README.md`, `PROJECT_STATUS.md`, `phase7e_preregistration.md`,
  `phase7e_annotation_protocol.md`, `phase7e_pre_evaluation_clarification.md`,
  `apply_phase7g_annotations.py`, `validate_phase7g_review.py`, `review_context.py`,
  `ROADMAP.md`, `statistical_power_and_limitations.md`, `runner.py`, `adapters/providers.py`,
  `metadata.py`, `phase8_eval_plan.json`, `preflight.py`, `metrics.py`, `phase7g_human_qc.md`
  alıntı hash'leri güncel dosyalarla eşleşiyor (`logs/07-cited-hashes.log`).
  Bu, rapor snapshot'ının bu HEAD'e ait olduğu iddiasını güçlendirir; `.git` nesnesi ZIP'te
  olmadığı için commit aidiyeti bağımsız doğrulanmış sayılmaz (`provenance-scope.md` §2).
- Raporun `300 passed / 50 failed` dış paket koşusu ile tarihsel `350 passed` beyanı farklı koşulardır;
  tek kanıt gibi birleştirilmedi. Tam suite bu E0 turunda çalıştırılmadı.

## 6. Okunanlar / yazılanlar / çalıştırılmayanlar

- Okunanlar: `AGENTS.md`, E0 briefi, worker sözleşmesi, üst plan §1–4 (E0 kısmı),
  rapor + kanıt eki + `Sohbet.md` ilgili bölümleri, `OKU_BENI.md`, `TESLIM_MANIFEST.json`,
  `contract_negative_tests.json`, `prospective_sensitivity.json/.py`, `verify_contract.py` (yalnız okuma),
  `pyproject.toml`, `phase7e_preregistration_hash.json`, `stimulus_dataset_v1.json`,
  test girişleri (18 dosya başlığı + `test_phase7g_qc.py` / `test_phase7g_tooling.py` / `test_benchmark_framework.py`
  hedefli incelemesi), `source_inventory.json`, `overlap_report.json`, `stimulus_overlap_report.json`,
  `stimulus_statistics.json`, `dataset_sources.md`, durum belgeleri (`README.md`, `PROJECT_STATUS.md`,
  `CURRENT_STATE_AND_NEXT_STEPS.md`, `ROADMAP.md`, `phase7g_human_qc.md`).
- Yazılanlar: yalnız `docs/reviews/llm-benchmark/E0/` altındaki belgeler ve kanıtlar.
- Çalıştırılmayanlar (bilerek): tam test suite'i, hakem QC negatif-test script'i
  (`verify_contract.py` — sentetik blind-label üretir, AGENTS.md yasağı), güç simülasyonu
  (`prospective_sensitivity.py` — raporun varsayımsal hesabı yeniden üretilmedi),
  gerçek model/API çağrısı, audit/QC yazımı. Ayrıntı `test-safety.md`.
