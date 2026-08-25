# Phase 6B — Kamu benchmark kaynakları ve lisans denetimi

## Denetim kapsamı

Bu belge 14 Ağustos 2026 tarihinde yapılan metadata düzeyindeki ön incelemeyi kaydeder. Ham dış dataset dosyaları repository’ye kopyalanmadı; kaynak satırları ve sample ID’leri icat edilmedi. Final manifest, immutable revision ve dosya hash’leri yakalanmadan oluşturulmayacaktır.

## Kaynak özeti

| Kaynak | Gözlenen kapsam | Şema / split | Lisans ve yayın durumu | Faz 6B kararı |
|---|---:|---|---|---|
| [XSTest](https://github.com/paul-rottger/xstest) | 450 prompt; 250 safe, 200 unsafe | Tek CSV; `id,prompt,type,label,focus,note` | Promptlar CC-BY-4.0; model completion lisansları ayrıdır | Promptlar attribution ile aday; immutable pin gerekli |
| [JBB-Behaviors](https://huggingface.co/datasets/JailbreakBench/JBB-Behaviors) | 100 harmful + 100 benign behavior; ayrı `judge_comparison/test` 300 | `behaviors/harmful`, `behaviors/benign`, `judge_comparison/test` | Dataset card/LICENSE MIT; AdvBench ve TDC/HarmBench upstream provenance ayrıca korunmalı | Harmful behavior, jailbreak prompt ile eşdeğer kabul edilemez |
| [WildGuardMix](https://huggingface.co/datasets/allenai/wildguardmix) | Train 86.759; test 1.725 | `wildguardtrain/train`, `wildguardtest/test` | Dataset card `odc-by`; gated erişim ve AI2 Responsible Use Guidelines | Raw veri commit edilmez; erişim, privacy ve locator politikası gerekli |

## XSTest

Resmî repository, `xstest_prompts.csv` dosyasını ve refusal/compliance sınıflandırma kodunu sağlar. Yayınlanan çalışmaya göre XSTest 250 safe promptu on prompt type altında ve 200 unsafe contrast promptu içerir. `type`, `label`, `focus` ve `note` alanları örneklerin güvenli/unsafe kontrast ve teknik-duyarlılık boyutlarını ayırmak için kullanılabilir.

XSTest prompt lisansı CC-BY-4.0’dır. Repository’de bulunan model completions aynı lisans kapsamında varsayılmayacaktır; bu nedenle completion dosyaları alınmayacaktır. Citation: Röttger et al., NAACL 2024, DOI `10.18653/v1/2024.naacl-long.301`.

## JailbreakBench / JBB-Behaviors

JBB-Behaviors’in `behaviors` config’i 100 harmful ve 100 benign behavior içerir. Satır şeması `Index`, `Goal`, `Target`, `Behavior`, `Category`, `Source` alanlarından oluşur. Harmful davranışların bir kısmı AdvBench ve TDC/HarmBench kaynaklıdır; kalan kısmı JBB tarafından özgün olarak hazırlanmıştır.

Bu dataset, davranış hedefleri ve affirmative target metinleri sağlar; tek başına bir jailbreak attack string koleksiyonu değildir. Gerçek jailbreak değerlendirmesi için JBB’nin ayrıca yayınladığı artifact’lerin yöntem, model, sürüm ve lisans bilgileri gerekir.

`judge_comparison/test` ayrı bir birimdir. Resmî açıklama bu setin 100 XSTest benign örneği içerdiğini ve farklı saldırı üretimlerinden gelen örneklerle birlikte judge karşılaştırması yaptığını belirtir. Bu nedenle ana JBB behavior split’i ile karıştırılmayacak ve bağımsız JBB örnek havuzu olarak kullanılmayacaktır.

Dataset card ve LICENSE MIT gösterse de, JBB’nin upstream source alanları için attribution ve yeniden dağıtım koşulları ayrıca kaydedilmelidir. Citation: Chao et al., NeurIPS 2024 Datasets and Benchmarks Track, DOI `10.57967/hf/2540`.

## WildGuardMix

WildGuardMix iki config/split sunar. `WildGuardTrain` 86.759 örnek, `WildGuardTest` 1.725 örnek olarak belgelenmiştir. Test split’i prompt-response çiftlerinde üç bağımsız anotatör, prompt harmfulness, response harmfulness ve response refusal etiketleri; ayrıca agreement alanları sağlar.

WildGuardTest içindeki `harmful` etiketi `jailbreak` ile eşdeğer değildir. `adversarial`, prompt harm, response harm ve refusal alanları ayrı tutulmalıdır. Train split’i eğitim amaçlıdır; evaluation pilotuna alınmayacaktır.

Dataset card `odc-by` lisansını, gated access’i ve AI2 Responsible Use Guidelines kabulünü belirtir. Ham WildGuard kayıtları bu repository’ye kopyalanmayacak; yalnızca erişim talimatı, immutable revision, hash ve izin verilen metadata saklanacaktır. Ayrıca dataset card’da native `sample_id` alanı belgelenmediği için row locator/content hash kullanımı açıkça “derived locator” olarak işaretlenmeden provenance tamamlanamaz.

## Lisans ve responsible release ilkesi

- Dış datasetler bu projenin özgün verisi değildir; yazarlarına/sağlayıcılarına aittir.
- Lisans bilgisi, citation, source URL, revision ve retrieval tarihi her seçilen örnekte korunmalıdır.
- CC-BY/MIT izinleri upstream kaynakların tüm koşullarını otomatik olarak çözmez.
- ODC-By ve gated responsible-use koşulları doğrulanmadan WildGuard raw text’i commit edilmez.
- Hassas adversarial promptlar, kişisel veri, gerçek sırlar ve model completionları varsayılan olarak repository dışında tutulur.

Detaylı machine-readable kayıt: `configs/phase6b_sources.json` ve `results/dataset_audit/source_inventory.json`.
