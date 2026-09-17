# E1a — Araştırma iddiası ve karar matrisi taslağı

Durum: Worker taslağı kabul edildi; insan araştırmacı kararları bekliyor. Kök: `/home/kaan/AI_Search`. Sahip: worker taslağı, insan araştırmacı kararı.  
Önkoşul: `docs/reviews/llm-benchmark/E0-acceptance.md`. Ortak kurallar: [worker sözleşmesi](llm-benchmark-worker-contract.md).

## Hedef

Mevcut belgelerdeki iddiaları dar fixed-history technical pilot construct'ına göre haritala. Bu görev etkili protokolü veya mühürlü belgeleri değiştirmez; araştırmacının inceleyeceği `DRAFT / NOT EFFECTIVE` karar matrisi üretir.

## Kapsam

Oku: üst plan E1a, `README.md`, `docs/research_questions.md`, `docs/phase7e_pre_evaluation_clarification.md`, `docs/ROADMAP.md`, rapor §2, §3, §7, §12, §14–16 ve E0 findings. Mühürlü belgeler salt okunurdur.

Yaz: `docs/reviews/llm-benchmark/E1a/claim-decisions.md`, README, komut/karşılaştırma kanıtları. README veya araştırma belgelerini bu pakette düzenleme.

## İstenen matris

Her iddia için kaynak konumu, mevcut ifade, `koru/daralt/terk et/geleceğe ertele`, önerilen ifade, kanıt, etkilenen hipotez/çıktı ve insan kararı alanı ver. En az şunları kapsa: whole-history packet, latent intent, pure user evidence, D'nin rolü, AM tanısal sınırı, NB/NH sınırı, assistant stance tabakaları, external validity, novelty/“first”, calibration ve contamination.

Önerilen en güçlü yayın iddiasını taslak olarak ver; yön, model, etki büyüklüğü veya başarı sonucu doldurma. D'nin yokluğunu semantic mekanizma kanıtı; AM'yi DU assistant etkisinin tanımlanması; hash'i contamination yokluğu sayma.

## Kabul ve durma

Matris belge drift'ini görünür kılar ve mekanizma iddialarını construct'tan ayırır. Hiçbir hüküm insan onayı olmadan `APPROVED` olmaz. Test gereksizdir; bağlantılar, dosya konumları, `git diff --check` ve frozen hashler doğrulanır. Worker taslağı teslim edip durur; ana inceleyici ve araştırmacı kararı E1a kabul kaydında tutulur.
