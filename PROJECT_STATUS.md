# Proje Durumu

**Güncel yetkili kayıt (2026-10-22): ARAŞTIRMA DONDURULDU; İNSAN GİRDİSİ BEKLENİYOR.**
[2026-09-10 dondurma kaydı](docs/reviews/llm-benchmark/PROJECT-FROZEN-2026-09-10.md)
ve [research preview sınırları](docs/research-preview-readiness.md) aşağıdaki tarihsel
açıklamalardan önce gelir. E1a/E1b/E1c teknik taslak kabulü bilimsel onay değildir;
aktif araştırma briefi yoktur. Phase 7G: rater_a 1/50, rater_b 0/50, KEEP 0/50;
Phase 8 kilitlidir. Tarihsel “hiçbir annotation yok” ifadeleri ilk rater girdisinden
önceki durumu anlatır; güncel sayılar bunların yerine geçer.


## Phase 7 özet durumu (yetkili tablo)

Bu tablo, aşağıdaki ayrıntılı bölümler arasında çelişki olması hâlinde geçerli olan tek yetkili kaynaktır.

| Faz | Durum | Not |
|---|---|---|
| Phase 7 (schema) | COMPLETE | `dataset/schema.json` 0.2.0 |
| Phase 7B | COMPLETE (exploratory) | Türkçe korpus; `EXPLORATORY_DRAFT_V0.1_TR` olarak korunuyor, primary pilot kapsamı dışında |
| Phase 7C / 7C-REVIEW | SUPERSEDED | Phase 7D yeniden tasarımıyla geçersiz kılındı |
| Phase 7D | COMPLETE | 50 research item tasarımı donduruldu |
| Phase 7E | COMPLETE | 50/50 KEEP · 50 researcher-approved · REVISE 0 · REJECT 0 · PENDING 0 |
| Phase 7F | COMPLETE | 50 research item · 171 koşul kaydı · İngilizce canonical final prompt'lar üretildi · yapısal/hash doğrulaması geçti |
| **Phase 7G** | **INCOMPLETE** | İnsan inceleme ve Workbench altyapısı COMPLETE · **iki bağımsız kör rater zorunlu (R2 kararı)** · rater_a 1/50 · rater_b 0/50 · ADJUDICATED 0/50 · PENDING 50 |
| **Phase 8** | **BLOCKED** | Kanonik Model Değerlendirmesi · Phase 7G tamamlanması ve GO/NO-GO gate bekleniyor (Bkz: `docs/ROADMAP.md`) |
| **Phase 9** | **PENDING** | Yanıt Skorlama & Etiketleme · 3 Kademeli Hibrit Skorlama Mimarisi (Kural + Model Yargıç + %20 İnsan Audit) |
| **Phase 10** | **PENDING** | Birincil İstatistiksel Analiz · Dondurulmuş SAP, Tabakalı Analiz (AM vs DU/NH) |
| **Phase 11** | **PENDING** | Sağlamlık ve Falsifikasyon · "Within-D Cohort" ($n=21$) güç izolasyonu, tekil madde duyarlılığı |
| **Phase 12** | **PENDING** | Çapraz Model Analizi · Bağlamsal kanıt işleme asimetrisi (meşru vs şüpheli) |
| **Phase 13** | **PENDING** | Uzman İncelemesi · Yalnızca dış geçerlilik ve sınırlılıklar; geriye dönük ground-truth değişimi yasak |
| **Phase 14** | **PENDING** | Nihai Araştırma Sentezi · Null sonuçlar dahil meşru bulgular; TR + EN yayın raporları |
| **Phase 15** | **PENDING** | Tekrarlanabilirlik & Çıkış Denetimi · Raw data -> Rapor zincirinin bağımsız doğrulanması |
| **Phase 16** | **PENDING** | Açık Kaynak Yayın · GitHub public release + Tehlikeli çıktılar için Responsible Redaction |

Ayrıntılı metodolojik şartname ve kısıtlar için bkz: [`docs/ROADMAP.md`](docs/ROADMAP.md).

Projede hâlâ **hiçbir** insan annotation'ı, uzman doğrulaması, ASR, refusal rate, latency ölçümü veya model/API değerlendirmesi bulunmamaktadır.

## Phase 6A durumu

Phase 6A smoke test altyapısı tamamlandı. 20 kayıtlık deterministik manifest, bounded retry, secret masking, model sürümü zorunluluğu, sağlayıcı preflight raporu ve gerçek/mock ayrımı eklendi. Bu ortamda `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `OPENWEIGHT_BASE_URL` veya gerekli Phase6A model/sürüm değişkenleri bulunmadığı için gerçek sağlayıcı çağrısı yapılmadı; OpenAI, Anthropic ve open-weight durumları `not_evaluated` olarak kaydedildi. Tam 300 kayıtlık evaluation çalıştırılmadı.

## Phase 6B durumu

XSTest, JBB-Behaviors ve WildGuardMix metadata düzeyinde incelendi. JBB `judge_comparison`–XSTest örtüşmesi, JBB behavior hedeflerinin jailbreak prompt olarak yorumlanamaması, WildGuard’ın gated/ODC-By koşulları ve native sample ID belirsizliği nedeniyle final public-benchmark manifesti oluşturulmadı. Audit raporları ve manifest approval gate’i hazırlandı; Phase 6B kullanıcı onayı bekliyor.

## Phase 7 durumu

Phase 7 schema audit onayından sonra `dataset/schema.json` `0.2.0` sürümüne genişletildi. Canonical final prompt, paired `final_prompt_only`/`full_context` koşulları, expected-vs-observed effect ayrımı ve authoring/QC provenance alanları için ilişkisel doğrulamalar eklendi. Geriye dönük v0.1.0 desteği korunuyor.

## Phase 7B durumu

50 özgün multi-turn kayıt deterministik construction pipeline ile oluşturuldu. Hedef hücre dağılımı 20/15/10/5, turn uzunluğu dağılımı 10/15/15/7/3 ve toplam turn sayısı 178 oldu. Dataset validation başarılı, duplicate sayısı 0. Bu kayıtların tamamı `llm_assisted_draft`, `researcher_qc=false` ve `external_validation_status=not_reviewed` olarak işaretlidir; insan araştırmacı QC’si ve model evaluation henüz yapılmadı.

## Phase 7C ve 7C-REVIEW durumu — SUPERSEDED

**Bu iki faz Phase 7D tarafından geçersiz kılınmıştır ve artık projenin güncel durumunu tanımlamaz.** Aşağıdaki kayıt tarihsel amaçlıdır.

Türkçe Phase 7B çıktısı silinmeden `EXPLORATORY_DRAFT_V0.1_TR` metadata etiketiyle korundu (bu hâlâ geçerlidir). İngilizce primary pilot için 50 satırlık bir design specification ve buna bağlı review tablosu oluşturulmuştu; tüm değerler `AI_PROPOSED` ve tüm satırlar `PENDING_RESEARCHER_INPUT` durumundaydı.

Bağımsız metodolojik hakem incelemesi bu tasarımda kritik bir kusur tespit etti: final prompt'lar, bağlamın sağlaması gereken risk/meşruiyet sinyalini kendileri taşıyordu. Bu nedenle Phase 7C tasarımı onaylanmak yerine **terk edildi** ve yerine Phase 7D matched-triplet/quadruplet tasarımı sıfırdan kuruldu. Phase 7C artefaktları depoda tarihsel kayıt olarak durmaktadır; primary pilot bunlara dayanmaz.

## Phase 7D durumu

Bağımsız metodolojik hakem incelemesi sonrası deney tasarımı sıfırdan yeniden kuruldu. Ana düzeltme: final prompt artık belirsizliğin merkezi olmak zorunda; risk/meşruiyet sinyalini final prompt'un kendisi taşıyamaz. Tasarım matched-triplet/quadruplet yapısına geçti: A=FINAL_PROMPT_ONLY, B=FULL_CONTEXT_LEGITIMATING, C=FULL_CONTEXT_INCRIMINATING, D=NEUTRAL_FILLER (uzunluk kontrolü). Final prompt tüm koşullarda byte-identical kalır. 50 research item metadata düzeyinde tanımlandı: 30 dual-use non-null, 7 persistent-ambiguity, 7 null-benign (taban kontrolü), 6 null-high-risk (tavan kontrolü). 21 item D koluna sahip. Analiz birimi research item'dır; A/B/C/D bağımsız örnek değildir. Hiçbir final prompt metni veya konuşma üretilmedi.

## Phase 7E durumu

Deney, stimulus üretiminden önce donduruldu. Pre-registration (`LLM-CTX-PILOT-2026-01`, v1.0.0), annotation protokolü ve istatistiksel karar kuralları yazıldı ve SHA-256 ile mühürlendi; composite protocol hash `results/dataset_audit/phase7e_preregistration_hash.json` içinde. Donan unsurlar: H1/H2/H3 ve H0a/H0b/H0c hipotezleri, F1–F6 falsifikasyon ölçütleri, 5 basamaklı ordinal disposition rubriği, Δ_AB/Δ_AC/Δ_BC/Δ_AD ölçütleri, dört durumlu D-kontrol yorumu, `context_effect_observed` eşiği ve gerekçesi, refusal-appropriateness referans etiketleri, ASR kapsamı, unscorable/missing/api_error kuralları, durdurma ve raporlama kuralları.

Phase 7D'nin üç hükmü Phase 7E'de düzeltildi: (1) `|Δ_AD| = 0` mutlak kapısı yerine negligible/partial/comparable/ambiguous D-durumları; (2) McNemar'ın dual-use ile null grupları arasında kullanımı hatalıydı — bunlar eşleşmiş değil bağımsız gruplar; Fisher exact'e taşındı; (3) Wilcoxon destekleyici analize indirildi, birincil sunum ordinal transition matrix oldu.

Bu bölümün yazıldığı anda 50 kaydın tamamı `review_decision=PENDING` durumundaydı; **bu durum artık geçerli değildir** — güncel sonuç için aşağıdaki “Phase 7E-EXECUTION sonucu” bölümüne bakınız. Hiçbir kayıt otomatik onaylanmadı ve reviewer kimliği hiçbir aşamada uydurulmadı.

Blind isolated-prompt review ve refusal-appropriateness referansları Phase 7E'de `NOT_STARTED` bırakıldı; bunlar Phase 7G kapsamındadır ve **hâlâ yapılmamıştır**. Model çağrısı, ASR, refusal rate veya latency hesabı yapılmadı. Türkçe exploratory dataset ve 300 kayıtlık public benchmark dataset'i byte düzeyinde değişmedi; bu durum test suite'inde SHA-256 ile doğrulanıyor.

## Phase 7E-EXECUTION altyapısı

Araştırmacı review'ünü kaydetmek için gereken altyapı kuruldu. Altyapı kurulduğu anda hiçbir karar verilmemişti; kararlar daha sonra araştırmacı tarafından sunuldu ve sonuç bir alt bölümde kayıtlıdır. Ajan hiçbir aşamada kendi yargısıyla KEEP/REVISE/REJECT üretmedi.

`scripts/apply_phase7e_decisions.py` yalnızca insan tarafından açıkça verilen kararları transkribe eder. Uyguladığı kurallar: reviewer kimliği zorunludur ve uydurulmaz; REVISE ve REJECT yazılı gerekçe olmadan reddedilir; notlar birebir saklanır, yeniden yazılmaz; anılmayan her kayıt PENDING kalır; halihazırda karara bağlanmış bir kaydın yeniden karara bağlanması sessizce üzerine yazılmak yerine çakışma olarak reddedilir; her yazımdan önce snapshot alınır; geçmiş `phase7e_review_history.jsonl` dosyasına yalnızca eklenir.

REVISE kararı version 1'i korur ve `revision_status=pending_revision` kaydı oluşturur; tasarımı otomatik yeniden yazmaz. REJECT kaydı silmez, gerekçe ve zaman damgasıyla saklar.

**Protokol manifest düzeltmesi (v1.0.0 -> v1.0.1):** v1.0.0, değişmesi gereken `phase7e_review.json` dosyasını donmuş protokol dosyaları arasına almıştı; bu haliyle ilk kararın kaydedilmesi freeze bütünlüğünü kıracaktı. Manifest artık bunun yerine değişmez `phase7e_design_snapshot.json` dosyasını kapsıyor. Dört protokol dokümanının SHA-256'sı v1.0.0 ile **byte düzeyinde aynı**; hiçbir hipotez, metrik, eşik, karar kuralı veya analiz yöntemi değişmedi. Düzeltme model değerlendirmesinden önce yapıldı ve `amendment` bloğunda önceki composite hash ile birlikte kayıtlı.

**Ön-değerlendirme açıklaması (v1.0.1 -> v1.0.2):** Denetim bulguları F-01 ve F-02 için araştırmacı kararlarıyla `docs/phase7e_pre_evaluation_clarification.md` dondurulmuş manifest'e eklendi: yapı, "bütün konuşma-bağlamı duyarlılığı" olarak netleştirildi (assistant-turn duruş katkısı bilinen bir yorumlama sınırlaması; assistant-turn-shared/differing raporlama strataları tanımlı; uyarıcılar byte düzeyinde değişmedi) ve §5'teki "user–user only" ifade düzeltildi (kastedilen developer/system kolunun olmaması; gerçekleşen yapı user–assistant–user(/user)). Hiçbir hipotez, metrik, eşik veya analiz kuralı değişmedi; dört özgün protokol dokümanı v1.0.0 baytlarına byte düzeyinde aynı.

## Phase 7E-EXECUTION sonucu

**Phase 7E COMPLETE.** Araştırmacı 50 kaydın tamamı için KEEP kararı verdi. Kararlar `apply_phase7e_decisions.py` ile kaydedildi: **KEEP=50, REVISE=0, REJECT=0, PENDING=0, researcher-approved=50.** Her karar `phase7e_review_history.jsonl` dosyasına append edildi ve yazımdan önce snapshot alındı. `reviewer_id` sağlanmadığı için null bırakıldı; `reviewer_role` olarak oturum içi self-review kaydedildi. Uydurulmuş kimlik yok.

## Phase 7F durumu — COMPLETE

50 araştırma kaydı için kontrollü İngilizce stimulus üretildi. Her kayıt tek bir canonical final prompt ve onun etrafında A/B/C (+ tasarımın belirttiği 21 kayıtta D) koşullarını içerir. Toplam 171 koşul örneği; **analiz birimi 171 değil 50 research item'dır**, A/B/C/D eşleşmiş tekrarlı koşullardır.

Final prompt her koşulda byte düzeyinde aynıdır — builder aynı string nesnesini enjekte eder, yani sapma yapısal olarak imkânsızdır. SHA-256 kaydedilir ve her koşulun son turundan yeniden türetilerek doğrulanır. Negatif kontrol testleri, tek boşluk eklendiğinde veya hash bozulduğunda validation'ın gerçekten kırıldığını gösteriyor.

Non-null 37 kaydın final prompt'u yasak liste altında yazıldı: yetki iddiası, lab/eğitim beyanı, gizleme/atlatma fiili, isimli hedef, kendini sınırlayan hedge yok. Yorum sinyali yalnızca B veya C bağlamında yaşar. Bunun başarılı olup olmadığı bu fazda **kanıtlanmadı** — metne dair bir hipotezdir ve Phase 7G'nin blind review'ü onu sınar.

Sonuçlar: structural error 0, safety flag 0, design leakage 0, overlap 0, generation flag 0. Bağlam koşulları arası tahmini token farkı ortalama 9.9, maksimum 33 (eşik 40). Turn sayısı sapması 0.

Tasarım-içerik çakışması: RI-DU-001 için D kolu taslaklanmıştı fakat onaylı `control_strategy` değeri `T`. Tasarım değil taslak geri çekildi ve bu karar dokümante edildi.

Tüm kayıtlar `researcher_qc=false`, `stimulus_review_status=PENDING`, `external_validation_status=not_reviewed`. `isolated_prompt_valence_observed`, `adjudicated_valence`, `refusal_appropriateness_reference` ve `model_observed_effect` null. Model çağrısı yok, blind review yok, ASR/refusal/latency hesabı yok. Pre-registration dokümanlarının SHA-256'sı değişmedi; Türkçe ve public benchmark dataset'leri byte düzeyinde aynı.

## Phase 7G durumu — INCOMPLETE

İnsan kalite kontrol enstrümanları kuruldu; **hiçbir inceleme yapılmadı**. 50 kaydın tamamı `PENDING`, `researcher_qc=false`, `stimulus_review_status=PENDING`. Araştırmacı annotation sunmadığı için ajan hiçbir valence, bağlam yargısı, güvenlik kararı veya review kararı üretmedi. Phase 7G tamamlanmadı.

**Körleme çakışması ve çözümü:** Faz brief §2 hakeme `research_item_id` gösterilmesine izin veriyor, ancak `RI-DU-`/`RI-AM-`/`RI-NB-`/`RI-NH-` önekleri §5'in gizlenmesini şart koştuğu kategoriyi doğrudan ele veriyor. Blind paket bu nedenle opak `BLIND-001`…`BLIND-050` kimlikleri ve deterministik karıştırma kullanıyor; eşleme `phase7g_blind_key.json` içinde mühürlü. Bu, Phase 7E'de zaten dondurulmuş annotation protokolü §2.2 ile birebir uyumludur. Blind paket kategori, beklenen etiket, tasarım alanı veya B/C/D bağlamı içermiyor; testler bunu doğruluyor.

**Kör sıralama araç tarafından zorlanıyor:** Bir kaydın izole prompt annotation'ı sunulmadan bağlam incelemesi kaydedilemiyor — araç reddediyor. KEEP kararı; context, safety ve naturalness incelemeleri tamamlanmadan, structural verification başarısızsa veya safety FAIL ise reddediliyor. REVISE version 1'i koruyup version 2 talebi açıyor ve prompt değişirse blind re-review zorunluluğunu kaydediyor. REJECT kaydı silmiyor.

**Uydurma istatistik koruması:** İki rater alanı mevcut; şu an 0 rater sunuldu, `inter_rater_status=not_available`, percent agreement ve Cohen's kappa `null`. Validator, status `not_available` iken herhangi bir uyum istatistiği görünürse hata veriyor. 50 örneklik pilot için kappa eşiği tanımlanmadı.

**Bağımsız yapısal yeniden doğrulama:** Canonical final prompt byte eşitliği ve SHA-256 uyumu 50/50 kayıtta yeniden doğrulandı, 0 başarısızlık. Bu otomatik kanıttır, insan onayı değildir ve hiçbir Phase 7G kapısını karşılamaz.

Model çağrısı yok, ASR/refusal/latency yok. Pre-registration, Phase 7D tasarımı ve Phase 7F stimulus v1 değişmedi; pre-review snapshot alındı.

## Proje

**LLM Security–Usability Benchmark**

## Durum

Erken aşama araştırma pilotu, Phase 7G insan kalite kontrol kapısında beklemektedir.

Phase 3 kapsamında güvenli ve redakte edilmiş 300 kayıtlık pilot dataset üretildi. Phase 7D–7F kapsamında bağlamsal risk yorumu pilotu için 50 research item tasarlandı, araştırmacı tarafından onaylandı ve kontrollü İngilizce stimulus'a (171 koşul kaydı) dönüştürüldü.

Henüz model değerlendirmesi, uzman anotasyonu, insan annotation'ı veya ölçülmüş sonuç bulunmuyor. Bir sonraki kapı Phase 7G insan QC'sidir; tamamlanmamıştır.

## Tamamlanan aşama

- **Phase 0 – Araştırma kapsamının tanımlanması:** Araştırma soruları, hipotez ve kapsam sınırları belgelendi.
- **Phase 1 – Tehdit taksonomisi:** İlk tehdit sınıflandırması ve sınıflandırma gerekçeleri belgelendi.
- **Phase 2 – Dataset şeması:** Ölçeklenebilir veri modeli, doğrulama kuralları ve testleri belgelendi.
- **Phase 3 – Pilot dataset construction:** 300 kayıtlı güvenli pilot dataset, deterministik üretim pipeline’ı ve kalite kontrolleri oluşturuldu.
- **Phase 4 – Annotation framework:** Çok boyutlu anotasyon yönergeleri, annotation schema, sentetik örnekler ve doğrulama testleri oluşturuldu.
- **Phase 5 – Benchmark framework:** Modüler loader, provider adapter’ları, runner, logging, latency, refusal detection, metrics ve mock dry-run oluşturuldu.
- **Phase 6A – Real-model smoke test hazırlığı:** 20 kayıtlık deterministik smoke manifesti, bounded retry, secret masking, model sürümü zorunluluğu, preflight raporu ve canlı çağrı kapısı oluşturuldu; mevcut ortamda provider çağrısı yapılmadı.
- **Phase 7 – Schema genişletmesi:** `dataset/schema.json` 0.2.0; canonical final prompt ve paired koşul doğrulamaları eklendi.
- **Phase 7B – Türkçe multi-turn korpus (exploratory):** 50 kayıt üretildi ve `EXPLORATORY_DRAFT_V0.1_TR` olarak korunuyor; primary pilot kapsamı dışındadır.
- **Phase 7D – Deney tasarımının yeniden kurulması:** Matched-triplet/quadruplet tasarım, final-prompt valence kontrolü ve 50 research item metadata düzeyinde tanımlandı.
- **Phase 7E – Pre-registration ve araştırmacı incelemesi:** Protokol donduruldu ve SHA-256 ile mühürlendi; araştırmacı 50/50 KEEP kararı verdi, 50 kayıt onaylandı.
- **Phase 7F – Kontrollü İngilizce stimulus üretimi:** 50 canonical final prompt ve 171 koşul kaydı (A/B/C ve 21 kayıtta D) üretildi; yapısal ve hash doğrulaması geçti, model değerlendirmesi yapılmadı.

## Devam eden aşama

- **Phase 7G – Blind isolated-prompt review + insan QC: INCOMPLETE.** İnceleme altyapısı (blind paket, mühürlü anahtar, kayıt araçları, adjudicate akışı, validator, testler) tamamlandı. İki-ratter zorunluluğu yürürlükte (R2 kararı): rater_a 1/50 (BLIND-001, kabul edilmiş), rater_b 0/50, ADJUDICATED 0/50, review kararları 0/50, `researcher_qc` 50/50 `false`.
- **Phase 8 – Gerçek model değerlendirmesi: NOT STARTED.** Model/API erişimi ve Phase 7G'nin tamamlanması bekleniyor.

## Oluşturulan dosyalar

- `PROJECT_STATUS.md`
- `docs/research_questions.md`
- `docs/threat_taxonomy.md`
- `dataset/schema.json`
- `docs/dataset_specification.md`
- `dataset/README.md`
- `dataset/validate.py`
- `tests/test_dataset_validation.py`
- `dataset/build_pilot.py`
- `dataset/pilot/README.md`
- `dataset/pilot/pilot_dataset.json`
- `dataset/pilot/records.jsonl`
- `dataset/pilot/attribution.json`
- `docs/pilot_sampling_plan.md`
- `tests/test_pilot_dataset.py`
- `docs/annotation_guidelines.md`
- `dataset/annotation_schema.json`
- `dataset/validate_annotations.py`
- `dataset/examples/synthetic_annotations.json`
- `tests/test_annotation_validation.py`
- `benchmark/__init__.py`
- `benchmark/types.py`
- `benchmark/errors.py`
- `benchmark/loader.py`
- `benchmark/latency.py`
- `benchmark/refusal.py`
- `benchmark/metrics.py`
- `benchmark/logging.py`
- `benchmark/metadata.py`
- `benchmark/runner.py`
- `benchmark/dry_run.py`
- `benchmark/adapters/base.py`
- `benchmark/adapters/mock.py`
- `benchmark/adapters/providers.py`
- `benchmark/adapters/__init__.py`
- `benchmark/README.md`
- `benchmark/runs/README.md`
- `benchmark/runs/.gitignore`
- `benchmark/runs/mock-dry-run/experiment_metadata.json`
- `benchmark/runs/mock-dry-run/responses.jsonl`
- `benchmark/runs/mock-dry-run/metrics.json`
- `docs/benchmark_framework.md`
- `tests/test_benchmark_framework.py`
- `benchmark/retry.py`
- `benchmark/smoke_test.py`
- `configs/phase6a_smoke.json`
- `tests/fixtures/phase6a_smoke_manifest.json`
- `tests/test_phase6a_smoke.py`
- `docs/phase6a_smoke_test.md`
- `docs/schema_changelog.md`
- `docs/phase7_schema_extension_proposal.md`
- `tests/test_schema_v02.py`
- `configs/phase7b_multiturn_construction.json`
- `scripts/build_multiturn_dataset.py`
- `dataset/pilot/multiturn/multiturn_dataset.json`
- `dataset/pilot/multiturn/records.jsonl`
- `dataset/pilot/multiturn/construction_plan_snapshot.json`
- `dataset/pilot/multiturn/README.md`
- `docs/multiturn_construction_methodology.md`
- `results/dataset_audit/multiturn_statistics.json`
- `results/dataset_audit/multiturn_validation.json`
- `results/dataset_audit/multiturn_construction_report.json`
- `tests/test_multiturn_construction.py`
- `scripts/build_researcher_design.py`
- `scripts/validate_multiturn_design.py`
- `dataset/pilot/multiturn/design_specification.json`
- `dataset/pilot/multiturn/EXPLORATORY_DRAFT_V0.1_TR.json`
- `docs/multiturn_researcher_design.md`
- `results/dataset_audit/multiturn_design_validation.json`
- `tests/test_multiturn_design.py`
- `scripts/build_multiturn_researcher_review.py`
- `scripts/validate_multiturn_researcher_review.py`
- `docs/multiturn_researcher_review.md`
- `results/dataset_audit/multiturn_researcher_review.json`
- `tests/test_multiturn_researcher_review.py`
- `results/README.md`
- `docs/PHASE_7D_EXPERIMENTAL_DESIGN.md`
- `docs/PHASE_7D_DESIGN_TABLE.md`
- `docs/phase7e_researcher_review.md`
- `docs/phase7e_preregistration.md`
- `docs/phase7e_annotation_protocol.md`
- `scripts/build_phase7e_review.py`
- `scripts/validate_phase7e_review.py`
- `scripts/freeze_phase7e_preregistration.py`
- `results/dataset_audit/phase7e_review.json`
- `results/dataset_audit/phase7e_preregistration_hash.json`
- `tests/test_phase7e_review.py`
- `scripts/apply_phase7e_decisions.py`
- `results/dataset_audit/phase7e_review_history.jsonl`
- `results/dataset_audit/phase7e_design_snapshot.json`
- `results/dataset_audit/snapshots/phase7e_review.v1.pre_execution.json`
- `dataset/pilot/multiturn/stimulus_content_du.py`
- `dataset/pilot/multiturn/stimulus_content_ctl.py`
- `dataset/pilot/multiturn/stimulus_dataset_v1.json`
- `dataset/pilot/multiturn/stimulus_records.jsonl`
- `dataset/pilot/multiturn/STIMULUS_README.md`
- `scripts/build_stimulus_dataset.py`
- `docs/phase7f_stimulus_generation.md`
- `results/dataset_audit/stimulus_statistics.json`
- `results/dataset_audit/stimulus_validation.json`
- `results/dataset_audit/stimulus_overlap_report.json`
- `results/dataset_audit/stimulus_safety_scan.json`
- `results/dataset_audit/stimulus_generation_report.json`
- `tests/test_phase7f_stimulus.py`
- `docs/phase7g_human_qc.md`
- `scripts/build_phase7g_review.py`
- `scripts/apply_phase7g_annotations.py`
- `scripts/validate_phase7g_review.py`
- `results/dataset_audit/phase7g_blind_review.json`
- `results/dataset_audit/phase7g_blind_key.json`
- `results/dataset_audit/phase7g_human_qc.json`
- `results/dataset_audit/phase7g_review_history.jsonl`
- `results/dataset_audit/phase7g_quality_summary.json`
- `results/dataset_audit/snapshots/phase7f_stimulus.v1.pre_qc.json`
- `tests/test_phase7g_qc.py`
- `.gitignore`

## Henüz yapılmayanlar

- Tam 300 kayıtlık evaluation ve bilimsel sonuç analizi yapılmadı.
- Savunma prototipi uygulanmadı.
- Model değerlendirmesi, uzman anotasyonu ve sonuç üretimi yapılmadı.
- Gerçek anotasyon veya uzman incelemesi yapılmadı; sentetik örnekler gerçek veri kümesinden ayrıdır.
- Gerçek provider evaluation çalıştırılmadı; Phase 6A preflight sonucunda OpenAI, Anthropic ve open-weight provider’ları eksik ortam değişkenleri nedeniyle `not_evaluated` olarak raporlandı. Mock dry-run ve unit testler çalıştırıldı.
- Phase 7B Türkçe korpusu için researcher QC, expert annotation ve model evaluation yapılmadı; bu korpus exploratory olarak korunmakta ve primary pilot kapsamı dışındadır.
- **Phase 7G INCOMPLETE:** 50/50 kayıt PENDING. Blind isolated-prompt annotation (rater_a 1/50, rater_b 0/50 — iki bağımsız kör rater zorunlu), bağlam incelemesi, insan güvenlik incelemesi, naturalness incelemesi ve review kararları araştırmacıdan bekleniyor. Hiçbir kayıt `researcher_qc=true` değildir.
- **Phase 8 NOT STARTED:** Model/API erişimi yok; ASR, refusal rate, latency ve model karşılaştırması hesaplanmadı.
- Stimulus metinleri insan tarafından incelenmedi; non-null prompt'ların gerçekten belirsiz olduğu doğrulanmadı.
- Harici public benchmark overlap denetimi hâlâ `preliminary_blocked`.

## Kritik not

Pilot kayıtları ve Phase 7F stimulus'ları güvenli, redakte edilmiş ve araştırma üretimi olarak oluşturulmuştur; **model sonucu, ASR, refusal rate, latency, insan annotation'ı veya uzman doğrulaması iddiası içermez.**

Phase 7F stimulus metinleri AI destekli taslaktır ve insan tarafından incelenmemiştir. Non-null final prompt'ların izole hâlde gerçekten belirsiz olduğu **doğrulanmamıştır**; bu bir yazım niyetidir ve Phase 7G'nin blind review'ü tarafından sınanacaktır. Kayıtların bu kapıdan düşmesi mümkündür ve yüksek düşüş oranı, dondurulmuş pre-registration'daki F6 falsifikasyon ölçütü uyarınca bilimsel bir bulgudur.

Phase 7G'ye ve ardından model değerlendirmesine geçiş için araştırmacı onayı beklenmektedir.
