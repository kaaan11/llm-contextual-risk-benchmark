# E3a — Yerel stimulus kusur envanteri (stimulus-issues)

**Statü: ENVANTER / KARAR DEĞİL.** Bu belge metin düzeltmez; REVISE/REJECT kararı vermez;
yeni sürüm üretmez. Aday satırlarındaki `REVIEW` önerisi insan QC kuyruğudur; worker tarafından
verilmiş KEEP hükmü YOKTUR. Koşullu dil kullanılır; geçmiş-zaman sonuç bildirimi yoktur;
hiçbir maddenin revizyonu peşinen hükmedilmez.

- Kapsam: `dataset/pilot/multiturn/stimulus_dataset_v1.json` (50 madde / 171 koşul, tam korpus;
  örnekleme yok) + `stimulus_content_du.py` / `stimulus_content_ctl.py` (yapım bağlamı) +
  `tests/test_phase7f_stimulus.py` (mevcut kontroller) + rapor P06/P13 + üst plan E3.
- Salt okunur: v1 baytları, QC kayıtları, audit geçmişi değişmedi (kanıt: `hashes-start/end.txt`).
- Makine-okunur tablo: `stimulus-issues.json` (19 aday + ölçümler + meta). Doğrudan alıntı
  çoğaltılmadı; konum turn-ID + SHA-256 ile verilir (md'de kısa önek, JSON'da tam hash).

## Yöntem (kurallar + popülasyonlar + sınırlar)

| Kural | Popülasyon | Ne bulur | Sınır |
| --- | --- | --- | --- |
| R-REF1 | 50 A-prompt | `this/these` + token (len≥4) belirteci | `that/those` dışarıda (ilgi zamiri baskın, ayrıştırma parsing ister); ad-öbekliği insana ait |
| R-REF2 | 50 madde × sıralı koşul çiftleri, assistant turları | Nadir token (len≥5, df≤2): Y-assistant'ta var, Y-user + prompt'ta yok, X-user'da var | Nadirlik ≠ önem; bağımsız benign seçim olabilir |
| R-DHINT | 21 D kolu | D-assistant ∩ prompt/B-assistant/C-assistant overlap katsayısı; ilk 5 kuyruk | Sıralama kusur hükmü DEĞİLDİR; semantik ipucu insana ait |
| R-STANCE/R-LEN | 50 madde | Jaccard uzaklığı, tur sayıları, bayt/kelime, kelime×1.3 heuristic (`build_stimulus_dataset.estimate_tokens`) | Betimleyici; token toleransı AÇIK (tokenizer profili belirtilmedi) |

Otomasyon aday üretir, hüküm vermez. Örneklerden korpus toplamına tahmin YOKTUR.

## 1. Yapısal bütünlük (koşullar-arası final-byte + tur yapısı)

- 50/50 maddede final kullanıcı metni bayt-eşit; kayıtlı SHA-256 yeniden türetmeyle eşleşti.
- 29 madde 3 koşullu (A/B/C) + 21 madde 4 koşullu (A/B/C/D); D varlığı `control_strategy=N`
  ile 21/21 eşleşir. Tur sayıları: A=1; B/C/D madde-içi eşit (AM u-a-u-u yapısı dahil).
- v1 SHA-256 başlangıç/bitiş aynı (`hashes-start/end.txt`). **T-STRUCT adayı YOK.**

## 2. Aday tablosu (19 satır → insan QC kuyruğu)

`loc` = turn-ID (tam metin hash'i JSON'da). `öneri` = REVIEW (insan kuyruğu) — KEEP hükmü yok.

| # | Madde / koşul | Tür | Konum | Gözlenen kanıt (kısa) | Alternatif | Otomatik sonuç | İnsan ihtiyacı | Öneri |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | RI-AM-002 / C | T-XCOND | …C-turn-01 | Nadir token (df=2) C-assistant'ta; aynı-koşul user + prompt'ta yok; B-user'da var (rapor P13 örüntüsü) | Bağımsız benign seçim | R-REF2 tetiklendi | Coherence: tur, koşul-dışı bilgiye dayanıyorsa naturalness | REVIEW |
| 2 | RI-AM-003 / C | T-XCOND | …C-turn-01 | Nadir token (df=2), aynı örüntü (B-user → C-assistant) | Bağımsız seçim | R-REF2 tetiklendi | Coherence/naturalness | REVIEW |
| 3 | RI-AM-006 / B | T-XCOND | …B-turn-01 | Nadir token (df=2), ters yön (C-user → B-assistant) | Bağımsız seçim | R-REF2 tetiklendi | Coherence/naturalness | REVIEW |
| 4 | RI-DU-006 / B | T-XCOND | …B-turn-01 | Nadir token (df=1), D-user → B-assistant | Bağımsız seçim | R-REF2 tetiklendi | Coherence/naturalness | REVIEW |
| 5 | RI-DU-008 / B | T-XCOND | …B-turn-01 | Nadir token (df=1), D-user → B-assistant | Bağımsız seçim | R-REF2 tetiklendi | Coherence/naturalness | REVIEW |
| 6 | RI-DU-022 / B | T-XCOND | …B-turn-01 | Nadir token (df=2), D-user → B-assistant | Bağımsız seçim | R-REF2 tetiklendi | Coherence/naturalness | REVIEW |
| 7 | RI-NB-003 / C | T-XCOND | …C-turn-01 | Nadir token (df=1), B-user → C-assistant | Bağımsız seçim | R-REF2 tetiklendi | Coherence + floor-kontrol yorumu | REVIEW |
| 8 | RI-AM-001 / A | T-REF | …A-turn-00 | A belirteci (this + adayı): gönderge yalnız bağlamda çözülür | Sıradan anafor; bağlam çözer | R-REF1 tetiklendi | Referent-vs-risk ayrımı + naturalness | REVIEW |
| 9 | RI-AM-002 / A | T-REF | …A-turn-00 | A belirteci (this + adayı) | Sıradan anafor | R-REF1 tetiklendi | Referent-vs-risk ayrımı | REVIEW |
| 10 | RI-AM-003 / A | T-REF | …A-turn-00 | A belirteci (sözlük-dışı aday olabilir) | Fiil/zarf kullanımı; kusur yok | R-REF1 tetiklendi (kural ham) | Ad-öbekliği + referent ayrımı | REVIEW |
| 11 | RI-AM-004 / A | T-REF | …A-turn-00 | A belirteci (this + adayı) | Sıradan anafor | R-REF1 tetiklendi | Referent-vs-risk ayrımı | REVIEW |
| 12 | RI-AM-005 / A | T-REF | …A-turn-00 | A belirteci (sözlük-dışı aday olabilir) | Zarf kullanımı; kusur yok | R-REF1 tetiklendi (kural ham) | Ad-öbekliği + referent ayrımı | REVIEW |
| 13 | RI-AM-006 / A | T-REF | …A-turn-00 | A belirteci (this + adayı) | Sıradan anafor | R-REF1 tetiklendi | Referent-vs-risk ayrımı | REVIEW |
| 14 | RI-AM-004 / D | T-DHINT-LEX | …D-turn-01 | Leksik-adjacency #1/21 (B/C ile 0.286) | Konu-komşu inert dolgu | Sıralama (hüküm değil) | Nötrlük (d_rationale yeterliliği) | REVIEW |
| 15 | RI-DU-008 / D | T-DHINT-LEX | …D-turn-01 | #2/21 (C ile 0.25) | İnert dolgu | Sıralama | Nötrlük | REVIEW |
| 16 | RI-DU-010 / D | T-DHINT-LEX | …D-turn-01 | #3/21 (prompt ile 0.2) | İnert dolgu | Sıralama | Nötrlük | REVIEW |
| 17 | RI-DU-028 / D | T-DHINT-LEX | …D-turn-01 | #4/21 (prompt ile 0.2) | İnert dolgu | Sıralama | Nötrlük | REVIEW |
| 18 | RI-AM-007 / D | T-DHINT-LEX | …D-turn-01 | #5/21 (B/C ile 0.2) | İnert dolgu | Sıralama | Nötrlük | REVIEW |
| 19 | RI-DU-004 / D | T-DHINT-HUMAN | …D-turn-01 | Rapor-kaynaklı yöntem-ipucu adayı; leksik tarama NEGATİF (0.0/0.0/0.0) — taramanın sınırını gösterir, geçerlemez | d_rationale'daki gibi adjacent-inert dolgu | Otomasyon tetiklemedi (P13 kaynağı) | Nötrlük + d_rationale yeterliliği | REVIEW |

Notlar: 10/12. satırlar kuralın ham tetiklemesidir (sözlük-dışı aday); insan ad-öbekliğini
belirler. 19. satır otomasyonun YAKALAYAMADIĞI türdendir; tarama negatifliği aklamaz.

## 3. Ayrımlar (brief §16)

- **Final-byte/tur bütünlüğü vs metinsel coherence:** Bütünlük 50/50 geçti (§1); coherence
  adayları (1–7) ayrı listedir. Biri diğerinin yerine geçmez.
- **Discourse referent vs risk ambiguity:** 8–13. satırlar gönderge adayıdır; risk belirsizliği
  oldukları doğrulanmadı. Ayrımı bağımsız rater yapar (E4); clarification ihtiyacı risk
  analiziyle karıştırılmaz.
- **D ipucu/semantik içerik:** 14–19. satırlar nötrlük adayıdır; D hareketi/hareketsizliği
  tek başına mekanizma kanıtı değildir (C-04 disiplini).
- **Assistant stance/specificity:** 43 maddede B/C assistant metni farklı, 7 AM'de özdeş
  (clarification C1–C3 bilinen sınırlama; kusur listesi DEĞİL). Jaccard uzaklıkları
  `stimulus-issues.json` measurements bölümündedir.
- **Byte vs token:** B/C/D bağlam bayt/kelime/heuristic sayıları measurements bölümündedir.
  D'nin 17/21 maddede bayt-kısa olması token ihlali SAYILMAZ; sağlayıcı tokenizer profili
  yoksa sonuç AÇIK kalır.

## 4. İnsan karar kuyruğu (E3b girdisi, karar DEĞİL)

- 19 aday → araştırmacı/rater incelemesi: coherence (1–7), referent ayrımı (8–13), D nötrlüğü
  (14–19). Her biri için gerekçeli koruma/REVISE/REJECT insan tarafından seçilir (E3b).
- Taranan popülasyon tam korpus olduğundan kuyruk dışı maddeler için worker bulgusu YOKTUR;
  bu, KEEP hükmü değildir.

## 5. Etkilenen hipotez/çıktı bağı

- F6 (izole-valence gate): 8–13. satırlar gate'i düşürebilirse bilimsel sonuçtur, bug değil.
- H0b/F2 (D yorumu): 14–19. satırlar D yorum sınırını etkiler; length/priming dili korunur.
- Estimand (C-01): Hiçbir satır whole-history kapsamını değiştirmez; metin değişikliği yok.
