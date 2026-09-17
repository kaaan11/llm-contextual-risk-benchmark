# E1b-R3 — Teslim kanıt paketi

Durum: **TAMAMLANDI (worker revizyonu; yeniden inceleme bekleniyor).**
Görev: [E1b-R3 briefi](../../../llm-benchmark-E1b-r3-task.md).
Önkoşul: `../E1b-r2-acceptance.md` (REVISION REQUIRED; iki yerleşim blokajı).
Sözleşme: [worker sözleşmesi](../../../llm-benchmark-worker-contract.md).

## Sonuç

E1b-R2'deki iki yerleşim hatası düzeltildi; R2'nin resolved criterion ve frozen §6.2
düzeltmeleri aynen korundu, başka alanlar yeniden tasarlanmadı.

- **R1:** `scoreable_view`/`unscorable_reason` F5 slotlarından çıkarıldı; F1–F4 + scoreability
  için ayrı Layer-C/post-evaluation `response_rating` zarfı tanımlandı (iki ham slot, stable
  farklı ID, provenance, agreement, ayrı adjudication, ham overwrite yok). §6.2 geçişleri bu
  zarfta çalışır; non-scorable outcome'da zarf oluşmaz.
- **R2:** `contested` F5 kökünde, resolved'dan bağımsız researcher-only alan; handling
  enum'larına girmez, disagreement'tan türemez; `resolved_reference=null` iken atanabilir.
- Kabul örnekleri 5 maddesi `rubric-draft.md` §6T'de karşılandı; uygulanabilirlik tablosu
  katman/zaman ayrımlı (6 Layer-C + 6 Layer-B satırı); gerçek/sentetik insan etiketi üretilmedi.

## Değişen dosyalar (yalnız bu dizin)

- `rubric-draft.md` (v0.4.0: §2T, §7C, §6T, katman/zaman tablosu).
- `schema-draft.json` (v0.4.0: `layer_timing`, `forbidden_cross_layer_fields`,
  `RESPONSE_RATING`, `contested_placement`, 12 satırlı uygulanabilirlik).
- `boundary-cases-r3.md` (yalnız etkilenenler: B-7T revize, B-8T güncelleme).
- `revision-map.md`, `README.md` (bu dosya), `comparisons.md`, `commands.jsonl`,
  `hashes-start.txt`, `hashes-end.txt`, `delivery.diff`, `run-outputs.sha256`, `logs/`.
- `../E1b/`, `../E1b-r1/`, `../E1b-r2/` kanıtları değişmedi (komut 04 ile doğrulandı).
  Üretim kodu, mühürlü belgeler, stimulus, audit/QC, insan rating'leri değişmedi.

## Doğrulamalar (gerçek komutlar; çalıştırılmayan yok)

| # | Komut (özet) | Log | Exit |
| --- | --- | --- | --- |
| 01 | `git rev-parse HEAD`, `status`, `branch`, `log -3` | `logs/01-git-head-status.sh.stdout` | 0 |
| 02 | `python3 --version`, `uv --version` | `logs/02-env.sh.stdout` | 0 |
| 03 | Yapısal kontroller: layer/timing, çapraz-katman yasakları, provenance, §6.2, contested, matris (60+ kontrol) | `logs/03-structural-checks.sh.stdout` | 0 |
| 04 | E1b + E1b-r1 + E1b-r2 ham kanıtı değişmezliği | `logs/04-prior-untouched.sh.stdout` | 0 |
| 05 | Frozen hashler: composite + stimulus 50/171 + audit prefix | `logs/05-frozen-hashes.sh.stdout` | 0 |
| 06 | `git diff --check` + `status` + `delivery.diff` üretimi | `logs/06-diff-check.sh.stdout` | 0 |
| 07 | Teslim içi bağlantı kontrolü (final, PASS) | `logs/07-link-check.sh.stdout` | 0 |
| 08 | `run-outputs.sha256` üretimi (belgeler + log stdout'ları; kendi üretim logu hariç) | `logs/08-run-outputs.sh.stdout` | 0 |

Kontroller rater etiketi üretmez. Not: 03 betiği bir kez betik-içi aşırı-katı dize eşleşmesi
(not metnindeki "contested" kelimesine takıldı) nedeniyle düzeltildi; teslim dosyaları hiç
değişmedi; `commands.jsonl` final geçen koşuyu kaydeder. `commands.jsonl` içinde çalıştırılmayan
komut yoktur; boş satır yoktur. `run-outputs.sha256` kendi üretim logunu kapsamaz; kendi hash'i
`logs/08-run-outputs.sh.stdout` içindedir.

## Olay notu (şeffaflık)

Teslim çalışması sırasında worker, E1b-r3 komutlarının yanında yanlışlıkla E1b-r2'nin
07/08 log adımlarını bir kez daha çalıştırdı (`commands.jsonl`'e 2 yinelenen kayıt + logların
deterministik yeniden yazımı). Teslim içerik dosyaları değişmedi. Onarım: yinelenen 2 kayıt
çıkarılarak `../E1b-r2/commands.jsonl` 8 kayda döndürüldü; manifesto öz-tutarlılığı yeniden
doğrulandı (PASS). Olay öncesi E1b-r3'ün 04 kontrolü (önceki teslimler değişmez) PASS idi;
olay sonrası E1b-r2 manifestosu tekrar PASS verdi. Bu not, onarımın denetlenebilirliği içindir.

## Sınırlılıklar

- Zarf alan adları, migrasyon, ID/version otoritesi (E2c); eşleme + tekrar + H3/F4 (E1c);
  `contested`/payda atamaları insan onayı bekler (`APPROVED` yok).
- Dış literatür bağımsız taranmadı.

## Devam

Teslimden sonra durulur. Sıradaki önkoşul: ana inceleyicinin yeniden incelemesi.
Kabul olmadan E1c/E2c başlamaz; Phase 7G/8 kapalıdır.
