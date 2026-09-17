# E6b — Prospective sensitivity ve karar eşiği kanıtı

Durum: E1c insan onayını bekliyor. Sahip: küçük worker.  
Ortak kurallar: [worker sözleşmesi](llm-benchmark-worker-contract.md).

## Hedef

Onaylı yeni endpoint için model çıktısı görülmeden yeniden üretilebilir sensitivity paketi hazırla. Bu çalışma gerçek model performansı, gözlenen power veya genel population garantisi değildir.

## Kapsam

Oku: E1c sözleşmesi, rapordaki `prospective_sensitivity.py/json`, `docs/statistical_power_and_limitations.md`, accepted population varsa E4b'nin yalnız sayıları. Yaz: yeni sürümlü analiz scripti/configi, testleri ve `docs/reviews/llm-benchmark/E6b/sensitivity-contract.md`. Eski rapor scriptini veya mühürlü belgeyi değiştirme.

## Senaryolar

Null dağılım eşitliği, farklı within-item varyans, item heterojenliği, run/block bağımlılığı, r=3/5/10, %10/%20/%30 attrition, error/filter/truncation ve uygun matematiksel rater-confusion parametreleri. DU=30, DU-D=14 başlangıç sayılarını ve E4b sonrası gerçek kabul sayılarını ayrı profiller olarak tut. Seed, scenario grid, test/CI, alpha/multiplicity ve karar eşiği outputlardan önce config hash'ine bağlanır.

Küçük hücre için frozen bootstrap yasağını sessizce delme. Exchangeability/independence ve binary endpoint varsayımlarını açıkla. Rater-confusion simülasyonu audit/QC kaydı veya sahte insan etiketi üretmez; yalnız soyut olasılık parametreleri kullanır.

## Kabul

Aynı seed/config aynı sayısal artefaktı üretir; farklı seed/hash görünürdür. Limit ve bilinen küçük örnek kontrolleri test edilir. Çıktıda büyük uyarı ve kapsam sınırı vardır. İnsan kararı bekleyen eşik uygulanmış gibi sunulmaz. Ağ/API/QC yazımı sıfırdır.

