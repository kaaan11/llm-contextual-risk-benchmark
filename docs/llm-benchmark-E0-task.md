# E0 — Referans, kanıt matrisi ve yeniden üretim sınırı

Durum: Uygulamaya hazır. Kök: `/home/kaan/AI_Search`. Yürütücü: küçük worker.  
Üst plan: [değerlendirme ve eylem planı](llm-benchmark-assessment-and-plan.md).  
Ortak kurallar: [worker sözleşmesi](llm-benchmark-worker-contract.md).

## Tek paket hedefi

Rapor bulgularını güncel çalışma ağacına bağlayan kalıcı başlangıç paketi üret. Bu görev kod düzeltmesi, protokol amendment'ı veya insan QC görevi değildir. Rapor yazarının `PROJECT-VERIFIED` etiketini yerel yeniden doğrulama yerine kullanma.

## Okuma ve yazma kapsamı

Önce `AGENTS.md` ve ortak sözleşmeyi oku. Ardından üst planın §1–4 E0 kısmı, `/home/kaan/GPT-Pro/reports/LLM_Benchmark` teslim manifestosu/README/ilgili P kanıtları, `pyproject.toml`, `results/dataset_audit/phase7e_preregistration_hash.json`, test girişleri, source/overlap raporları ve durum belgeleri.

Yalnız `docs/reviews/llm-benchmark/E0/` altına yaz. Üretim kodu, config, test, audit ve veri dosyası değiştirme. Rapor ZIP'ini kalıcı repo içine açma; gerekiyorsa salt okunur geçici dizin kullan.

## Alt işler

1. HEAD, dirty/untracked kapsam, Python ve bağımlılık ortamı ile rapor kaynak hashlerini `baseline.md` içinde kaydet.
2. P01–P15 ve S01/S02 için `yerelde doğrulandı / rapor kanıtı / açık / çürütüldü` matrisi üret. Her satır dosya/satır, yöntem ve kanıt sınırı taşısın.
3. Testleri ağ, gerçek audit/QC yazımı ve sentetik rater üretimi açısından sınıflandır. Güvenle çalıştırılabilir hedefli komutları `test-safety.md` içinde öner; riskli komutu çalıştırma.
4. Blind key'in yalnız varlık/paketleme kapsamını kaydet; içerik/hash veya mapping'i teslim dosyalarına taşıma.
5. Hash bütünlüğü, commit bağı, source lisansı, overlap ve contamination yokluğu iddialarını `provenance-scope.md` içinde ayır.
6. Başlangıç/bitişte frozen composite, stimulus v1 50/171, QC sayıları ve audit history prefix kontrollerini tekrar et.

## Kabul ölçütleri

- Rapor kaynakları ve farklı koşu beyanları tek kanıt gibi birleştirilmez.
- Her önemli plan bulgusunun güncel sahibi ve durumu vardır; örnek vaka toplam etki sayısı diye sunulmaz.
- Çalıştırılmayan test veya bulunmayan dış artefakt görülmüş/geçmiş sayılmaz.
- Başlangıç kullanıcı değişiklikleri ve bütün mühürlü dosyalar korunur.
- Teslim yalnız belge/kanıt üretir; Phase 7G veya Phase 8 durumu değişmez.

## Doğrulama ve teslim

En az `git diff --check`, hash/composite kontrolü ve teslim içi bağlantı kontrolü yap. Gerçek komutları `commands.jsonl` ve `logs/` altında kaydet. `baseline.md`, `findings.md`, `test-safety.md`, `provenance-scope.md`, başlangıç/bitiş hashleri ve README teslim edilir. E0 bittiğinde dur ve ana inceleyici kabulünü bekle.

