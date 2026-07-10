# i18n extraction pipeline


The global OverMortal build ships full localization for zh_cn/en/de/ru/es (per `apk_analysis/om/ex/assets/i18n_config.json`). Extraction (done 2026-07-07):

1. Language tables are `lua64_config_lua_us_i18n_0..6.lua.bytes.unity3d` in the lua asset pack. Decrypt with `apk_analysis/om/decrypt_lua.py <entry> decrypted` (needs UnityPy — installed in the project `.venv`).
2. Decrypted LuaJIT bytecode stores each string as: `<zh key>\x01\x00\x04\x07es<S>\x07de<S>\x07ru<S>\x07en<S>` where each `<S>` is uleb128(len+5)-prefixed UTF-8. Parse by scanning for `\x01\x00\x04\x07es`.
3. Results: `apk_analysis/i18n_all.json` (130,039 EN→{ru,de,es,zh} entries, gitignored) and `apk_analysis/i18n_en_ru.json`. Curated 78-term app glossary committed at `data/i18n_glossary.json`.

Gotchas: the plain "Gush" entry is Venom Gush ("Поток яда") — fruit gush uses "поток" (see the gush-guarantee toast string). Official RU stage names are non-literal (Nascent Soul = "Пробуждение", Incarnation = "Формирование", Voidbreak = "Преодоление"). The RU localization itself sometimes leaves "Gush"/"Respira Stone" untranslated.
