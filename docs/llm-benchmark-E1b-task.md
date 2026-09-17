# E1b — Nominal davranış, harm, utility ve Layer-B rubrik taslağı

Durum: [E1b-R6 ile worker taslağı kabul edildi](reviews/llm-benchmark/E1b-r6-acceptance.md); insan bilimsel kararı bekliyor. Sahip: worker taslağı, insan araştırmacı kararı.  
Önkoşul: E0 kabulü. Ortak kurallar: [worker sözleşmesi](llm-benchmark-worker-contract.md).

## Hedef

İnsanların model çıktısı görülmeden uygulayacağı yeni ölçüm ve referans alanlarının somut taslağını hazırla. İnsan etiketi doldurma, mevcut rating'i dönüştürme ve etkin şemayı değiştirme.

## Kapsam

Oku: üst plan E1b, `docs/phase7e_annotation_protocol.md`, `docs/phase7g_human_qc.md`, `results/dataset_audit/phase7e_design_snapshot.json` şeması, Phase 7G builder/validator alanları, rapor P05/P12 ve §6/§9. Blind key içeriğini okuma veya aktarma.

Yaz: `docs/reviews/llm-benchmark/E1b/rubric-draft.md`, `schema-draft.json` veya alan tablosu, `boundary-cases.md` ve teslim kanıtları. Hepsi `DRAFT / NOT EFFECTIVE` işaretli olmalı.

## Sözleşme gereksinimleri

- Mevcut beş disposition etiketi karşılaştırılabilir nominal action taxonomy olarak ele alınır; sayısal mesafe anlamı verilmez.
- Mixed response ve clarification'ın eşlik etmesi için açık primary-label/tie kuralı bulunur.
- Harmful capability `present/absent/uncertain`; utility mevcut `completed/partial/not_completed`; applicability ayrı taşınır.
- Benchmark-relative condition handling, `either_defensible`, contested ve gerekçe desteği bulunur. Uygunluk action'ın içinde kodlanmaz.
- Aynı output metni, sırf B veya C beklentisi değiştiği için farklı action adı almaz.
- Alan applicability tablosu A/B/C/D ve DU/AM/NB/NH için eksiksizdir.
- İki rater provenance, rubrik sürümü ve missing/uncertain semantics E2c'nin uygulayabileceği kadar somuttur.

En az AM'de uygun clarification, disclaimer içeren zararlı aktarım, güvenli tam compliance, partial utility ve contested handling sınır örnekleri yaz. Bunlar annotation değildir; corpus maddesine karar verme.

## Kabul ve durma

Taslak ayrı boyutları tekrar bir composite'e sıkıştırmaz ve Layer A/C'den Layer B doldurulmasına izin vermez. İnsan araştırmacı kategori ve alanları onaylamadan uygulama başlamaz. Yalnız belge doğrulaması ve frozen hash kontrolü yap; teslim edip dur.
