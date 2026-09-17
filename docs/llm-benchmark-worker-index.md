# LLM Benchmark — Worker brief dizini

Üst plan: [LLM Benchmark değerlendirmesi ve eylem planı](llm-benchmark-assessment-and-plan.md).  
Ortak sözleşme: [Worker teslim ve kanıt sözleşmesi](llm-benchmark-worker-contract.md).  
İnceleme düzeni: [İnceleme dizini README](reviews/llm-benchmark/README.md).

**Kampanya durumu:** 2026-09-10 tarihinde kullanıcı kararıyla [insan-girdisi kapısında donduruldu](reviews/llm-benchmark/PROJECT-FROZEN-2026-09-10.md). Aktif worker briefi yoktur. Yeniden başlatmada önce dondurma kaydındaki bütünlük ve insan karar/rater önkoşulları doğrulanır.

Bu dizin, küçük worker modellerine tek seferde verilecek dar görevleri listeler. Her worker yalnız kendi briefini, ortak sözleşmeyi, belirtilen önkoşul kabul kayıtlarını ve briefteki kaynakları okumalıdır. Bir sonraki göreve kendiliğinden geçmez.

## Yürütme sırası

| Sıra | Brief | Sahip | Önkoşul | Durum |
| --- | --- | --- | --- | --- |
| 1 | [E0](llm-benchmark-E0-task.md) | worker | plan | [Kabul edildi](reviews/llm-benchmark/E0-acceptance.md) |
| 2 | [E1a](llm-benchmark-E1a-task.md) | worker + araştırmacı kararı | E0 kabulü | [Taslak kabul; insan kararı bekliyor](reviews/llm-benchmark/E1a-acceptance.md) |
| 3 | [E1b](llm-benchmark-E1b-task.md) | worker + araştırmacı kararı | E0 kabulü | [Taslak kabul; insan kararı bekliyor](reviews/llm-benchmark/E1b-r6-acceptance.md) |
| 3R | [E1b-R1](llm-benchmark-E1b-revision-task.md) | worker + araştırmacı kararı | E1b revision kararı | [Düzeltme gerekli](reviews/llm-benchmark/E1b-r1-acceptance.md) |
| 3R2 | [E1b-R2](llm-benchmark-E1b-r2-task.md) | worker + araştırmacı kararı | E1b-R1 revision kararı | [Düzeltme gerekli](reviews/llm-benchmark/E1b-r2-acceptance.md) |
| 3R3 | [E1b-R3](llm-benchmark-E1b-r3-task.md) | worker + araştırmacı kararı | E1b-R2 revision kararı | [Düzeltme gerekli](reviews/llm-benchmark/E1b-r3-acceptance.md) |
| 3R4 | [E1b-R4](llm-benchmark-E1b-r4-task.md) | worker + araştırmacı kararı | E1b-R3 revision kararı | [Düzeltme gerekli](reviews/llm-benchmark/E1b-r4-acceptance.md) |
| 3R5 | [E1b-R5](llm-benchmark-E1b-r5-task.md) | worker + araştırmacı kararı | E1b-R4 revision kararı | [Düzeltme gerekli](reviews/llm-benchmark/E1b-r5-acceptance.md) |
| 3R6 | [E1b-R6](llm-benchmark-E1b-r6-task.md) | worker + araştırmacı kararı | E1b-R5 revision kararı | [Kabul](reviews/llm-benchmark/E1b-r6-acceptance.md) |
| 4 | [E1c](llm-benchmark-E1c-task.md) | worker + araştırmacı kararı | E1a ve düzeltilmiş E1b taslakları | [Düzeltme gerekli](reviews/llm-benchmark/E1c-acceptance.md) |
| 4R | [E1c-R1](llm-benchmark-E1c-r1-task.md) | worker + araştırmacı kararı | E1c revision kararı | [Düzeltme gerekli](reviews/llm-benchmark/E1c-r1-acceptance.md) |
| 4R2 | [E1c-R2](llm-benchmark-E1c-r2-task.md) | worker + araştırmacı kararı | E1c-R1 revision kararı | [Düzeltme gerekli](reviews/llm-benchmark/E1c-r2-acceptance.md) |
| 4R3 | [E1c-R3](llm-benchmark-E1c-r3-task.md) | worker + araştırmacı kararı | E1c-R2 revision kararı | [Taslak kabul; insan kararı bekliyor](reviews/llm-benchmark/E1c-r3-acceptance.md) |
| 5 | [E2a](llm-benchmark-E2a-task.md) | worker | E0 kabulü | [Düzeltme gerekli](reviews/llm-benchmark/E2a-acceptance.md) |
| 5R | [E2a-R1](llm-benchmark-E2a-r1-task.md) | worker | E2a revision kararı | [Düzeltme gerekli](reviews/llm-benchmark/E2a-r1-acceptance.md) |
| 5R2 | [E2a-R2](llm-benchmark-E2a-r2-task.md) | worker | E2a-R1 revision kararı | [Kabul](reviews/llm-benchmark/E2a-r2-acceptance.md) |
| 6 | [E2b](llm-benchmark-E2b-task.md) | worker | E2a, ilgili E1 sözleşmesi | Donduruldu; insan E1 kararı bekliyor |
| 7 | [E2c](llm-benchmark-E2c-task.md) | worker | E1b onayı, E2a/E2b | Bekliyor |
| 8 | [E3a](llm-benchmark-E3a-task.md) | worker, salt okunur stimulus | E0 kabulü | [Düzeltme gerekli](reviews/llm-benchmark/E3a-acceptance.md) |
| 8R | [E3a-R1](llm-benchmark-E3a-r1-task.md) | worker, salt okunur stimulus | E3a revision kararı | [Düzeltme gerekli](reviews/llm-benchmark/E3a-r1-acceptance.md) |
| 8R2 | [E3a-R2](llm-benchmark-E3a-r2-task.md) | worker, salt okunur stimulus | E3a-R1 revision kararı | [Kabul](reviews/llm-benchmark/E3a-r2-acceptance.md) |
| 9 | [E3b](llm-benchmark-E3b-task.md) | koşullu worker | İnsan kararı ve açık yetki | Donduruldu / kilitli |
| 10 | [E4a](llm-benchmark-E4a-human-task.md) | gerçek insan rater'lar | E1–E3 hazırlık kapısı | Donduruldu; rater yok |
| 11 | [E4b](llm-benchmark-E4b-human-task.md) | araştırmacı | E4a | İnsan işi |
| 12 | [E5a](llm-benchmark-E5a-task.md) | worker | E1c onayı | Bekliyor |
| 13 | [E5b](llm-benchmark-E5b-task.md) | worker | E1c onayı | Bekliyor |
| 14 | [E5c](llm-benchmark-E5c-task.md) | worker | E5a/E5b sözleşmeleri | Bekliyor |
| 15 | [E5d](llm-benchmark-E5d-task.md) | worker | E4b, E5a–E5c | Bekliyor |
| 16 | [E6a](llm-benchmark-E6a-task.md) | worker | E1c onayı, E5a schedule | Bekliyor |
| 17 | [E6b](llm-benchmark-E6b-task.md) | worker | E1c onayı | Bekliyor |
| 18 | [E6c](llm-benchmark-E6c-task.md) | worker | E5 ve E6a/E6b | Bekliyor |
| 19 | [E7](llm-benchmark-E7-review-task.md) | ana inceleyici + araştırmacı | E0–E6 | Kilitli |

E2a ve E3a, E0 kabulünden sonra paralel yürütülebilir. E1 onayından sonra E5a/E5b, E6b ve insan hazırlığı bağımsız ilerleyebilir. Aynı QC dosyalarını değiştiren E2a–E2c sıralıdır. Bu tablo uygulama yetkisi veya bilimsel onay değildir.
