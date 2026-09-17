# E5c — Outcome, retry, attempt ve gecikme sözleşmesi

Durum: E5a/E5b sözleşmelerini bekliyor. Sahip: küçük worker.  
Ortak kurallar: [worker sözleşmesi](llm-benchmark-worker-contract.md).

## Hedef

Planlanan logical job, fiziksel provider attempt, skorlanabilir başarı ve eksik sonucu ayrı temsil et. Retry/backoff ile ölçülebilen çağrı sürelerini ayır; ölçülemeyen server inference'a yanlış `pure_inference_latency_ms` değeri verme.

## Kod kapsamı

Oku/değiştir: `benchmark/types.py`, `runner.py`, `retry.py`, `logging.py`, `latency.py`, `errors.py`, gerektiği kadar adapter response alanları ve ilgili benchmark testleri. E6 analiz formüllerini veya E5d completion manifestini uygulama.

## Sözleşme

- Her expected job `success/error/provider_filter/timeout/truncated/not_run/missing` gibi onaylı tek outcome ile uzlaşır; karar/score yalnız uygun başarıda vardır.
- Attempt ledger her fiziksel dispatch'i sıra, başlangıç/bitiş, retry nedeni ve güvenli hata koduyla taşır. `planned = terminal outcomes`; attempts ayrı toplamdır.
- Retry policy terminal parse/config/budget hatasını tekrar etmez; backoff ve Retry-After/deadline davranışı ayrı tutulur. Bütçe sahipliği E5d'de tek noktaya bağlanacaksa burada interface tanımlanır.
- Client wall, network/provider round-trip, backoff ve tüm attempt süreleri adlarıyla raporlanır. Sağlayıcı server inference sağlamıyorsa `pure_inference_latency_ms=null` ve neden bulunur.
- Error, timeout, filter ve truncation refusal/safety kararı sayılmaz. Ham response, prompt, credential veya kontrolsüz exception kaydı yoktur.

## Kabul

Fake transport/clock ile retry sonrası başarı, kalıcı timeout, terminal config/parse, filter/truncation, deadline, missing ve duplicate resume yollarını sınayan testler gerekir. Fiziksel cap arayüzü varsa hiçbir dispatch cap'i aşmaz. Ağ çağrısı sıfır; mevcut gerçek audit/run artefaktları değişmez. `outcome-latency-contract.md` ve kanıt paketi teslim edilir.

