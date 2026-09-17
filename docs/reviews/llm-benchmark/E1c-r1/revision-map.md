# E1c-R1 — Revizyon haritası (revision map)

E1c acceptance R1–R5'in `E1c-r1` karşılığı. `../E1c/` kanıtı değişmedi. Korunanlar: nominal
madde-eşit yaklaşım, legacy ayrımı, karşıörnekler, `DRAFT / NOT EFFECTIVE`.

| Blokaj | E1c kusuru | Düzeltme (dosya/bölüm) | Kabul karşılama |
| --- | --- | --- | --- |
| R1 payda | `uncertain`/`partial`/gap/applicability davranışı tanımsızdı | `estimand-contract.md` §2 kapalı tablo (E-act/E-harm/E-util); H-U1/H-U2, H-T1a/H-T1b, D-A/D-B seçenek (onaysız) | Her durum tek payda davranışına veya seçeneğe sahip |
| R2 job | Anahtar model/run boyutsuzdu | §3 canonical job + attempt/gözlem + E5a ref | İki model/run duplicate sayılmaz; retry yeni gözlem sayılmaz |
| R3 strata | `stratified_by_assistant_stance` ekseni yoktu | §1 iki eksen (kategori + stance) + havuz yasağı + 0/0 raporu | Strata zorunlu, ayrı, havuzsuz |
| R4 CI | "Exact CI" + TBD çelişkisi; CP kapsamı yanlıştı | §5 O-C1–O-C4 (varsayım/sınır/kapsam); CP tek-oranla sınırlı; exact vaadi yok | TBD exact sunulmaz; CP doğru kapsamda |
| R5 payda | D-A/D-B uygulanmış gibi yazılmıştı | §6 seçenek tablosu + "uygulanan kural YOK"; teknik kapılar ayrı | Seçimsiz kural yok |
| Matematik | KÖ-1/KÖ-3 rapor sayılarıydı | §7 deterministik yeniden hesap (stdlib; logda) + KÖ-3 16/14 kurulumu | p=1.862645149230957e-09; E=5.75; P=0.5281675159 |

## Korunanlar (yeniden tasarım yok)

- E1c endpoint ailesi, legacy haritası gövdesi, amendment mekaniği, H3/F4/eşik seçenekleri,
  test/CI varsayımları, multiplicity, hipotez haritası.
- Etkilenen legacy satırları yalnız `legacy-delta.md`'de (L-05/L-09/L-12 revize + L-16/L-17/L-18 ek).
- Amendment tam metni `../E1c/amendment-draft.md`'de durur; delta `amendment-delta.md`'dedir.

## Etkilenen dosyalar

- Değişen (bu dizinde yeni): `estimand-contract.md` (v0.2), `amendment-delta.md`,
  `legacy-delta.md`.
- Değişmeyen: `../E1c/*`, mühürlü belgeler, stimulus, audit/QC, kod, insan rating'leri.
