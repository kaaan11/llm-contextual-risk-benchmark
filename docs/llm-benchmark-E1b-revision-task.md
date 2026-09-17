# E1b-R1 — Layer-B rubrik sözleşmesi düzeltmesi

Durum: Hazır. Kök: `/home/kaan/AI_Search`. Yürütücü: E1b worker.  
Önkoşul: [E1b revision kararı](reviews/llm-benchmark/E1b-acceptance.md).  
Ortak kurallar: [worker sözleşmesi](llm-benchmark-worker-contract.md).

## Tek paket hedefi

E1b teslimindeki R1–R5 blokajlarını kapatıp E2c'nin uygulayabileceği tutarlı bir Layer-B record ve rubric sözleşmesi üret. Kabul edilmiş nominal taxonomy, output-merkezlilik, ayrı harm/utility, no-composite, abstract boundary-case ve `DRAFT / NOT EFFECTIVE` sınırlarını koru.

## Değişiklik kapsamı

Worker'ın mevcut E1b kanıtını üzerine yazma. Yeni teslim dizini `docs/reviews/llm-benchmark/E1b-r1/` olsun. Düzeltilmiş `rubric-draft.md`, `schema-draft.json`, yalnız etkilenen boundary cases ve `revision-map.md` üret. Üretim kodu, frozen belgeler, stimulus, audit/QC ve insan rating'leri değişmez.

## Zorunlu düzeltmeler

1. **Condition criterion:** Layer-B condition reference içinde stable criterion ID, izin verilen yardım, sınırlandırılacak harmful capability ve clarification'ın ne zaman yeterli olduğu açık alanlarla tanımlansın. F3 referansı var olan schema alanına çözülsün. Eksik criterion skor üretmesin.
2. **İki-rater envelope:** Her condition için `rater_a` ve `rater_b` ham referans kayıtları; stable farklı reviewer ID, rol, timestamp, session, rubric version ve maruziyet beyanı; agreement/disagreement ve ayrı adjudication nesnesi tanımlansın. Rol kimlik yerine geçmesin. Ham kayıtlar overwrite edilmesin.
3. **Normatif durumlar:** `either_defensible`, `contested` ve inter-rater disagreement birbirinden ayrıştırılsın. Tek rater anlaşmazlığı otomatik contested üretmesin. Atama aşaması/sahibi ve analysis denominator davranışı insan kararı gerektiren seçenek olarak işaretlensin.
4. **Scoreability:** Explicit `scoreable/unscorable_content` görüşü confidence'dan ayrı olsun. İki düşük confidence otomatik unscorable olmasın; frozen iki-rater/adjudication kuralı korunsun.
5. **Operational outcome sınırı:** F1–F4 yalnız skorlanabilir response için tanımlansın. `api_error`, timeout, filter, truncation, not_run ve missing E5c outcome sözleşmesine devredilsin; E1b bunları birbirine dönüştürmesin.
6. JSON `requires` kuralları koşullu alanları doğru anlatsın: örneğin inapplicability reason yalnız `not_applicable` için gerekir. Schema örnek veri veya insan etiketi içermesin.

## Kabul örnekleri

- F3 criterion ref, şemadaki aynı condition criterion ID'sine çözülür; eksik/dangling ref reddedilir.
- Aynı reviewer ID iki slotta reddedilir; farklı rol fakat aynı ID kabul edilmez. İki ham görüş adjudication sonrası da korunur.
- `allow_with_safeguards` ve `decline` rater ayrılığı workflow disagreement olur; kendiliğinden `contested` olmaz.
- İki low-confidence rating kendi başına `unscorable_content` üretmez; iki explicit unscorable görüş ayrı durumdur.
- Timeout/error taşıyan outcome için F1–F4 alanları yasaktır; response missing nedeni korunur.
- Aynı output B/C'de aynı F1'i alır; harm, utility ve handling yine ayrı kalır.

## Doğrulama ve teslim

JSON parse, alan/ref bütünlüğü, enum ayrıklığı, applicability matrisi ve yasak durumlar için rater etiketi üretmeyen yapısal kontroller çalıştır. `commands.jsonl`, checksum, link, frozen hash ve audit prefix kanıtlarını E1b-r1 dizininde bırak. İnsan karar seçeneklerini `APPROVED` yapma. Teslimden sonra dur ve yeniden inceleme bekle.

