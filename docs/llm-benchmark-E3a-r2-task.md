# E3a-R2 — Exact stance eşliği ve fail-closed output yolu

Durum: Hazır. Kök: `/home/kaan/AI_Search`. Yürütücü: E3a worker, stimulus salt okunur.  
Önkoşul: [E3a-R1 inceleme kararı](reviews/llm-benchmark/E3a-r1-acceptance.md).  
Ortak kurallar: [worker sözleşmesi](llm-benchmark-worker-contract.md).

## Tek paket hedefi

E3a-R1'de kalan iki helper sorununu kapat: assistant shared/differing alanını exact turn-metni
eşliğine bağla ve output yazımını repo içindeki diğer bütün dosyalara karşı fail-closed yap.
R-REF provenance'ını, karar-değil dilini, 19 aday kuyruğunu ve salt-okunur veri sınırını koru.

## Teslim kapsamı

Yeni teslim dizini `docs/reviews/llm-benchmark/E3a-r2/` olsun. Güncel
`helpers/e3a_scan.py`, `stimulus-issues.md`, `stimulus-issues.json`, revision map ve standart
kanıt paketini üret. Önceki E3a/E3a-R1 teslimlerini, stimulus/content kaynaklarını, QC/audit
kayıtlarını ve testleri değiştirme.

## Zorunlu düzeltmeler

1. `assistant_shared_bc` değerini B ve C koşullarındaki assistant turn dizilerinin sıra ve metin
   baytlarıyla exact eşliğinden hesapla. Normalize token kümelerini bu boolean için kullanma.
2. `assistant_jaccard_bc` ayrı betimleyici lexical ölçüm olarak kalabilir. Belgede exact boolean
   ile Jaccard'ın farklı ölçümler olduğunu yaz.
3. Mevcut frozen dataset için exact sonucu bağımsız doğrula: 7 shared, 43 differing. Helper'ın
   exact olmayan token-set eşliğini ayırt eden küçük, insan anotasyonu içermeyen yapısal unit
   örneği ekle veya doğrudan helper fonksiyonu üzerinden kanıtla.
4. Output yolu input yoluyla aynı resolve oluyorsa yazmadan reddet.
5. Repo içi allowlist yalnız bu teslimin `stimulus-issues.json` dosyası olsun. Repo içindeki
   diğer her hedefi, `docs/phase7e_preregistration.md` dahil, yazmadan reddet. Repo dışındaki
   caller-owned geçici output yolu kullanılabilir.
6. Output path güvenlik kontrollerini herhangi bir `write_text/open(..., 'w')` öncesinde uygula.
   Symlink/`..` kaçışlarını `resolve()` ile değerlendir.
7. Kanıt komutu kalıcı helper ile repo dışı geçici çıktı üretip teslim JSON'u ile byte-eşitlik
   kursun; ayrıca input==output, frozen docs yolu ve repo içi başka bir dosya için retleri
   içerik değiştirmeden doğrulasın.

## Kabul

- `assistant_shared_bc` exact turn-text eşliğidir; Jaccard/token eşliği değildir.
- 7/43 sonucu exact yöntemle yeniden üretilir.
- Helper stimulus inputunu, dört mühürlü protokol dosyasını, dataset/results/content/test/helper
  yollarını output olarak kabul etmez.
- Yalnız E3a-R2 teslim JSON'u ve repo dışı geçici çıktı yazılabilir.
- R-REF 6/6 hash, dört açık insan kararı, 19 REVIEW adayı ve frozen/audit hashleri korunur.

Teslimden sonra dur; E3b'ye geçme. Beklenen ana teslim:
`docs/reviews/llm-benchmark/E3a-r2/README.md`.
