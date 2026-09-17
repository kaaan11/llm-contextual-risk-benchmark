# E3a-R1 — Yeniden üretilebilir tarama ve R-REF provenance düzeltmesi

Durum: Hazır. Kök: `/home/kaan/AI_Search`. Yürütücü: E3a worker, stimulus salt okunur.  
Önkoşul: [E3a inceleme kararı](reviews/llm-benchmark/E3a-acceptance.md).  
Ortak kurallar: [worker sözleşmesi](llm-benchmark-worker-contract.md).

## Tek paket hedefi

E3a'nın doğrulanmış yapısal sayımlarını ve karar-değil sınırını koruyarak envanteri kalıcı
artefaktlardan yeniden üretilebilir hale getir; altı R-REF kaydına hash provenance'ı ekle ve ham
regex eşleşmesini discourse hükmüne dönüştüren dili kaldır.

## Teslim kapsamı

Yeni teslim dizini `docs/reviews/llm-benchmark/E3a-r1/` olsun. Düzeltilmiş
`stimulus-issues.md`, `stimulus-issues.json`, `helpers/e3a_scan.py`, revision map ve standart
kanıt paketini üret. Önceki E3a teslimini, stimulus v1'i, kaynak content dosyalarını, QC/audit
kayıtlarını ve testleri değiştirme.

## Zorunlu düzeltmeler

1. Tarama helper'ını `helpers/e3a_scan.py` altında kalıcı teslim et. Girdi stimulus yolu ile çıktı
   yolunu parametre olarak alsın; frozen girdiye veya varsayılan repo verisine yazmasın.
2. Helper'ı kullanarak envanteri geçici bir output yoluna yeniden üret ve teslim edilen JSON ile
   byte-eşit veya açıkça tanımlı canonical-JSON eşliği doğrula. `commands.jsonl`, loglar ve
   manifest kalıcı helper'ı kapsasın; `/tmp` altındaki kayıp kaynağa bağımlılık kalmasın.
3. Token normalization, stopword kümesi, document-frequency evreni, ordered-pair davranışı,
   overlap formülü, tie ordering ve top-5 seçimini helper ile belge arasında birebir tut.
4. Altı R-REF1 bulgusunun her birine canonical A turn ID ve tam `text_sha256` ekle. Hashi frozen
   stimulus metninden bağımsız doğrula.
5. R-REF Markdown ve JSON kanıtlarından doğrudan prompt parçalarını çıkar. Kanıt yalnız detector
   sınıfını ve eşleşme konumunu söylesin; kaynak metne turn ID/hash ile gidilsin.
6. “Referent context ile çözülür” gibi otomatik hükmü kaldır. Şunların tümü insan kararı olarak
   açık kalsın: eşleşmenin noun phrase olup olmadığı, gerçek bir referent bulunup bulunmadığı,
   referentin context gerektirip gerektirmediği ve risk ambiguity ilişkisi.
7. 50/171, 50/50 final-byte, 29/21 D ayrımı, 7/43 exact assistant eşliği ve 19-aday sayısı
   yeniden hesaplanmalı. Aday sayısı yöntem düzeltmesi nedeniyle değişirse eski/yeni farkını
   açıklayıp her yeni satırı aynı karar-değil standardıyla taşı.

## Kabul

- Temiz bir geçici outputta teslim helper'ı aynı makine-okunur envanteri üretir.
- Altı R-REF satırının tümünde çözülen tam hash vardır ve hiçbirinde prompt alıntısı yoktur.
- `this behave`/`this before` benzeri ham eşleşmeler referent kanıtı diye sunulmaz.
- Otomatik adaylar yalnız REVIEW kuyruğudur; insan naturalness/safety veya E3b kararı üretilmez.
- Stimulus, content kaynakları, QC/audit ve frozen dosyalar değişmez.

Teslimden sonra dur; E3b'ye geçme. Beklenen ana teslim:
`docs/reviews/llm-benchmark/E3a-r1/README.md`.
