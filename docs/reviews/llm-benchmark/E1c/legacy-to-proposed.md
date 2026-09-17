# E1c — Eski→önerilen haritası (legacy-to-proposed)

**Statü: DRAFT / NOT EFFECTIVE.** Eski kurallar arşivlenir, sessizce değiştirilmez. Yeni statüler
öneridir; onay insan araştırmacınındır.

## Kural haritası

| # | Eski kural (frozen konum) | Eski statü | Önerilen statü | Gerekçe | Etkilenen çıktı |
| --- | --- | --- | --- | --- | --- |
| L-01 | Ordinal Δ_AB/Δ_AC/Δ_BC/Δ_AD aritmetiği (prereg §8:130-138) | Birincil metrik | **KALDIR (arşiv)** | §8'in kendi "not interval" uyarısıyla §8.1 büyüklük karşılaştırması çelişir; monoton recoding karşıörneği (KÖ-2) | H1–H3 yön hesapları; transition sunumu kalır |
| L-02 | D-state makinesi (prereg §8.1:140-154) | Falsifikasyon kontrolü | **KALDIR (arşiv)** | Uzaklık büyüklüğüne dayanır; D'nin semantic güvencesi yok (C-04) | H0b/F2 yorumu → D kohort kontrastları |
| L-03 | `context_effect_observed` bayrağı (prereg §8.2:156-169) | Birincil flag (H1) | **KALDIR (arşiv)**; en fazla "sampled modal discordance" arşiv dili | Sıfır-etki stokastik modelde 5,75/30 pozitif (KÖ-3); madde-düzeyi etki kanıtı olamaz | H1 ifadesi → E ailesi kontrastları |
| L-04 | Wilcoxon signed-rank (prereg §14:245,259-266) | Destekleyici | **KALDIR** (destek rol dahil) | Sıra-büyüklük monoton recoding altında korunmaz; symmetry/ties caveat'leri frozen metinde zaten var | B→C çıkarımı → transition matrix + exact CI (+ opsiyonel sign testi) |
| L-05 | McNemar B/C appropriateness violation (prereg §14:243) | Birincil inferential | **İKİNCİL'e indir (ad değişikliğiyle)** | S01: hata-asimetrisi ölçer, davranış etkisi değil | Ad: *paired-binary error-asymmetry*; korunması insan kararı |
| L-06 | McNemar dual-vs-null yasağı (prereg §14:251-253) | Yasak | **KORU** | Bağımsız gruplar eşleşmiş değildir | Grup karşılaştırması → Fisher (ikincil) |
| L-07 | Fisher dual-vs-null (prereg §14:247) | İkincil | **KORU** | Betimleyici vurgu küçük-eşit gruplara uygundur | Raporlama aynen |
| L-08 | Transition matrix + discordant counts (prereg §14:241-242) | Birincil betimleyici | **KORU + GENİŞLET** (nominal dağılım kontrastları E-act/E-harm/E-util) | Kategori kimlikleri recoding'e dayanıklıdır | Birincil sunum |
| L-09 | Clopper–Pearson (prereg §14:244) | Birincil inferential | **KORU** | Exact, whole-stratum oranlara uygundur | CI raporlaması |
| L-10 | Küçük-hücre yasakları (prereg §14:254-257) | Yasak | **KORU** | n≈5–7 test yok; n<20 bootstrap yok; prevalence yok; cross-model yok | E6b duyarlılık sınırları |
| L-11 | Multiplicity adjustmentsız H1–H3 (prereg §14:268-270) | Beyan | **KORU** (yeni confirmatory eklenirse ayrı amendment) | Betimleyici vurgu; alpha iddiası yok | Raporlama dili |
| L-12 | Unscorable/missing/api_error kuralları (prereg §15:272-283) | Kural | **KORU + ÇEVİR** (yanıt-düzeyi E1b F-görünümü + koşul-dağılım paydası; imputation yok; sessiz düşürme yok) | Tekrarların tamamı korunur; modal-drop kalkar | §3 missing/exclusion politikası |
| L-13 | H3 `median Δ_BC ≥ 0` / F4 `median Δ_BC ≤ 0` (prereg §2:33-34, §19:325-326) | Hipotez/falsifier | **SEÇENEKLİ REVİZYON** (§5 tablo: harm-dili strict veya confirmatory-dışı) | Sıfır iki tarafta; karar verilemez | H3/F4 ifadeleri |
| L-14 | `non-trivial share` (H1), `meaningful/dominant` (F1–F2) | Eşik dili | **SEÇENEKLİ** (kaldır [Öneri] veya pre-set δ_k [TBD]) | Operasyonel değil; güç belgesi Δ≥0,35 tek başına yetmez | H1/F1–F2 ifadeleri |
| L-15 | Power belgesi Δ≥0,35 %80 iddiası + bootstrap önerisi | Doküman | **DÜZELT** (E1c §5 + E6b prospective; frozen n<20 yasağı korunur) | Varyans/discordance yok; küçük-hücre bootstrap frozen'a aykırı | Güç/duyarlılık bölümü |

## Arşiv kaydı (eski kurallar burada korunur)

Superseded kurallar (L-01–L-04 metinleri) frozen belgelerde aynen durur; bu taslak onları
değiştirmez. Etkinleşme sonrası eski kurallar "superseded-by-amendment (tarih/sürüm)" damgasıyla
arşiv bölümünde anılır; analizde kullanılmaz. Eski→yeni fark listesi `amendment-draft.md` §2'dedir.
