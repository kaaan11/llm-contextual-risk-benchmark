# E3a-R1 — Revizyon haritası (revision map)

E3a acceptance R1–R3'ün `E3a-r1` karşılığı. `../E3a/` teslimi değişmedi. Korunanlar: yapısal
sayımlar (50/171, 50/50, 29/21, 7/43, 19 aday), karar-değil sınırı, ayrımlar, REVIEW-kuyruk
disiplini.

| Blokaj | E3a kusuru | Düzeltme (dosya/bölüm) | Kabul karşılama |
| --- | --- | --- | --- |
| R1 üretilebilirlik | Betik `/tmp`'deydi; yöntem eksikti | `helpers/e3a_scan.py` (parametrik `--stimulus/--output`, korumalı-yol retli, deterministik); yöntem tablosu helper ile birebir; temp-output bayt-eşliği (03 logu) | Kalıcı helper aynı JSON'u üretir; `/tmp` bağımlılığı yok |
| R2 provenance | 6 R-REF'te hash yok + prompt parçası vardı | JSON `location.text_sha256` (6/6 bağımsız doğrulandı) + `human_decision_needed`/`human_decisions_open`; md+JSON kanıtlardan parça çıkarıldı | 6 satırda tam hash, hiçbirinde alıntı yok |
| R3 hüküm dili | "Referent bağlamla çözülür" otomatik hükümdü | Kanıt = dedektör + konum; dört karar açık alan (`human_decisions_open`); ham eşleşmeler referent kanıtı değil | Adaylar REVIEW kuyruğu; naturalness/E3b üretilmedi |

## Eski/yeni farkı (sayı aynı: 19)

- Aynı satır anahtarları; düşen/yeni satır yok. R-REF: +hash, +dörtlü, −parça. R-REF2:
  +kaynak-tur hashleri, kanıttan token adı çıkarıldı (konum+hash korunur; tutarlılık notu).
  Meta: helper/provenance eklendi. Kural mantığı değişmedi.

## Etkilenen dosyalar

- Değişen (bu dizinde yeni): `helpers/e3a_scan.py`, `stimulus-issues.md`,
  `stimulus-issues.json`.
- Değişmeyen: `../E3a/*`, stimulus v1, content kaynakları, QC/audit, testler, kod.
