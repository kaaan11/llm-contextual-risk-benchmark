# Phase 7B — Özgün multi-turn construction metodolojisi

## 1. Amaç ve sınır

Phase 7B, “Konuşma bağlamı teknik olarak hassas veya potansiyel olarak adversarial bir final prompt’un risk yorumunu maddi olarak değiştirir mi?” sorusunu daha sonra iki koşulla incelemek üzere 50 özgün konuşma oluşturur:

1. `final_prompt_only`
2. `full_context`

Bu aşamada model çağrısı, benchmark evaluation, ASR, refusal rate, latency ölçümü veya expert annotation yapılmaz.

## 2. Construction planı

Üretimden önce [phase7b_multiturn_construction.json](<C:/Users/Kaan/Documents/ChatGPT/AI_Search/configs/phase7b_multiturn_construction.json>) oluşturuldu. Plan; hedef hücreyi, contextual mechanism’i, beklenen risk profilini, confidence’ı, domain’i, turn sayısını ve final prompt’u içerir.

Hedef hücreler:

| Hedef | Sayı | Araştırma amacı |
|---|---:|---|
| `context_changes_interpretation` | 20 | Bağlamın meşruiyet veya risk yorumunu değiştirdiği durumlar |
| `context_has_no_material_effect` | 15 | Bağlamın ek kanıt sağlamadığı null/no-effect durumları |
| `legitimate_technical_context` | 10 | Teknik olarak sofistike fakat meşru görevlerde over-refusal riskini inceleme |
| `ambiguous_or_borderline` | 5 | Bilginin yetersiz kaldığı ve kesin ground truth iddiası taşımayan durumlar |

Hedef turn dağılımı 2/3/4/5/6 turn için sırasıyla 10/15/15/7/3’tür. Her ek turn, intent, environment, authorization, risk escalation veya ambiguity hakkında bilgi sağlamak için kullanılmıştır; filler turn eklenmemiştir.

### Category ve expected context effect ayrımı

`category`, araştırma tasarım hücresidir: `context_changes_interpretation`, `context_has_no_material_effect`, `legitimate_technical_context` veya `ambiguous_or_borderline`.

`expected_context_effect` ise bağlamın final prompt yorumuna ilişkin tasarım beklentisidir: `context_increases_legitimacy`, `context_increases_risk`, `context_reduces_ambiguity`, `context_increases_ambiguity`, `context_has_no_material_effect` veya `context_is_irrelevant`.

Bu iki alan aynı eksen değildir ve aynı dağılımı vermek zorunda değildir. Mevcut İngilizce design önerisinde category dağılımı 20/15/10/5; expected effect dağılımı ise sırasıyla `context_increases_legitimacy=18`, `context_increases_risk=7`, `context_reduces_ambiguity=7`, `context_has_no_material_effect=10`, `context_is_irrelevant=5` ve `context_increases_ambiguity=3` şeklindedir. Bunların tamamı researcher approval bekleyen AI-proposed değerlerdir.

## 3. Authoring ve provenance

Bu construction çalışmasındaki metinler bu oturumda LLM-assisted draft olarak oluşturulmuştur. Bu nedenle her record:

- `authoring_method=llm_assisted_draft`
- `generation_assistance=drafting_only`
- `source=original`
- `source_seed=null`
- `researcher_qc=false`
- `external_validation_status=not_reviewed`

değerlerini taşır. Public benchmark prompt’ları kopyalanmamış ve public source seed kullanılmamıştır. `researcher_qc=true` veya `researcher_reviewed` değeri insan araştırmacı incelemesi olmadan yazılmamıştır.

## 4. Canonical prompt sözleşmesi

Pipeline final user mesajını tek kaynaktan `canonical_final_prompt` olarak alır ve şunları otomatik üretir:

- UTF-8 SHA-256 hash.
- `final_prompt_only.prompt` kopyası.
- Full-context son user turn’ü.
- `full_context.turn_ids` sıralı listesi.

Validator exact string equality kullanır. Trim, case-fold veya Unicode normalization uygulanmaz. Böylece iki evaluation koşulunun final prompt’u gerçekten aynıdır.

## 5. Güvenlik sınırları

Metinler yüksek seviyeli ve güvenli tutulmuştur. Kayıtlarda gerçek credential, kişisel veri, özel altyapı, gerçek hedef, deploy edilebilir malware, persistence, credential theft, exploitation procedure, evasion payload veya yıkıcı komut bulunmamalıdır. Pipeline ayrıca kod bloklarını, bariz secret biçimlerini, e-posta adreslerini ve bazı operasyonel payload kalıplarını reddeden bir safety scan çalıştırır.

Bu filtreler insan güvenlik incelemesinin yerine geçmez; yalnızca construction öncesi otomatik bir bariyerdir.

## 6. Validation ve çıktılar

Pipeline şunları doğrular:

- 50 candidate plan kaydı ve hedef dağılımları.
- Unique `sample_id` ve `conversation_id`.
- Turn role ve ardışık sequence.
- Canonical prompt, final-prompt-only ve full-context eşitliği.
- Canonical SHA-256.
- Controlled vocabulary alanları.
- `dataset_version=0.2.0` ile root sürüm eşitliği.
- `model_observed_effect=null`.
- `researcher_qc=false` ve `external_validation_status=not_reviewed`.
- Source/original ve `source_seed=null` tutarlılığı.
- PII ve operasyonel içerik için temel safety scan.

Üretilen audit dosyaları:

- [multiturn_statistics.json](<C:/Users/Kaan/Documents/ChatGPT/AI_Search/results/dataset_audit/multiturn_statistics.json>)
- [multiturn_validation.json](<C:/Users/Kaan/Documents/ChatGPT/AI_Search/results/dataset_audit/multiturn_validation.json>)
- [multiturn_construction_report.json](<C:/Users/Kaan/Documents/ChatGPT/AI_Search/results/dataset_audit/multiturn_construction_report.json>)

## 7. Araştırmacı QC kapısı ve metodolojik sınırlama

Otomatik validation “şema ve construction ilişkileri geçerli” demektir; insan review veya expert validation demek değildir. Bu çalıştırmada 50/50 kayıt `researcher_qc=false` olarak bırakılmıştır. Beklenen context effect tasarım hipotezidir, ground truth değildir; model sonucu ile üzerine yazılmamalıdır.

Bir sonraki adım araştırmacının 50 kaydı tek tek inceleyip gerekirse düzeltmesi, QC kararını açıkça kaydetmesi ve bundan sonra ayrı onayla küçük kontrollü model evaluation planlamasıdır. Bu pipeline otomatik olarak evaluation’a geçmez.
