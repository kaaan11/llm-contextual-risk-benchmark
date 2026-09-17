# E5b — Uygulanan provider girdisi ve provenance

Durum: E1c insan onayını bekliyor. Sahip: küçük worker.  
Ortak kurallar: [worker sözleşmesi](llm-benchmark-worker-contract.md).

## Hedef

Config'te ilan edilen değer ile adapter'ın gerçekten göndereceği payload arasındaki bağı kur. Canlı endpoint çağrısı yapma; injected transport ile exact request capture kullan.

## Kod kapsamı

Oku/değiştir: `configs/phase8_eval_plan.json`, `benchmark/preflight.py`, `benchmark/metadata.py`, `benchmark/types.py`, `benchmark/adapters/providers.py`, `benchmark/runner.py` içindeki request kurma ve ilgili testler. Güncel provider desteği iddiası gerekiyorsa ana inceleyici resmi belge doğrulamasına bırak; tarihsel config adayını kullanılabilir varsayma.

## Davranış sözleşmesi

- Kanonik parametre şeması `max_tokens/max_output_tokens` uyuşmazlığını tek anlamla çözer; provider çevirisi kaydedilir.
- Çözülmüş system text ve hash, messages, tool availability ve generation parametreleri adapter sonrası canonical payload kimliğine bağlanır.
- İstenen exact model, dönen provider model ID, fingerprint/revision varsa ve finish/stop reason ayrı kaydedilir. Request metadata modeli provider dönüşü diye kopyalanmaz.
- Desteklenmeyen seed/parameter sessiz düşürülmez; dispatch öncesi reddedilir veya açık `not_transmitted` statüsü insan tarafından onaylanan sözleşmeye göre taşınır.
- Alias + bağımsız version metadata endpoint pinleme diye sunulmaz. Credential ve authorization header loglanmaz.

## Kabul

Injected transport ile OpenAI/Anthropic/open-weight payload capture, missing parameter, system aktarımı ve response provenance yolları sınanır; ağ erişimi sıfırdır. Başarılı mevcut desteklenen mock davranışı korunur. `payload-contract.md`, config destek matrisi ve kanıt paketi teslim edilir. Canonical strict gate E5d'ye bırakılır.

