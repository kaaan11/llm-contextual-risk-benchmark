# Pilot Çalışma İstatistiksel Güç Analizi ve Sınırlılıklar

**Protokol:** `LLM-CTX-PILOT-2026-01`  
**Tasarım Düzeyi:** Phase 7D Matched-Triplet/Quadruplet ($N=50$)  
**Doküman Türü:** Metodolojik Değerlendirme ve Ön-Analiz Kılavuzu

---

## 1. Örneklem Yapısı ve Analiz Birimi

Bu pilot çalışmada toplam 50 araştırma kaydı (research item) ve bunlara bağlı 171 koşul örneği yer almaktadır:

| Kategori | Kod | Örneklem ($n$) | Koşullar |
| :--- | :--- | :--- | :--- |
| Çift Kullanımlı (Non-Null) | `RI-DU-` | 30 | A, B, C, D (bazılarında) |
| Kalıcı Belirsizlik (Persistent Ambiguity) | `RI-AM-` | 7 | A, B, C, D |
| Taban Kontrolü (Null-Benign) | `RI-NB-` | 7 | A, B, C |
| Tavan Kontrolü (Null-High-Risk) | `RI-NH-` | 6 | A, B, C |
| **Toplam** | | **50** | **171 koşul** |

> **Kritik Kural:** Analiz birimi 171 koşul kaydı değil, **50 araştırma kaydıdır**. A, B, C ve D kolları bağımsız gözlemler değil, aynı canonical prompt etrafında eşleşmiş (matched / repeated-measures) koşullardır.

---

## 2. İstatistiksel Güç ve Minimum Saptanabilir Etki (MDE)

### 2.1 Çift Kullanımlı Grup ($n=30$)
- **Kullanılan Testler:** Eşleşmiş ordinal geçiş analizi, McNemar testi ve destekleyici Wilcoxon işaretli sıra testi.
- **Güç Analizi:** $\alpha = 0.05$ ve hedeflenen güç $1 - \beta = 0.80$ alındığında:
  - Bu örneklem büyüklüğü, **orta ve büyük etki büyüklüklerini** ($\Delta_{BC} \ge 0.35$) tespit etmek için yeterli güce sahiptir.
  - Küçük etki büyüklüklerinde ($\Delta_{BC} \le 0.20$) testin tip II hata (etki varken tespit edememe) riski yüksektir ($\beta > 0.40$).

### 2.2 Kontrol ve Taban/Tavan Grupları ($n=7$ ve $n=6$)
- **Kullanılan Testler:** Fisher's exact test ve taban/tavan sapma kontrolü.
- **Güç Sınırlılığı:** $n=7$ (`RI-NB-`) ve $n=6$ (`RI-NH-`) grupları bağımsız hipotez testi için aşırı düşüktür:
  - Bu gruplar istatistiksel anlamlılık kanıtlamak için değil, modelin uçlarda beklenen tavan (high-risk red) veya taban (benign kabul) davranışını gösterip göstermediğini denetleyen **kalite/geçerlilik kapıları (sanity check gates)** olarak değerlendirilmelidir.
  - Bu alt gruplarda p-değerine dayalı çıkarım yapılmamalıdır.

---

## 3. Asistan Turu Tabakalanması (F-01 ve C3 Kısıtları)

- `RI-AM-` (7 kayıt) asistan turlarının B ve C koşullarında bayt düzeyinde özdeş olduğu tek gruptur (`assistant_turn_shared`).
- `RI-DU-` (30) ve `RI-NH-` (6) gruplarında ise asistan turları tutum farkı taşımaktadır (`assistant_turn_differing`).
- **Analiz Zorunluluğu:** Phase 8 sonuçları raporlanırken $\Delta_{BC}$ hem genel havuzda hem de bu iki tabakada bağımsız olarak ayrıştırılarak raporlanmalıdır (`stratified_by_assistant_stance`). AM grubundaki etki, kullanıcı bağlamının saf etkisini test eden en temiz tanı koludur.

---

## 4. Phase 8 Raporlama İlkeleri

1. **P-Hacking Yasağı:** Küçük alt gruplarda anlamlılık aramak yerine, etki büyüklükleri ($\Delta$) ve \%95 bootstrap güven aralıkları (CI) raporlanmalıdır.
2. **Ordinal Geçiş Matrisleri:** Modelin davranışsal değişimi sadece ikili (binary) ret oranı olarak değil, 5 basamaklı ordinal geçiş matrisi olarak sunulmalıdır.
3. **Genişletme Önerisi:** Pilot sonuçları anlamlı bir bağlamsal etki sinyali verirse, nihai benchmark için grup başına $n \ge 50$ (toplam $N \ge 200$) olacak şekilde genişletilmiş faz planlanmalıdır.
