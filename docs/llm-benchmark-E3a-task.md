# E3a — Yerel stimulus kusur envanteri

Durum: [E3a-R2 ile kabul edildi](reviews/llm-benchmark/E3a-r2-acceptance.md). Sahip: küçük worker, stimulus salt okunur.  
Ortak kurallar: [worker sözleşmesi](llm-benchmark-worker-contract.md).

## Hedef

Raporun AM002, referent belirsizliği, DU004 ve D priming örneklerini bütün korpusta ölçülü bir sorun envanterine dönüştür. Metin düzeltme, REVISE/REJECT kararı veya yeni sürüm üretme.

## Okuma/yazma kapsamı

Oku: stimulus v1, `stimulus_content_du.py`, `stimulus_content_ctl.py`, `tests/test_phase7f_stimulus.py`, P06/P13 kanıtları ve üst plan E3. Yaz: yalnız `docs/reviews/llm-benchmark/E3a/stimulus-issues.md`, makine-okunur bulgu tablosu ve kanıt paketi.

## İnceleme matrisi

Her aday için item/condition, doğrudan alıntıyı çoğaltmadan konum/hash, sorun türü, gözlenen kanıt, alternatif açıklama, otomatik kontrol sonucu, insan karar ihtiyacı ve önerilen `KEEP/REVIEW` durumu ver. Şunları ayır:

- koşullar arası final-byte ve tur yapısı bütünlüğü;
- discourse referent/coherence ile risk ambiguity;
- D'nin görev çözüm ipucu veya semantic içerik taşıması;
- assistant stance/specificity farkı;
- byte uzunluğu ile tokenizer'a özgü token toleransı.

Tokenizer/profil önceden belirtilmemişse token ihlali sonucu verme. Otomatik arama insan naturalness/safety kararına dönüşmez. Örneklerden toplam etki sayısı tahmin etme; taranan popülasyon ve rule açık olsun.

## Kabul ve durma

50/171 kapsam sayısı, final-byte eşliği ve v1 hash'i başlangıç/bitişte aynıdır. Envanter insan karar kuyruğunu somutlaştırır; hiçbir stimulus metni veya QC kaydı değişmez. Hedefli salt okunur kontroller ve `git diff --check` sonrası teslim et, E3b'ye geçme.
