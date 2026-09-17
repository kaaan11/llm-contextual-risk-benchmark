# E2a — Ana inceleyici kararı

Tarih: 2026-09-10. İnceleyici: Sol. Durum: **REVISION REQUIRED. E2a KABUL EDİLMEDİ.**

## Doğrulanan düzeltmeler

[E2a briefi](../../llm-benchmark-E2a-task.md), kod farkı, testler ve kanıt paketi incelendi.
Teslim önemli iki ana davranışı eklemiştir:

- `record_context`, PENDING/PARTIAL/unresolved durumlarda context açılmasını reddeder.
- Blind `gate_result=FAIL`, KEEP writer'ında ve onaylı kayıt validator'ında reddedilir; karar
  CLI'ı KEEP teklifini kapatır.
- Ret edilen batch işlemleri için bellek-içi geri alma eklenmiş ve hedefli mutation testleri
  yazılmıştır.
- CLI context listesi kırık mappingleri fail-closed biçimde atlar; validator'ın ayrıca
  işaretlemesi amaçlanmıştır.

Worker'ın 132 hedefli ve 372 tam-suite sonucu bağımsız tekrarlandı; ikisi de geçti. Sekiz komut
kaydı, log hedefleri, `run-outputs.sha256`, bağlantılar ve `git diff --check` doğrulandı.
Stimulus ile frozen artefaktlar değişmedi; audit geçmişleri 51 ve 5 satırla aynı hashlerde kaldı.

## Bloklayıcı eksikler

### R1 — KEEP kapısı kanıt yerine yalnız status alanına güveniyor

`record_decision`, `validate()` ve `keep_eligibility` yalnız `blind_status` ile `gate_result`
alıyor; `blind_item_eligible_for_context` içindeki iki slot, provenance, agreement/adjudication
kontrolünü çağırmıyor. Bellek-içi karşıörnekte iki rater slotu tamamen boşken yalnız
`annotation_status=ADJUDICATED` ve `gate_result=PASS` verilerek writer KEEP kaydetti ve validator
hiç hata üretmedi. Bu, planın “status alanına güvenmek yerine gerekli dayanakları doğrula” kabulünü
ihlal eder.

### R2 — Farklı insan kimliği doğrulanmıyor

`_slot_proven`, `reviewer_id` yerine yalnız ortak bir `reviewer_role` bulunmasını yeterli sayar ve
iki slotun kimliklerini karşılaştırmaz. Bellek-içi karşıörnekte iki slotta aynı `reviewer_id`
bulunmasına rağmen `blind_item_eligible_for_context` `True` döndürdü. Kayıt API'sinin yeni veri
yazarken aynı ID'yi reddetmesi, yüklenmiş veya bozulmuş durumu güvenli yapmaz. Context, KEEP ve
validator sınırları iki dolu, birbirinden farklı kalıcı insan kimliği görmelidir; rol adı tek
başına kimlik değildir.

### R3 — Validator, PARTIAL/unresolved durumda açılmış context'i yakalamıyor

Validator'ın blind-ordering bölümü yalnız status `PENDING` iken context kaydını hata sayıyor.
Canlı PARTIAL_ONE_RATER kaydının bellek-içi kopyasında `context_review.status=COMPLETE` yapıldığında
validator blind-ordering hatası üretmedi. Writer artık bu durumu oluşturmasa da diskten yüklenen
eski/bozuk state fail-closed doğrulanmalıdır. Context `NOT_STARTED` değilse tam
`blind_item_eligible_for_context` kanıtı aranmalıdır.

### R4 — Eksik veya tutarsız gate sonucu KEEP'i engellemiyor

`blind_keep_blockers`, ADJUDICATED kayıtta `gate_result=None` veya bilinmeyen bir değer için
blocker üretmez. Validator yalnız gate sonucu adjudication'dan önce yazılmışsa hata verir;
adjudicated valence sonrası gate'in mevcut, izinli ve kategoriye göre yeniden hesaplanan sonuçla
tutarlı olduğunu doğrulamaz. KEEP için gate sonucu `{PASS, REVIEW}` olmalı; FAIL, eksik, bilinmeyen
ve türetilen sonuçla uyuşmayan değerler fail-closed reddedilmelidir.

## Karar ve devam

Mevcut testlerin geçmesi bu karşıörnekleri kapsamamalarından kaynaklanıyor; ana kapı henüz
status-forgery ve yüklenmiş bozuk state'e karşı fail-closed değildir. Ham E2a teslimi korunacaktır.
[E2a-R1 briefi](../../llm-benchmark-E2a-r1-task.md) yalnız R1–R4 düzeltmeleriyle sınırlıdır.
