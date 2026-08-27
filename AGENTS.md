# LLM Security–Usability Benchmark — Repository Rules (AGENTS.md)

Bu depo, büyük dil modellerinde bağlamsal risk yorumunu (`LLM-CTX-PILOT-2026-01` protokolü altında) araştıran bilimsel bir pilot çalışmadır. Bu repoda çalışan her model veya ajan aşağıdaki araştırma ve veri bütünlüğü kurallarına uymak zorundadır.

---

## 1. Araştırma Bütünlüğü ve Dondurulmuş Protokol

- **Mühürlü Artefaktlar Dokunulmazdır:** `docs/phase7e_preregistration.md`, `docs/phase7e_annotation_protocol.md`, `docs/PHASE_7D_EXPERIMENTAL_DESIGN.md` ve `dataset/pilot/multiturn/stimulus_dataset_v1.json` dosyaları composite hash ile mühürlenmiştir. İnsan araştırmacı onayı ve resmi protokol eki (`docs/phase7e_pre_evaluation_clarification.md`) olmadan bu dosyalarda tek bir bayt dahi değiştirilemez.
- **Stimulus Metni Sabittir:** 50 research item'a ait 171 koşul kaydının prompt ve asistan metinleri dondurulmuştur. Değişiklik yapılamaz.

---

## 2. Phase 7G İnsan Kalite Kontrolü ve İki-Rater Kapısı (R2)

- **İki Bağımsız Rater Şartı:** Phase 7G tamamlanması ve `KEEP` kararı için iki bağımsız kör rater (`rater_a` ve `rater_b`) zorunludur.
- **Yapay Anotasyon Yasağı:** Ajan hiçbir aşamada kendi inisiyatifiyle sentetik veya sahte kör rater anotasyonu (`probably_benign`, `probably_harmful` vb.) üretemez. Anotasyonlar yalnızca gerçek insan girdisinden kaydedilebilir.
- **Phase 8 Kilidi:** Phase 7G iki-rater ve insan QC onay kapısı kapanmadan hiçbir gerçek model evaluation veya API çağrısı başlatılamaz.

---

## 3. Metrik ve Kanıt Zinciri Standartları

- **Append-Only Denetim:** `results/dataset_audit/*.jsonl` review geçmişleri yalnızca append-only çalışır; geçmiş silinemez veya ezilemez.
- **Gecikme Ayrıştırması:** Model çağrılarında retry/backoff gecikmeleri ile saf model inferans gecikmesi (`pure_inference_latency_ms`) ayrı raporlanmalıdır.
- **Tabakalı Raporlama:** Phase 8 analizinde asistan turu özdeş olan (AM) ve farklı olan (DU/NH) gruplar bağımsız tabakalar (`stratified_by_assistant_stance`) olarak ele alınmalıdır.
