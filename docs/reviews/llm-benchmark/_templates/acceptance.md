# <ID> — Ana inceleyici kabul kararı

Tarih: `<YYYY-MM-DD>`. İnceleyici: `<kimlik>`. Durum: **KABUL | DÜZELTME GEREKLİ | RED**.

## İnceleme ve bağımsız kanıt

İncelenen diff, sözleşme, günlük ve başlangıç/bitiş envanterlerini yaz. Ana inceleyicinin yeniden çalıştırdığı komutları ve gerçek sonuçlarını worker sonuçlarından ayrı göster.

## Kabul ölçütleri

| Ölçüt | Kanıt | Sonuç |
| --- | --- | --- |
| `<brief ölçütü>` | `<dosya/log/yeniden kontrol>` | PASS/FAIL |

## Bütünlük ve kapsam sınırı

Mühürlü protokol/stimulus hashleri, audit prefix'i, kullanıcı değişiklikleri, ağ/API ve insan annotation durumunu açıkla. Bilimsel karar bekliyorsa teknik teslimin kabulünü etkin protokol onayıyla karıştırma.

## Karar ve devam

Kabul edilen kesin kapsamı, bloklayıcı olmayan açık maddeleri ve açılan bir sonraki briefi yaz. Fazın bütünü kapanmadıysa bunu başlık düzeyinde belirt. Üst plan durum tablosunu ancak bu karar kaydedildikten sonra güncelle.

