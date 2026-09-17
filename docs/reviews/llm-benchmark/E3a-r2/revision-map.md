# E3a-R2 — Revizyon haritası (revision map)

E3a-R1 acceptance R1–R2'nin `E3a-r2` karşılığı. `../E3a/`, `../E3a-r1/` teslimleri değişmedi.
Korunanlar: R-REF provenance'ı, karar-değil dili, 19 REVIEW adayı, salt-okunur sınır, yapısal
sayımlar.

| Blokaj | E3a-R1 kusuru | Düzeltme (dosya/bölüm) | Kabul karşılama |
| --- | --- | --- | --- |
| R1 exact eşlik | Token-kümesi eşitliği kullanılıyordu | Helper `assistant_shared_exact` (sıralı rol+UTF-8 bayt) + `assistant_jaccard` ayrı ölçüm; JSON `assistant_shared_bc` exact; md yöntem tablosu ayrımı yazar | Exact 7/43 yeniden üretildi (tümü AM); ayrım unit örneği logda (04) |
| R2 output koruması | Yalnız dataset/results reddediliyordu; input==output serbestti | `resolve_output`: input==output ret; repo-içi allowlist yalnız bu teslim JSON'u; diğer tüm repo yolları ret; kontroller her yazımdan önce, `resolve()` ile | input==output, frozen docs yolu, başka repo dosyası retleri içerik değiştirmeden doğrulandı (05 logu) |

## Korunanlar (yeniden tasarım yok)

- R-REF 6/6 hash + dörtlü açık kararlar; 19 aday anahtarları; R-REF2/DHINT kuralları;
  karar-değil dili; E3b sınırı.

## Etkilenen dosyalar

- Değişen (bu dizinde yeni): `helpers/e3a_scan.py`, `stimulus-issues.md`,
  `stimulus-issues.json` (ölçüm alanı exact; değerler bu korpusta aynı uzantıda).
- Değişmeyen: `../E3a/*`, `../E3a-r1/*`, stimulus, content, QC/audit, testler, kod.
