# E0 — Test güvenliği sınıflandırması (test-safety)

Kural: test çıktıları `/tmp` altında `mktemp -d` ile oluşturulan gerçek dizine yazılır.
Mock transport ve matematiksel sentetik satırlar açıkça fixture olarak işaretlenir; gerçek QC veya
ampirik model sonucu gibi sunulmaz. AGENTS.md sentetik kör-rater anotasyonu üretmeyi yasakladığından,
böyle veri isteyen test yazılmaz/çalıştırılmaz; durum geçişleri boş/eksik kayıtlarla, saf doğrulama
fonksiyonlarıyla ya da rater semantiği taşımayan yapısal fixture'larla sınanır.
Riskli komut çalıştırılmadı; aşağıda yalnız öneri vardır, icra kaydı yoktur.

## 1. Sınıflandırma (dosya düzeyinde, statik inceleme)

Canlı ağ = gerçek provider HTTP çağrısı. Gerçek QC yazımı = `results/dataset_audit/*.jsonl` veya
`phase7g_*.json` dosyalarına yazım. Sentetik rater = `probably_benign` vb. kör-rater anotasyonu üretimi.

| Test dosyası | Canlı ağ | Gerçek QC yazımı | Sentetik rater üretimi | Not |
| --- | --- | --- | --- | --- |
| `tests/test_annotate_blind.py` | Yok | Yok (in-memory + mock wizard) | Yok (yapısal fixture, `B1/B2/B3`) | Güvenli aday |
| `tests/test_annotation_validation.py` | Yok | Yok | Yok | Güvenli aday (şema + örnek JSON) |
| `tests/test_benchmark_framework.py` | Yok (injected transport + `MockAdapter`; `OPENAI/ANTHROPIC_API_KEY` yalnız `patch.dict` placeholder) | Yok (`InMemoryResponseLogger` / `tempfile`) | Yok | Güvenli aday; `JsonlResponseLogger` yazımı yalnız `tempfile` altında incelenmeli |
| `tests/test_dataset_validation.py` | Yok | Yok | Yok | Güvenli aday |
| `tests/test_multiturn_construction.py` | Yok | Yok | Yok | Güvenli aday (spec'ten build, bellekte) |
| `tests/test_multiturn_design.py` | Yok | Yok | Yok | Güvenli aday |
| `tests/test_multiturn_researcher_review.py` | Yok | Yok | Yok | Güvenli aday |
| `tests/test_phase6a_smoke.py` | Yok (retry/mock + config okuma; gerçek provider çağrısı `not_evaluated` yolunda) | Yok | Yok | Güvenli aday; secret masking yolu ayrıca gözlenmeli |
| `tests/test_phase6b_audit.py` | Yok (metadata düzeyi; raw indirme yok) | Yok | Yok | Güvenli aday |
| `tests/test_phase7_schema_audit.py` | Yok | Yok | Yok | Güvenli aday |
| `tests/test_phase7e_review.py` | Yok | Yok (beklenti: snapshot + append-only okuma) | Yok | Güvenli aday; çalıştırmadan önce hedef doğrulaması gerekir |
| `tests/test_phase7f_stimulus.py` | Yok | Yok | Yok | Güvenli aday (byte/hash kontrolleri) |
| `tests/test_phase7g_qc.py` | Yok | Yok (`copy.deepcopy` + saf `validate*` çağrıları; `AUDIT` yolları yalnız okuma) | Kısmi-risk: `ambiguous_dual_use` vb. valence string'leri deepcopy fixture'larda ve `record_*` çağrılarında kullanılır | Hedefli alt küme güvenli olabilir; bütün dosya tek komutta koşulmaz. `record_blind/record_context/record_decision` içeren testler yalnız okunan canlı dosyalar üzerinde değil, deepcopy fixture üzerinde çalışır — E0'da bu ayrım korunur |
| `tests/test_phase7g_tooling.py` | Yok (`_load` mock'lu; `compute_agreement_stats` sentetik matris ama rater semantiği taşımayan yapısal sayım) | Yok | Yok (4 satırlık matris, kör-rater üretimi değil) | Güvenli aday |
| `tests/test_phase8_dryrun.py` | Yok (mock dry-run) | Yok (çıktı geçici dizine) | Yok | Güvenli aday |
| `tests/test_pilot_dataset.py` | Yok | Yok | Yok | Güvenli aday |
| `tests/test_remediation_regressions.py` | Yok | Yok | Yok | Güvenli aday; çalıştırmadan önce hedef doğrulaması gerekir |
| `tests/test_schema_v02.py` | Yok | Yok | Yok | Güvenli aday |
| Rapor paketi `verify_contract.py` | Yok | Yok (OKU_BENI: gerçek dosyaya yazmaz) | **VAR — ÇALIŞTIRMA** (kaynak builder'dan geçici sentetik key + SYNTHETIC anotasyon, bellekte kalsa da AGENTS.md yasağına takılır) | E0'da çalıştırılmadı; açık insan talimatı olmadan yürütülmez |
| Rapor paketi `prospective_sensitivity.py` | Yok (NumPy+SciPy) | Yok (çıktıyı kendi dizinine yazar) | Yok (matematiksel senaryo) | E0'da çalıştırılmadı (üst plan §1 sınırı korunur; E6b kararı bekler) |

Hiçbir repo testi canlı ağ yapmaz; hiçbir repo testi gerçek audit/QC dosyasına yazmaz (statik incelemede
`write_text`/`append_history` çağrısı test dosyalarında yoktur; yazma yolları `tempfile`/bellek içindir).
Bu, çalıştırma garantisi değil, statik sınıflandırmadır.

## 2. Güvenle çalıştırılabilir hedefli komutlar (öneri; E0'da icra edilmedi)

Ortamda `pytest` yok (`logs/02-env.log`); önce salt okunur hedef doğrulaması, sonra `/tmp` çıktısı gerekir.
Her komut `mktemp -d` ile oluşturulan gerçek dizine yazar; `results/` altına yazılmaz.

```bash
TMPD=$(mktemp -d) && python3 -m pytest tests/test_dataset_validation.py -q -p no:cacheprovider 2>&1 | tee "$TMPD/test_dataset_validation.log"
TMPD=$(mktemp -d) && python3 -m pytest tests/test_phase7f_stimulus.py -q -p no:cacheprovider 2>&1 | tee "$TMPD/test_phase7f_stimulus.log"
TMPD=$(mktemp -d) && python3 -m pytest tests/test_phase7g_tooling.py -q -p no:cacheprovider 2>&1 | tee "$TMPD/test_phase7g_tooling.log"
TMPD=$(mktemp -d) && python3 scripts/validate_phase7g_review.py 2>&1 | tee "$TMPD/validate_phase7g_review.log"
```

`test_phase7g_qc.py` için dosyanın tamamı değil, yalnız yazmasız saf-doğrulama alt kümesi önerilir
(ör. `validate`/`validate_blind`/`evaluate_gate` yolları); `record_*` içeren testler E2a öncesi
ana inceleyici tarafından tek tek onaylanmalıdır.

## 3. Çalıştırılmaması gerekenler (E0'da çalıştırılmadı)

- `python verify_contract.py /path/to/combined/repository --output ...` — sentetik blind-label üretir;
  AGENTS.md §2 yasağı + E0 briefi §3 yasağı. Açık insan talimatı olmadan yürütülmez.
- Tam offline suite (`python -m pytest tests/`) — E0 briefi istemiyor; `pytest` kurulu değil;
  bağımlılık kurulumu/yükseltmesi E0 kapsamı dışında. Ağ/eksik bağımlılık engeli test başarısızlığı
  diye gizlenmez.
- `prospective_sensitivity.py` yeniden üretimi — bu turda rapor değerlendirmesidir; yeni sistematik
  hesap E6b'nindir.
- Gerçek audit/QC yazan her komut (`apply_phase7g_annotations.py` `blind/context/decide/adjudicate`
  modları `--dry-run` dışında), wizard CLI'ları, canlı Phase 8 koşuları, model/API çağrıları.

## 4. Ortam notu

`pytest` yokluğu bir test sonucu değildir. Bu E0 paketinde hedefli test çalıştırılmadı;
`commands.jsonl` içinde çalıştırılmayan komut yoktur. Yukarıdaki komutlar öneridir, icra kaydı değildir.
E0'ın çalıştırdığı gerçek komutlar yalnız read-only hash/sayaç/`rg`/`git diff --check`/bağlantı
kontrolleridir (`commands.jsonl`, `logs/`).
