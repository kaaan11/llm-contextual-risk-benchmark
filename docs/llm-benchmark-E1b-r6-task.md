# E1b-R6 — Çözülebilir ref ve adjudication final şeması

Durum: Hazır. Kök: `/home/kaan/AI_Search`. Yürütücü: E1b worker.  
Önkoşul: [E1b-R5 inceleme kararı](reviews/llm-benchmark/E1b-r5-acceptance.md).  
Ortak kurallar: [worker sözleşmesi](llm-benchmark-worker-contract.md).

## Tek paket hedefi

R5 alan tanımlarını ve R4 presence mantığını değiştirmeden bütün schema ref'lerini gerçekten
çözülebilir yap; adjudication final payload'ını aynı sözleşmeye bağlı açık bir schema olarak
tanımla. Bu tur bilimsel kural veya alan ekleme turu değildir.

## Teslim kapsamı

Yeni teslim dizini `docs/reviews/llm-benchmark/E1b-r6/` olsun. Düzeltilmiş şema, kısa ref notu,
revision map ve standart kanıt paketi üret. Önceki kanıtlar, kod, frozen dosyalar, stimulus,
audit/QC ve insan rating'leri değişmez.

## Zorunlu düzeltmeler

1. F1–F4 tanımlarını adreslenebilir bir map veya JSON Schema `$defs` altında tut. Nested alanlar
   gerçek JSON Pointer/`$ref` ile bu hedeflere çözülsün. `fields` dizisi korunacaksa geçerli indeks
   pointer'ı kullan; ID-map tercih edilirse tek canonical tanım otoritesi açık olsun.
2. Duplicate shape kopyaları ref hedefinden drift edememeli. Mümkünse kopyayı kaldır; kalması
   gerekiyorsa linter tam ilgili shape'i karşılaştırsın.
3. Adjudication için açık `final_payload_schema` tanımla. `final_scoreable_view` discriminator'ı
   unscorable ve scoreable dallarını ayırsın; final F1–F4/reason/gap/resolution alanları aynı
   çözülebilir ref hedeflerini kullansın. Serbest metin `final_field_scope` tek başına yeterli değil.
4. Linter her ref'i belge kökünden token-token traverse ederek çözsün ve hedef ID/type'ı
   doğrulasın. `#/fields/F1` gibi geçersiz pointer kabul edilmesin.
5. Yalıtılmış belleki/kopya negatif varyantta geçerli bir ref'i bozuk hedefe çevir; linter'ın
   bunu reddettiğini kanıtla. Canlı teslim dosyasını bozma.
6. R2–R5 davranış ve katman kuralları aynen kalsın; insan etiketi üretme.

## Kabul

- Bütün ref'ler gerçek çözümleyiciyle doğru hedefe ulaşır; unresolved ref listesi boştur.
- Bozuk-pointer negatif kontrolü başarısızlığı yakalar.
- Adjudication final payload'ı iki discriminator dalında kapalı ve refsiz tahmine ihtiyaç
  bırakmayacak biçimde tanımlıdır.
- Presence, gap, applicability, §6.2, resolved criterion ve contested regresyonları geçer.

Standart checksum/link/frozen/audit kanıtlarını bırak; teslimden sonra dur.

