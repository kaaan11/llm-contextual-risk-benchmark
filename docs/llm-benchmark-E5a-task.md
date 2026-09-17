# E5a — Beklenen Phase 8 yürütme çizelgesi

Durum: E1c insan onayını bekliyor. Sahip: küçük worker.  
Ortak kurallar: [worker sözleşmesi](llm-benchmark-worker-contract.md).

## Tek paket hedefi

Observed response satırlarından bağımsız, model başına bütün planlanan `item × condition × repetition` işlerini önceden üreten deterministik schedule sözleşmesi ekle. Provider dispatch, retry ve analiz uygulaması bu paketin dışında.

## Kod kapsamı

Oku/değiştir: `scripts/run_phase8_mock_dryrun.py` case builder'ı, `benchmark/types.py`, `benchmark/metadata.py`, config loader/gerekirse yeni küçük `benchmark/schedule.py` ve doğrudan `tests/test_phase8_dryrun.py`/yeni hedefli test. E4b yoksa yalnız mevcut v1 için offline schedule üret; canonical accepted population freeze etme.

## Sözleşme

- Tekil anahtar model/experiment sürümü, research_item_id, condition code ve `repeat_index=1..r` taşır.
- Tam v1 ve r=3 için model başına 513 logical job; condition dağılımı 171×3'tür. D'siz item'a D üretilmez.
- Expected schedule hash'i selection/dataset/protocol/config ve sıra politikasına bağlanır.
- Her iş fresh history taşır. Counterbalanced/interleaved order ve block amacı onaylı E1c ile uyumlu, deterministik ve test edilebilirdir.
- Generation seed stratejisi repeat kimliğini sessizce aynı output garantisi diye sunmaz.
- Retry physical attempt'tir; yeni repeat veya yeni expected job değildir.

## Kabul

Sıra yeniden üretilebilir, anahtarlar unique, eksik/duplicate expected job fixture'ları belirlenebilir ve üç tekrar üç item gibi sayılmaz. Zararsız mock ile payload dispatch olmadan schedule testi yap. `schedule-contract.md`, örnek şema ve standart kanıt paketi teslim et. E5b/E5c'ye geçme.

