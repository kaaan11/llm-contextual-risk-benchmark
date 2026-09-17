# E2a-R1 — Kanıt-temelli iki-rater ve gate doğrulaması

Durum: Hazır. Kök: `/home/kaan/AI_Search`. Yürütücü: E2a worker.  
Önkoşul: [E2a inceleme kararı](reviews/llm-benchmark/E2a-acceptance.md).  
Ortak kurallar: [worker sözleşmesi](llm-benchmark-worker-contract.md).

## Tek paket hedefi

E2a kapılarını status alanından bağımsız, gerçek kayıt dayanaklarını doğrulayan tek ortak sınıra
bağla. Context writer/list, KEEP writer/CLI ve validator aynı iki-rater, resolution ve gate
kanıtını kullansın. E2b/E2c rubriğini veya üretim annotation verisini değiştirme.

## Zorunlu düzeltmeler

1. Ortak eligibility girdisi yalnız status/gate ikilisi olmasın; ilgili blind item ve category
   mappingi üzerinden iki rater slotunu, provenance'ı, agreement/adjudication akışını ve gate
   tutarlılığını doğrulasın.
2. İki slotta da dolu, kalıcı bir insan kimliği iste ve kimliklerin farklı olduğunu doğrula.
   Ortak/generic `reviewer_role` tek başına iki farklı insan kanıtı değildir. Mevcut üretim
   verisine kimlik veya annotation uydurma; eksik kayıt fail-closed kalsın.
3. `record_context`, context CLI listesi, `record_decision(KEEP)`, karar CLI'ı ve validator aynı
   ortak eligibility sonucunu kullansın. Yalnız `annotation_status=ADJUDICATED` hiçbirinde yeterli
   olmasın.
4. Validator, context review `NOT_STARTED` dışındaysa blind item'ın tam context eligibility
   kanıtını arasın. PARTIAL, unresolved, eksik slot/provenance ve aynı kimlik durumlarını diskten
   yüklenmiş state'te hata olarak raporlasın.
5. Adjudicated kayıtta `gate_result` ve `gate_flag` değerlerini `adjudicated_valence` + key category
   üzerinden `evaluate_gate` ile yeniden doğrula. KEEP yalnız tutarlı `PASS` veya `REVIEW` için
   mümkün olsun; `FAIL`, eksik, bilinmeyen veya uyuşmayan gate fail-closed reddedilsin.
6. Ret yolundaki nesne/dosya/snapshot/history mutation-yok garantisini ve mevcut FAIL→KEEP
   yasağını koru.

## Zorunlu karşıörnek testleri

- Boş rater slotları + elle `ADJUDICATED/PASS` statusu: context ve KEEP writer reddeder; validator
  hata verir; CLI uygun göstermez.
- Aynı `reviewer_id` iki slotta: context/KEEP/validator reddeder.
- PARTIAL veya unresolved blind kayıt + önceden `context_review=COMPLETE`: validator hata verir.
- Geçerli-looking iki slot + eksik, bilinmeyen veya category/valence ile uyuşmayan gate sonucu:
  KEEP reddedilir ve validator hata verir.
- Reddedilen batch çağrısı önceki mutationları tamamen geri alır.

Testlerde gerçek insan adına annotation, valence veya pozitif iki-rater kaydı uydurma. Negatif
yapısal ihlal vektörleri kullan; gerçek pozitif geçiş insan girdisi gelene kadar açık kabul örneği
olarak kalabilir. Üretim QC/audit JSON'larına yazma ve append-only geçmişi değiştirme.

Teslimden sonra dur. Beklenen ana teslim: `docs/reviews/llm-benchmark/E2a-r1/README.md`.
