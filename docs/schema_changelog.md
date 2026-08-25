# Şema değişiklik günlüğü

## 0.2.0 — Phase 7 paired multi-turn uzantısı

Durum: Uygulandı; 50 yeni multi-turn örneği henüz oluşturulmadı.

### Amaç

`0.1.0` şeması sıralı multi-turn kayıtlarını taşıyabiliyordu; ancak aynı konuşmanın yalnızca son prompt ve tam bağlam koşullarında değerlendirilmesini, canonical prompt kimliğini ve tasarım/provenance metadata’sını açıkça garanti etmiyordu. `0.2.0`, bu eksikleri tamamlar ve gelecekteki gözlenen model etkisini tasarımcının beklenen etkisinden ayırır.

### Yeni kayıt alanları

`record_type: "multi_turn"` olan `0.2.0` kayıtlarında aşağıdaki alanlar zorunludur:

- `conversation_id`: Dataset genelinde benzersiz konuşma kimliği.
- `canonical_final_prompt`: Her iki değerlendirme koşulunun authoritative final user prompt’u.
- `canonical_final_prompt_sha256`: Canonical prompt’un UTF-8 byte’ları üzerinden SHA-256 özeti.
- `evaluation_conditions.final_prompt_only`: Yalnızca canonical final prompt koşulu.
- `evaluation_conditions.full_context`: Sıralı tüm turn kimlikleri ve final prompt turn kimliği.
- `expected_context_effect`: Araştırmacının model çalıştırılmadan önceki beklentisi.
- `model_observed_effect`: Başlangıçta zorunlu olarak `null`; evaluation sonucu değildir ve expected alanının üzerine yazılamaz.
- `expected_risk_profile`: Tasarım metadata’sındaki beklenen risk seviyesi; uzman anotasyonu değildir.
- `design_confidence`: Tasarım kararına duyulan `low`/`medium`/`high` güven.
- `composition_cell`, `context_signal_types`, `expected_interpretation` ve `expected_context_effect_rationale`: Tasarımın bağlam bileşimini açıklayan kontrollü alanlar.
- `authoring_method`, `generation_assistance`, `source_seed`: Yazım ve kaynak/provenance bilgisi.
- `source` ve record-level `dataset_version`: Kaydın özgün/adapted kaynak statüsü ve ait olduğu dataset sürümü.
- `researcher_specified_llm_assisted_draft`: Araştırmacı design specification’ı onayladıktan sonra AI-assisted draft üretimini açıkça belirtmek için gelecekte kullanılacak authoring değeri.
- `researcher_qc`: Araştırmacı kalite kontrolünün gerçekten yapılıp yapılmadığını belirten boolean.
- `external_validation_status`: Varsayılan akışta `not_reviewed` veya `researcher_reviewed`; uzman/dış doğrulama iddiası eklenmez.
- `created_at`: Kayıt üretim zamanı.

### Eşitlik ve bütünlük kuralları

- Canonical prompt üzerinde otomatik normalizasyon yapılmaz; karşılaştırma exact string equality ile yapılır.
- `final_prompt_only.prompt`, `canonical_final_prompt` ile birebir aynı olmalıdır.
- `full_context.turn_ids`, record içindeki turn sırasıyla birebir aynı olmalıdır.
- Son turn bir user turn olmalı ve `content.text`, canonical prompt ile birebir aynı olmalıdır. `content_ref` tek başına bu koşulu kanıtlamadığı için validator tarafından kabul edilmez.
- Canonical ve condition prompt hash’leri UTF-8 SHA-256 ile yeniden hesaplanarak kontrol edilir.

### Geriye dönük uyumluluk

- `schema_version: "0.1.0"` kayıtları yeniden yazılmaz ve mevcut Phase 3/5/6 altyapısı korunur.
- `schema_version: "0.2.0"` single-turn kayıtları, multi-turn paired alanlarını zorunlu kılmaz.
- `schema_version: "0.2.0"` multi-turn kayıtlarında yeni alanlar zorunludur.
- v0.2.0 multi-turn kayıtlarında `source=original` ve record `dataset_version` kök dataset sürümüyle eşleşmelidir; eski v0.1.0 kayıtları source alanı olmadan geçerliliğini korur.
- `dataset/validate.py`, eski v0.1.0 manifestlerini ve yeni v0.2.0 paired kayıtlarını aynı API ile doğrular.

### Bilinçli olarak kapsam dışında bırakılanlar

Bu sürüm örnek üretmez, public benchmark kayıtlarını değiştirmez, expert annotation oluşturmaz ve model evaluation çalıştırmaz. `model_observed_effect` ancak gelecekteki kontrollü evaluation artifact’leri için açık opt-in doğrulama seçeneğiyle doldurulabilir.
