# E6a — Sürümlü item-level analiz uygulaması

Durum: E1c insan onayı ve E5a schedule'ı bekliyor. Sahip: küçük worker.  
Ortak kurallar: [worker sözleşmesi](llm-benchmark-worker-contract.md).

## Hedef

Generic response-row metriklerinden ayrı, onaylı E1c estimandını expected schedule ve Layer-B sözleşmesine göre uygulayan sürümlü analiz ekle. Gerçek model sonucu üretme veya eski `analysis.json` üzerine yazma.

## Kapsam

Oku/değiştir: `benchmark/metrics.py` yalnız uyumluluk sınırı için, yeni küçük analysis modülü/CLI, schedule/outcome tipleri ve doğrudan testler. Analysis output input run/schedule/reference/protocol hashleri ile `analysis_definition_version` taşır.

## Sözleşme

- Analiz birimi research item'dır; bütün geçerli tekrarlar korunur. Row sayısı expected denominator değildir.
- DU/AM/NB/NH, DU-D ve `stratified_by_assistant_stance` ayrı raporlanır. Gruplar tabaka adına birleştirilmez.
- Nominal action kategori kontrastları ile harm/utility ayrı hesaplanır; applicability, uncertain, contested/either_defensible ve zero denominator açık davranır.
- Missing/error/filter/truncation, duplicate ve repeat coverage koşul/grup/model bazında görünürdür. Mode disagreement unscorable content sayılmaz.
- Onaylanmış item-eşit ağırlık, farklı repeat coverage nedeniyle row ağırlığına dönüşmez.
- Error-asymmetry endpoint'i varsa context effect'ten ayrı ad/çıktıdadır. Legacy ordinal/modal sonuç yalnız açık legacy analysis version ile yeniden üretilebilir.

## Zorunlu kabul örnekleri

Sabit action/farklı reference davranış kontrastı sıfır; nominal recoding invariant; eş dağılımlı stochastic fixture kesin item-effect etiketi üretmez; unequal repeat counts ağırlığı bozmaz; AM clarification yanlış hareket sayılmaz; missing Layer-B skor üretmez. Ayrıca expected missing/duplicate fixture'ları gerekir. Matematiksel fixture insan annotation değildir ve ampirik sonuç dizinine yazılmaz. Hedefli testler ve kanıt paketi içinde `analysis-contract.md` teslim edilir.

