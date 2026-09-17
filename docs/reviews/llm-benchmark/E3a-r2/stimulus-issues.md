# E3a-R2 — Yerel stimulus kusur envanteri (stimulus-issues)

**Statü: ENVANTER / KARAR DEĞİL.** `../E3a/`, `../E3a-r1/` teslimleri değişmedi; bu dosya R2
düzeltmelerini içeren güncel belgedir. Metin düzeltme, REVISE/REJECT kararı ve yeni sürüm
YOKTUR. `REVIEW` önerisi insan QC kuyruğudur; worker KEEP hükmü VERMEDİ. Koşullu dil;
geçmiş-zaman sonuç bildirimi yok; revizyon peşinen hükmedilmedi.

- Kapsam: stimulus v1 (50/171, tam korpus) + content modülleri + phase7f testleri + P06/P13 +
  üst plan E3. Salt okunur (kanıt: `hashes-start/end.txt`).
- Makine-okunur tablo: `stimulus-issues.json` — `helpers/e3a_scan.py` ile üretildi, repo-dışı
  geçici output ile bayt-eşitliği doğrulandı (03 logu). Doğrudan alıntı YOKTUR: konum turn-ID
  + tam SHA-256 ile verilir.
- Tarama betiği teslim altındadır (`helpers/e3a_scan.py`); kurallar aşağıda helper ile
  birebir tanımlıdır.

## Yöntem (helper ile birebir)

| Kural | Popülasyon | Tanım | Sınır |
| --- | --- | --- | --- |
| Normalizasyon | Tüm metinler | Regex `[a-z0-9]+` (küçük harf); len≥5 tut; STOPWORDS çıkar; stemming yok | Liste helper'da donduruldu |
| DF evreni | 50 madde | Pre-final turlarda madde-başına varlık | — |
| **Exact eşlik** | 50 madde | B/C assistant tur dizilerinin **sıralı (rol, UTF-8 bayt) eşitliği**; sıra, büyük/küçük harf, noktalama, stopword farkları sayılır | Normatif `assistant_shared_bc` alanı budur |
| **Jaccard** | 50 madde | İçerik-token kümeleri arası betimleyici uzaklık | Ayrı lexical ölçüm; shared boolean DEĞİLDİR. Bu korpusta uzantı aynı (7/43), yoğunluk farklı — tesadüf, eşdeğerlik değil (ayrım unit örneği 04 logunda) |
| R-REF1 | 50 A-prompt | `\b(this\|these)\s+([a-z][a-z\-]{3,})`; that/those dışarıda | Eşleşme dedektör kaydıdır |
| R-REF2 | 50 madde × sıralı çiftler | Nadir token (len≥5, df≤2): Y-assistant'ta var, Y-user + prompt'ta yok, X-USER'da var | Nadirlik ≠ önem |
| R-DHINT | 21 D kolu | Overlap `\|A&B\|/min(\|A\|,\|B\|)` (3 ondalık); azalan max; bağda korpus sırası; ilk 5 kuyruk | Sıralama hüküm DEĞİLDİR |
| R-LEN | 50 madde | Bayt/kelime/heuristic `round(kelime×1.3)` | Token toleransı AÇIK |

Otomasyon aday üretir, hüküm vermez. Örnekten toplama tahmin YOKTUR.

## 1. Yapısal bütünlük (yeniden hesaplandı)

- 50/50 final-byte eşliği; 29×3 + 21×4 koşul; D–strateji 21/21; tur sayıları madde-içi eşit.
  **T-STRUCT adayı YOK.**
- Exact stance: 7 shared (tümü AM) / 43 differing — bağımsız doğrulandı (04 logu).

## 2. Aday tablosu (19 satır → insan QC kuyruğu)

`loc` = turn-ID (tam hash JSON'da). Kanıt dedektör sınıfı + konumdur; metin parçası YOKTUR.
R-REF satırlarında dört insan-kararı açık tutulur (JSON `human_decisions_open`).

| # | Madde / koşul | Tür | Konum | Kanıt | Açık insan kararları | Öneri |
| --- | --- | --- | --- | --- | --- | --- |
| 1–7 | 7 XCOND satırı (AM-002/C, AM-003/C, AM-006/B, DU-006/B, DU-008/B, DU-022/B, NB-003/C) | T-XCOND | İlgili assistant turu (kaynak user turları JSON'da) | R-REF2 tetiklendi (df≤2) | Coherence: koşul-dışı bilgiye dayanma? + naturalness (7: +floor yorumu) | REVIEW |
| 8–13 | 6 AM A-promptu | T-REF | …A-turn-00 (her biri) | R-REF1 tetiklendi | Ad-öbeği? / referent? / bağlam? / risk-ilişkisi? | REVIEW |
| 14–18 | 5 D kolu (AM-004, DU-008, DU-010, DU-028, AM-007) | T-DHINT-LEX | …D-turn-01 (her biri) | Leksik-adjacency ilk 5 (değerler JSON'da) | Nötrlük + d_rationale yeterliliği | REVIEW |
| 19 | RI-DU-004 / D | T-DHINT-HUMAN | …D-turn-01 | Rapor-kaynaklı aday; leksik tarama negatif — sınır kanıtı | Nötrlük + d_rationale yeterliliği | REVIEW |

Notlar: ham eşleşmelerin sözlük-dışı adayları referent kanıtı sayılmaz (R3 disiplini).
1. satır rapor P13 örüntüsünün konumudur. 19. satır otomasyonun YAKALAYAMADIĞI türdendir.

## 3. Ayrımlar (E3a/E3a-R1 ile aynı)

Bütünlük ≠ coherence; referent ≠ risk (dörtlü açık karar); D-hareketi ≠ mekanizma (C-04);
stance farkı bilinen sınırlama (kusur değil); bayt ≠ token (tolerans AÇIK).

## 4. İnsan karar kuyruğu + sayımlar

- 19 aday → E3b incelemesi. Sayılar yeniden hesaplandı: 50/171, 50/50, 29/21, exact 7/43,
  19 aday (E3a/E3a-R1 ile aynı anahtarlar; yöntem R1'deki gibi, exact alanı R2'de normatif).
- Taranmayan maddeler için worker bulgusu YOKTUR (KEEP hükmü değildir).

## 5. Hipotez bağı (korunur)
