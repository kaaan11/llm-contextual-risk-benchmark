# LLM Benchmark — Proje dondurma kaydı

Tarih: **2026-09-10**  
Karar: **DONDURULDU / İNSAN GİRDİSİ BEKLENİYOR**  
Başlangıç commit'i: `9dd9d31607b3d97c02fe3ef9b7cfb68b4a3ed50e`

## Neden durduruldu?

Projede Phase 7G'nin gerektirdiği iki bağımsız gerçek insan rater mevcut değildir. Ayrıca E1a, E1b ve E1c için hazırlanıp teknik açıdan kabul edilen bilimsel karar taslakları araştırmacı tarafından yürürlüğe alınmamıştır. Ajan bu girdileri üretemez veya insan kararı yerine geçecek anotasyon, referans, adjudication ya da `KEEP` kararı yazamaz.

Bu nedenle yeni worker briefi aktif değildir. E2b, E2c, E3b, E4 ve bunlara bağlı sonraki işler başlatılmayacaktır. Phase 8 gerçek model değerlendirmesi veya API çağrısı kesinlikle kapalıdır.

## Kabul edilmiş son durum

- E0 kabul edildi: [kabul kaydı](E0-acceptance.md).
- E2a, R2 teslimiyle kabul edildi: [kabul kaydı](E2a-r2-acceptance.md).
- E3a sorun envanteri, R2 teslimiyle kabul edildi: [kabul kaydı](E3a-r2-acceptance.md).
- E1a teknik taslağı kabul edildi; insan bilimsel kararı bekliyor: [kabul kaydı](E1a-acceptance.md).
- E1b teknik taslağı R6 ile kabul edildi; insan bilimsel kararı bekliyor: [kabul kaydı](E1b-r6-acceptance.md).
- E1c teknik taslağı R3 ile kabul edildi; insan bilimsel kararı bekliyor: [kabul kaydı](E1c-r3-acceptance.md).

Worker teslimlerinin teknik kabulü protokol değişikliklerini yürürlüğe sokmaz ve Phase 7G/E4 insan kapısını kapatmaz.

## Dondurma anındaki bütünlük kanıtı

| Artefakt | SHA-256 / kayıt |
| --- | --- |
| `docs/phase7e_preregistration.md` | `7d46e0fba94a88beaa27a4c41efa209e3c89619b3f3dd5e96877997aa99bf87c` |
| `docs/phase7e_annotation_protocol.md` | `41c628b801a08d85e52d3f6fe79eb711e9e949b76ad29cdc425356fb742fefa4` |
| `docs/PHASE_7D_EXPERIMENTAL_DESIGN.md` | `e120652648bbec68cca3bed95ce924f0ce27f2f1cc2661334edea62f4fd23688` |
| `dataset/pilot/multiturn/stimulus_dataset_v1.json` | `2f78e79e19d844b84b6bc06a0c2bef47e19283cc7c54b91f6ae283e1a74af077` |
| `results/dataset_audit/phase7e_review_history.jsonl` | 51 satır; `e145afed133bb4f7995d0e1fffb6d169f51fbd29ce9e0b6edbd73c19cf3b866c` |
| `results/dataset_audit/phase7g_review_history.jsonl` | 5 satır; `23755e0f2a37db370f9a3532a3a7e495e0f71c33e75dbb73c9e7632b8a550a15` |

Çalışma ağacı dondurma anında bilinçli olarak dirty/untracked durumdadır; kabul edilmiş worker kodları, görev kartları ve inceleme paketleri henüz commitlenmemiştir. `.gitignore` değişikliği ve `uv.lock` kullanıcıya ait mevcut çalışma olarak korunmuştur. Bu kayıt temiz bir commit veya release etiketi iddiası değildir.

## Yeniden başlatma kapısı

Yeni oturum önce bu dosyayı, [worker indeksini](../../llm-benchmark-worker-index.md), [ana planı](../../llm-benchmark-assessment-and-plan.md) ve yukarıdaki en son kabul kayıtlarını okumalıdır. Ardından:

1. Çalışma ağacının ve yukarıdaki mühürlü/audit hashlerinin dondurma kaydıyla uyumu doğrulanır. Audit geçmişi append-only değerlendirilir; ek satırlar varsa eski 51/5 satırlık prefix'in korunduğu kanıtlanır.
2. Araştırmacı E1a/E1b/E1c karar matrislerini açık ve izlenebilir biçimde onaylar veya revize eder. Bu karar verilmeden E2b açılmaz.
3. E3a envanterindeki maddeler için insan `KEEP/REVISE/REJECT` kararları kaydedilir. Stimulus değişikliği gerekirse ayrıca açık yazma yetkisi ve resmi protokol eki gerekir; v1 yerinde değiştirilmez.
4. Phase 7G/E4 için iki bağımsız gerçek insan rater ve maruziyet/provenance düzeni sağlanır. İnsan bulunmadan annotation veya kabul manifestosu üretilmez.
5. Önkoşullar doğrulandıktan sonra koordinatör yalnız sıradaki tek açık briefi etkinleştirir. Phase 8 ancak iki-rater insan QC kapısı ve sonraki go/no-go koşulları tamamlanınca ayrıca yetkilendirilebilir.

Projeyi sürdürmek için önerilen yeni oturum başlangıç cümlesi: `docs/reviews/llm-benchmark/PROJECT-FROZEN-2026-09-10.md kaydından devam et; önce bütünlük ve insan-girdi önkoşullarını doğrula.`
