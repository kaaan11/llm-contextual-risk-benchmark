# E3b — Onaylı stimulus kararı ve sürümleme

Durum: **KİLİTLİ / KOŞULLU**. Sahip: insan kararı sonrası worker.  
Önkoşul: E3a kabulü, madde bazlı insan `KEEP/REVISE/REJECT` kararı, açık yazma yetkisi ve resmi protokol eki. Ortak kurallar: [worker sözleşmesi](llm-benchmark-worker-contract.md).

## Başlama kapısı

Briefi alan worker önce somut insan karar kaydını ve izin verilen dosya listesini doğrular. Bunlar yoksa hiçbir stimulus metni üretmeden `BLOCKED: HUMAN DECISION REQUIRED` raporuyla durur. Plan veya E3a önerisi yazma yetkisi değildir.

## Koşullu hedef

Yalnız onaylanan maddeler için v1'i koruyan yeni stimulus sürümünü, kaynak bağı ve yeniden-QC kapsamını uygula. REJECT kararı metin silme yetkisi vermez; kabul manifestosundan dışlama olarak ele alınır. Final prompt değişirse yeni kör inceleme zorunluluğunu manifestoya koy.

## Kabul

- V1 ve dört mühürlü artefakt bayt olarak değişmez; eski audit geçmişi korunur.
- Her fark insan karar ID'si, revision nedeni, önceki/yeni hash ve etkilenen koşullarla bağlıdır.
- Yeni sürümde item içi final prompt byte equality, şema, tur yapısı ve güvenlik kontrolleri geçer.
- Yetkili aralık dışı metin değişmez; toplu rewrite veya LLM ile serbest yeniden yazım yapılmaz.
- Yeni sürüm Phase 7G tamamlandı diye işaretlenmez; yalnız yeniden-QC girdisi olur.

Teslim kapsamı insan kararında ayrıca belirtilir. Worker E4'ü veya canlı evaluation'ı başlatmadan durur.

