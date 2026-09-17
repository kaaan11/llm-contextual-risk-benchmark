# E7 — Son GO/NO-GO incelemesi ve canlı yürütüme devir

Durum: **ANA İNCELEYİCİ / ARAŞTIRMACI İŞİ; E0–E6 TAMAMLANMADAN KİLİTLİ.**

## Amaç

Kabul edilmiş teknik teslimleri, etkin insan-onaylı protokolü, gerçek Phase 7G popülasyonunu ve offline provayı bağımsız yeniden doğrulayıp somut bir GO/NO-GO kaydı üretmek. Bu kayıt kendi başına canlı API çağrısını başlatmaz.

## İnceleme kapsamı

1. E0–E6 acceptance kayıtları, açık maddeler ve çalışma ağacı diff/hash bağı.
2. Mühürlü eski protokol ile onaylı amendment/sürüm zinciri; stimulus ve Layer-B/accepted population kimlikleri.
3. Schedule, exact model/provider/system/generation config, payload contract, retry/deadline, physical cap ve completion manifest.
4. Analysis definition, sensitivity varsayımları, missing/duplicate/coverage ve AM vs DU/NH stance tabakaları.
5. README, PROJECT_STATUS, CURRENT_STATE_AND_NEXT_STEPS, ROADMAP ve power belgesi arasındaki drift. Mühürlü belge yalnız resmi ek/sürüm yoluyla ele alınır.

## Bağımsız doğrulama

Ana inceleyici worker loglarına dayanmakla yetinmez: kritik QC kapısı, zero-dispatch preflight, schedule sayıları, payload capture, cap, failure ledger, analysis karşıörnekleri, offline integration, frozen hash ve append-only prefix kontrollerini yeni geçici dizinde yeniden çalıştırır. Tam test sonucu ile hedefli yeniden kontrol sayısını ayrı raporlar.

## Teslim

`docs/reviews/llm-benchmark/E7-go-no-go.md` şu kimlikleri taşır: HEAD/diff, protocol/amendment, dataset/stimulus, accepted population/reference, exact run config/payload, expected schedule, analysis version, model sayısı, logical job/physical cap/human scoring bütçesi ve açık riskler. Her açık madde `GO blocker / claim limitation / deferred feature` olarak sınıflanır.

GO için E4 gerçek iki-rater kapısı, E5 execution ve E6 analysis/prova birlikte kapanmalıdır. Sağlayıcı/model erişilebilirliği zamanı geldiğinde resmi kaynakla yeniden doğrulanır; unavailable model sessizce değiştirilmez. GO sonrası canlı komut ancak kullanıcı tarafından ayrıca yetkilendirilirse çalıştırılır.

