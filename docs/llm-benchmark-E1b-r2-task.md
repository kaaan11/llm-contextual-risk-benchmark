# E1b-R2 — Çözülmüş criterion ve frozen scoreability düzeltmesi

Durum: Hazır. Kök: `/home/kaan/AI_Search`. Yürütücü: E1b worker.  
Önkoşul: [E1b-R1 inceleme kararı](reviews/llm-benchmark/E1b-r1-acceptance.md).  
Ortak kurallar: [worker sözleşmesi](llm-benchmark-worker-contract.md).

## Tek paket hedefi

E1b-R1'de kalan iki blokajı kapat: F3 için tek ve provenance'lı çözülmüş condition criterion
tanımla; `unscorable_content` akışını frozen annotation protocol §6.2 ile birebir uyumlu yap.
E1b ve E1b-R1 kanıtlarını değiştirme. Taxonomy, iki-rater kimliği, ham kayıtların korunması,
disagreement/contested ayrımı, operational-outcome sınırı ve no-composite kararlarını yeniden
tasarlama.

## Teslim kapsamı

Yeni teslim dizini `docs/reviews/llm-benchmark/E1b-r2/` olsun. Düzeltilmiş `rubric-draft.md`,
`schema-draft.json`, yalnız etkilenen sınır örnekleri, `revision-map.md` ve standart kanıt paketini
üret. Üretim kodu, mühürlü belgeler, stimulus, audit/QC ve insan rating'leri değişmez.

## Zorunlu düzeltmeler

1. F5 zarfında iki ham rater criterion önerisini aynen koruyan ayrı bir `resolved_reference`
   nesnesi tanımla. Nesne stable `criterion_id`, criterion version, çözülmüş
   `allowed_assistance`, `restricted_capability`, `clarification_sufficiency`, resolution source
   (`rater_agreement` veya `adjudication`), kaynak ham slot referansları ve gerekiyorsa adjudication
   referansı taşısın.
2. İki rater criterion üçlüsünde anlaşmışsa resolved nesnenin nasıl ve kim tarafından kayda
   geçirildiğini açıkla; ham slotlardan birini sessizce canonical seçme. Uyuşmazlık çözülmeden
   resolved reference oluşmasın.
3. F3 `criterion_ref`, aynı koşuldaki **resolved** criterion ID/version'a çözülmek zorunda olsun.
   Missing, pending veya dangling resolved reference varken F3 alanları yasak ve sonuç açıkça
   `not_scored_missing_criterion` olsun.
4. Frozen `docs/phase7e_annotation_protocol.md` §6.2'yi aynen uygula: iki rater da explicit
   `unscorable_content` verdiğinde final durum için ek adjudication şartı yoktur. Yalnız tek rater
   unscorable dediğinde disagreement/adjudication gerekir. İki low confidence yine unscorable
   üretmez.
5. Şema kuralları bu geçişleri koşullu ve makinece uygulanabilir biçimde anlatsın. Örnek insan
   etiketi veya gerçek condition criterion içeriği üretme.

## Kabul örnekleri

- Aynı criterion üçlüsünde anlaşan iki farklı reviewer'ın ham kayıtları korunur; provenance'lı
  resolved reference oluşur ve F3 yalnız onun ID/version'ına bağlanır.
- Criterion üçlüleri farklıyken agreement=`disagree` ve adjudication yoksa resolved reference ve
  F3 reddedilir.
- Adjudication çözümü ham iki öneriyi değiştirmez; resolved source adjudication'ı gösterir.
- İki explicit unscorable görüşü doğrudan final `unscorable_content` üretir.
- Bir explicit unscorable ile bir scoreable görüşü adjudication bekler; iki low confidence kendi
  başına unscorable üretmez.

## Doğrulama ve durma

JSON parse, ref/version bütünlüğü, geçiş matrisi, ham kayıt immutability'si ve frozen §6.2 uyumu
için rater etiketi üretmeyen yapısal kontroller çalıştır. Checksum, link, frozen hash ve audit
prefix kanıtlarını E1b-r2 altında bırak. İnsan kararlarını `APPROVED` yapma. Teslimden sonra dur ve
yeniden inceleme bekle.

