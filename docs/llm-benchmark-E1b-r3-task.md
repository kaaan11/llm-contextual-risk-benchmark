# E1b-R3 — Layer-B/Layer-C zarf ayrımı

Durum: Hazır. Kök: `/home/kaan/AI_Search`. Yürütücü: E1b worker.  
Önkoşul: [E1b-R2 inceleme kararı](reviews/llm-benchmark/E1b-r2-acceptance.md).  
Ortak kurallar: [worker sözleşmesi](llm-benchmark-worker-contract.md).

## Tek paket hedefi

E1b-R2'de kalan iki yerleşim hatasını düzelt: response scoreability'yi post-evaluation Layer-C
zarfına taşı ve researcher-only `contested` statüsünü condition-reference köküne geri koy. R2'nin
resolved criterion ve frozen §6.2 düzeltmelerini aynen koru; başka alanları yeniden tasarlama.

## Teslim kapsamı

Yeni teslim dizini `docs/reviews/llm-benchmark/E1b-r3/` olsun. Düzeltilmiş rubrik, şema, yalnız
etkilenen sınır örnekleri, revision map ve standart kanıt paketini üret. Önceki teslimler, üretim
kodu, mühürlü belgeler, stimulus, audit/QC ve insan rating'leri değişmez.

## Zorunlu düzeltmeler

1. Layer-B/pre-evaluation F5 rater slotlarından `scoreable_view` ve `unscorable_reason` çıkar.
   Condition handling, criterion önerisi, context reading ve Layer-B provenance burada kalır.
2. F1–F4 response değerlendirmesi için ayrı Layer-C/post-evaluation iki-rater zarfı tanımla.
   Her ham slot stable farklı reviewer ID, rol, timestamp, session, rubric version, response
   exposure/provenance, F1–F4 görüşleri, gerekçeler, confidence ve explicit `scoreable_view`
   taşısın. Ham slotlar adjudication ile overwrite edilmesin.
3. Frozen §6.2 geçişini Layer-C zarfında uygula: iki explicit unscorable doğrudan final; tek
   taraflı unscorable disagreement/adjudication; low confidence tek başına unscorable üretmez.
   Non-scoreable operational outcome varsa bu response-rating zarfı oluşturulmasın.
4. F3'ün resolved criterion ID/version bağı ve resolved-reference provenance akışı aynen kalsın.
5. `contested` alanını F5 condition-reference kökünde resolved reference'tan bağımsız tut.
   Researcher-only olsun; handling enum'larına girmesin ve disagreement'tan türemesin.
6. Uygulanabilirlik tablosunda Layer-B ve Layer-C alanlarını ayrı satırlarda doğru zaman/katmanla
   göster. Gerçek veya sentetik insan etiketi üretme.

## Kabul örnekleri

- Model çıktısını görmeyen Layer-B slotunda response scoreability/F1–F4 alanları reddedilir.
- Scoreable response için iki ayrı Layer-C ham görüşü ve provenance saklanır; adjudication hamı
  değiştirmez.
- İki Layer-C explicit unscorable görüşü ek adjudication olmadan final unscorable üretir.
- Operational timeout/error için Layer-C rating zarfı ve F1–F4 yasaktır.
- `resolved_reference=null` iken researcher condition'ı contested işaretleyebilir; alan criterion
  nesnesinin içinde değildir ve rater disagreement bunu otomatik üretmez.

## Doğrulama ve durma

JSON parse, layer/timing matrisi, yasak çapraz-katman alanları, iki-rater provenance, frozen §6.2,
resolved-ref bütünlüğü ve contested yerleşimi için etiketsiz yapısal kontroller çalıştır. Standart
checksum/link/frozen/audit kanıtlarını bırak. Teslimden sonra dur ve yeniden inceleme bekle.

