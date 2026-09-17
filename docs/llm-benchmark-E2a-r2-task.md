# E2a-R2 — Phase completion kanıtı ve fixture temizliği

Durum: Hazır. Kök: `/home/kaan/AI_Search`. Yürütücü: E2a worker.  
Önkoşul: [E2a-R1 inceleme kararı](reviews/llm-benchmark/E2a-r1-acceptance.md).  
Ortak kurallar: [worker sözleşmesi](llm-benchmark-worker-contract.md).

## Tek paket hedefi

E2a-R1'de kalan iki blokajı kapat: Phase 7G completion'ı gerçek iki-rater dayanaklarına bağla ve
bu teslim zincirinde eklenen pozitif sentetik blind-rater fixture'larını kaldır. E2a-R1'in
context, KEEP, gate consistency ve atomicity düzeltmelerini koru.

## Zorunlu düzeltmeler

1. `phase_complete=true` doğrulamasında her blind item için tam kanıt-temelli iki-rater
   eligibility ara: iki dolu ve farklı kalıcı insan kimliği, iki rating, timestamp ve
   agreement veya tamamlanmış adjudication. Yalnız `annotation_status=ADJUDICATED` yeterli olmasın.
2. Phase completion kontrolü final karar türünden bağımsız olsun. KEEP, REVISE veya REJECT ile
   kapanan her item iki gerçek kör rater kapısından geçmiş olmalıdır.
3. `validate_blind` ve/veya phase-level validator, status ile slot/resolution kanıtı arasındaki
   tutarsızlığı fail-closed raporlasın. Ortak helper'ı kullan; paralel ve drift edebilecek ikinci
   eligibility mantığı yazma.
4. E2a/E2a-R1 zincirinde eklenen pozitif sentetik iki-rater kayıtlarını kaldır: sentetik
   reviewer ID + valence + timestamp ile eligible agreement/adjudication veya PASS sonucu
   üreten helper/test bulunmasın.
5. Negatif testleri yapısal ihlal vektörleriyle tut. Gerekiyorsa eligibility'nin alt
   bağımlılığını mock/stub ederek writer/validator/CLI kablolamasını sınayabilirsin; mock insan
   annotation payload'ı üretmemeli. Depoda önceden yetkili pozitif fixture yoksa gerçek pozitif
   E2E yolunu test etme ve açık kabul örneği olarak belgelemeye devam et.
6. Üretim QC/audit JSON'larına, insan rating'lerine, frozen belgelere ve stimulus metnine yazma.

## Zorunlu karşıörnek

Bellek içi yapısal state'te tüm blind item statusları `ADJUDICATED`, fakat slot kanıtları
boş/eksik; bütün QC kararları gerekçeli REJECT ve `phase_complete=true`. Validator en az bir
iki-rater/phase-completion hatası üretmelidir. Bu fixture'a valence, reviewer kimliği veya insan
anotasyonu ekleme.

Kabul ayrıca kaynak taramasında E2a zincirinin yeni testlerinde sentetik pozitif iki-rater
helper/kayıt kalmamasını, hedefli ve tam offline suite'in geçmesini, ret atomicity'sini ve
frozen/audit hashlerinin korunmasını gerektirir.

Teslimden sonra dur. Beklenen ana teslim: `docs/reviews/llm-benchmark/E2a-r2/README.md`.
