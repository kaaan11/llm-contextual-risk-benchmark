# E3a-R1 — Yerel stimulus kusur envanteri (stimulus-issues)

**Statü: ENVANTER / KARAR DEĞİL.** `../E3a/` teslimi değişmedi; bu dosya R1 düzeltmelerini
içeren güncel belgedir. Metin düzeltme, REVISE/REJECT kararı ve yeni sürüm YOKTUR. `REVIEW`
önerisi insan QC kuyruğudur; worker KEEP hükmü VERMEDİ. Koşullu dil; geçmiş-zaman sonuç
bildirimi yok; revizyon peşinen hükmedilmedi.

- Kapsam: stimulus v1 (50/171, tam korpus) + content modülleri (yapım bağlamı) + phase7f
  testleri + P06/P13 + üst plan E3. Salt okunur (kanıt: `hashes-start/end.txt`).
- Makine-okunur tablo: `stimulus-issues.json` — `helpers/e3a_scan.py` ile üretildi, geçici
  output ile bayt-eşitliği doğrulandı (03 logu). Doğrudan alıntı YOKTUR (R-REF dahil tüm
  satırlar): konum turn-ID + tam SHA-256 ile verilir; kaynak metne oradan gidilir.
- Tarama betiği geçicide değil, teslim altındadır (`helpers/e3a_scan.py`); kurallar aşağıda
  helper ile birebir tanımlıdır.

## Yöntem (helper ile birebir)

| Kural | Popülasyon | Tanım | Sınır |
| --- | --- | --- | --- |
| Normalizasyon | Tüm metinler | Regex `[a-z0-9]+` (küçük harf); len≥5 tut; STOPWORDS çıkar; stemming yok | — |
| STOPWORDS | Sabit küme (helper kaynağında tam liste; örn. işlev sözcükleri + tek harfler + kısaltma parçaları) | — | Liste helper'da donduruldu |
| DF evreni | 50 madde | Pre-final tur metinlerinde madde-başına varlık sayımı | — |
| R-REF1 | 50 A-prompt | `\b(this\|these)\s+([a-z][a-z\-]{3,})` (büyük/küçük duyarsız); that/those dışarıda (ilgi-zamiri baskın) | Eşleşme detector kaydıdır; ad-öbekliği/hüküm insana ait |
| R-REF2 | 50 madde × sıralı koşul çiftleri | Nadir token (len≥5, df≤2): Y-assistant'ta var, Y-user + prompt'ta yok, X-USER'da var (X≠Y) | Nadirlik ≠ önem |
| R-DHINT | 21 D kolu | Overlap katsayısı `\|A&B\|/min(\|A\|,\|B\|)` (3 ondalık); D-assistant vs prompt/B/C-assistant; azalan max; bağ eşitliğinde korpus sırası (stable sort); ilk 5 kuyruk | Sıralama hüküm DEĞİLDİR |
| R-STANCE/R-LEN | 50 madde | Jaccard uzaklığı; bayt (UTF-8); kelime (boşluk); heuristic `round(kelime×1.3)` (`build_stimulus_dataset.estimate_tokens`) | Betimleyici; token toleransı AÇIK |

Otomasyon aday üretir, hüküm vermez. Örnekten toplama tahmin YOKTUR.

## 1. Yapısal bütünlük (yeniden hesaplandı)

- 50/50 final-byte eşliği; 29×3 + 21×4 koşul; D varlığı `control_strategy=N` ile 21/21;
  tur sayıları madde-içi eşit (AM u-a-u-u dahil). **T-STRUCT adayı YOK.**

## 2. Aday tablosu (19 satır → insan QC kuyruğu)

`loc` = turn-ID (tam hash JSON'da). Kanıt dedektör sınıfı + konumdur; metin parçası YOKTUR.
R-REF satırlarında dört insan-kararı açık tutulur: ad-öbeği mi? / gerçek referent var mı? /
bağlam gerektirir mi? / risk-ambiguity ilişkisi? (JSON `human_decisions_open`.)

| # | Madde / koşul | Tür | Konum | Kanıt (dedektör + konum) | Açık insan kararları | Öneri |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | RI-AM-002 / C | T-XCOND | …C-turn-01 (B-user kaynaklı) | R-REF2 tetiklendi (df=2) | Coherence: koşul-dışı bilgiye dayanma? + naturalness | REVIEW |
| 2 | RI-AM-003 / C | T-XCOND | …C-turn-01 (B-user kaynaklı) | R-REF2 tetiklendi (df=2) | Coherence + naturalness | REVIEW |
| 3 | RI-AM-006 / B | T-XCOND | …B-turn-01 (C-user kaynaklı) | R-REF2 tetiklendi (df=2) | Coherence + naturalness | REVIEW |
| 4 | RI-DU-006 / B | T-XCOND | …B-turn-01 (D-user kaynaklı) | R-REF2 tetiklendi (df=1) | Coherence + naturalness | REVIEW |
| 5 | RI-DU-008 / B | T-XCOND | …B-turn-01 (D-user kaynaklı) | R-REF2 tetiklendi (df=1) | Coherence + naturalness | REVIEW |
| 6 | RI-DU-022 / B | T-XCOND | …B-turn-01 (D-user kaynaklı) | R-REF2 tetiklendi (df=2) | Coherence + naturalness | REVIEW |
| 7 | RI-NB-003 / C | T-XCOND | …C-turn-01 (B-user kaynaklı) | R-REF2 tetiklendi (df=1) | Coherence + floor yorumu | REVIEW |
| 8–13 | 6 AM A-promptu | T-REF | …A-turn-00 (her biri) | R-REF1 tetiklendi (belirteç + token) | Ad-öbeği? / referent? / bağlam? / risk-ilişkisi? | REVIEW |
| 14–18 | 5 D kolu (AM-004, DU-008, DU-010, DU-028, AM-007) | T-DHINT-LEX | …D-turn-01 (her biri) | Leksik-adjacency ilk 5 (değerler JSON'da) | Nötrlük + d_rationale yeterliliği | REVIEW |
| 19 | RI-DU-004 / D | T-DHINT-HUMAN | …D-turn-01 | Rapor-kaynaklı aday; leksik tarama negatif (0.0/0.0/0.0) — sınır kanıtı | Nötrlük + d_rationale yeterliliği | REVIEW |

Notlar: 8–13. satırlarda ham eşleşmenin sözlük-dışı adayları da vardır; ad-öbekliği
belirlenmeden referent kanıtı sayılmaz (R3). 1. satır rapor P13 örüntüsünün konumudur.
19. satır otomasyonun YAKALAYAMADIĞI türdendir.

## 3. Ayrımlar (E3a ile aynı)

- Bütünlük ≠ coherence (§1 vs 1–7); referent ≠ risk (8–13, dört açık karar);
  D-hareketi ≠ mekanizma (14–19, C-04); stance farkı bilinen sınırlama (43/7, kusur değil);
  bayt ≠ token (17/21 bayt-kısalık ihlal sayılmaz; tolerans AÇIK).

## 4. İnsan karar kuyruğu + eski/yeni farkı

- 19 aday → E3b incelemesi (coherence 1–7; referent dörtlüsü 8–13; D nötrlüğü 14–19).
  Sayı E3a ile aynı (19); satır anahtarları aynı. Fark: R-REF satırlarında tam hash +
  `human_decisions_open` dörtlüsü eklendi, prompt parçası kanıtlardan çıkarıldı;
  R-REF2 satırlarında token adı kanıttan çıkarıldı (konum+hash korunur), kaynak-tur hashleri
  eklendi; meta helper/provenance taşır. Kural mantığı değişmedi; yeni satır yok, düşen satır
  yok. Taranmayan maddeler için worker bulgusu YOKTUR (KEEP hükmü değildir).

## 5. Hipotez bağı (E3a §5 korunur)
