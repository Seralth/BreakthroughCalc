"""Tiny gettext-style i18n for the desktop GUI.

tr(s) looks up the English source string in the current language's dict and
falls back to English (s itself). Game terms come verbatim from the game's
own localization (data/i18n_glossary.json / official EN->xx dictionary);
app prose is translated by hand.

reverse(s) maps a translated display string (any language) back to its
English source — used to turn combo display text back into internal keys
and to migrate legacy settings that stored localized display names.
"""

from __future__ import annotations

LANGS = {"en": "English", "ru": "Русский", "de": "Deutsch", "es": "Español", "zh": "中文"}

_current = "en"


def set_lang(code: str):
    global _current
    _current = code if code in LANGS else "en"


def get_lang() -> str:
    return _current


def tr(s: str) -> str:
    if _current == "en":
        return s
    return TRANSLATIONS.get(_current, {}).get(s, s)


def reverse(s: str) -> str:
    """Translated display string (any language) -> English source; identity
    for English/unknown strings."""
    return _REVERSE.get(s, s)


TRANSLATIONS = {
 "ru": {
  "← Back": "← Назад",
  "Calculator": "Калькулятор",
  "Reference": "Справка",
  "Guide": "Гид",
  # -- game terms (official localization) --------------------------------
  "Novice": "Неофит", "Connection": "Подключение", "Foundation": "Фундамент",
  "Virtuoso": "Сотворение", "Nascent Soul": "Пробуждение",
  "Incarnation": "Формирование", "Voidbreak": "Преодоление",
  "Wholeness": "Слияние", "Perfection": "Совершенство", "Nirvana": "Нирвана",
  "Celestial": "Небесный", "Eternal": "Бессмертие", "Supreme": "Высш.",
  "Early": "Начальная", "Middle": "Средняя", "Late": "(Поздняя)",
  "Stage": "Стадия", "Grade": "Ступень", "Half-step": "Половина",
  "Breakthrough": "Переход",
  "None": "Нет", "Common": "Обыч.", "Uncommon": "Необыч.", "Rare": "Редк.",
  "Epic": "Эпич.", "Legendary": "Легендарн.", "Mythic": "Мифич.",
  "Abode Aura": "Аура обители", "Absorption Ratio": "Эфф. поглощения",
  "Aura Gem": "Самоцвет ауры", "Respira": "Дыхание ци", "Strive": "Стремление",
  "Myrimon Fruit": "Фрукт Миримона", "Aura Extractor": "Извлекатель ауры",
  "Gush": "Поток", "Quality": "Качество",
  "Starsea Vase": "Ваза астроморья", "Dual-Star Mirror": "Зеркало двузведья",
  "Timereversal Pearl": "Жемчужина обращения времени",
  "Star Mark": "Звездная метка", "Cultivation Pill": "Пилюля дао",
  # -- window chrome / toolbar -------------------------------------------
  "Breakthrough Calculator": "Калькулятор переходов",
  "Profile:": "Профиль:",
  "New / Save As…": "Новый / Сохранить как…",
  "Delete": "Удалить", "Reset": "Сбросить",
  "Check for updates": "Проверить обновления",
  "Installed: v{}. Checks the latest GitHub release.":
      "Установлено: v{}. Проверяет последний релиз на GitHub.",
  "Update check failed": "Не удалось проверить обновления",
  "Update available: v{}": "Доступно обновление: v{}",
  "Up to date (v{})": "У вас последняя версия (v{})",
  "Donate ♥": "Поддержать ♥",
  "Support development by gifting in-game vouchers.":
      "Поддержите разработку, подарив внутриигровые ваучеры.",
  "Theme:": "Тема:", "Language:": "Язык:",
  "New / Save As": "Новый / Сохранить как",
  "Profile name:": "Имя профиля:",
  "Support the calculator": "Поддержать калькулятор",
  "If the calculator saves you time, you can support development by "
  "gifting in-game vouchers:<ol>"
  "<li>Open <a href='{}'>SEAGM — OverMortal vouchers</a></li>"
  "<li>Pick any voucher amount</li>"
  "<li>Paste the RID below into the site's <b>RID</b> field</li></ol>":
      "Если калькулятор экономит вам время, вы можете поддержать разработку, "
      "подарив внутриигровые ваучеры:<ol>"
      "<li>Откройте <a href='{}'>SEAGM — ваучеры OverMortal</a></li>"
      "<li>Выберите любой номинал</li>"
      "<li>Вставьте RID ниже в поле <b>RID</b> на сайте</li></ol>",
  "Copy RID": "Скопировать RID",
  # -- Cultivation Base group ---------------------------------------------
  "Cultivation Base": "Основа совершенствования",
  "Grade progress": "Прогресс ступени",
  "Apply to Cultivation Speed": "Применить к скорости совершенствования",
  "Cultivation Speed (XP / Cosmoapsis)": "Скорость совершенствования (опыт за фазу инь-ян)",
  "Target Stage": "Целевая стадия",
  "Target half-step": "Целевая половина",
  "Target grade": "Целевая ступень",
  "Optional: a half-step within the target Stage. Blank = start of the Stage.":
      "Необязательно: половина внутри целевой стадии. Пусто = начало стадии.",
  "Optional: a grade within the target half-step. Blank = start of the half-step.":
      "Необязательно: ступень внутри целевой половины. Пусто = начало половины.",
  "Timegate lifts in": "Врата времени откроются через",
  " days": " дн.",
  "Prestock for target (overcap)": "Запас до цели (избыток)",
  "At timegate": "К вратам времени",
  "stocked {} early": "запас готов за {} до врат",
  "short by {}": "не хватает {}",
  "Optional: days until the world-level timegate lifts (shown in-game once someone "
  "reaches the last half-step). Compared against the prestock time. Reminder: use "
  "Myrimon fruits BEFORE the gate — the gate unlocks the next realm, so they lose the +50% highest-realm bonus.":
      "Необязательно: дней до открытия мировых врат времени (видно в игре, когда кто-то "
      "достигает последней половины). Сравнивается со временем накопления запаса. Напоминание: "
      "используйте плоды Миримон ДО врат — врата открывают следующий мир, и плоды теряют бонус +50% высшего мира.",
  "Overcap needed for the target, in the game's own display convention (XP since the "
  "start of the final half-step ÷ that half-step's total), and the time to stock it. "
  "While timegated you stay parked at the Stage cap, so XP accrues at your CURRENT "
  "speed — no future-grade speedups. Slower than the ungated 'Target reached in'.":
      "Необходимый избыток для цели в игровом формате (опыт с начала последней половины ÷ "
      "её общий объём) и время его накопления. Во время врат вы стоите на пределе стадии, "
      "опыт идёт с ТЕКУЩЕЙ скоростью — без ускорений будущих ступеней. Медленнее, чем "
      "«Целевая стадия через» без врат.",
  "Whether your stocked XP reaches the target before the timegate lifts.":
      "Достигнет ли ваш запас опыта цели до открытия врат времени.",
  "Server #1's Stage (Strive)": "Стадия №1 сервера (Стремление)",
  "Mature server (world level 30+)": "Зрелый сервер (уровень мира 30+)",
  "Your Abode Aura as shown on the Cultivation Bonus screen. With Absorption "
  "Ratio entered, Cultivation Speed = Abode Aura × Absorption Ratio.":
      "Аура обители, как показано на экране «Бонус совершенствования». Если введена "
      "эфф. поглощения, то скорость совершенствования = аура обители × эфф. поглощения.",
  "Optional: your server's #1 cultivator's Stage. Models your Strive stepping DOWN as you "
  "break through toward them (estimated; assumes #1 stays put; live value is server-computed hourly). "
  "Leave blank to hold Strive constant.":
      "Необязательно: стадия лучшего культиватора вашего сервера. Моделирует СНИЖЕНИЕ вашего "
      "Стремления по мере приближения к нему (оценка; предполагается, что №1 стоит на месте; "
      "реальное значение сервер пересчитывает ежечасно). Оставьте пустым, чтобы Стремление не менялось.",
  "Server age changes how Strive is computed. Mature servers (world level 30+, "
  "the common case) use finer level-gap tiers plus a realm-gap bonus (cap ~120%); "
  "young servers use the plain realm-gap table (cap 70%). Only used when "
  "Server #1's Stage is set.":
      "Возраст сервера влияет на расчёт Стремления. Зрелые серверы (уровень мира 30+, "
      "обычный случай) используют более точные уровневые ступени плюс бонус за разницу царств "
      "(предел ~120%); молодые серверы — простую таблицу разницы царств (предел 70%). "
      "Учитывается только если задана стадия №1 сервера.",
  # -- Pills group ----------------------------------------------------------
  "Cultivation Pills": "Пилюли дао",
  "Pill rank": "Ранг пилюли",
  "Cultivation pill effect": "Эффект пилюли дао",
  "Daily pill attempts (shared)": "Дневные попытки пилюль (общие)",
  "Legendary (Gold) used / day": "Легендарн. (золотых) в день",
  "Epic (Purple) used / day": "Эпич. (фиолетовых) в день",
  "Rare (Blue) used / day": "Редк. (синих) в день",
  "Already used today's pills/respira": "Сегодняшние пилюли/дыхание ци уже использованы",
  "Reset in (h)": "Сброс через (ч)",
  "Star Marks (+XP ratio)": "Звездные метки (+опыт, доля)",
  "＋ Add source": "＋ Добавить источник",
  "＋ From catalog": "＋ Из каталога",
  "Total: {} %": "Итого: {} %",
  "source (e.g. technique book, curio)": "источник (напр., книга техник, древность)",
  "varies": "варьируется",
  "info": "справка", "pill limit": "лимит пилюль",
  "Add a pill-effect source (a technique book, a curio, …). Their percentages sum.":
      "Добавьте источник эффекта пилюль (книга техник, древность, …). Их проценты суммируются.",
  "Known pill-effect sources from the game data. Click to add "
  "(prefilled, editable); already-added sources are hidden.":
      "Известные источники эффекта пилюль из данных игры. Нажмите, чтобы добавить "
      "(предзаполнено, можно править); уже добавленные источники скрыты.",
  "Shared daily attempt limit for all cultivation pills (vase red pills are exempt).":
      "Общий дневной лимит попыток для всех пилюль дао (красные пилюли из вазы не считаются).",
  "Check if you've already taken today's daily pills and Respira. The "
  "projection then defers that boost to the next daily reset (today runs "
  "at base speed). Mainly affects short estimates.":
      "Отметьте, если сегодняшние пилюли и дыхание ци уже использованы. Тогда прогноз "
      "отложит этот прирост до следующего ежедневного сброса (сегодня — базовая скорость). "
      "Влияет в основном на короткие оценки.",
  "Hours until the game's daily reset. Only used when the box above is "
  "checked: the projection runs the window until the reset without the "
  "daily pill/Respira XP (and defers event Respira to the reset), then "
  "resumes the normal daily routine.":
      "Часов до ежедневного сброса в игре. Учитывается только при отмеченной галочке выше: "
      "прогноз до сброса идёт без опыта от пилюль/дыхания ци (событийное дыхание ци откладывается "
      "до сброса), затем возобновляется обычный дневной режим.",
  "Your in-game 'Cultivation Pill EXP Bonus' for this pill rarity (mainly from "
  "Constellation Altar Star Marks). Entered as a ratio: 0.10 = +10%.":
      "Ваш внутриигровой бонус опыта пилюль дао для этой редкости (в основном от звездных меток "
      "Алтаря созвездий). Вводится долей: 0.10 = +10%.",
  "Attempts used: {} / {} (shared; vase red pills exempt)":
      "Использовано попыток: {} / {} (общие; красные пилюли из вазы не считаются)",
  "  ⚠ over limit — extra pills won't count":
      "  ⚠ сверх лимита — лишние пилюли не засчитаются",
  # -- Artifacts group -------------------------------------------------------
  "Creation Artifacts": "Артефакты творения",
  "Artifact": "Артефакт", "Star": "Звезда", "Skin": "Облик", "Charge": "Зарядить",
  "Transmog skin: refined pills give +8% Cultivation EXP":
      "Облик: очищенные пилюли дают +8% опыта дао",
  "Transmog skin: Duplication consumes 10% less Energy":
      "Облик: дублирование потребляет на 10% меньше энергии",
  "Transmog skin: Timereversal Pearl Energy Cost -10%":
      "Облик: стоимость энергии жемчужины обращения времени -10%",
  "Daily Energy Charge: 30 Fateum/Destium adds 100 Energy to this artifact, once per day. Check if you use it every day.":
      "Ежедневная зарядка: 30 фатеума/дестиума добавляют 100 энергии этому артефакту, раз в день. "
      "Отметьте, если пользуетесь каждый день.",
  "Vase input pill": "Входная пилюля вазы",
  "Blue/White": "Синяя/белая", "Purple (Epic)": "Фиолетовая (эпич.)",
  "Gold (Legendary)": "Золотая (легендарн.)",
  "Which pill quality you refine into red pills. Refines are discounted by input "
  "quality (Epic -5%, Legendary -20% Energy), so feeding gold pills yields extra "
  "red pills over time. Base cost also depends on pill rank (75-100 energy).":
      "Какое качество пилюль вы очищаете в красные. Очистка дешевеет с качеством входа "
      "(эпич. -5%, легендарн. -20% энергии), поэтому золотые пилюли со временем дают больше "
      "красных. Базовая стоимость также зависит от ранга пилюли (75-100 энергии).",
  "EXP per 10 energy": "Опыт за 10 энергии",
  # -- Respira group ---------------------------------------------------------
  "Attempts / day": "Попыток в день",
  "Sources…": "Источники…",
  "Extra attempts today": "Доп. попытки сегодня",
  "Base EXP / attempt": "Базовый опыт за попытку",
  "Your daily Respira attempt limit as shown in-game (base + permanent "
  "bonus attempts). The base limit is 10/day. "
  "Leave out temporary event attempts.":
      "Ваш дневной лимит попыток дыхания ци, как показано в игре (базовые + постоянные "
      "бонусные попытки). Базовый лимит — 10 в день. Временные событийные попытки не учитывайте.",
  "One-off extra Respira attempts available today only (event/item). "
  "Credited once, not as a daily rate.":
      "Разовые дополнительные попытки дыхания ци только на сегодня (событие/предмет). "
      "Засчитываются один раз, а не как дневная норма.",
  "The base (non-crit) Cultivation EXP from one Respira attempt — see the "
  "note below the field.":
      "Базовый (без крита) опыт дао за одну попытку дыхания ци — см. примечание под полем.",
  "Known Respira bonus sources. Checkable entries add/remove daily "
  "attempts from the field. Greyed entries are informational only: "
  "Respira EXP bonuses are already inside your in-game EXP tooltip, "
  "and pill-attempt bonuses belong in the Daily pill attempts input.":
      "Известные источники бонусов дыхания ци. Отмечаемые пункты добавляют/убирают дневные "
      "попытки в поле. Серые пункты — только для справки: бонусы опыта дыхания ци уже входят "
      "в игровую подсказку опыта, а бонусы попыток пилюль вводятся в поле дневных попыток пилюль.",
  "Do a few Respira: most give the same small EXP (the base — enter that); "
  "some give 2×/5×/10× (crits — ignore, handled automatically).":
      "Сделайте несколько дыханий ци: большинство даёт одинаковый малый опыт (это база — "
      "введите её); некоторые дают 2×/5×/10× (криты — игнорируйте, учитываются автоматически).",
  # -- Myrimon group ----------------------------------------------------------
  "Fruit rank": "Ранг фрукта",
  "Highest rank (+50%)": "Высший ранг (+50%)",
  "No. of Myrimon Fruits": "Кол-во фруктов Миримона",
  "Culti level": "Уровень совершенствования",
  "Quality level": "Уровень качества",
  "Gush level": "Уровень потока",
  "Aura Extractor quality": "Качество извлекателя ауры",
  "Number of Myrimon Fruits processed through the Aura Extractor.":
      "Число фруктов Миримона, обработанных извлекателем ауры.",
  # -- note -------------------------------------------------------------------
  "Note: Strive (the catch-up bonus, from Nascent Soul) fades as you close the gap to "
  "your server's #1. Set \"Server #1's Stage\" above to model that drop-off (estimated); "
  "leave it blank to hold Strive constant. Low/zero-strive players are unaffected either way.":
      "Примечание: Стремление (догоняющий бонус, с Пробуждения) убывает по мере сокращения "
      "отставания от №1 сервера. Задайте выше «Стадию №1 сервера», чтобы смоделировать это "
      "убывание (оценка); оставьте пустым, чтобы Стремление не менялось. На игроков с низким/нулевым "
      "Стремлением это не влияет.",
  # -- results ------------------------------------------------------------------
  "Results (current)": "Результаты (текущие)",
  "Half-step breakthrough in": "Переход половины через",
  "Stage breakthrough in": "Переход стадии через",
  "Target Stage reached in": "Целевая стадия через",
  "Abode Aura (implied)": "Аура обители (расчётная)",
  "Cultivation XP / day": "Опыт дао в день",
  "Effective XP / day": "Эффективный опыт в день",
  "Pill XP / day": "Опыт от пилюль в день",
  "Daily XP share (pills+Respira / gem)": "Доля дневного опыта (пилюли+дыхание ци / самоцвет)",
  "Daily XP share (daily flat XP / gem)": "Доля дневного опыта (фиксированный опыт / самоцвет)",
  "Ascension blessing": "Благословение вознесения",
  "Blessing before Voidbreak Middle": "Благословение до Преодоления (Средняя)",
  "XP elixirs / day": "Эликсиров опыта / день",
  "EXP per elixir": "Опыт за эликсир",
  "Elixir effectiveness": "Эффективность эликсира",
  "Elixir XP / day": "Опыт с эликсиров / день",
  "Share of your effective daily XP that comes from flat sources "
  "(pills + Respira + elixirs), and the Aura Gem's speed bonus on "
  "cultivation. Flat XP does not scale with grade EXP, so a high share "
  "means slower progress at higher grades than raw speed suggests.":
      "Доля эффективного дневного опыта из фиксированных источников (пилюли + дыхание ци + "
      "эликсиры) и бонус скорости самоцвета ауры к совершенствованию. Фиксированный опыт не "
      "растёт с опытом ступеней, поэтому высокая доля означает более медленный прогресс на "
      "высоких ступенях, чем предполагает чистая скорость.",
  "Ascension Virya blessing: persistent absorption-ratio bonus in percentage "
  "points (Perfection (C) +20 and Perfect +20 — with both, enter 40). Enter the "
  "Absorption Ratio above as displayed in-game: it already includes this.":
      "Благословение вирьи вознесения: постоянный бонус к коэффициенту поглощения в процентных "
      "пунктах (Совершенство (C) +20 и Идеал +20 — с обоими введите 40). Коэффициент поглощения "
      "выше вводите как показано в игре: он уже включает этот бонус.",
  "The conditional blessing tier (+20 percentage points) that the game removes "
  "at Voidbreak Middle. Kept separate so projections past Voidbreak Middle "
  "drop it.":
      "Условный уровень благословения (+20 процентных пунктов), который игра убирает на "
      "Преодолении (Средняя). Вводится отдельно, чтобы прогнозы дальше этой точки его не учитывали.",
  "Absorption ratio must exceed the blessing bonus.":
      "Коэффициент поглощения должен превышать бонус благословения.",
  "Auto": "Авто",
  "Sources": "Источники",
  "Vault": "Хранилище",
  "Max shelf": "Макс. полка",
  "Elixirs": "Эликсиры",
  "Attempts and Base EXP fill themselves — attempts from the game's base 10 plus your Vault bonuses, Base EXP from your Stage estimate times your Vault's book bonuses. Overwrite either with your in-game reading (clear a field to go back to the estimate). Most Respira give the same small EXP — that is the base; 2×/5×/10× crits are handled automatically.": "Попытки и базовый опыт заполняются сами — попытки из базовых 10 игры плюс бонусы Хранилища, базовый опыт из оценки по Стадии, умноженной на книжные бонусы Хранилища. Впишите свои игровые значения, чтобы переопределить (очистите поле, чтобы вернуть оценку). Большинство респир дают одинаковый малый опыт — это база; криты 2×/5×/10× учитываются автоматически.",
  "Exclusive manuals give combat stats, so they do not feed the calculator — track them here to keep your whole collection in one place.": "Эксклюзивные техники дают боевые характеристики и не влияют на калькулятор — отмечайте их здесь, чтобы вся коллекция была в одном месте.",
  "Blessings": "Благословения",
  "Base EXP fills itself from your Stage; overwrite it with your in-game reading for exact numbers (clear it to go back to the estimate). Most Respira give the same small EXP — that is the base; 2×/5×/10× crits are handled automatically.": "Базовый опыт заполняется сам по вашей Стадии; впишите своё игровое значение для точных чисел (очистите поле, чтобы вернуть оценку). Большинство респир дают одинаковый малый опыт — это база; криты 2×/5×/10× учитываются автоматически.",
  "Empty shelf": "Очистить полку",
  "Set every book on this shelf back to not learned.": "Вернуть всем книгам на этой полке статус «не изучено».",
  "Record what you own once; fields with a shelf chip can then fill themselves.": "Запишите то, чем владеете, один раз; поля с меткой полки смогут заполняться сами.",
  "Set every book on this shelf to its final tier.": "Установить всем книгам на этой полке последний тир.",
  "Library": "Библиотека",
  "Treasury": "Сокровищница",
  "Companions": "Спутники",
  "Universal": "Общие",
  "Exclusive": "Эксклюзивные",
  "Set each book's tier once; the bonuses it has unlocked flow to the calculator on their own. Dots show the book's chapter bonuses: filled ones are active at your tier, and colored dots mark the cultivation chapters — pill, Respira and abode-aura bonuses worth working toward.":
   "Задайте тир каждой книги один раз; открытые ею бонусы сами попадут в калькулятор. Точки показывают бонусы глав книги: закрашенные активны на вашем тире, а цветные отмечают главы культивации — бонусы пилюль, дыхания ци и ауры обители, к которым стоит стремиться.",
  "Exclusive technique manuals give combat stats only, so they are not tracked yet. This shelf will fill in later.":
   "Эксклюзивные техники дают только боевые характеристики, поэтому пока не отслеживаются. Эта полка заполнится позже.",
  "auto": "авто",
  "shelf": "полка",
  "Click to let the shelf fill this field.":
      "Нажмите, чтобы полка заполняла это поле.",
  "Shelf-managed. Click to edit manually.":
      "Заполняется полкой. Нажмите, чтобы редактировать вручную.",
  "Some owned sources have unrecorded amounts.":
      "У некоторых источников величина ещё не записана.",
  "Record what you own once; fields with a shelf chip can then fill "
  "themselves. Entries marked * carry amounts that are not "
  "exactly established.":
      "Отметьте один раз, чем вы владеете; поля с меткой полки смогут заполняться сами. "
      "Записи со * содержат не до конца установленные величины.",
  "Base values (before sources)": "Базовые значения (без источников)",
  "Daily Respira attempts before any owned source. The game "
  "grants 10 by default.":
      "Дневные попытки дыхания ци без учёта источников. По умолчанию игра даёт 10.",
  "Daily pill limit before any owned source.":
      "Дневной лимит пилюль без учёта источников.",
  "Respira attempts / day": "Попытки дыхания ци / день",
  "Daily pill limit": "Дневной лимит пилюль",
  "Tier ": "Уровень ",
  "Maxed": "Максимум",
  "Amount or unlock tier not exactly established.": "Величина или тир открытия не до конца установлены.",
  "Technique books": "Книги техник",
  "Immortal friends": "Бессмертные друзья",
  "Ascension blessings": "Благословения вознесения",
  "Curios": "Диковинки",
  "Respira Effect books": "Книги эффекта дыхания ци",
  "Fill Base EXP from your Stage's Respira base (measured for "
  "Nascent Soul and Incarnation, extrapolated ×2.0225 per Stage "
  "elsewhere) times (1 + Respira Effect books %).":
      "Заполнить базовый опыт по базе дыхания ци вашей ступени (измерено для Зарождения "
      "души и Перевоплощения, для остальных экстраполяция ×2,0225 за ступень), умноженной "
      "на (1 + % книг эффекта дыхания ци).",
  "Your total ACTIVE 'Respira Effect' percent from technique books. Only "
  "used by the Auto button: Base EXP = Stage base × (1 + this %).":
      "Суммарный АКТИВНЫЙ процент «эффекта дыхания ци» из книг техник. Используется только "
      "кнопкой «Авто»: базовый опыт = база ступени × (1 + этот %).",
  "XP elixirs consumed per day.": "Эликсиров опыта, используемых в день.",
  "Cultivation EXP granted by one elixir (item tooltip).":
      "Опыт совершенствования за один эликсир (из описания предмета).",
  "Elixir effectiveness percent after elixir tolerance (100 = full effect).":
      "Эффективность эликсира в процентах с учётом толерантности (100 = полный эффект).",
  "Mythic pills / day": "Мифич. пилюль в день",
  "Pearl XP / day": "Опыт от жемчужины в день",
  "Respira XP / day": "Опыт дыхания ци в день",
  "XP from fruits": "Опыт от фруктов",
  "Fruit time saved": "Экономия времени от фруктов",
  "Copy results": "Скопировать результаты",
  "Copied ✓": "Скопировано ✓",
  "Pin as A": "Закрепить как A",
  "Pinned A": "Закреплено A",
  "Clear A": "Очистить A",
  "{}% of daily XP / +{}% speed": "{}% дневного опыта / +{}% скорости",
  "Share of your effective daily XP that comes from flat sources "
  "(pills + Respira), and the Aura Gem's speed bonus on cultivation. "
  "Flat XP does not scale with grade EXP, so a high share means slower "
  "progress at higher grades than raw speed suggests.":
      "Доля эффективного дневного опыта из фиксированных источников (пилюли + дыхание ци) "
      "и бонус скорости самоцвета ауры к совершенствованию. Фиксированный опыт не растёт "
      "с опытом ступеней, поэтому высокая доля означает более медленный прогресс на высоких "
      "ступенях, чем предполагает чистая скорость.",
  "(best {} / worst {})": "(лучший {} / худший {})",
  # -- tooltips (calculator inputs) ------------------------------------------
  "The in-game Cultivation Speed: XP gained per 8-second Cosmoapsis tick.":
      "Внутриигровая скорость совершенствования: опыт за 8-секундный такт (фаза инь-ян).",
  "Your Absorption Ratio as a percent (e.g. 27.5). Shown below is the Stage's base for the selected Grade.":
      "Ваша эфф. поглощения в процентах (напр., 27.5). Ниже показана база стадии для выбранной ступени.",
  "How far into the current Grade you are, as a percent.":
      "Насколько вы продвинулись по текущей ступени, в процентах.",
  "Aura Gem rarity. In-game it's claimable storage that accrues gem% of your cultivation speed "
  "(up to 18-32h per claim); modeled as a continuous speed multiplier on cultivation only — "
  "pills/Respira are flat XP and are NOT boosted by the gem.":
      "Редкость самоцвета ауры. В игре это накопитель, собирающий процент вашей скорости "
      "совершенствования (до 18-32 ч на сбор); моделируется как постоянный множитель скорости "
      "только для совершенствования — пилюли/дыхание ци дают фиксированный опыт и самоцветом НЕ усиливаются.",
  "Optional: a future Stage to time your arrival at.":
      "Необязательно: будущая стадия, до которой считать время.",
  "Daily pill-use limit that caps Gold/Purple/Blue usage.":
      "Дневной лимит пилюль, ограничивающий золотые/фиолетовые/синие.",
  "Timereversal Pearl: EXP granted per 10 energy.":
      "Жемчужина обращения времени: опыт за 10 энергии.",
  # -- warnings / diagnostics -------------------------------------------------
  "Implied total aura bonus: {}%  (Abode = 130 × {})":
      "Расчётный общий бонус ауры: {}%  (обитель = 130 × {})",
  "Expected speed: {} / Cosmoapsis": "Ожидаемая скорость: {} за фазу инь-ян",
  "  — entered speed {} is {}% off; one of the readings is stale":
      "  — введённая скорость {} отличается на {}%; одно из значений устарело",
  "Base Absorption: {}%  ·  Strive: {}%": "Базовое поглощение: {}%  ·  Стремление: {}%",
  "  ⚠ below base — Strive can't be negative":
      "  ⚠ ниже базы — Стремление не может быть отрицательным",
  "  ⚠ Strive over the 120% cap": "  ⚠ Стремление выше предела 120%",
  "  · Strive above 120% — normal in later realms (overcap); "
  "cap tables beyond the mortal world aren't modeled.":
      "  · Стремление выше 120% — нормально в поздних царствах (сверх предела); "
      "таблицы пределов за смертным миром не моделируются.",
  "Base Absorption: {}%  (Strive unlocks at Nascent Soul)":
      "Базовое поглощение: {}%  (Стремление открывается на Пробуждении)",
  "  ⚠ below base": "  ⚠ ниже базы",
  # -- engine errors -----------------------------------------------------------
  "Select a valid stage / phase / grade.": "Выберите корректные стадию / половину / ступень.",
  "Cultivation speed and absorption ratio must be > 0.":
      "Скорость совершенствования и эфф. поглощения должны быть > 0.",
  "Target must be after your current grade.": "Цель должна быть после текущей ступени.",
  # -- star upgrade dialog -------------------------------------------------------
  "Upgrade level": "Уровень улучшения",
  "Cultivation Pill Effect: {}%": "Эффект пилюли дао: {}%",
 },

 "de": {
  "← Back": "← Zurück",
  "Calculator": "Rechner",
  "Reference": "Referenz",
  "Guide": "Leitfaden",
  "Novice": "Anfänger", "Connection": "Verbindung", "Foundation": "Stiftung",
  "Virtuoso": "Virtuoso", "Nascent Soul": "Werdende Seele",
  "Incarnation": "Menschwerdung", "Voidbreak": "Leerenbruch",
  "Wholeness": "Ganzheit", "Perfection": "Perfektion", "Nirvana": "Nirwana",
  "Celestial": "Himmlisch", "Eternal": "Ewig", "Supreme": "Höchste",
  "Early": "Früh", "Middle": "Mitte", "Late": "Spät",
  "Stage": "Bühne", "Grade": "Grad", "Half-step": "Halber Schritt zu",
  "Breakthrough": "Durchbruch",
  "None": "Keiner", "Common": "Gemeinsam", "Uncommon": "Ungewöhnlich",
  "Rare": "Selten", "Epic": "Epos", "Legendary": "Legendär", "Mythic": "Mythisch",
  "Abode Aura": "Wohnsitz-Aura", "Absorption Ratio": "Absorptionsverhältnis",
  "Aura Gem": "Aura-Juwel", "Respira": "Atmung", "Strive": "Streben",
  "Myrimon Fruit": "Myrimon-Frucht", "Aura Extractor": "Aura-Extraktor",
  "Gush": "Schwall", "Quality": "Qualität",
  "Starsea Vase": "Starsea-Vase", "Dual-Star Mirror": "Doppelsternspiegel",
  "Timereversal Pearl": "Zeitumkehrperle",
  "Star Mark": "Stern Mark", "Cultivation Pill": "Kultivierungspille",
  "Breakthrough Calculator": "Durchbruch-Rechner",
  "Profile:": "Profil:",
  "New / Save As…": "Neu / Speichern unter…",
  "Delete": "Löschen", "Reset": "Zurücksetzen",
  "Check for updates": "Nach Updates suchen",
  "Installed: v{}. Checks the latest GitHub release.":
      "Installiert: v{}. Prüft das neueste GitHub-Release.",
  "Update check failed": "Update-Prüfung fehlgeschlagen",
  "Update available: v{}": "Update verfügbar: v{}",
  "Up to date (v{})": "Auf dem neuesten Stand (v{})",
  "Donate ♥": "Spenden ♥",
  "Support development by gifting in-game vouchers.":
      "Unterstütze die Entwicklung mit In-Game-Gutscheinen.",
  "Theme:": "Design:", "Language:": "Sprache:",
  "New / Save As": "Neu / Speichern unter",
  "Profile name:": "Profilname:",
  "Support the calculator": "Den Rechner unterstützen",
  "If the calculator saves you time, you can support development by "
  "gifting in-game vouchers:<ol>"
  "<li>Open <a href='{}'>SEAGM — OverMortal vouchers</a></li>"
  "<li>Pick any voucher amount</li>"
  "<li>Paste the RID below into the site's <b>RID</b> field</li></ol>":
      "Wenn dir der Rechner Zeit spart, kannst du die Entwicklung mit "
      "In-Game-Gutscheinen unterstützen:<ol>"
      "<li>Öffne <a href='{}'>SEAGM — OverMortal-Gutscheine</a></li>"
      "<li>Wähle einen beliebigen Gutscheinbetrag</li>"
      "<li>Füge die RID unten in das <b>RID</b>-Feld der Seite ein</li></ol>",
  "Copy RID": "RID kopieren",
  "Cultivation Base": "Kultivierungsbasis",
  "Grade progress": "Grad-Fortschritt",
  "Apply to Cultivation Speed": "Auf Anbaugeschwindigkeit anwenden",
  "Cultivation Speed (XP / Cosmoapsis)": "Anbaugeschwindigkeit (EXP / Cosmoapsis)",
  "Target Stage": "Ziel-Bühne",
  "Target half-step": "Ziel-Halbschritt",
  "Target grade": "Ziel-Grad",
  "Optional: a half-step within the target Stage. Blank = start of the Stage.":
      "Optional: ein halber Schritt innerhalb der Ziel-Bühne. Leer = Beginn der Bühne.",
  "Optional: a grade within the target half-step. Blank = start of the half-step.":
      "Optional: ein Grad innerhalb des Ziel-Halbschritts. Leer = Beginn des halben Schritts.",
  "Timegate lifts in": "Zeittor öffnet in",
  " days": " Tage",
  "Prestock for target (overcap)": "Vorrat fürs Ziel (Überlauf)",
  "At timegate": "Am Zeittor",
  "stocked {} early": "{} vor dem Tor fertig",
  "short by {}": "fehlen {}",
  "Optional: days until the world-level timegate lifts (shown in-game once someone "
  "reaches the last half-step). Compared against the prestock time. Reminder: use "
  "Myrimon fruits BEFORE the gate — the gate unlocks the next realm, so they lose the +50% highest-realm bonus.":
      "Optional: Tage bis das Welt-Zeittor öffnet (im Spiel sichtbar, sobald jemand den letzten "
      "Halbschritt erreicht). Wird mit der Vorratszeit verglichen. Erinnerung: Myrimon-Früchte "
      "VOR dem Tor verwenden — das Tor schaltet das nächste Reich frei, wodurch sie den +50%-Höchstreich-Bonus verlieren.",
  "Overcap needed for the target, in the game's own display convention (XP since the "
  "start of the final half-step ÷ that half-step's total), and the time to stock it. "
  "While timegated you stay parked at the Stage cap, so XP accrues at your CURRENT "
  "speed — no future-grade speedups. Slower than the ungated 'Target reached in'.":
      "Benötigter Überlauf fürs Ziel im Anzeigeformat des Spiels (EP seit Beginn des letzten "
      "Halbschritts ÷ dessen Gesamt-EP) und die Zeit zum Ansparen. Während des Zeittors stehst "
      "du am Stufen-Limit, EP läuft mit AKTUELLER Geschwindigkeit — ohne die Beschleunigung "
      "späterer Grade. Langsamer als das ungegatete „Ziel-Bühne erreicht in“.",
  "Whether your stocked XP reaches the target before the timegate lifts.":
      "Ob dein EP-Vorrat das Ziel erreicht, bevor das Zeittor öffnet.",
  "Server #1's Stage (Strive)": "Bühne der Server-Nr. 1 (Streben)",
  "Mature server (world level 30+)": "Reifer Server (Weltstufe 30+)",
  "Your Abode Aura as shown on the Cultivation Bonus screen. With Absorption "
  "Ratio entered, Cultivation Speed = Abode Aura × Absorption Ratio.":
      "Deine Wohnsitz-Aura wie im Anbaubonus-Bildschirm angezeigt. Mit eingetragenem "
      "Absorptionsverhältnis gilt: Anbaugeschwindigkeit = Wohnsitz-Aura × Absorptionsverhältnis.",
  "Optional: your server's #1 cultivator's Stage. Models your Strive stepping DOWN as you "
  "break through toward them (estimated; assumes #1 stays put; live value is server-computed hourly). "
  "Leave blank to hold Strive constant.":
      "Optional: die Bühne des besten Kultivierenden deines Servers. Modelliert, wie dein "
      "Streben SINKT, während du zu ihm aufschließt (geschätzt; nimmt an, dass Nr. 1 stehen "
      "bleibt; der Live-Wert wird stündlich serverseitig berechnet). Leer lassen, um das "
      "Streben konstant zu halten.",
  "Server age changes how Strive is computed. Mature servers (world level 30+, "
  "the common case) use finer level-gap tiers plus a realm-gap bonus (cap ~120%); "
  "young servers use the plain realm-gap table (cap 70%). Only used when "
  "Server #1's Stage is set.":
      "Das Serveralter ändert die Streben-Berechnung. Reife Server (Weltstufe 30+, der "
      "Normalfall) nutzen feinere Stufenabstands-Staffeln plus einen Reichsabstands-Bonus "
      "(Obergrenze ~120%); junge Server die einfache Reichsabstands-Tabelle (Obergrenze 70%). "
      "Wird nur genutzt, wenn die Bühne der Server-Nr. 1 gesetzt ist.",
  "Cultivation Pills": "Kultivierungspillen",
  "Pill rank": "Pillenrang",
  "Cultivation pill effect": "Wirkung der Kultivierungspille",
  "Daily pill attempts (shared)": "Tägliche Pillenversuche (geteilt)",
  "Legendary (Gold) used / day": "Legendär (Gold) pro Tag",
  "Epic (Purple) used / day": "Epos (Lila) pro Tag",
  "Rare (Blue) used / day": "Selten (Blau) pro Tag",
  "Already used today's pills/respira": "Heutige Pillen/Atmung bereits genutzt",
  "Reset in (h)": "Reset in (h)",
  "Star Marks (+XP ratio)": "Stern-Marken (+EXP-Verhältnis)",
  "＋ Add source": "＋ Quelle hinzufügen",
  "＋ From catalog": "＋ Aus Katalog",
  "Total: {} %": "Gesamt: {} %",
  "source (e.g. technique book, curio)": "Quelle (z. B. Technikbuch, Kuriosität)",
  "varies": "variiert",
  "info": "Info", "pill limit": "Pillenlimit",
  "Add a pill-effect source (a technique book, a curio, …). Their percentages sum.":
      "Füge eine Pillenwirkungs-Quelle hinzu (Technikbuch, Kuriosität, …). Die Prozente summieren sich.",
  "Known pill-effect sources from the game data. Click to add "
  "(prefilled, editable); already-added sources are hidden.":
      "Bekannte Pillenwirkungs-Quellen aus den Spieldaten. Anklicken zum Hinzufügen "
      "(vorausgefüllt, editierbar); bereits hinzugefügte Quellen sind ausgeblendet.",
  "Shared daily attempt limit for all cultivation pills (vase red pills are exempt).":
      "Geteiltes tägliches Versuchslimit für alle Kultivierungspillen (rote Vasen-Pillen ausgenommen).",
  "Check if you've already taken today's daily pills and Respira. The "
  "projection then defers that boost to the next daily reset (today runs "
  "at base speed). Mainly affects short estimates.":
      "Ankreuzen, wenn die heutigen Pillen und Atmung bereits genutzt sind. Die Prognose "
      "verschiebt den Schub dann auf den nächsten Tagesreset (heute läuft Basistempo). "
      "Betrifft vor allem kurze Schätzungen.",
  "Hours until the game's daily reset. Only used when the box above is "
  "checked: the projection runs the window until the reset without the "
  "daily pill/Respira XP (and defers event Respira to the reset), then "
  "resumes the normal daily routine.":
      "Stunden bis zum Tagesreset des Spiels. Nur genutzt, wenn das Kästchen oben angekreuzt "
      "ist: die Prognose läuft bis zum Reset ohne die tägliche Pillen-/Atmungs-EXP "
      "(Event-Atmung wird auf den Reset verschoben) und nimmt dann die normale Tagesroutine auf.",
  "Your in-game 'Cultivation Pill EXP Bonus' for this pill rarity (mainly from "
  "Constellation Altar Star Marks). Entered as a ratio: 0.10 = +10%.":
      "Dein In-Game-EXP-Bonus für Kultivierungspillen dieser Seltenheit (v. a. von "
      "Sternbild-Altar-Stern-Marken). Als Verhältnis eingeben: 0.10 = +10%.",
  "Attempts used: {} / {} (shared; vase red pills exempt)":
      "Versuche genutzt: {} / {} (geteilt; rote Vasen-Pillen ausgenommen)",
  "  ⚠ over limit — extra pills won't count":
      "  ⚠ über dem Limit — zusätzliche Pillen zählen nicht",
  "Creation Artifacts": "Schöpfungsartefakte",
  "Artifact": "Artefakt", "Star": "Stern", "Skin": "Haut", "Charge": "Aufladung",
  "Transmog skin: refined pills give +8% Cultivation EXP":
      "Skin: veredelte Pillen geben +8% Anbau-EXP",
  "Transmog skin: Duplication consumes 10% less Energy":
      "Skin: Vervielfältigung verbraucht 10% weniger Energie",
  "Transmog skin: Timereversal Pearl Energy Cost -10%":
      "Skin: Energiekosten der Zeitumkehrperle -10%",
  "Daily Energy Charge: 30 Fateum/Destium adds 100 Energy to this artifact, once per day. Check if you use it every day.":
      "Tägliche Energieaufladung: 30 Fateum/Destium geben diesem Artefakt einmal täglich "
      "100 Energie. Ankreuzen, wenn du sie jeden Tag nutzt.",
  "Vase input pill": "Vasen-Eingabepille",
  "Blue/White": "Blau/Weiß", "Purple (Epic)": "Lila (Epos)",
  "Gold (Legendary)": "Gold (Legendär)",
  "Which pill quality you refine into red pills. Refines are discounted by input "
  "quality (Epic -5%, Legendary -20% Energy), so feeding gold pills yields extra "
  "red pills over time. Base cost also depends on pill rank (75-100 energy).":
      "Welche Pillenqualität du zu roten Pillen veredelst. Die Veredelung wird mit der "
      "Eingabequalität günstiger (Epos -5%, Legendär -20% Energie), Goldpillen bringen also "
      "mit der Zeit mehr rote Pillen. Die Basiskosten hängen zudem vom Pillenrang ab "
      "(75-100 Energie).",
  "EXP per 10 energy": "EXP pro 10 Energie",
  "Attempts / day": "Versuche / Tag",
  "Sources…": "Quellen…",
  "Extra attempts today": "Zusätzliche Versuche heute",
  "Base EXP / attempt": "Basis-EXP / Versuch",
  "Your daily Respira attempt limit as shown in-game (base + permanent "
  "bonus attempts). The base limit is 10/day. "
  "Leave out temporary event attempts.":
      "Dein tägliches Atmungs-Versuchslimit wie im Spiel angezeigt (Basis + permanente "
      "Bonusversuche). Das Basislimit beträgt 10/Tag. Temporäre Event-Versuche weglassen.",
  "One-off extra Respira attempts available today only (event/item). "
  "Credited once, not as a daily rate.":
      "Einmalige zusätzliche Atmungsversuche nur für heute (Event/Gegenstand). "
      "Wird einmal gutgeschrieben, nicht als Tagesrate.",
  "The base (non-crit) Cultivation EXP from one Respira attempt — see the "
  "note below the field.":
      "Die Basis-Anbau-EXP (ohne Krit) eines Atmungsversuchs — siehe Hinweis unter dem Feld.",
  "Known Respira bonus sources. Checkable entries add/remove daily "
  "attempts from the field. Greyed entries are informational only: "
  "Respira EXP bonuses are already inside your in-game EXP tooltip, "
  "and pill-attempt bonuses belong in the Daily pill attempts input.":
      "Bekannte Atmungs-Bonusquellen. Ankreuzbare Einträge fügen dem Feld tägliche Versuche "
      "hinzu bzw. entfernen sie. Ausgegraute Einträge sind nur informativ: Atmungs-EXP-Boni "
      "stecken bereits im EXP-Tooltip des Spiels, und Pillenversuchs-Boni gehören ins Feld "
      "der täglichen Pillenversuche.",
  "Do a few Respira: most give the same small EXP (the base — enter that); "
  "some give 2×/5×/10× (crits — ignore, handled automatically).":
      "Führe einige Atmungen aus: die meisten geben dieselbe kleine EXP (die Basis — diese "
      "eintragen); manche geben 2×/5×/10× (Krits — ignorieren, wird automatisch verrechnet).",
  "Fruit rank": "Fruchtrang",
  "Highest rank (+50%)": "Höchster Rang (+50%)",
  "No. of Myrimon Fruits": "Anzahl Myrimon-Früchte",
  "Culti level": "Kultivierungsstufe",
  "Quality level": "Qualitätsstufe",
  "Gush level": "Schwall-Stufe",
  "Aura Extractor quality": "Qualität des Aura-Extraktors",
  "Number of Myrimon Fruits processed through the Aura Extractor.":
      "Anzahl der im Aura-Extraktor verarbeiteten Myrimon-Früchte.",
  "Note: Strive (the catch-up bonus, from Nascent Soul) fades as you close the gap to "
  "your server's #1. Set \"Server #1's Stage\" above to model that drop-off (estimated); "
  "leave it blank to hold Strive constant. Low/zero-strive players are unaffected either way.":
      "Hinweis: Das Streben (der Aufhol-Bonus, ab Werdende Seele) schwindet, während du zum "
      "Server-Ersten aufschließt. Setze oben die „Bühne der Server-Nr. 1“, um diesen Abfall zu "
      "modellieren (geschätzt); leer lassen, um das Streben konstant zu halten. Spieler mit "
      "niedrigem/keinem Streben sind so oder so unberührt.",
  "Results (current)": "Ergebnisse (aktuell)",
  "Half-step breakthrough in": "Halber-Schritt-Durchbruch in",
  "Stage breakthrough in": "Bühnen-Durchbruch in",
  "Target Stage reached in": "Ziel-Bühne erreicht in",
  "Abode Aura (implied)": "Wohnsitz-Aura (impliziert)",
  "Cultivation XP / day": "Anbau-EXP / Tag",
  "Effective XP / day": "Effektive EXP / Tag",
  "Pill XP / day": "Pillen-EXP / Tag",
  "Daily XP share (pills+Respira / gem)": "Tages-EXP-Anteil (Pillen+Atmung / Juwel)",
  "Daily XP share (daily flat XP / gem)": "Tages-EXP-Anteil (fixe EXP / Juwel)",
  "Ascension blessing": "Aufstiegssegen",
  "Blessing before Voidbreak Middle": "Segen vor Leerenbruch (Mitte)",
  "XP elixirs / day": "EXP-Elixiere / Tag",
  "EXP per elixir": "EXP pro Elixier",
  "Elixir effectiveness": "Elixier-Wirksamkeit",
  "Elixir XP / day": "Elixier-EXP / Tag",
  "Share of your effective daily XP that comes from flat sources "
  "(pills + Respira + elixirs), and the Aura Gem's speed bonus on "
  "cultivation. Flat XP does not scale with grade EXP, so a high share "
  "means slower progress at higher grades than raw speed suggests.":
      "Anteil der effektiven Tages-EXP aus fixen Quellen (Pillen + Atmung + Elixiere) und "
      "der Geschwindigkeitsbonus des Aura-Juwels auf die Kultivierung. Fixe EXP skalieren "
      "nicht mit den Stufen-EXP; ein hoher Anteil bedeutet auf höheren Stufen langsameren "
      "Fortschritt, als die reine Geschwindigkeit nahelegt.",
  "Ascension Virya blessing: persistent absorption-ratio bonus in percentage "
  "points (Perfection (C) +20 and Perfect +20 — with both, enter 40). Enter the "
  "Absorption Ratio above as displayed in-game: it already includes this.":
      "Aufstiegs-Virya-Segen: dauerhafter Absorptionsraten-Bonus in Prozentpunkten "
      "(Perfektion (C) +20 und Perfekt +20 — mit beiden 40 eingeben). Die Absorptionsrate "
      "oben wie im Spiel angezeigt eingeben: sie enthält diesen Bonus bereits.",
  "The conditional blessing tier (+20 percentage points) that the game removes "
  "at Voidbreak Middle. Kept separate so projections past Voidbreak Middle "
  "drop it.":
      "Die bedingte Segensstufe (+20 Prozentpunkte), die das Spiel bei Leerenbruch (Mitte) "
      "entfernt. Separat geführt, damit Prognosen über diesen Punkt hinaus sie fallen lassen.",
  "Absorption ratio must exceed the blessing bonus.":
      "Die Absorptionsrate muss den Segensbonus übersteigen.",
  "Auto": "Auto",
  "Respira Effect books": "Atmungseffekt-Bücher",
  "Sources": "Quellen",
  "Vault": "Tresor",
  "Max shelf": "Regal maxen",
  "Elixirs": "Elixiere",
  "Attempts and Base EXP fill themselves — attempts from the game's base 10 plus your Vault bonuses, Base EXP from your Stage estimate times your Vault's book bonuses. Overwrite either with your in-game reading (clear a field to go back to the estimate). Most Respira give the same small EXP — that is the base; 2×/5×/10× crits are handled automatically.": "Versuche und Basis-EXP füllen sich selbst — Versuche aus den 10 Basisversuchen des Spiels plus deinen Tresor-Boni, Basis-EXP aus der Stufenschätzung mal deinen Buch-Boni aus dem Tresor. Überschreibe beides mit deinem Spielwert (Feld leeren stellt die Schätzung wieder her). Die meisten Respira geben dieselbe kleine EXP — das ist die Basis; 2×/5×/10×-Crits werden automatisch berücksichtigt.",
  "Exclusive manuals give combat stats, so they do not feed the calculator — track them here to keep your whole collection in one place.": "Exklusive Handbücher geben Kampfwerte und fließen nicht in den Rechner — verfolge sie hier, damit die ganze Sammlung an einem Ort ist.",
  "Blessings": "Segen",
  "Base EXP fills itself from your Stage; overwrite it with your in-game reading for exact numbers (clear it to go back to the estimate). Most Respira give the same small EXP — that is the base; 2×/5×/10× crits are handled automatically.": "Basis-EXP füllt sich selbst aus deiner Stufe; überschreibe sie mit deinem Spielwert für exakte Zahlen (Feld leeren stellt die Schätzung wieder her). Die meisten Respira geben dieselbe kleine EXP — das ist die Basis; 2×/5×/10×-Crits werden automatisch berücksichtigt.",
  "Empty shelf": "Regal leeren",
  "Set every book on this shelf back to not learned.": "Setzt jedes Buch in diesem Regal auf „nicht erlernt“ zurück.",
  "Record what you own once; fields with a shelf chip can then fill themselves.": "Erfasse deinen Besitz einmal; Felder mit Regal-Chip können sich dann selbst ausfüllen.",
  "Set every book on this shelf to its final tier.": "Setzt jedes Buch in diesem Regal auf die letzte Stufe.",
  "Library": "Bibliothek",
  "Treasury": "Schatzkammer",
  "Companions": "Gefährten",
  "Universal": "Universell",
  "Exclusive": "Exklusiv",
  "Set each book's tier once; the bonuses it has unlocked flow to the calculator on their own. Dots show the book's chapter bonuses: filled ones are active at your tier, and colored dots mark the cultivation chapters — pill, Respira and abode-aura bonuses worth working toward.":
   "Lege die Stufe jedes Buchs einmal fest; die freigeschalteten Boni fließen von selbst in den Rechner. Punkte zeigen die Kapitelboni des Buchs: gefüllte sind auf deiner Stufe aktiv, und farbige Punkte markieren die Kultivierungskapitel — Pillen-, Atmungs- und Wohnsitz-Aura-Boni, auf die es sich hinzuarbeiten lohnt.",
  "Exclusive technique manuals give combat stats only, so they are not tracked yet. This shelf will fill in later.":
   "Exklusive Technikhandbücher geben nur Kampfwerte und werden daher noch nicht erfasst. Dieses Regal füllt sich später.",
  "auto": "auto",
  "shelf": "Regal",
  "Click to let the shelf fill this field.":
      "Klicken, damit das Regal dieses Feld füllt.",
  "Shelf-managed. Click to edit manually.":
      "Vom Regal verwaltet. Klicken, um manuell zu bearbeiten.",
  "Some owned sources have unrecorded amounts.":
      "Bei einigen Quellen ist die Höhe noch nicht erfasst.",
  "Record what you own once; fields with a shelf chip can then fill "
  "themselves. Entries marked * carry amounts that are not "
  "exactly established.":
      "Einmal eintragen, was Sie besitzen; Felder mit Regal-Chip füllen sich dann selbst. "
      "Mit * markierte Einträge haben nicht exakt belegte Werte.",
  "Base values (before sources)": "Basiswerte (vor Quellen)",
  "Daily Respira attempts before any owned source. The game "
  "grants 10 by default.":
      "Tägliche Atmungsversuche ohne Quellen. Das Spiel gewährt standardmäßig 10.",
  "Daily pill limit before any owned source.":
      "Tägliches Pillenlimit ohne Quellen.",
  "Respira attempts / day": "Atmungsversuche / Tag",
  "Daily pill limit": "Tägliches Pillenlimit",
  "Tier ": "Stufe ",
  "Maxed": "Maximiert",
  "Amount or unlock tier not exactly established.": "Wert oder Freischalt-Stufe nicht exakt belegt.",
  "Technique books": "Technikbücher",
  "Immortal friends": "Unsterbliche Freunde",
  "Ascension blessings": "Aufstiegssegen",
  "Curios": "Kuriositäten",
  "Fill Base EXP from your Stage's Respira base (measured for "
  "Nascent Soul and Incarnation, extrapolated ×2.0225 per Stage "
  "elsewhere) times (1 + Respira Effect books %).":
      "Basis-EXP aus der Atmungs-Basis Ihrer Stufe füllen (gemessen für Werdende Seele "
      "und Inkarnation, sonst ×2,0225 pro Stufe extrapoliert), multipliziert mit "
      "(1 + Atmungseffekt-Bücher-%).",
  "Your total ACTIVE 'Respira Effect' percent from technique books. Only "
  "used by the Auto button: Base EXP = Stage base × (1 + this %).":
      "Ihr gesamter AKTIVER 'Atmungseffekt'-Prozentsatz aus Technikbüchern. Nur vom "
      "Auto-Knopf verwendet: Basis-EXP = Stufenbasis × (1 + dieser %).",
  "XP elixirs consumed per day.": "Pro Tag verbrauchte EXP-Elixiere.",
  "Cultivation EXP granted by one elixir (item tooltip).":
      "Kultivierungs-EXP eines Elixiers (Gegenstands-Tooltip).",
  "Elixir effectiveness percent after elixir tolerance (100 = full effect).":
      "Elixier-Wirksamkeit in Prozent nach Elixiertoleranz (100 = volle Wirkung).",
  "Mythic pills / day": "Mythische Pillen / Tag",
  "Pearl XP / day": "Perlen-EXP / Tag",
  "Respira XP / day": "Atmungs-EXP / Tag",
  "XP from fruits": "EXP aus Früchten",
  "Fruit time saved": "Durch Früchte gesparte Zeit",
  "Copy results": "Ergebnisse kopieren",
  "Copied ✓": "Kopiert ✓",
  "Pin as A": "Als A anheften",
  "Pinned A": "Angeheftet A",
  "Clear A": "A löschen",
  "{}% of daily XP / +{}% speed": "{}% der Tages-EXP / +{}% Tempo",
  "Share of your effective daily XP that comes from flat sources "
  "(pills + Respira), and the Aura Gem's speed bonus on cultivation. "
  "Flat XP does not scale with grade EXP, so a high share means slower "
  "progress at higher grades than raw speed suggests.":
      "Anteil deiner effektiven Tages-EXP aus Fixquellen (Pillen + Atmung) und der "
      "Tempobonus des Aura-Juwels auf die Kultivierung. Fix-EXP skaliert nicht mit der "
      "Grad-EXP; ein hoher Anteil bedeutet also langsameren Fortschritt in höheren Graden, "
      "als das reine Tempo vermuten lässt.",
  "(best {} / worst {})": "(bester {} / schlechtester {})",
  "The in-game Cultivation Speed: XP gained per 8-second Cosmoapsis tick.":
      "Die Anbaugeschwindigkeit im Spiel: EXP pro 8-Sekunden-Cosmoapsis-Tick.",
  "Your Absorption Ratio as a percent (e.g. 27.5). Shown below is the Stage's base for the selected Grade.":
      "Dein Absorptionsverhältnis in Prozent (z. B. 27.5). Darunter steht die Basis der Bühne "
      "für den gewählten Grad.",
  "How far into the current Grade you are, as a percent.":
      "Wie weit du im aktuellen Grad bist, in Prozent.",
  "Aura Gem rarity. In-game it's claimable storage that accrues gem% of your cultivation speed "
  "(up to 18-32h per claim); modeled as a continuous speed multiplier on cultivation only — "
  "pills/Respira are flat XP and are NOT boosted by the gem.":
      "Seltenheit des Aura-Juwels. Im Spiel ein abholbarer Speicher, der Juwel-% deiner "
      "Anbaugeschwindigkeit ansammelt (bis 18-32 h pro Abholung); modelliert als dauerhafter "
      "Tempomultiplikator nur auf die Kultivierung — Pillen/Atmung sind Fix-EXP und werden "
      "vom Juwel NICHT verstärkt.",
  "Optional: a future Stage to time your arrival at.":
      "Optional: eine künftige Bühne, deren Erreichen berechnet wird.",
  "Daily pill-use limit that caps Gold/Purple/Blue usage.":
      "Tägliches Pillenlimit, das Gold/Lila/Blau begrenzt.",
  "Timereversal Pearl: EXP granted per 10 energy.":
      "Zeitumkehrperle: EXP pro 10 Energie.",
  "Implied total aura bonus: {}%  (Abode = 130 × {})":
      "Implizierter Gesamt-Aurabonus: {}%  (Wohnsitz = 130 × {})",
  "Expected speed: {} / Cosmoapsis": "Erwartetes Tempo: {} / Cosmoapsis",
  "  — entered speed {} is {}% off; one of the readings is stale":
      "  — eingetragenes Tempo {} weicht um {}% ab; einer der Werte ist veraltet",
  "Base Absorption: {}%  ·  Strive: {}%": "Basis-Absorption: {}%  ·  Streben: {}%",
  "  ⚠ below base — Strive can't be negative":
      "  ⚠ unter der Basis — Streben kann nicht negativ sein",
  "  ⚠ Strive over the 120% cap": "  ⚠ Streben über der 120%-Obergrenze",
  "  · Strive above 120% — normal in later realms (overcap); "
  "cap tables beyond the mortal world aren't modeled.":
      "  · Streben über 120% — in späteren Reichen normal (Überkappung); "
      "Obergrenzen-Tabellen jenseits der sterblichen Welt sind nicht modelliert.",
  "Base Absorption: {}%  (Strive unlocks at Nascent Soul)":
      "Basis-Absorption: {}%  (Streben schaltet sich bei Werdende Seele frei)",
  "  ⚠ below base": "  ⚠ unter der Basis",
  "Select a valid stage / phase / grade.": "Wähle gültige Bühne / Phase / Grad.",
  "Cultivation speed and absorption ratio must be > 0.":
      "Anbaugeschwindigkeit und Absorptionsverhältnis müssen > 0 sein.",
  "Target must be after your current grade.": "Das Ziel muss nach dem aktuellen Grad liegen.",
  "Upgrade level": "Verbesserungsstufe",
  "Cultivation Pill Effect: {}%": "Wirkung der Kultivierungspille: {}%",
 },

 "es": {
  "← Back": "← Atrás",
  "Calculator": "Calculadora",
  "Reference": "Referencia",
  "Guide": "Guía",
  "Novice": "Principiante", "Connection": "Conexión", "Foundation": "Fundación",
  "Virtuoso": "Virtuoso", "Nascent Soul": "Alma Naciente",
  "Incarnation": "Encarnación", "Voidbreak": "Ruptura del Vacío",
  "Wholeness": "Plenitud", "Perfection": "Perfección", "Nirvana": "Nirvana",
  "Celestial": "Celestial", "Eternal": "Eterno", "Supreme": "Supremo",
  "Early": "Inicial", "Middle": "Intermedio", "Late": "Fase final",
  "Stage": "Etapa", "Grade": "Rango", "Half-step": "A mitad de camino de",
  "Breakthrough": "Adelante",
  "None": "Ninguno", "Common": "Común", "Uncommon": "Poco común",
  "Rare": "Raro", "Epic": "Épico", "Legendary": "Legendario", "Mythic": "Mítico",
  "Abode Aura": "Aura de la morada", "Absorption Ratio": "Relación de absorción",
  "Aura Gem": "Gema de aura", "Respira": "Inhala", "Strive": "Esfuerzo",
  "Myrimon Fruit": "Fruta Myrimon", "Aura Extractor": "Extractora de Aura",
  "Gush": "Oleada", "Quality": "Calidad",
  "Starsea Vase": "Jarrón del Mar Estelar", "Dual-Star Mirror": "Espejo de Dos Estrellas",
  "Timereversal Pearl": "Perla de Inversión Temporal",
  "Star Mark": "Marca Estelar", "Cultivation Pill": "Píldora de cultivo",
  "Breakthrough Calculator": "Calculadora de avance",
  "Profile:": "Perfil:",
  "New / Save As…": "Nuevo / Guardar como…",
  "Delete": "Eliminar", "Reset": "Restablecer",
  "Check for updates": "Buscar actualizaciones",
  "Installed: v{}. Checks the latest GitHub release.":
      "Instalado: v{}. Comprueba la última versión en GitHub.",
  "Update check failed": "Error al buscar actualizaciones",
  "Update available: v{}": "Actualización disponible: v{}",
  "Up to date (v{})": "Actualizado (v{})",
  "Donate ♥": "Donar ♥",
  "Support development by gifting in-game vouchers.":
      "Apoya el desarrollo regalando cupones del juego.",
  "Theme:": "Tema:", "Language:": "Idioma:",
  "New / Save As": "Nuevo / Guardar como",
  "Profile name:": "Nombre del perfil:",
  "Support the calculator": "Apoyar la calculadora",
  "If the calculator saves you time, you can support development by "
  "gifting in-game vouchers:<ol>"
  "<li>Open <a href='{}'>SEAGM — OverMortal vouchers</a></li>"
  "<li>Pick any voucher amount</li>"
  "<li>Paste the RID below into the site's <b>RID</b> field</li></ol>":
      "Si la calculadora te ahorra tiempo, puedes apoyar el desarrollo regalando "
      "cupones del juego:<ol>"
      "<li>Abre <a href='{}'>SEAGM — cupones de OverMortal</a></li>"
      "<li>Elige cualquier importe</li>"
      "<li>Pega el RID de abajo en el campo <b>RID</b> del sitio</li></ol>",
  "Copy RID": "Copiar RID",
  "Cultivation Base": "Base de cultivo",
  "Grade progress": "Progreso del rango",
  "Apply to Cultivation Speed": "Aplicar a la velocidad de cultivo",
  "Cultivation Speed (XP / Cosmoapsis)": "Velocidad de cultivo (EXP / Cosmoapsis)",
  "Target Stage": "Etapa objetivo",
  "Target half-step": "Medio paso objetivo",
  "Target grade": "Rango objetivo",
  "Optional: a half-step within the target Stage. Blank = start of the Stage.":
      "Opcional: un medio paso dentro de la etapa objetivo. Vacío = inicio de la etapa.",
  "Optional: a grade within the target half-step. Blank = start of the half-step.":
      "Opcional: un rango dentro del medio paso objetivo. Vacío = inicio del medio paso.",
  "Timegate lifts in": "La puerta temporal abre en",
  " days": " días",
  "Prestock for target (overcap)": "Reserva para el objetivo (exceso)",
  "At timegate": "En la puerta temporal",
  "stocked {} early": "reserva lista {} antes",
  "short by {}": "faltan {}",
  "Optional: days until the world-level timegate lifts (shown in-game once someone "
  "reaches the last half-step). Compared against the prestock time. Reminder: use "
  "Myrimon fruits BEFORE the gate — the gate unlocks the next realm, so they lose the +50% highest-realm bonus.":
      "Opcional: días hasta que abra la puerta temporal del mundo (visible en el juego cuando "
      "alguien alcanza el último medio paso). Se compara con el tiempo de reserva. Recordatorio: "
      "usa las frutas Myrimon ANTES de la puerta — al abrir se desbloquea el siguiente reino y pierden el bono de +50% de reino máximo.",
  "Overcap needed for the target, in the game's own display convention (XP since the "
  "start of the final half-step ÷ that half-step's total), and the time to stock it. "
  "While timegated you stay parked at the Stage cap, so XP accrues at your CURRENT "
  "speed — no future-grade speedups. Slower than the ungated 'Target reached in'.":
      "Exceso necesario para el objetivo en el formato del juego (EXP desde el inicio del último "
      "medio paso ÷ su total) y el tiempo para reservarlo. Durante la puerta permaneces en el "
      "tope de la etapa, la EXP avanza a tu velocidad ACTUAL — sin las mejoras de rangos futuros. "
      "Más lento que «Etapa objetivo alcanzada en» sin puerta.",
  "Whether your stocked XP reaches the target before the timegate lifts.":
      "Si tu EXP reservada alcanza el objetivo antes de que abra la puerta temporal.",
  "Server #1's Stage (Strive)": "Etapa del n.º 1 del servidor (Esfuerzo)",
  "Mature server (world level 30+)": "Servidor maduro (nivel de mundo 30+)",
  "Your Abode Aura as shown on the Cultivation Bonus screen. With Absorption "
  "Ratio entered, Cultivation Speed = Abode Aura × Absorption Ratio.":
      "Tu Aura de la morada tal como aparece en la pantalla de Bono de cultivo. Con la "
      "Relación de absorción introducida, velocidad de cultivo = Aura de la morada × "
      "Relación de absorción.",
  "Optional: your server's #1 cultivator's Stage. Models your Strive stepping DOWN as you "
  "break through toward them (estimated; assumes #1 stays put; live value is server-computed hourly). "
  "Leave blank to hold Strive constant.":
      "Opcional: la Etapa del cultivador n.º 1 de tu servidor. Modela cómo tu Esfuerzo BAJA "
      "a medida que te acercas a él (estimado; supone que el n.º 1 no avanza; el valor real "
      "lo calcula el servidor cada hora). Déjalo vacío para mantener el Esfuerzo constante.",
  "Server age changes how Strive is computed. Mature servers (world level 30+, "
  "the common case) use finer level-gap tiers plus a realm-gap bonus (cap ~120%); "
  "young servers use the plain realm-gap table (cap 70%). Only used when "
  "Server #1's Stage is set.":
      "La edad del servidor cambia cómo se calcula el Esfuerzo. Los servidores maduros "
      "(nivel de mundo 30+, el caso habitual) usan tramos más finos de diferencia de nivel "
      "más un bono por diferencia de reino (tope ~120%); los servidores jóvenes usan la "
      "tabla simple de diferencia de reino (tope 70%). Solo se usa si se fija la Etapa del "
      "n.º 1 del servidor.",
  "Cultivation Pills": "Píldoras de cultivo",
  "Pill rank": "Rango de píldora",
  "Cultivation pill effect": "Efecto de la Píldora de Cultivo",
  "Daily pill attempts (shared)": "Intentos diarios de píldoras (compartidos)",
  "Legendary (Gold) used / day": "Legendarias (doradas) al día",
  "Epic (Purple) used / day": "Épicas (moradas) al día",
  "Rare (Blue) used / day": "Raras (azules) al día",
  "Already used today's pills/respira": "Píldoras/Inhala de hoy ya usadas",
  "Reset in (h)": "Reinicio en (h)",
  "Star Marks (+XP ratio)": "Marcas Estelares (+EXP, proporción)",
  "＋ Add source": "＋ Añadir fuente",
  "＋ From catalog": "＋ Del catálogo",
  "Total: {} %": "Total: {} %",
  "source (e.g. technique book, curio)": "fuente (p. ej. libro de técnica, curiosidad)",
  "varies": "varía",
  "info": "info", "pill limit": "límite de píldoras",
  "Add a pill-effect source (a technique book, a curio, …). Their percentages sum.":
      "Añade una fuente de efecto de píldora (un libro de técnica, una curiosidad, …). "
      "Sus porcentajes se suman.",
  "Known pill-effect sources from the game data. Click to add "
  "(prefilled, editable); already-added sources are hidden.":
      "Fuentes de efecto de píldora conocidas de los datos del juego. Pulsa para añadir "
      "(prellenado, editable); las fuentes ya añadidas se ocultan.",
  "Shared daily attempt limit for all cultivation pills (vase red pills are exempt).":
      "Límite diario compartido de intentos para todas las píldoras de cultivo "
      "(las píldoras rojas del jarrón están exentas).",
  "Check if you've already taken today's daily pills and Respira. The "
  "projection then defers that boost to the next daily reset (today runs "
  "at base speed). Mainly affects short estimates.":
      "Marca si ya tomaste las píldoras diarias y el Inhala de hoy. La proyección aplaza "
      "entonces ese impulso hasta el próximo reinicio diario (hoy corre a velocidad base). "
      "Afecta sobre todo a las estimaciones cortas.",
  "Hours until the game's daily reset. Only used when the box above is "
  "checked: the projection runs the window until the reset without the "
  "daily pill/Respira XP (and defers event Respira to the reset), then "
  "resumes the normal daily routine.":
      "Horas hasta el reinicio diario del juego. Solo se usa con la casilla de arriba "
      "marcada: la proyección corre hasta el reinicio sin la EXP diaria de píldoras/Inhala "
      "(y aplaza el Inhala de evento al reinicio), y luego retoma la rutina diaria normal.",
  "Your in-game 'Cultivation Pill EXP Bonus' for this pill rarity (mainly from "
  "Constellation Altar Star Marks). Entered as a ratio: 0.10 = +10%.":
      "Tu bono de EXP de píldoras de cultivo del juego para esta rareza (principalmente de "
      "las Marcas Estelares del Altar de constelaciones). Se introduce como proporción: "
      "0.10 = +10%.",
  "Attempts used: {} / {} (shared; vase red pills exempt)":
      "Intentos usados: {} / {} (compartidos; píldoras rojas del jarrón exentas)",
  "  ⚠ over limit — extra pills won't count":
      "  ⚠ sobre el límite — las píldoras extra no contarán",
  "Creation Artifacts": "Artefactos de la Creación",
  "Artifact": "Artefacto", "Star": "Estrella", "Skin": "Apariencia", "Charge": "Cargar",
  "Transmog skin: refined pills give +8% Cultivation EXP":
      "Apariencia: las píldoras refinadas dan +8% de EXP de Cultivo",
  "Transmog skin: Duplication consumes 10% less Energy":
      "Apariencia: el Duplicado consume 10% menos de Energía",
  "Transmog skin: Timereversal Pearl Energy Cost -10%":
      "Apariencia: Costo de Energía de la Perla de Inversión Temporal -10%",
  "Daily Energy Charge: 30 Fateum/Destium adds 100 Energy to this artifact, once per day. Check if you use it every day.":
      "Carga diaria de Energía: 30 Fateum/Destium añaden 100 de Energía a este artefacto, "
      "una vez al día. Marca si la usas cada día.",
  "Vase input pill": "Píldora de entrada del jarrón",
  "Blue/White": "Azul/blanca", "Purple (Epic)": "Morada (épica)",
  "Gold (Legendary)": "Dorada (legendaria)",
  "Which pill quality you refine into red pills. Refines are discounted by input "
  "quality (Epic -5%, Legendary -20% Energy), so feeding gold pills yields extra "
  "red pills over time. Base cost also depends on pill rank (75-100 energy).":
      "Qué calidad de píldora refinas en píldoras rojas. El refinado se abarata según la "
      "calidad de entrada (épica -5%, legendaria -20% de Energía), así que alimentar píldoras "
      "doradas produce más rojas con el tiempo. El costo base también depende del rango de "
      "la píldora (75-100 de energía).",
  "EXP per 10 energy": "EXP por 10 de energía",
  "Attempts / day": "Intentos / día",
  "Sources…": "Fuentes…",
  "Extra attempts today": "Intentos extra hoy",
  "Base EXP / attempt": "EXP base / intento",
  "Your daily Respira attempt limit as shown in-game (base + permanent "
  "bonus attempts). The base limit is 10/day. "
  "Leave out temporary event attempts.":
      "Tu límite diario de intentos de Inhala como aparece en el juego (base + intentos "
      "extra permanentes). El límite base es 10/día. No incluyas los intentos temporales de evento.",
  "One-off extra Respira attempts available today only (event/item). "
  "Credited once, not as a daily rate.":
      "Intentos extra de Inhala de una sola vez, solo para hoy (evento/objeto). "
      "Se acreditan una vez, no como tasa diaria.",
  "The base (non-crit) Cultivation EXP from one Respira attempt — see the "
  "note below the field.":
      "La EXP de Cultivo base (sin crítico) de un intento de Inhala — mira la nota bajo "
      "el campo.",
  "Known Respira bonus sources. Checkable entries add/remove daily "
  "attempts from the field. Greyed entries are informational only: "
  "Respira EXP bonuses are already inside your in-game EXP tooltip, "
  "and pill-attempt bonuses belong in the Daily pill attempts input.":
      "Fuentes conocidas de bonos de Inhala. Las entradas marcables añaden o quitan "
      "intentos diarios del campo. Las entradas en gris son solo informativas: los bonos de "
      "EXP de Inhala ya están dentro de tu descripción de EXP del juego, y los bonos de "
      "intentos de píldoras van en el campo de intentos diarios de píldoras.",
  "Do a few Respira: most give the same small EXP (the base — enter that); "
  "some give 2×/5×/10× (crits — ignore, handled automatically).":
      "Haz varios Inhala: la mayoría da la misma EXP pequeña (la base — introduce esa); "
      "algunos dan 2×/5×/10× (críticos — ignóralos, se manejan automáticamente).",
  "Fruit rank": "Rango de fruta",
  "Highest rank (+50%)": "Rango máximo (+50%)",
  "No. of Myrimon Fruits": "N.º de Frutas Myrimon",
  "Culti level": "Nivel de cultivo",
  "Quality level": "Nivel de calidad",
  "Gush level": "Nivel de oleada",
  "Aura Extractor quality": "Calidad de la Extractora de Aura",
  "Number of Myrimon Fruits processed through the Aura Extractor.":
      "Número de Frutas Myrimon procesadas en la Extractora de Aura.",
  "Note: Strive (the catch-up bonus, from Nascent Soul) fades as you close the gap to "
  "your server's #1. Set \"Server #1's Stage\" above to model that drop-off (estimated); "
  "leave it blank to hold Strive constant. Low/zero-strive players are unaffected either way.":
      "Nota: el Esfuerzo (el bono de alcance, desde Alma Naciente) se desvanece a medida "
      "que reduces la distancia con el n.º 1 de tu servidor. Fija arriba la «Etapa del n.º 1 "
      "del servidor» para modelar esa caída (estimado); déjalo vacío para mantener el "
      "Esfuerzo constante. Los jugadores con Esfuerzo bajo o nulo no se ven afectados.",
  "Results (current)": "Resultados (actuales)",
  "Half-step breakthrough in": "Avance de media etapa en",
  "Stage breakthrough in": "Avance de Etapa en",
  "Target Stage reached in": "Etapa objetivo alcanzada en",
  "Abode Aura (implied)": "Aura de la morada (implícita)",
  "Cultivation XP / day": "EXP de cultivo / día",
  "Effective XP / day": "EXP efectiva / día",
  "Pill XP / day": "EXP de píldoras / día",
  "Daily XP share (pills+Respira / gem)": "Cuota de EXP diaria (píldoras+Inhala / gema)",
  "Daily XP share (daily flat XP / gem)": "Cuota de EXP diaria (EXP fija / gema)",
  "Ascension blessing": "Bendición de ascensión",
  "Blessing before Voidbreak Middle": "Bendición antes de Ruptura del Vacío (Intermedio)",
  "XP elixirs / day": "Elixires de EXP / día",
  "EXP per elixir": "EXP por elixir",
  "Elixir effectiveness": "Eficacia del elixir",
  "Elixir XP / day": "EXP de elixires / día",
  "Share of your effective daily XP that comes from flat sources "
  "(pills + Respira + elixirs), and the Aura Gem's speed bonus on "
  "cultivation. Flat XP does not scale with grade EXP, so a high share "
  "means slower progress at higher grades than raw speed suggests.":
      "Parte de tu EXP diaria efectiva que proviene de fuentes fijas (píldoras + Inhala + "
      "elixires), y el bono de velocidad de la gema de aura a la cultivación. La EXP fija "
      "no escala con la EXP de los grados: una cuota alta implica un progreso más lento en "
      "grados altos de lo que sugiere la velocidad.",
  "Ascension Virya blessing: persistent absorption-ratio bonus in percentage "
  "points (Perfection (C) +20 and Perfect +20 — with both, enter 40). Enter the "
  "Absorption Ratio above as displayed in-game: it already includes this.":
      "Bendición Virya de ascensión: bono permanente al índice de absorción en puntos "
      "porcentuales (Perfección (C) +20 y Perfecto +20 — con ambos, introduce 40). Introduce "
      "arriba el índice de absorción tal como lo muestra el juego: ya incluye este bono.",
  "The conditional blessing tier (+20 percentage points) that the game removes "
  "at Voidbreak Middle. Kept separate so projections past Voidbreak Middle "
  "drop it.":
      "El nivel condicional de la bendición (+20 puntos porcentuales) que el juego retira en "
      "Ruptura del Vacío (Intermedio). Se introduce aparte para que las proyecciones más allá "
      "de ese punto lo descarten.",
  "Absorption ratio must exceed the blessing bonus.":
      "El índice de absorción debe superar el bono de la bendición.",
  "Auto": "Auto",
  "Respira Effect books": "Libros de efecto de Inhala",
  "Sources": "Fuentes",
  "Vault": "Bóveda",
  "Max shelf": "Maximizar estante",
  "Elixirs": "Elixires",
  "Attempts and Base EXP fill themselves — attempts from the game's base 10 plus your Vault bonuses, Base EXP from your Stage estimate times your Vault's book bonuses. Overwrite either with your in-game reading (clear a field to go back to the estimate). Most Respira give the same small EXP — that is the base; 2×/5×/10× crits are handled automatically.": "Los intentos y la EXP base se rellenan solos — los intentos desde los 10 básicos del juego más los bonos de tu Bóveda, la EXP base desde la estimación de tu Etapa multiplicada por los bonos de libros de la Bóveda. Sobrescribe cualquiera con tu lectura del juego (vacía el campo para volver a la estimación). La mayoría de Respira dan la misma EXP pequeña — esa es la base; los críticos 2×/5×/10× se manejan automáticamente.",
  "Exclusive manuals give combat stats, so they do not feed the calculator — track them here to keep your whole collection in one place.": "Los manuales exclusivos dan estadísticas de combate y no alimentan la calculadora — regístralos aquí para tener toda la colección en un solo lugar.",
  "Blessings": "Bendiciones",
  "Base EXP fills itself from your Stage; overwrite it with your in-game reading for exact numbers (clear it to go back to the estimate). Most Respira give the same small EXP — that is the base; 2×/5×/10× crits are handled automatically.": "La EXP base se rellena sola según tu Etapa; sobrescríbela con tu lectura del juego para cifras exactas (vacía el campo para volver a la estimación). La mayoría de Respira dan la misma EXP pequeña — esa es la base; los críticos 2×/5×/10× se manejan automáticamente.",
  "Empty shelf": "Vaciar estante",
  "Set every book on this shelf back to not learned.": "Devuelve todos los libros de este estante a «no aprendido».",
  "Record what you own once; fields with a shelf chip can then fill themselves.": "Registra lo que posees una vez; los campos con chip de estante podrán rellenarse solos.",
  "Set every book on this shelf to its final tier.": "Pone todos los libros de este estante en su nivel final.",
  "Library": "Biblioteca",
  "Treasury": "Tesorería",
  "Companions": "Compañeros",
  "Universal": "Universales",
  "Exclusive": "Exclusivas",
  "Set each book's tier once; the bonuses it has unlocked flow to the calculator on their own. Dots show the book's chapter bonuses: filled ones are active at your tier, and colored dots mark the cultivation chapters — pill, Respira and abode-aura bonuses worth working toward.":
   "Fija el nivel de cada libro una sola vez; los bonos desbloqueados llegan solos a la calculadora. Los puntos muestran los bonos por capítulo del libro: los rellenos están activos en tu nivel, y los puntos de color marcan los capítulos de cultivo — bonos de píldoras, Inhala y aura de la morada por los que vale la pena avanzar.",
  "Exclusive technique manuals give combat stats only, so they are not tracked yet. This shelf will fill in later.":
   "Los manuales de técnica exclusivos solo dan estadísticas de combate, así que aún no se registran. Este estante se completará más adelante.",
  "auto": "auto",
  "shelf": "estante",
  "Click to let the shelf fill this field.":
      "Haz clic para que el estante rellene este campo.",
  "Shelf-managed. Click to edit manually.":
      "Gestionado por el estante. Haz clic para editarlo a mano.",
  "Some owned sources have unrecorded amounts.":
      "Algunas fuentes que posees tienen cantidades sin registrar.",
  "Record what you own once; fields with a shelf chip can then fill "
  "themselves. Entries marked * carry amounts that are not "
  "exactly established.":
      "Registra una vez lo que posees; los campos con chip del estante podrán rellenarse solos. "
      "Las entradas con * tienen cantidades no establecidas con exactitud.",
  "Base values (before sources)": "Valores base (antes de fuentes)",
  "Daily Respira attempts before any owned source. The game "
  "grants 10 by default.":
      "Intentos diarios de Inhala sin fuentes. El juego concede 10 por defecto.",
  "Daily pill limit before any owned source.":
      "Límite diario de píldoras sin fuentes.",
  "Respira attempts / day": "Intentos de Inhala / día",
  "Daily pill limit": "Límite diario de píldoras",
  "Tier ": "Nivel ",
  "Maxed": "Al máximo",
  "Amount or unlock tier not exactly established.": "Cantidad o nivel de desbloqueo no establecidos con exactitud.",
  "Technique books": "Libros de técnica",
  "Immortal friends": "Amigos inmortales",
  "Ascension blessings": "Bendiciones de ascensión",
  "Curios": "Curiosidades",
  "Fill Base EXP from your Stage's Respira base (measured for "
  "Nascent Soul and Incarnation, extrapolated ×2.0225 per Stage "
  "elsewhere) times (1 + Respira Effect books %).":
      "Rellena la EXP base con la base de Inhala de tu etapa (medida para Alma Naciente "
      "e Encarnación, extrapolada ×2,0225 por etapa en el resto) por "
      "(1 + % de libros de efecto de Inhala).",
  "Your total ACTIVE 'Respira Effect' percent from technique books. Only "
  "used by the Auto button: Base EXP = Stage base × (1 + this %).":
      "Tu porcentaje ACTIVO total de 'efecto de Inhala' de los libros de técnica. Solo "
      "lo usa el botón Auto: EXP base = base de la etapa × (1 + este %).",
  "XP elixirs consumed per day.": "Elixires de EXP consumidos al día.",
  "Cultivation EXP granted by one elixir (item tooltip).":
      "EXP de cultivación de un elixir (descripción del objeto).",
  "Elixir effectiveness percent after elixir tolerance (100 = full effect).":
      "Eficacia del elixir en porcentaje tras la tolerancia (100 = efecto completo).",
  "Mythic pills / day": "Píldoras míticas / día",
  "Pearl XP / day": "EXP de la perla / día",
  "Respira XP / day": "EXP de Inhala / día",
  "XP from fruits": "EXP de frutas",
  "Fruit time saved": "Tiempo ahorrado por frutas",
  "Copy results": "Copiar resultados",
  "Copied ✓": "Copiado ✓",
  "Pin as A": "Fijar como A",
  "Pinned A": "Fijado A",
  "Clear A": "Borrar A",
  "{}% of daily XP / +{}% speed": "{}% de la EXP diaria / +{}% de velocidad",
  "Share of your effective daily XP that comes from flat sources "
  "(pills + Respira), and the Aura Gem's speed bonus on cultivation. "
  "Flat XP does not scale with grade EXP, so a high share means slower "
  "progress at higher grades than raw speed suggests.":
      "Parte de tu EXP diaria efectiva que viene de fuentes fijas (píldoras + Inhala) y el "
      "bono de velocidad de la Gema de aura sobre el cultivo. La EXP fija no escala con la "
      "EXP del rango, así que una cuota alta implica un progreso más lento en rangos altos "
      "de lo que sugiere la velocidad bruta.",
  "(best {} / worst {})": "(mejor {} / peor {})",
  "The in-game Cultivation Speed: XP gained per 8-second Cosmoapsis tick.":
      "La velocidad de cultivo del juego: EXP ganada por cada tic de Cosmoapsis de 8 segundos.",
  "Your Absorption Ratio as a percent (e.g. 27.5). Shown below is the Stage's base for the selected Grade.":
      "Tu Relación de absorción en porcentaje (p. ej. 27.5). Abajo se muestra la base de la "
      "Etapa para el Rango seleccionado.",
  "How far into the current Grade you are, as a percent.":
      "Cuánto has avanzado en el Rango actual, en porcentaje.",
  "Aura Gem rarity. In-game it's claimable storage that accrues gem% of your cultivation speed "
  "(up to 18-32h per claim); modeled as a continuous speed multiplier on cultivation only — "
  "pills/Respira are flat XP and are NOT boosted by the gem.":
      "Rareza de la Gema de aura. En el juego es un almacén reclamable que acumula el % de "
      "la gema de tu velocidad de cultivo (hasta 18-32 h por reclamo); se modela como un "
      "multiplicador de velocidad continuo solo sobre el cultivo — las píldoras/Inhala son "
      "EXP fija y NO se ven potenciadas por la gema.",
  "Optional: a future Stage to time your arrival at.":
      "Opcional: una Etapa futura para calcular tu llegada.",
  "Daily pill-use limit that caps Gold/Purple/Blue usage.":
      "Límite diario de píldoras que restringe el uso de doradas/moradas/azules.",
  "Timereversal Pearl: EXP granted per 10 energy.":
      "Perla de Inversión Temporal: EXP otorgada por 10 de energía.",
  "Implied total aura bonus: {}%  (Abode = 130 × {})":
      "Bono total de aura implícito: {}%  (morada = 130 × {})",
  "Expected speed: {} / Cosmoapsis": "Velocidad esperada: {} / Cosmoapsis",
  "  — entered speed {} is {}% off; one of the readings is stale":
      "  — la velocidad introducida {} difiere un {}%; una de las lecturas está desactualizada",
  "Base Absorption: {}%  ·  Strive: {}%": "Absorción base: {}%  ·  Esfuerzo: {}%",
  "  ⚠ below base — Strive can't be negative":
      "  ⚠ por debajo de la base — el Esfuerzo no puede ser negativo",
  "  ⚠ Strive over the 120% cap": "  ⚠ Esfuerzo por encima del tope del 120%",
  "  · Strive above 120% — normal in later realms (overcap); "
  "cap tables beyond the mortal world aren't modeled.":
      "  · Esfuerzo por encima del 120% — normal en reinos posteriores (sobretope); las "
      "tablas de topes más allá del mundo mortal no están modeladas.",
  "Base Absorption: {}%  (Strive unlocks at Nascent Soul)":
      "Absorción base: {}%  (el Esfuerzo se desbloquea en Alma Naciente)",
  "  ⚠ below base": "  ⚠ por debajo de la base",
  "Select a valid stage / phase / grade.": "Selecciona una etapa / fase / rango válidos.",
  "Cultivation speed and absorption ratio must be > 0.":
      "La velocidad de cultivo y la relación de absorción deben ser > 0.",
  "Target must be after your current grade.": "El objetivo debe estar después del rango actual.",
  "Upgrade level": "Nivel de mejora",
  "Cultivation Pill Effect: {}%": "Efecto de la Píldora de Cultivo: {}%",
 },

 "zh": {
  "← Back": "← 返回",
  "Calculator": "计算器",
  "Reference": "参考",
  "Guide": "指南",
  "Novice": "凡躯", "Connection": "练气", "Foundation": "筑基",
  "Virtuoso": "练腑", "Nascent Soul": "元婴",
  "Incarnation": "化神期", "Voidbreak": "万象破虚",
  "Wholeness": "合", "Perfection": "大乘", "Nirvana": "脱胎",
  "Celestial": "象", "Eternal": "金仙境", "Supreme": "至尊",
  "Early": "前期", "Middle": "中期", "Late": "后期",
  "Stage": "期", "Grade": "阶", "Half-step": "半步",
  "Breakthrough": "突破",
  "None": "无", "Common": "荒废", "Uncommon": "绿色", "Rare": "蓝色",
  "Epic": "紫色", "Legendary": "橙色", "Mythic": "超越仙品",
  "Abode Aura": "洞府灵气", "Absorption Ratio": "吸收率",
  "Aura Gem": "纳灵石", "Respira": "吐纳", "Strive": "奋起",
  "Myrimon Fruit": "万妖果", "Aura Extractor": "化灵台",
  "Gush": "灵涌", "Quality": "品质",
  "Starsea Vase": "星海瓶", "Dual-Star Mirror": "双星镜",
  "Timereversal Pearl": "逆尘珠",
  "Star Mark": "星痕", "Cultivation Pill": "道行丹",
  "Breakthrough Calculator": "突破计算器",
  "Profile:": "配置：",
  "New / Save As…": "新建 / 另存为…",
  "Delete": "删除", "Reset": "重置",
  "Check for updates": "检查更新",
  "Installed: v{}. Checks the latest GitHub release.":
      "已安装：v{}。检查 GitHub 最新版本。",
  "Update check failed": "检查更新失败",
  "Update available: v{}": "有可用更新：v{}",
  "Up to date (v{})": "已是最新版本（v{}）",
  "Donate ♥": "捐献 ♥",
  "Support development by gifting in-game vouchers.":
      "通过赠送游戏内代金券支持开发。",
  "Theme:": "主题：", "Language:": "语言：",
  "New / Save As": "新建 / 另存为",
  "Profile name:": "配置名称：",
  "Support the calculator": "支持本计算器",
  "If the calculator saves you time, you can support development by "
  "gifting in-game vouchers:<ol>"
  "<li>Open <a href='{}'>SEAGM — OverMortal vouchers</a></li>"
  "<li>Pick any voucher amount</li>"
  "<li>Paste the RID below into the site's <b>RID</b> field</li></ol>":
      "如果本计算器为你节省了时间，可以通过赠送游戏内代金券支持开发：<ol>"
      "<li>打开 <a href='{}'>SEAGM — OverMortal 代金券</a></li>"
      "<li>选择任意面额</li>"
      "<li>把下方的 RID 粘贴到网站的 <b>RID</b> 栏</li></ol>",
  "Copy RID": "复制 RID",
  "Cultivation Base": "修为基础",
  "Grade progress": "小境界进度",
  "Apply to Cultivation Speed": "应用到修炼速度",
  "Cultivation Speed (XP / Cosmoapsis)": "修炼速度（修为/周天）",
  "Target Stage": "目标境界",
  "Target half-step": "目标半步",
  "Target grade": "目标阶",
  "Optional: a half-step within the target Stage. Blank = start of the Stage.":
      "可选：目标境界内的半步。留空 = 境界开始处。",
  "Optional: a grade within the target half-step. Blank = start of the half-step.":
      "可选：目标半步内的阶。留空 = 半步开始处。",
  "Timegate lifts in": "时间之门开启于",
  " days": " 天",
  "Prestock for target (overcap)": "目标预存（溢出）",
  "At timegate": "开门时",
  "stocked {} early": "提前 {} 存满",
  "short by {}": "还差 {}",
  "Optional: days until the world-level timegate lifts (shown in-game once someone "
  "reaches the last half-step). Compared against the prestock time. Reminder: use "
  "Myrimon fruits BEFORE the gate — the gate unlocks the next realm, so they lose the +50% highest-realm bonus.":
      "可选：距世界时间之门开启的天数（有人到达最后半步后游戏内可见）。与预存时间对比。"
      "提醒：请在开门前使用弥力蒙果——开门解锁下一境界后，果实将失去 +50% 最高境界加成。",
  "Overcap needed for the target, in the game's own display convention (XP since the "
  "start of the final half-step ÷ that half-step's total), and the time to stock it. "
  "While timegated you stay parked at the Stage cap, so XP accrues at your CURRENT "
  "speed — no future-grade speedups. Slower than the ungated 'Target reached in'.":
      "达到目标所需的溢出百分比（按游戏显示方式：自最后半步开始累计的经验 ÷ 该半步总量）"
      "及预存所需时间。被时间之门限制时停在境界上限，经验按当前速度累积——没有未来阶的加速。"
      "比无门的“达到目标境界还需”更慢。",
  "Whether your stocked XP reaches the target before the timegate lifts.":
      "你的预存经验能否在时间之门开启前达到目标。",
  "Server #1's Stage (Strive)": "服务器第一名的境界（奋起）",
  "Mature server (world level 30+)": "成熟服务器（世界等级30+）",
  "Your Abode Aura as shown on the Cultivation Bonus screen. With Absorption "
  "Ratio entered, Cultivation Speed = Abode Aura × Absorption Ratio.":
      "修炼增幅界面显示的洞府灵气。填入吸收率后，修炼速度 = 洞府灵气 × 吸收率。",
  "Optional: your server's #1 cultivator's Stage. Models your Strive stepping DOWN as you "
  "break through toward them (estimated; assumes #1 stays put; live value is server-computed hourly). "
  "Leave blank to hold Strive constant.":
      "可选：本服第一名修士的境界。用于模拟你在追赶过程中奋起逐步下降（估算；假设第一名不动；"
      "实际值由服务器每小时计算）。留空则奋起保持不变。",
  "Server age changes how Strive is computed. Mature servers (world level 30+, "
  "the common case) use finer level-gap tiers plus a realm-gap bonus (cap ~120%); "
  "young servers use the plain realm-gap table (cap 70%). Only used when "
  "Server #1's Stage is set.":
      "服务器年龄会影响奋起的计算方式。成熟服务器（世界等级30+，常见情况）使用更细的等级差档位"
      "加境界差加成（上限约120%）；新服务器使用简单的境界差表（上限70%）。仅在设置了服务器第一名"
      "的境界时生效。",
  "Cultivation Pills": "道行丹",
  "Pill rank": "丹药品阶",
  "Cultivation pill effect": "修为丹服用效果",
  "Daily pill attempts (shared)": "每日丹药次数（共享）",
  "Legendary (Gold) used / day": "每日使用橙色（金）丹药",
  "Epic (Purple) used / day": "每日使用紫色丹药",
  "Rare (Blue) used / day": "每日使用蓝色丹药",
  "Already used today's pills/respira": "今日丹药/吐纳已用完",
  "Reset in (h)": "距刷新（小时）",
  "Star Marks (+XP ratio)": "星痕（+修为比例）",
  "＋ Add source": "＋ 添加来源",
  "＋ From catalog": "＋ 从目录添加",
  "Total: {} %": "合计：{} %",
  "source (e.g. technique book, curio)": "来源（如功法书、古宝）",
  "varies": "不定",
  "info": "说明", "pill limit": "丹药次数",
  "Add a pill-effect source (a technique book, a curio, …). Their percentages sum.":
      "添加一个丹药效果来源（功法书、古宝等）。百分比相加。",
  "Known pill-effect sources from the game data. Click to add "
  "(prefilled, editable); already-added sources are hidden.":
      "游戏数据中已知的丹药效果来源。点击添加（已预填，可编辑）；已添加的来源会隐藏。",
  "Shared daily attempt limit for all cultivation pills (vase red pills are exempt).":
      "所有道行丹共享的每日次数上限（净瓶红丹不计入）。",
  "Check if you've already taken today's daily pills and Respira. The "
  "projection then defers that boost to the next daily reset (today runs "
  "at base speed). Mainly affects short estimates.":
      "如果今天的丹药和吐纳已用完请勾选。预测会把这部分收益推迟到下次每日刷新（今天按基础速度计算）。"
      "主要影响短期估算。",
  "Hours until the game's daily reset. Only used when the box above is "
  "checked: the projection runs the window until the reset without the "
  "daily pill/Respira XP (and defers event Respira to the reset), then "
  "resumes the normal daily routine.":
      "距游戏每日刷新的小时数。仅在勾选上方选项时生效：刷新前的时间段不计每日丹药/吐纳修为"
      "（活动吐纳推迟到刷新后），之后恢复正常的每日安排。",
  "Your in-game 'Cultivation Pill EXP Bonus' for this pill rarity (mainly from "
  "Constellation Altar Star Marks). Entered as a ratio: 0.10 = +10%.":
      "该品质丹药在游戏内的修为加成（主要来自星宿坛星痕）。按比例填写：0.10 = +10%。",
  "Attempts used: {} / {} (shared; vase red pills exempt)":
      "已用次数：{} / {}（共享；净瓶红丹不计入）",
  "  ⚠ over limit — extra pills won't count":
      "  ⚠ 超出上限 — 多余丹药不生效",
  "Creation Artifacts": "造化至宝",
  "Artifact": "至宝", "Star": "星级", "Skin": "装扮", "Charge": "充能",
  "Transmog skin: refined pills give +8% Cultivation EXP":
      "装扮：炼化的丹药+8%境界修为",
  "Transmog skin: Duplication consumes 10% less Energy":
      "装扮：增殖消耗能量-10%",
  "Transmog skin: Timereversal Pearl Energy Cost -10%":
      "装扮：逆尘珠消耗能量-10%",
  "Daily Energy Charge: 30 Fateum/Destium adds 100 Energy to this artifact, once per day. Check if you use it every day.":
      "每日充能：花费30机缘玉/天机玉为该至宝增加100能量，每天一次。如果每天都用请勾选。",
  "Vase input pill": "净瓶投入丹药",
  "Blue/White": "蓝/白", "Purple (Epic)": "紫色丹", "Gold (Legendary)": "橙色丹（金）",
  "Which pill quality you refine into red pills. Refines are discounted by input "
  "quality (Epic -5%, Legendary -20% Energy), so feeding gold pills yields extra "
  "red pills over time. Base cost also depends on pill rank (75-100 energy).":
      "你炼化成红丹的丹药品质。投入品质越高炼化越省能量（紫色-5%，橙色-20%），"
      "长期来看投入金丹能多出红丹。基础消耗还取决于丹药品阶（75-100能量）。",
  "EXP per 10 energy": "每10能量的修为",
  "Attempts / day": "每日次数",
  "Sources…": "来源…",
  "Extra attempts today": "今日额外次数",
  "Base EXP / attempt": "每次基础修为",
  "Your daily Respira attempt limit as shown in-game (base + permanent "
  "bonus attempts). The base limit is 10/day. "
  "Leave out temporary event attempts.":
      "游戏内显示的每日吐纳次数上限（基础+永久加成次数）。基础上限为每天10次。不含临时活动次数。",
  "One-off extra Respira attempts available today only (event/item). "
  "Credited once, not as a daily rate.":
      "仅限今日的一次性额外吐纳次数（活动/道具）。只计一次，不按每日计算。",
  "The base (non-crit) Cultivation EXP from one Respira attempt — see the "
  "note below the field.":
      "一次吐纳的基础（非暴击）境界修为 — 见输入框下方说明。",
  "Known Respira bonus sources. Checkable entries add/remove daily "
  "attempts from the field. Greyed entries are informational only: "
  "Respira EXP bonuses are already inside your in-game EXP tooltip, "
  "and pill-attempt bonuses belong in the Daily pill attempts input.":
      "已知的吐纳加成来源。可勾选项会在输入框中增减每日次数。灰色项仅供参考："
      "吐纳修为加成已包含在游戏内修为提示中，丹药次数加成请填到每日丹药次数一栏。",
  "Do a few Respira: most give the same small EXP (the base — enter that); "
  "some give 2×/5×/10× (crits — ignore, handled automatically).":
      "多做几次吐纳：大多数给相同的较小修为（即基础值 — 填这个）；"
      "偶尔出现2×/5×/10×（暴击 — 忽略，程序会自动处理）。",
  "Fruit rank": "果实品阶",
  "Highest rank (+50%)": "最高品阶（+50%）",
  "No. of Myrimon Fruits": "万妖果数量",
  "Culti level": "修炼等级",
  "Quality level": "品质等级",
  "Gush level": "灵涌等级",
  "Aura Extractor quality": "化灵台品质",
  "Number of Myrimon Fruits processed through the Aura Extractor.":
      "通过化灵台处理的万妖果数量。",
  "Note: Strive (the catch-up bonus, from Nascent Soul) fades as you close the gap to "
  "your server's #1. Set \"Server #1's Stage\" above to model that drop-off (estimated); "
  "leave it blank to hold Strive constant. Low/zero-strive players are unaffected either way.":
      "注：奋起（追赶加成，元婴起解锁）会随着你与本服第一名差距缩小而衰减。在上方设置"
      "「服务器第一名的境界」可模拟这一衰减（估算）；留空则奋起保持不变。奋起低/为零的玩家不受影响。",
  "Results (current)": "结果（当前）",
  "Half-step breakthrough in": "半步突破还需",
  "Stage breakthrough in": "境界突破还需",
  "Target Stage reached in": "达到目标境界还需",
  "Abode Aura (implied)": "洞府灵气（推算）",
  "Cultivation XP / day": "每日修炼修为",
  "Effective XP / day": "每日有效修为",
  "Pill XP / day": "每日丹药修为",
  "Daily XP share (pills+Respira / gem)": "每日修为占比（丹药+吐纳 / 纳灵石）",
  "Daily XP share (daily flat XP / gem)": "每日修为占比（固定修为 / 纳灵石）",
  "Ascension blessing": "飞升福泽",
  "Blessing before Voidbreak Middle": "万象破虚中期前的福泽",
  "XP elixirs / day": "每日经验灵药",
  "EXP per elixir": "每个灵药的修为",
  "Elixir effectiveness": "灵药效果",
  "Elixir XP / day": "灵药修为 / 天",
  "Share of your effective daily XP that comes from flat sources "
  "(pills + Respira + elixirs), and the Aura Gem's speed bonus on "
  "cultivation. Flat XP does not scale with grade EXP, so a high share "
  "means slower progress at higher grades than raw speed suggests.":
      "有效每日修为中来自固定来源（丹药 + 吐纳 + 灵药）的占比，以及纳灵石对修炼速度的加成。"
      "固定修为不随境界修为增长，占比越高，高境界的实际进度就越慢于速度所示。",
  "Ascension Virya blessing: persistent absorption-ratio bonus in percentage "
  "points (Perfection (C) +20 and Perfect +20 — with both, enter 40). Enter the "
  "Absorption Ratio above as displayed in-game: it already includes this.":
      "飞升福泽（精进）：吸收率的永久加成，按百分点计（大乘 (C) +20 与圆满 +20——两者都有请输入 40）。"
      "上方的吸收率请按游戏内显示填写：其中已包含此加成。",
  "The conditional blessing tier (+20 percentage points) that the game removes "
  "at Voidbreak Middle. Kept separate so projections past Voidbreak Middle "
  "drop it.":
      "条件福泽（+20 个百分点），到万象破虚中期时被移除。单独填写，以便超过该点的预测不再计入。",
  "Absorption ratio must exceed the blessing bonus.":
      "吸收率必须高于福泽加成。",
  "Auto": "自动",
  "Sources": "来源",
  "Vault": "宝库",
  "Max shelf": "整层拉满",
  "Elixirs": "灵液",
  "Attempts and Base EXP fill themselves — attempts from the game's base 10 plus your Vault bonuses, Base EXP from your Stage estimate times your Vault's book bonuses. Overwrite either with your in-game reading (clear a field to go back to the estimate). Most Respira give the same small EXP — that is the base; 2×/5×/10× crits are handled automatically.": "次数与基础经验会自动填充——次数来自游戏基础的10次加上宝库加成，基础经验来自阶段估算乘以宝库的功法加成。可用游戏内读数覆盖（清空字段即恢复估算）。大多数吐纳给出相同的小额经验——那就是基础值；2×/5×/10×暴击会自动计入。",
  "Exclusive manuals give combat stats, so they do not feed the calculator — track them here to keep your whole collection in one place.": "专属功法提供战斗属性，不影响计算器——在这里记录，让整个收藏集中在一处。",
  "Blessings": "祝福",
  "Base EXP fills itself from your Stage; overwrite it with your in-game reading for exact numbers (clear it to go back to the estimate). Most Respira give the same small EXP — that is the base; 2×/5×/10× crits are handled automatically.": "基础经验会根据你的阶段自动填充；想要精确数字可用游戏内读数覆盖（清空即恢复估算）。大多数吐纳给出相同的小额经验——那就是基础值；2×/5×/10×暴击会自动计入。",
  "Empty shelf": "整层清空",
  "Set every book on this shelf back to not learned.": "将此书架上所有书恢复为未学习。",
  "Record what you own once; fields with a shelf chip can then fill themselves.": "把你拥有的内容记录一次；带书架标记的字段即可自动填充。",
  "Set every book on this shelf to its final tier.": "将此书架上所有书设为最终品阶。",
  "Library": "藏书阁",
  "Treasury": "珍宝阁",
  "Companions": "道友",
  "Universal": "通用",
  "Exclusive": "专属",
  "Set each book's tier once; the bonuses it has unlocked flow to the calculator on their own. Dots show the book's chapter bonuses: filled ones are active at your tier, and colored dots mark the cultivation chapters — pill, Respira and abode-aura bonuses worth working toward.":
   "每本书的品阶只需设置一次；已解锁的加成会自动进入计算器。圆点表示书的章节加成：实心的在你当前品阶已生效，彩色圆点标记修炼相关章节——丹药、吐纳和洞府灵气加成，值得优先追求。",
  "Exclusive technique manuals give combat stats only, so they are not tracked yet. This shelf will fill in later.":
   "专属功法只提供战斗属性，暂不跟踪。此书架以后会补全。",
  "auto": "自动",
  "shelf": "书架",
  "Click to let the shelf fill this field.":
      "点击后由书架自动填写此栏。",
  "Shelf-managed. Click to edit manually.":
      "由书架管理。点击改为手动编辑。",
  "Some owned sources have unrecorded amounts.":
      "部分已拥有的来源数值尚未记录。",
  "Record what you own once; fields with a shelf chip can then fill "
  "themselves. Entries marked * carry amounts that are not "
  "exactly established.":
      "只需登记一次你拥有的内容；带书架标记的输入栏即可自动填写。"
      "带 * 的条目数值尚未完全确定。",
  "Base values (before sources)": "基础值（不含来源）",
  "Daily Respira attempts before any owned source. The game "
  "grants 10 by default.":
      "不含任何来源的每日吐纳次数。游戏默认给予 10 次。",
  "Daily pill limit before any owned source.":
      "不含任何来源的每日丹药上限。",
  "Respira attempts / day": "每日吐纳次数",
  "Daily pill limit": "每日丹药上限",
  "Tier ": "第",
  "Maxed": "已满级",
  "Amount or unlock tier not exactly established.": "数值或解锁品阶尚未完全确定。",
  "Technique books": "功法典籍",
  "Immortal friends": "仙友",
  "Ascension blessings": "飞升福泽",
  "Curios": "珍宝",
  "Respira Effect books": "吐纳效果典籍",
  "Fill Base EXP from your Stage's Respira base (measured for "
  "Nascent Soul and Incarnation, extrapolated ×2.0225 per Stage "
  "elsewhere) times (1 + Respira Effect books %).":
      "按当前境界的吐纳基础值填充基础修为（元婴与化神为实测，其余按每境界×2.0225外推），"
      "再乘以（1 + 吐纳效果典籍%）。",
  "Your total ACTIVE 'Respira Effect' percent from technique books. Only "
  "used by the Auto button: Base EXP = Stage base × (1 + this %).":
      "功法典籍中当前生效的「吐纳效果」总百分比。仅供「自动」按钮使用："
      "基础修为 = 境界基础值 ×（1 + 该百分比）。",
  "XP elixirs consumed per day.": "每日使用的经验灵药数量。",
  "Cultivation EXP granted by one elixir (item tooltip).":
      "单个灵药提供的修为（物品说明）。",
  "Elixir effectiveness percent after elixir tolerance (100 = full effect).":
      "灵药效果百分比（计入灵药耐受后；100 = 完整效果）。",
  "Mythic pills / day": "每日红丹数",
  "Pearl XP / day": "每日逆尘珠修为",
  "Respira XP / day": "每日吐纳修为",
  "XP from fruits": "果实修为",
  "Fruit time saved": "果实节省时间",
  "Copy results": "复制结果",
  "Copied ✓": "已复制 ✓",
  "Pin as A": "固定为A",
  "Pinned A": "已固定A",
  "Clear A": "清除A",
  "{}% of daily XP / +{}% speed": "占每日修为{}% / 速度+{}%",
  "Share of your effective daily XP that comes from flat sources "
  "(pills + Respira), and the Aura Gem's speed bonus on cultivation. "
  "Flat XP does not scale with grade EXP, so a high share means slower "
  "progress at higher grades than raw speed suggests.":
      "有效每日修为中来自固定来源（丹药+吐纳）的占比，以及纳灵石对修炼的速度加成。"
      "固定修为不随小境界所需修为增长，占比越高，高境界的实际进度就越慢于纯速度的预期。",
  "(best {} / worst {})": "（最好 {} / 最差 {}）",
  "The in-game Cultivation Speed: XP gained per 8-second Cosmoapsis tick.":
      "游戏内修炼速度：每8秒一个周天获得的修为。",
  "Your Absorption Ratio as a percent (e.g. 27.5). Shown below is the Stage's base for the selected Grade.":
      "你的吸收率百分比（如27.5）。下方显示所选小境界的基础值。",
  "How far into the current Grade you are, as a percent.":
      "当前小境界的完成度，按百分比。",
  "Aura Gem rarity. In-game it's claimable storage that accrues gem% of your cultivation speed "
  "(up to 18-32h per claim); modeled as a continuous speed multiplier on cultivation only — "
  "pills/Respira are flat XP and are NOT boosted by the gem.":
      "纳灵石品质。游戏内它是可领取的储存，按纳灵石百分比累积你的修炼速度（每次可存18-32小时）；"
      "此处模拟为仅作用于修炼的持续速度乘数 — 丹药/吐纳是固定修为，不受纳灵石加成。",
  "Optional: a future Stage to time your arrival at.":
      "可选：计算到达某个未来境界的时间。",
  "Daily pill-use limit that caps Gold/Purple/Blue usage.":
      "限制橙/紫/蓝丹药使用的每日次数上限。",
  "Timereversal Pearl: EXP granted per 10 energy.":
      "逆尘珠：每10能量获得的修为。",
  "Implied total aura bonus: {}%  (Abode = 130 × {})":
      "推算总灵气加成：{}%（洞府 = 130 × {}）",
  "Expected speed: {} / Cosmoapsis": "预期速度：{} / 周天",
  "  — entered speed {} is {}% off; one of the readings is stale":
      "  — 填入的速度 {} 偏差 {}%；某个读数已过期",
  "Base Absorption: {}%  ·  Strive: {}%": "基础吸收：{}%  ·  奋起：{}%",
  "  ⚠ below base — Strive can't be negative":
      "  ⚠ 低于基础值 — 奋起不能为负",
  "  ⚠ Strive over the 120% cap": "  ⚠ 奋起超过120%上限",
  "  · Strive above 120% — normal in later realms (overcap); "
  "cap tables beyond the mortal world aren't modeled.":
      "  · 奋起超过120% — 在后期境界属正常（超上限）；人间界之后的上限表未建模。",
  "Base Absorption: {}%  (Strive unlocks at Nascent Soul)":
      "基础吸收：{}%（奋起于元婴解锁）",
  "  ⚠ below base": "  ⚠ 低于基础值",
  "Select a valid stage / phase / grade.": "请选择有效的境界 / 半步 / 小境界。",
  "Cultivation speed and absorption ratio must be > 0.":
      "修炼速度和吸收率必须大于0。",
  "Target must be after your current grade.": "目标必须在当前阶之后。",
  "Upgrade level": "升级等级",
  "Cultivation Pill Effect: {}%": "修为丹服用效果：{}%",
 },
}

# translated display string -> English source, across all languages
_REVERSE = {}
for _lang in TRANSLATIONS.values():
    for _en, _xx in _lang.items():
        _REVERSE.setdefault(_xx, _en)


# Duration suffixes for display-time localization of engine fmt_days output.
# The engine string stays canonical English ("1D 12H 0M  (~1.2 yr)") — tests
# and cross-engine parity compare its exact output.
_DUR_SUFFIXES = {
    "ru": ("д", "ч", "м", "г"),
    "de": ("T", "Std", "Min", "J"),
    "es": ("d", "h", "min", "años"),
    "zh": ("天", "时", "分", "年"),
}

_DUR_RE = None
_YR_RE = None


def tr_duration(s: str) -> str:
    """Localize a fmt_days string at display time; identity for English."""
    global _DUR_RE, _YR_RE
    suf = _DUR_SUFFIXES.get(get_lang())
    if suf is None:
        return s
    import re
    if _DUR_RE is None:
        _DUR_RE = re.compile(r"(\d+)D (\d+)H (\d+)M")
        _YR_RE = re.compile(r"\(~([\d.]+) yr\)")
    joiner = "" if get_lang() == "zh" else " "
    s = _DUR_RE.sub(lambda m: f"{m[1]}{suf[0]}{joiner}{m[2]}{suf[1]}{joiner}{m[3]}{suf[2]}", s)
    s = _YR_RE.sub(lambda m: f"(~{m[1]}{joiner}{suf[3]})", s)
    return s
