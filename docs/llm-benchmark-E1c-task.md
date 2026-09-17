# E1c — Estimand, analiz ve amendment taslağı

Durum: [E1c-R3 ile worker taslağı kabul edildi](reviews/llm-benchmark/E1c-r3-acceptance.md); insan bilimsel kararları bekliyor. Sahip: worker taslağı, insan araştırmacı kararı.  
Önkoşul: E0 kabulü ve E1a/E1b teslimleri. Ortak kurallar: [worker sözleşmesi](llm-benchmark-worker-contract.md).

## Hedef

Eski ve önerilen ölçüm sözleşmesi arasındaki farkı açık bir pre-evaluation amendment taslağına dönüştür. Taslak etkin protokol değildir; mevcut `rules_changed=false` açıklamasına eklenmez ve mühürlü dosyalar değiştirilmez.

## Kapsam

Oku: üst plan E1c, E1a/E1b taslakları, `docs/phase7e_preregistration.md` §7–16, `docs/statistical_power_and_limitations.md`, rapor P03/P04/P08/P15, S01 ve §8/§10/§11. Yaz: `docs/reviews/llm-benchmark/E1c/amendment-draft.md`, `estimand-contract.md`, `legacy-to-proposed.md` ve kanıt paketi.

## İstenen içerik

Primary/secondary endpointleri, analiz birimini, item ağırlığını, bütün tekrarların kullanımını, missing/duplicate/error/exclusion politikasını, applicability ve zero denominator davranışını, test/CI varsayımlarını ve multiplicity yaklaşımını tanımla. DU=30, DU-D=14 ve control gruplarını örneklem büyütmek için birleştirme.

Kategori başına item-eşit B/C dağılım kontrastı ile harm ve utility kontrastlarını başlangıç önerisi olarak yaz. Mode ikincil ve açık sınırlı olabilir. McNemar korunursa koşula göre referanslanan paired binary error-asymmetry endpoint'i olarak adlandır; davranışsal context effect yerine koyma. Ordinal distance, D-adjusted effect flag ve Wilcoxon yorumunun eski→yeni statüsünü açıkla. H3/F4'ün sıfırdaki çakışması ve “non-trivial/meaningful/dominant” ifadeleri için somut karar seçenekleri ver.

## Kabul ve durma

Karşıörnekler taslak sözleşmede beklenen sonuçla yer alır: sabit davranış/farklı referans, monoton recoding ve eş dağılımlı stokastik koşullar. Worker birincil endpoint, alfa/CI veya bilimsel eşiği onaylanmış gibi seçmez; seçenek ve öneri sunar. İnsan kararı alınmadan E5/E6'ya etkin sözleşme devretme. Frozen hashleri doğrula ve dur.
