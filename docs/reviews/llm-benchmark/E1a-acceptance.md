# E1a — Ana inceleyici kabul kararı

Tarih: 2026-09-09. İnceleyici: Sol. Durum: **WORKER TASLAĞI KABUL EDİLDİ; İNSAN ARAŞTIRMACI KARARLARI BEKLİYOR. E1 AÇIK.**

## İnceleme ve bağımsız kanıt

[E1a briefi](../../llm-benchmark-E1a-task.md), worker README'si, `claim-decisions.md`, comparisons, başlangıç/bitiş hashleri, komut defteri, diff ve loglar incelendi. Teslim yalnız `docs/reviews/llm-benchmark/E1a/` altında yeni belge/kanıt üretmiş; README, araştırma belgeleri, mühürlü protokol, stimulus, QC ve audit kayıtları değiştirilmemiştir.

Ana inceleyici şu noktaları kaynaklardan yeniden kontrol etti:

- Matris C-01–C-14 olmak üzere 14 tekil satır içeriyor. Whole-history construct, latent intent, pure user evidence, D, AM, NB/NH, assistant stance, external validity, novelty, calibration, contamination, iki-insan primary, eski RQ kapsamı ve güç/hipotez drift'i kapsanmış.
- Her satır kaynak, mevcut/önerilen ifade, karar türü, kanıt, etkilenen çıktı ve boş insan-kararı alanı taşıyor. 14 insan-kararı alanının hiçbiri `APPROVED` yapılmamış.
- `claim-decisions.md` başlığı ve yayın iddiası `DRAFT / NOT EFFECTIVE`; yön, model adı, etki büyüklüğü veya başarı sonucu doldurulmamış.
- Clarification C3–C8'in 7 shared / 43 differing tabakaları, AM non-control ve D limitation hükümleri matrisle uyumlu. Eski `research_questions.md` 300 örnek/Pareto/savunma kapsamı ile ROADMAP'in judge + %20 insan drift'i görünür.
- `commands.jsonl` altı boşluksuz, geçerli JSON kaydı içeriyor; hepsinin exit code'u 0 ve üç log hedefi mevcut. Checksum manifestosundaki tüm girdiler doğrulandı; E0'daki self-reference sorunu tekrarlanmamış.
- Teslim içi Markdown bağlantıları geçerli ve `git diff --check` temiz.

Bağımsız frozen kontrolünde protocol per-file hashleri ve composite `47ae3fed4117639ef2575135a6ca63f000f4fcc8c052c629355f6ccf4bbcfc6f` eşleşti. Stimulus v1 SHA-256 `2f78e79e…`; audit history 51/5 satır ve E0'da kabul edilen hashlerle aynı. Blind key içeriği teslim paketine taşınmamış. Kod/test davranışı değişmediği için E1a kapsamında test çalıştırılmadı.

## Kabul ölçütleri

| Ölçüt | Kanıt | Sonuç |
| --- | --- | --- |
| Zorunlu iddia alanlarının tamamı haritalanmış | C-01–C-14 | PASS |
| Belge drift'i görünür | Giriş drift listesi + C-12/C-13/C-14 | PASS |
| Construct, mekanizma ve external-validity iddiaları ayrılmış | C-01–C-08, kontrol listesi | PASS |
| Yayın cümlesi sonuç/model/yön uydurmuyor | Taslak yayın iddiası | PASS |
| İnsan kararı uydurulmamış | 14 boş karar alanı, DRAFT statüsü | PASS |
| Mühürlü ve append-only veriler korunmuş | Worker hashleri + bağımsız kontrol | PASS |
| Teslim kanıtları makinece doğrulanabilir | JSONL, checksum, link ve diff kontrolü | PASS |

## Zorunlu ifade düzeltmeleri ve insan karar sınırı

Worker ham teslimi kanıt olarak değiştirilmeden korunmuştur. Etkin amendment veya güncel iddia belgesine geçerken iki taslak ifade düzeltilmelidir:

1. **C-04:** “DU004 türü kusurlu D'ler versioned revise edilir” ifadesi insan stimulus hükmünü peşinen veriyor. E3a yalnız envanter çıkaracak; araştırmacı kusuru doğrulayıp REVISE seçerse E3b sürümleme yapabilir. Etkin metin koşullu yazılmalıdır.
2. **C-06:** “bu script altında spurious escalation/laundering gözlenmedi/geçti” henüz model sonucu yokken geçmiş zamanlı sonuç bildiriyor. Pre-evaluation sözleşmesi “değerlendirilecek/yalnız şu dar yorumu destekleyebilir” biçiminde olmalı. Gerçek gözlem dili ancak geçerli Phase 8 sonrası doldurulur.

Yayın iddiasındaki “karşılaştırdık/belgeledik” geçmiş zamanı, sonuç sonrası kullanılacak bir cümle şablonu olarak kabul edilebilir; pre-evaluation belgede yer alırsa açık gelecek/plan diliyle yazılmalıdır.

Bu kabul, C-01–C-14 önerilerinin bilimsel olarak onaylandığı anlamına gelmez. İnsan araştırmacı `koru/daralt/terk et/ertele` kararlarını ve yayın kapsamını E1 bilimsel kapısı kapanmadan açıkça kaydetmelidir. Worker teslimi karar vermeye yeterli bir taslak olarak kabul edilmiştir.

## Karar ve devam

E1a worker kapsamı tamamlandı ve kabul edildi. En güçlü materyal sonuç, mevcut whole-history clarification'ın korunabileceği; latent-intent/pure-user-evidence/genel-safety/first/calibration iddialarının ise daraltma veya terk kararı gerektirdiğini görünür kılan karar matrisidir. Dış literatür bağımsız doğrulanmadığı için novelty hükmü rapor kaynağı sınırında kalır.

Sıradaki worker paketi [E1b — nominal davranış, harm, utility ve Layer-B rubrik taslağı](../../llm-benchmark-E1b-task.md). E1b taslağı E0 kabulüne dayanarak başlayabilir; E1a insan kararları E1c amendment ve E1 genel kapısından önce kapanmalıdır. E1a kabulü Phase 7G veya Phase 8'i açmaz.

