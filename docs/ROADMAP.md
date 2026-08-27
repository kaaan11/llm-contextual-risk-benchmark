# LLM Contextual Risk Benchmark — Uçtan Uca Araştırma Yol Haritası (Phases 8–16)

**Protokol:** `LLM-CTX-PILOT-2026-01`  
**Sürüm:** 1.1.0 (Audit & Remediation Güncellemesi)  
**Tasarım:** Phase 7D Matched-Triplet/Quadruplet ($N=50$, 171 Koşul Kaydı)

---

## Faz Genel Bakış ve Durum Tablosu

| Faz | Tanım | Çıktı / Artefakt | Durum |
| :--- | :--- | :--- | :--- |
| **Phase 7G** | **İki-Rater İnsan Kalite Kontrolü** | `phase7g_human_qc.json`, `phase7g_blind_review.json` | 🔄 **DEVAM EDİYOR** (1/50 rater_a) |
| **Phase 8** | **Kanonik Model Değerlendirmesi** | Dondurulmuş `raw_responses.jsonl` | ⛔ **KİLİTLİ** (Phase 7G bekliyor) |
| **Phase 9** | **Yanıt Skorlama ve Etiketleme** | `scored_responses.jsonl` (Kademeli Hibrit) | ⏳ Bekliyor |
| **Phase 10** | **Birincil İstatistiksel Analiz** | `primary_results.json` (SAP bazlı) | ⏳ Bekliyor |
| **Phase 11** | **Sağlamlık ve Falsifikasyon** | `falsification_report.md` | ⏳ Bekliyor |
| **Phase 12** | **Çapraz Model Karşılaştırması** | `cross_model_analysis.md` | ⏳ Bekliyor |
| **Phase 13** | **Uzman Değerlendirmesi** | `expert_review_report.md` | ⏳ Bekliyor |
| **Phase 14** | **Nihai Araştırma Sentezi** | `final_report_tr.md`, `final_report_en.md` | ⏳ Bekliyor |
| **Phase 15** | **Tekrarlanabilirlik & Çıkış Denetimi** | `reproducibility_audit.json` | ⏳ Bekliyor |
| **Phase 16** | **Açık Kaynak Yayın (Public Release)** | GitHub Public Repo + Zenodo / Hugging Face | ⏳ Bekliyor |

---

## Phase 8: Kanonik Model Değerlendirmesi (Canonical Model Evaluation)

Phase 7G'nin 50 maddesi `KEEP` onayı almadan ve **Phase 8 GO / NO-GO Gate** kapanmadan hiçbir gerçek model çağrısı yapılamaz.

### 1. Kapsam ve Hacim
* 50 araştırma kaydı $\times$ koşullar = **171 koşul örneği**.
* $M$ adet hedef model (Örn. 6 frontier ve açık ağırlıklı model):
  $$\text{Toplam Çağrı} = 171 \times M = 1.026 \text{ kanonik yanıt}$$

### 2. Dondurulmuş Çalıştırma Kriterleri (Preflight Manifest)
* **Tarihli Model Snapshot Zorunluluğu:** Dinamik takma adlar (alias) yasaktır. Yalnızca sabit tarihli sürümler kullanılır (`gpt-4o-2024-08-06`, `claude-3-5-sonnet-20241022`, `Meta-Llama-3-70B-Instruct`).
* **Örnekleme Hiperparametreleri:** `temperature = 0.0`, `seed = 42`, `top_p = 1.0`, `max_output_tokens = 1024`.
* **Deterministik Çağrı Sırası:** Koşullar rastgele değil, önceden mühürlenmiş tohum (`run_order_seed`) ile sıralanır.
* **Triplet Düzeyinde Veri Bütünlüğü Kuralı:** Eğer bir model bir kaydın triplet koşullarından (`A`, `B` veya `C`) birinde kalıcı hata (rate limit, timeout vb.) verirse, o model için o kayıt analize dahil edilmez. **Asla eksik veri uydurma / tamamlama (imputation) yapılmaz.**
* **Deviation Log:** Herhangi bir istisnai durumda stimulus değiştirilmez; `results/deviations/` altına append-only sapma kaydı açılır.

---

## Phase 9: Yanıt Puanlama ve Etiketleme (Response Annotation & Scoring)

Model yanıtlarının niyet ve güvenlik durumuna göre yapılandırılmış etiketlere dönüştürülmesi aşamasıdır.

### Kademeli Hibrit Skorlama Mimarisi (Tiered Scoring Architecture)
1.026 yanıtın insan darboğazına girmesini ve LLM hakemliğinin dairesel önyargısını (circular bias) önlemek için 3 kademeli sistem uygulanır:

1. **Katman 1 (Deterministik Kural Tabanlı):** [`benchmark/refusal.py`](file:///home/kaan/AI_Search/benchmark/refusal.py) regex motoruyla bariz retler (`refusal`) ve bariz kabuller anında ayrıştırılır.
2. **Katman 2 (Dondurulmuş Model Yargıç):** Gri bölgede kalan veya nüanslı yanıtlar için dondurulmuş açık kaynaklı bir model (Llama-3-70B), önceden belirlenmiş sabit rubrik ile ön-skorlama yapar (`disposition`, `task_fidelity`, `utility`).
3. **Katman 3 (İki-Rater İnsan Doğrulama Kapısı):** Çıkan tüm yanıtların rastgele tabakalanmış **en az %20'si** insan araştırmacılar tarafından kör olarak denetlenir. İnsan ve Model Yargıç uyumu $\kappa \ge 0.85$ olmadığı sürece otomatik skorlar kabul edilmez; uyuşmayan kümeler doğrudan insan hakemliğine devredilir.

---

## Phase 10: Birincil İstatistiksel Analiz (Primary Analysis)

Önceden dondurulmuş İstatistiksel Analiz Planı (SAP) çalıştırılır. P-hacking kesinlikle yasaktır.

### Temel Karşılaştırma Eksenleri
* **$A \leftrightarrow B$:** Meşru bağlamın ret oranını düşürme ve faydayı artırma etkisi (Legitimating Context Effect).
* **$A \leftrightarrow C$:** Şüpheli/riskli bağlamın temkinliliği artırma etkisi (Concerning Context Effect).
* **$B \leftrightarrow C$:** Modelin bağlamsal ayrıştırma gücü (Contextual Discrimination).
* **Tabakalı Raporlama Zorunluluğu (F-01 / C3):**
  * `assistant_turn_shared` (RI-AM-001..007, $n=7$): Saf kullanıcı bağlamının tanı kolu.
  * `assistant_turn_differing` ($n=43$): Asistan tutum farkı içeren ana akım kol.

---

## Phase 11: Sağlamlık ve Falsifikasyon (Robustness & Falsification)

Bu fazın amacı hipotezi doğrulamak değil, **"sonucu çürütmeye veya parçalamaya çalışmaktır"**.

### Temel Falsifikasyon Testleri
1. **Tekil Madde Hassasiyeti (Influence Analysis):** Elde edilen istatistiksel etki yalnızca 1-2 baskın maddeden mi kaynaklanıyor? (Leave-one-out çapraz denetimi).
2. **D Kolu Falsifikasyonu ("Within-D Quadruplet Cohort", $n=21$):** Nötr dolgu bağlamı ($D$) meşru ($B$) veya riskli ($C$) bağlamla aynı etkiyi üretiyor mu? Sırf token uzunluğu artışı modeli yanıltıyor mu? (Güç asimetrisini önlemek için $n=21$ içinde matched-pairs olarak çalıştırılır).
3. **AM Strata Karşılaştırması:** Asistan turlarının özdeş olduğu 7 maddede etki tamamen kayboluyor mu?
4. **Taban / Tavan Geçerlilik Denetimi:** Null-benign ($NB=7$) ve Null-highrisk ($NH=6$) kontrolleri beklenen uç davranışları eksiksiz sergiliyor mu?

---

## Phase 12: Çapraz Model Karşılaştırması (Cross-Model Analysis)

Farklı model ailelerinin bağlamsal kanıtları işleme asimetrisi incelenir.
* **Duyarlılık Profilleri:** Hangi modeller meşru bağlama aşırı duyarlıyken riskli bağlamı görmezden geliyor (veya tam tersi)?
* **Refusal Disparity:** Model büyüklüğü (parametre sayısı) arttıkça bağlam duyarlılığı artıyor mu yoksa System-1 refleksif retler baskın mı kalıyor?

---

## Phase 13: Uzman İncelemesi (Expert Review)

Sınırda kalan (borderline) vakalar, model anomalileri ve beklenmeyen sapmalar alan uzmanlarına sunulur.
* **Kural:** Uzman incelemesi geriye dönük olarak ground-truth'u veya birincil istatistiksel analiz sonuçlarını **asla değiştiremez**.
* **Kapsam:** Yalnızca dış geçerlilik (external validity), sınırlılıklar ve tartışma bölümü için nitel derinlik sağlar.

---

## Phase 14: Nihai Araştırma Sentezi (Final Research Synthesis)

* **Sonuç Tarafsızlığı:** `hypothesis_supported`, `partially_supported`, `model_dependent`, `category_dependent`, `unsupported` veya `inconclusive` sonuçlarının tümü eşit derecede meşrudur.
* **Yayın Raporları:**
  * `reports/final_report_tr.md`: Türkçe detaylı araştırma monografisi.
  * `reports/final_report_en.md`: Uluslararası akademik yayın formatında (NeurIPS/ACL şablonunda) İngilizce makale taslağı.

---

## Phase 15: Tekrarlanabilirlik ve Çıkış Denetimi (Reproducibility & Release Audit)

Yayın öncesi bağımsız bir denetim ajanı/iş parçacığı tarafından tüm araştırma hattı sıfırdan koşturulur:
$$\text{Raw Responses} \longrightarrow \text{Annotations} \longrightarrow \text{Metrics} \longrightarrow \text{Stats} \longrightarrow \text{Tables/Figures} \longrightarrow \text{Final Report}$$

### Denetim Kontrol Listesi
- [ ] API anahtarları, gizli token'lar ve PII tamamen temizlenmiş mi?
- [ ] Composite protocol hash (`phase7e_preregistration_hash.json`) \%100 eşleşiyor mu?
- [ ] Raporlardaki tüm sayılar ve tablolar ham veriden deterministik olarak yeniden üretilebiliyor mu?
- [ ] Lisans ve atıf gereksinimleri eksiksiz mi?

---

## Phase 16: Açık Kaynak Yayın (Public Release)

Araştırmanın kamuoyuna ve bilim dünyasına sunulması:
1. **Genel GitHub Deposu:** Tüm kaynak kodlar, testler, stimulus veri seti, metrikler, analiz script'leri ve raporlar.
2. **Korumalı Araştırma Erişimi (Responsible Disclosure):**
   * Tehlikeli operasyonel exploit veya saldırı adımları içeren ham model yanıtları açık repoda maskelenir (`[REDACTED_FOR_SAFETY]`).
   * Bu veriler akademik doğrulama amacıyla talep eden araştırmacılara denetimli erişim protokolü ile sağlanır.
