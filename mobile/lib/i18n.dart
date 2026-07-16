/// Hand-rolled localization: no flutter_localizations/intl dependency.
///
/// Game terms (stages, phases, resources, item names) come verbatim from the
/// game's own localization files (data/i18n_glossary.json / the full APK
/// dictionary); app prose is translated by hand. English is the fallback for
/// any missing or empty entry.
///
/// The app persists and computes with INTERNAL keys ('Nascent', 'EARLY',
/// 'Legendary', ...); only display strings go through [tr] / [trStage] /
/// [trPhase], so saved inputs survive language switches.
library;

/// Supported languages, code -> native name (for the picker).
const langs = {
  'en': 'English',
  'ru': 'Русский',
  'de': 'Deutsch',
  'es': 'Español',
  'zh': '中文',
};

/// Current UI language code. The app does full-page rebuilds on change, so a
/// plain mutable top-level is enough (set from SharedPreferences before the
/// first build).
String currentLang = 'en';

/// Translate [s] into the current language; falls back to English ([s]
/// itself) when there is no (or an empty) translation.
String tr(String s) {
  if (currentLang == 'en') return s;
  final v = _t[s]?[currentLang];
  return (v == null || v.isEmpty) ? s : v;
}

/// Display name for an internal stage key ('Nascent' -> 'Пробуждение').
String trStage(String key) => tr(key);

const _phaseNames = {'EARLY': 'Early', 'MIDDLE': 'Middle', 'LATE': 'Late'};

/// Display name for an internal phase key ('EARLY' -> 'Early'/'Начальная').
String trPhase(String key) => tr(_phaseNames[key] ?? key);

/// Order: ru, de, es, zh. Keys are the English strings used in the code.
const Map<String, Map<String, String>> _t = {
  // Engine validation errors (mapped at display time; engine stays English).
  'Select a valid stage / phase / grade.': {
    'ru': 'Выберите корректные стадию / половину / ступень.',
    'de': 'Wähle gültige Stufe / Phase / Grad.',
    'es': 'Selecciona etapa / fase / grado válidos.',
    'zh': '请选择有效的阶段/半步/品阶。',
  },
  'Cultivation speed and absorption ratio must be > 0.': {
    'ru': 'Скорость совершенствования и эфф. поглощения должны быть > 0.',
    'de': 'Anbaugeschwindigkeit und Absorptionsrate müssen > 0 sein.',
    'es': 'La velocidad de cultivo y la eficiencia de absorción deben ser > 0.',
    'zh': '修炼速度和吸收效率必须大于 0。',
  },
  'Target must be after your current grade.': {
    'ru': 'Цель должна быть после текущей ступени.',
    'de': 'Das Ziel muss nach dem aktuellen Grad liegen.',
    'es': 'El objetivo debe estar después del grado actual.',
    'zh': '目标必须在当前品阶之后。',
  },
  // ---- stages (official; 'Nascent' is the game's 'Nascent Soul') ----------
  'Novice': {'ru': 'Неофит', 'de': 'Anfänger', 'es': 'Principiante', 'zh': '凡躯'},
  'Connection': {'ru': 'Подключение', 'de': 'Verbindung', 'es': 'Conexión', 'zh': '练气'},
  'Foundation': {'ru': 'Фундамент', 'de': 'Stiftung', 'es': 'Fundación', 'zh': '筑基/锻骨'},
  'Virtuoso': {'ru': 'Сотворение', 'de': 'Virtuoso', 'es': 'Virtuoso', 'zh': '练腑'},
  'Nascent': {'ru': 'Пробуждение', 'de': 'Werdende Seele', 'es': 'Alma Naciente', 'zh': '元婴/元武/元罡/元冥'},
  'Incarnation': {'ru': 'Формирование', 'de': 'Menschwerdung', 'es': 'Encarnación', 'zh': '化神期'},
  'Voidbreak': {'ru': 'Преодоление', 'de': 'Leerenbruch', 'es': 'Ruptura del Vacío', 'zh': '万象破虚'},
  'Wholeness': {'ru': 'Слияние', 'de': 'Ganzheit', 'es': 'Plenitud', 'zh': '合'},
  'Perfection': {'ru': 'Совершенство', 'de': 'Perfektion', 'es': 'Perfección', 'zh': '大乘/大乘'},
  'Nirvana': {'ru': 'Нирвана', 'de': 'Nirwana', 'es': 'Nirvana', 'zh': '脱胎'},
  'Celestial': {'ru': 'Небесный', 'de': 'Himmlisch', 'es': 'Celestial', 'zh': '象'},
  'Eternal': {'ru': 'Бессмертие', 'de': 'Ewig', 'es': 'Eterno', 'zh': '金仙境'},
  'Supreme': {'ru': 'Высш.', 'de': 'Höchste', 'es': 'Supremo', 'zh': '至尊'},
  // ---- phases (official) ---------------------------------------------------
  'Early': {'ru': 'Начальная', 'de': 'Früh', 'es': 'Inicial', 'zh': '前期'},
  'Middle': {'ru': 'Средняя', 'de': 'Mitte', 'es': 'Intermedio', 'zh': '中期'},
  'Late': {'ru': '(Поздняя)', 'de': 'Spät', 'es': 'Fase final', 'zh': '后期'},
  'N/A': {'ru': 'Н/Д', 'de': 'N/A', 'es': 'N/A', 'zh': '空'},
  // ---- rarities (official) -------------------------------------------------
  'None': {'ru': 'Нет', 'de': 'Keiner', 'es': 'Ninguno', 'zh': '无'},
  'Common': {'ru': 'Обыч.', 'de': 'Gemeinsam', 'es': 'Común', 'zh': '荒废'},
  'Uncommon': {'ru': 'Необыч.', 'de': 'Ungewöhnlich', 'es': 'Poco común', 'zh': '绿色'},
  'Rare': {'ru': 'Редк.', 'de': 'Selten', 'es': 'Raro', 'zh': '蓝色'},
  'Epic': {'ru': 'Эпич.', 'de': 'Epos', 'es': 'Épico', 'zh': '紫色'},
  'Legendary': {'ru': 'Легендарн.', 'de': 'Legendär', 'es': 'Legendario', 'zh': '橙色'},
  'Mythic': {'ru': 'Мифич.', 'de': 'Mythisch', 'es': 'Mítico', 'zh': '超越仙品'},
  // ---- game terms (official) -----------------------------------------------
  'Stage': {'ru': 'Стадия', 'de': 'Bühne', 'es': 'Etapa', 'zh': '期'},
  'Half-step': {'ru': 'Половина', 'de': 'Halber Schritt zu', 'es': 'A mitad de camino de', 'zh': '半步'},
  'Grade': {'ru': 'Ступень', 'de': 'Grad', 'es': 'Rango', 'zh': '品阶'},
  'Abode Aura': {'ru': 'Аура обители', 'de': 'Wohnsitz-Aura', 'es': 'Aura de la morada', 'zh': '洞府灵气'},
  'Cultivation Speed': {'ru': 'Скорость совершенствования', 'de': 'Anbaugeschwindigkeit', 'es': 'Velocidad de cultivo', 'zh': '修炼速度'},
  'Aura Gem': {'ru': 'Самоцвет ауры', 'de': 'Aura-Juwel', 'es': 'Gema de aura', 'zh': '纳灵石'},
  'Respira': {'ru': 'Дыхание ци', 'de': 'Atmung', 'es': 'Inhala', 'zh': '吐纳'},
  'Myrimon Fruit': {'ru': 'Фрукт Миримона', 'de': 'Myrimon-Frucht', 'es': 'Fruta Myrimon', 'zh': '万妖果'},
  'Starsea Vase': {'ru': 'Ваза астроморья', 'de': 'Starsea-Vase', 'es': 'Jarrón del Mar Estelar', 'zh': '星海瓶'},
  'Dual-Star Mirror': {'ru': 'Зеркало двузведья', 'de': 'Doppelsternspiegel', 'es': 'Espejo de Dos Estrellas', 'zh': '双星镜'},
  'Timereversal Pearl': {'ru': 'Жемчужина обращения времени', 'de': 'Zeitumkehrperle', 'es': 'Perla de Inversión Temporal', 'zh': '逆尘珠'},
  'Cultivation Pill Effect': {'ru': 'Эффект пилюли дао', 'de': 'Wirkung der Kultivierungspille', 'es': 'Efecto de la Píldora de Cultivo', 'zh': '修为丹服用效果'},
  'Skin': {'ru': 'Облик', 'de': 'Haut', 'es': 'Apariencia', 'zh': '装扮'},
  'Star': {'ru': 'Звезда', 'de': 'Stern', 'es': 'Estrella', 'zh': '星级'},
  'Donate': {'ru': 'Сделать взнос', 'de': 'Spenden', 'es': 'Donar', 'zh': '捐献'},
  'Language': {'ru': 'Язык', 'de': 'Sprache', 'es': 'Idioma', 'zh': '语言'},
  // ---- pill colors ----------------------------------------------------------
  'Blue': {'ru': 'Синяя', 'de': 'Blau', 'es': 'Azul', 'zh': '蓝'},
  'Purple': {'ru': 'Фиолетовая', 'de': 'Lila', 'es': 'Morada', 'zh': '紫'},
  'Gold': {'ru': 'Золотая', 'de': 'Gold', 'es': 'Oro', 'zh': '金'},
  // ---- app chrome ------------------------------------------------------------
  'Breakthrough Calculator': {'ru': 'Калькулятор Перехода', 'de': 'Durchbruch-Rechner', 'es': 'Calculadora de Adelante', 'zh': '突破计算器'},
  'Calculator': {'ru': 'Калькулятор', 'de': 'Rechner', 'es': 'Calculadora', 'zh': '计算器'},
  'Reference': {'ru': 'Справка', 'de': 'Referenz', 'es': 'Referencia', 'zh': '参考'},
  'Guide': {'ru': 'Гайд', 'de': 'Anleitung', 'es': 'Guía', 'zh': '指南'},
  'Vault': {'ru': 'Хранилище', 'de': 'Tresor', 'es': 'Bóveda', 'zh': '宝库'},
  'Library': {'ru': 'Библиотека', 'de': 'Bibliothek', 'es': 'Biblioteca', 'zh': '藏书阁'},
  'Treasury': {'ru': 'Сокровищница', 'de': 'Schatzkammer', 'es': 'Tesorería', 'zh': '珍宝阁'},
  'Companions': {'ru': 'Спутники', 'de': 'Gefährten', 'es': 'Compañeros', 'zh': '道友'},
  'Universal': {'ru': 'Общие', 'de': 'Universell', 'es': 'Universales', 'zh': '通用'},
  'Exclusive': {'ru': 'Эксклюзивные', 'de': 'Exklusiv', 'es': 'Exclusivas', 'zh': '专属'},
  'Max': {'ru': 'Макс', 'de': 'Max', 'es': 'Máx', 'zh': '满'},
  'Blessings': {'ru': 'Благословения', 'de': 'Segen', 'es': 'Bendiciones', 'zh': '祝福'},
  'Base EXP fills itself from your Stage; overwrite it with your in-game reading for exact numbers (clear it to go back to the estimate). Most Respira give the same small EXP — that is the base; 2×/5×/10× crits are handled automatically.': {
    'ru': 'Базовый опыт заполняется сам по вашей Стадии; впишите своё игровое значение для точных чисел (очистите поле, чтобы вернуть оценку). Большинство респир дают одинаковый малый опыт — это база; криты 2×/5×/10× учитываются автоматически.',
    'de': 'Basis-EXP füllt sich selbst aus deiner Stufe; überschreibe sie mit deinem Spielwert für exakte Zahlen (Feld leeren stellt die Schätzung wieder her). Die meisten Respira geben dieselbe kleine EXP — das ist die Basis; 2×/5×/10×-Crits werden automatisch berücksichtigt.',
    'es': 'La EXP base se rellena sola según tu Etapa; sobrescríbela con tu lectura del juego para cifras exactas (vacía el campo para volver a la estimación). La mayoría de Respira dan la misma EXP pequeña — esa es la base; los críticos 2×/5×/10× se manejan automáticamente.',
    'zh': '基础经验会根据你的阶段自动填充；想要精确数字可用游戏内读数覆盖（清空即恢复估算）。大多数吐纳给出相同的小额经验——那就是基础值；2×/5×/10×暴击会自动计入。'},
  'Max shelf': {'ru': 'Макс. полка', 'de': 'Regal maxen', 'es': 'Maximizar estante', 'zh': '整层拉满'},
  'Empty shelf': {'ru': 'Очистить полку', 'de': 'Regal leeren', 'es': 'Vaciar estante', 'zh': '整层清空'},
  'Not learned': {'ru': 'Не изучено', 'de': 'Nicht erlernt', 'es': 'No aprendido', 'zh': '未学习'},
  'pill effect': {'ru': 'эффект пилюль', 'de': 'Pilleneffekt', 'es': 'efecto de píldora', 'zh': '丹药效果'},
  'attempts': {'ru': 'попыток', 'de': 'Versuche', 'es': 'intentos', 'zh': '次数'},
  'Track your books, curios and companions once; the bonuses flow to the calculator.': {
    'ru': 'Запишите книги, диковинки и спутников один раз; бонусы сами попадут в калькулятор.',
    'de': 'Erfasse Bücher, Kuriositäten und Gefährten einmal; die Boni fließen in den Rechner.',
    'es': 'Registra tus libros, curiosidades y compañeros una vez; los bonos llegan a la calculadora.',
    'zh': '一次性记录你的功法、珍宝与道友，加成会自动进入计算器。'},
  'T': {'ru': 'Т', 'de': 'T', 'es': 'N', 'zh': '阶'},
  'lv': {'ru': 'ур', 'de': 'St', 'es': 'nv', 'zh': '级'},
  'Immortal friends': {'ru': 'Бессмертные друзья', 'de': 'Unsterbliche Freunde', 'es': 'Amigos inmortales', 'zh': '仙友'},
  'Ascension blessings': {'ru': 'Благословения вознесения', 'de': 'Aufstiegssegen', 'es': 'Bendiciones de ascensión', 'zh': '飞升祝福'},
  'Base values (before sources)': {'ru': 'Базовые значения (до источников)', 'de': 'Basiswerte (vor Quellen)', 'es': 'Valores base (antes de fuentes)', 'zh': '基础值（不含来源）'},
  'Respira attempts / day': {'ru': 'Попытки респиры / день', 'de': 'Respira-Versuche / Tag', 'es': 'Intentos de Respira / día', 'zh': '每日吐纳次数'},
  'Daily pill limit': {'ru': 'Дневной лимит пилюль', 'de': 'Tägliches Pillenlimit', 'es': 'Límite diario de píldoras', 'zh': '每日丹药上限'},
  'Auto-fill calculator fields': {'ru': 'Автозаполнение полей калькулятора', 'de': 'Rechnerfelder automatisch füllen', 'es': 'Autocompletar campos de la calculadora', 'zh': '自动填充计算器字段'},
  'Writes the Vault\'s totals into pill effect, attempts and Respira fields whenever the Vault changes.': {
    'ru': 'При каждом изменении Хранилища записывает его итоги в поля эффекта пилюль, попыток и респиры.',
    'de': 'Schreibt die Tresor-Summen bei jeder Änderung in die Felder für Pilleneffekt, Versuche und Respira.',
    'es': 'Escribe los totales de la Bóveda en los campos de efecto de píldora, intentos y Respira cada vez que cambia.',
    'zh': '宝库变化时，自动把合计写入丹药效果、次数和吐纳字段。'},
  'Set each book\'s tier once; the bonuses it has unlocked flow to the calculator on their own. Dots show the book\'s chapter bonuses: filled ones are active at your tier.': {
    'ru': 'Задайте тир каждой книги один раз; открытые ею бонусы сами попадут в калькулятор. Точки показывают бонусы глав книги: закрашенные активны на вашем тире.',
    'de': 'Lege die Stufe jedes Buchs einmal fest; die freigeschalteten Boni fließen von selbst in den Rechner. Punkte zeigen die Kapitelboni: gefüllte sind auf deiner Stufe aktiv.',
    'es': 'Fija el nivel de cada libro una sola vez; los bonos desbloqueados llegan solos a la calculadora. Los puntos muestran los bonos por capítulo: los rellenos están activos en tu nivel.',
    'zh': '每本书的品阶只需设置一次；已解锁的加成会自动进入计算器。圆点表示章节加成：实心的在当前品阶已生效。'},
  'Exclusive technique manuals give combat stats only, so they are not tracked yet. This shelf will fill in later.': {
    'ru': 'Эксклюзивные техники дают только боевые характеристики, поэтому пока не отслеживаются. Эта полка заполнится позже.',
    'de': 'Exklusive Technikhandbücher geben nur Kampfwerte und werden daher noch nicht erfasst. Dieses Regal füllt sich später.',
    'es': 'Los manuales de técnica exclusivos solo dan estadísticas de combate, así que aún no se registran. Este estante se completará más adelante.',
    'zh': '专属功法只提供战斗属性，暂不跟踪。此书架以后会补全。'},
  'Theme': {'ru': 'Тема', 'de': 'Design', 'es': 'Tema', 'zh': '主题'},
  'More': {'ru': 'Ещё', 'de': 'Mehr', 'es': 'Más', 'zh': '更多'},
  'Check for updates': {'ru': 'Проверить обновления', 'de': 'Nach Updates suchen', 'es': 'Buscar actualizaciones', 'zh': '检查更新'},
  'Update check failed — are you online?': {
    'ru': 'Не удалось проверить обновления — есть ли подключение к сети?',
    'de': 'Updateprüfung fehlgeschlagen — sind Sie online?',
    'es': 'Error al buscar actualizaciones — ¿estás conectado?',
    'zh': '检查更新失败——请检查网络连接',
  },
  'Up to date': {'ru': 'У вас последняя версия', 'de': 'Auf dem neuesten Stand', 'es': 'Actualizado', 'zh': '已是最新版本'},
  'Update available': {'ru': 'Доступно обновление', 'de': 'Update verfügbar', 'es': 'Actualización disponible', 'zh': '有可用更新'},
  'View': {'ru': 'Просмотр', 'de': 'Ansehen', 'es': 'Ver', 'zh': '查看'},
  'Dismiss': {'ru': 'Скрыть', 'de': 'Ausblenden', 'es': 'Descartar', 'zh': '忽略'},
  'Close': {'ru': 'Закрыть', 'de': 'Schließen', 'es': 'Cerrar', 'zh': '关闭'},
  'Cancel': {'ru': 'Отмена', 'de': 'Abbrechen', 'es': 'Cancelar', 'zh': '取消'},
  'OK': {'ru': 'ОК', 'de': 'OK', 'es': 'Aceptar', 'zh': '确定'},
  'Add': {'ru': 'Добавить', 'de': 'Hinzufügen', 'es': 'Agregar', 'zh': '添加'},
  'Catalog': {'ru': 'Каталог', 'de': 'Katalog', 'es': 'Catálogo', 'zh': '目录'},
  'Copy link': {'ru': 'Скопировать ссылку', 'de': 'Link kopieren', 'es': 'Copiar enlace', 'zh': '复制链接'},
  'Copy RID': {'ru': 'Скопировать RID', 'de': 'RID kopieren', 'es': 'Copiar RID', 'zh': '复制RID'},
  'Link copied': {'ru': 'Ссылка скопирована', 'de': 'Link kopiert', 'es': 'Enlace copiado', 'zh': '链接已复制'},
  'Site link copied': {'ru': 'Ссылка на сайт скопирована', 'de': 'Seitenlink kopiert', 'es': 'Enlace del sitio copiado', 'zh': '网站链接已复制'},
  'RID copied': {'ru': 'RID скопирован', 'de': 'RID kopiert', 'es': 'RID copiado', 'zh': 'RID已复制'},
  'Support the calculator': {'ru': 'Поддержать калькулятор', 'de': 'Den Rechner unterstützen', 'es': 'Apoya la calculadora', 'zh': '支持计算器'},
  'If the calculator saves you time, you can support development by gifting in-game vouchers:': {
    'ru': 'Если калькулятор экономит вам время, вы можете поддержать разработку, подарив внутриигровые ваучеры:',
    'de': 'Wenn der Rechner Ihnen Zeit spart, können Sie die Entwicklung mit In-Game-Gutscheinen unterstützen:',
    'es': 'Si la calculadora te ahorra tiempo, puedes apoyar el desarrollo regalando vales del juego:',
    'zh': '如果计算器为您节省了时间，可以通过赠送游戏代金券支持开发：',
  },
  '1. Open the SEAGM OverMortal voucher page': {
    'ru': '1. Откройте страницу ваучеров OverMortal на SEAGM',
    'de': '1. Öffnen Sie die SEAGM-OverMortal-Gutscheinseite',
    'es': '1. Abre la página de vales de OverMortal en SEAGM',
    'zh': '1. 打开SEAGM的OverMortal代金券页面',
  },
  '2. Pick any voucher amount': {
    'ru': '2. Выберите любую сумму ваучера',
    'de': '2. Wählen Sie einen beliebigen Gutscheinbetrag',
    'es': '2. Elige cualquier importe de vale',
    'zh': '2. 选择任意代金券金额',
  },
  "3. Paste the RID below into the site's RID field": {
    'ru': '3. Вставьте RID ниже в поле RID на сайте',
    'de': '3. Fügen Sie die RID unten in das RID-Feld der Seite ein',
    'es': '3. Pega el RID de abajo en el campo RID del sitio',
    'zh': '3. 将下方RID粘贴到网站的RID栏',
  },
  'Open this link in your browser to download the release:': {
    'ru': 'Откройте эту ссылку в браузере, чтобы скачать релиз:',
    'de': 'Öffnen Sie diesen Link im Browser, um die Version herunterzuladen:',
    'es': 'Abre este enlace en tu navegador para descargar la versión:',
    'zh': '在浏览器中打开此链接以下载新版本：',
  },
  // ---- section headers -------------------------------------------------------
  'Cultivation Base': {'ru': 'База совершенствования', 'de': 'Kultivierungsbasis', 'es': 'Base de cultivo', 'zh': '修为基础'},
  'Cultivation Pills': {'ru': 'Пилюли дао', 'de': 'Kultivierungspillen', 'es': 'Píldoras de cultivo', 'zh': '道行丹'},
  'Creation Artifacts': {'ru': 'Артефакты творения', 'de': 'Schöpfungsartefakte', 'es': 'Artefactos de la Creación', 'zh': '造化至宝'},
  // ---- field labels -----------------------------------------------------------
  'Grade progress (%)': {'ru': 'Прогресс ступени (%)', 'de': 'Grad-Fortschritt (%)', 'es': 'Progreso del rango (%)', 'zh': '品阶进度 (%)'},
  'Absorption Ratio (%)': {'ru': 'Эфф. поглощения (%)', 'de': 'Absorptionsverhältnis (%)', 'es': 'Relación de absorción (%)', 'zh': '吸收率 (%)'},
  'Target Stage': {'ru': 'Целевая стадия', 'de': 'Ziel-Bühne', 'es': 'Etapa objetivo', 'zh': '目标期'},
  'Target half-step': {'ru': 'Целевая половина', 'de': 'Ziel-Halbschritt', 'es': 'Medio paso objetivo', 'zh': '目标半步'},
  'Target grade': {'ru': 'Целевая ступень', 'de': 'Ziel-Grad', 'es': 'Grado objetivo', 'zh': '目标阶'},
  'Timegate lifts in (days)': {'ru': 'Врата времени откроются через (дн.)', 'de': 'Zeittor öffnet in (Tage)', 'es': 'La puerta temporal abre en (días)', 'zh': '时间之门开启于（天）'},
  'Prestock for target (overcap)': {'ru': 'Запас до цели (избыток)', 'de': 'Vorrat fürs Ziel (Überlauf)', 'es': 'Reserva para el objetivo (exceso)', 'zh': '目标预存（溢出）'},
  'At timegate': {'ru': 'К вратам времени', 'de': 'Am Zeittor', 'es': 'En la puerta temporal', 'zh': '开门时'},
  'stocked {} early': {'ru': 'запас готов за {} до врат', 'de': '{} vor dem Tor fertig', 'es': 'reserva lista {} antes', 'zh': '提前 {} 存满'},
  'short by {}': {'ru': 'не хватает {}', 'de': 'fehlen {}', 'es': 'faltan {}', 'zh': '还差 {}'},
  'Current build': {'ru': 'Текущая сборка', 'de': 'Aktueller Build', 'es': 'Compilación actual', 'zh': '当前版本'},
  'Share build': {'ru': 'Поделиться билдом', 'de': 'Build teilen', 'es': 'Compartir build', 'zh': '分享配置'},
  'Export copies a text code of ALL your inputs to the clipboard — send it to someone and they can import it to see exactly what you entered.': {
    'ru': 'Экспорт копирует текстовый код ВСЕХ ваших вводов в буфер обмена — отправьте его кому-нибудь, и он сможет импортировать его и увидеть точно, что вы ввели.',
    'de': 'Export kopiert einen Textcode ALLER Eingaben in die Zwischenablage — verschicke ihn, und der Empfänger kann ihn importieren und genau sehen, was du eingegeben hast.',
    'es': 'Exportar copia un código de texto con TODAS tus entradas al portapapeles — envíaselo a alguien y podrá importarlo para ver exactamente lo que ingresaste.',
    'zh': '导出会将你所有输入的文本代码复制到剪贴板——发送给他人，对方导入后即可看到你输入的全部内容。',
  },
  'Paste a build code to import': {'ru': 'Вставьте код билда для импорта', 'de': 'Build-Code zum Import einfügen', 'es': 'Pega un código de build para importar', 'zh': '粘贴配置代码以导入'},
  'Export': {'ru': 'Экспорт', 'de': 'Export', 'es': 'Exportar', 'zh': '导出'},
  'Import': {'ru': 'Импорт', 'de': 'Import', 'es': 'Importar', 'zh': '导入'},
  'Build code copied': {'ru': 'Код билда скопирован', 'de': 'Build-Code kopiert', 'es': 'Código de build copiado', 'zh': '配置代码已复制'},
  'Build imported': {'ru': 'Билд импортирован', 'de': 'Build importiert', 'es': 'Build importado', 'zh': '配置已导入'},
  'Invalid build code': {'ru': 'Неверный код билда', 'de': 'Ungültiger Build-Code', 'es': 'Código de build no válido', 'zh': '配置代码无效'},
  'Server #1 Stage (Strive)': {'ru': 'Стадия №1 сервера (Стремление)', 'de': 'Bühne des Server-Ersten (Streben)', 'es': 'Etapa del n.º 1 del servidor (Esfuerzo)', 'zh': '全服第一期（奋起）'},
  '(none)': {'ru': '(нет)', 'de': '(keine)', 'es': '(ninguna)', 'zh': '（无）'},
  'Mature server (world 30+)': {'ru': 'Зрелый сервер (мир 30+)', 'de': 'Reifer Server (Welt 30+)', 'es': 'Servidor maduro (mundo 30+)', 'zh': '成熟服务器（世界30+）'},
  "Already used today's pills/respira": {
    'ru': 'Сегодняшние пилюли/дыхание ци уже использованы',
    'de': 'Heutige Pillen/Atmung bereits verbraucht',
    'es': 'Píldoras/Inhala de hoy ya usadas',
    'zh': '今日丹药/吐纳已使用',
  },
  'Reset in (h)': {'ru': 'Сброс через (ч)', 'de': 'Reset in (Std.)', 'es': 'Reinicio en (h)', 'zh': '重置倒计时（小时）'},
  'Pill rank': {'ru': 'Ранг пилюли', 'de': 'Pillenrang', 'es': 'Rango de píldora', 'zh': '丹药品阶'},
  'Daily pill attempts': {'ru': 'Пилюль в день (лимит)', 'de': 'Tägliche Pillenversuche', 'es': 'Intentos de píldora diarios', 'zh': '每日丹药次数'},
  'Legendary (Gold) / day': {'ru': 'Легендарн. (золотые) / день', 'de': 'Legendär (Gold) / Tag', 'es': 'Legendario (Oro) / día', 'zh': '橙色（金）/ 天'},
  'Epic (Purple) / day': {'ru': 'Эпич. (фиолетовые) / день', 'de': 'Epos (Lila) / Tag', 'es': 'Épico (Morada) / día', 'zh': '紫色（紫）/ 天'},
  'Rare (Blue) / day': {'ru': 'Редк. (синие) / день', 'de': 'Selten (Blau) / Tag', 'es': 'Raro (Azul) / día', 'zh': '蓝色（蓝）/ 天'},
  'Star Mark: Blue (+ratio)': {'ru': 'Звездная метка: синяя (+доля)', 'de': 'Stern Mark: Blau (+Anteil)', 'es': 'Marca Estelar: Azul (+proporción)', 'zh': '星痕：蓝（+比例）'},
  'Star Mark: Purple (+ratio)': {'ru': 'Звездная метка: фиолетовая (+доля)', 'de': 'Stern Mark: Lila (+Anteil)', 'es': 'Marca Estelar: Morada (+proporción)', 'zh': '星痕：紫（+比例）'},
  'Star Mark: Gold (+ratio)': {'ru': 'Звездная метка: золотая (+доля)', 'de': 'Stern Mark: Gold (+Anteil)', 'es': 'Marca Estelar: Oro (+proporción)', 'zh': '星痕：金（+比例）'},
  'Vase input pill': {'ru': 'Пилюля для вазы', 'de': 'Pille für die Vase', 'es': 'Píldora para el jarrón', 'zh': '净瓶投入丹药'},
  'Pearl EXP per 10 energy': {'ru': 'Опыт жемчужины за 10 энергии', 'de': 'Perlen-EXP pro 10 Energie', 'es': 'EXP de perla por 10 de energía', 'zh': '逆尘珠每10能量经验'},
  'Daily charge': {'ru': 'Ежедн. зарядка', 'de': 'Tägliche Aufladung', 'es': 'Carga diaria', 'zh': '每日充能'},
  'Attempts / day': {'ru': 'Попыток / день', 'de': 'Versuche / Tag', 'es': 'Intentos / día', 'zh': '每日次数'},
  'Respira sources': {'ru': 'Источники дыхания ци', 'de': 'Atmungsquellen', 'es': 'Fuentes de Inhala', 'zh': '吐纳来源'},
  'Extra attempts today': {'ru': 'Доп. попытки сегодня', 'de': 'Zusätzliche Versuche heute', 'es': 'Intentos extra hoy', 'zh': '今日额外次数'},
  'Base EXP / attempt': {'ru': 'Базовый опыт / попытка', 'de': 'Basis-EXP / Versuch', 'es': 'EXP base / intento', 'zh': '每次基础经验'},
  "Do a few Respira: most give the same small EXP (the base — enter that); some give 2×/5×/10× (crits — ignore, handled automatically).": {
    'ru': 'Сделайте несколько дыханий ци: большинство дает одинаковый малый опыт (это база — введите ее); некоторые дают 2×/5×/10× (криты — игнорируйте, учитываются автоматически).',
    'de': 'Führen Sie einige Atmungen aus: die meisten geben dieselbe kleine EXP (die Basis — diese eintragen); manche geben 2×/5×/10× (Krits — ignorieren, wird automatisch berücksichtigt).',
    'es': 'Haz varios Inhala: la mayoría da la misma EXP pequeña (la base — introduce esa); algunos dan 2×/5×/10× (críticos — ignóralos, se calculan automáticamente).',
    'zh': '多做几次吐纳：大多数给相同的少量经验（即基础值——填这个）；有些给2×/5×/10×（暴击——忽略，会自动计算）。',
  },
  'Fruit rank': {'ru': 'Ранг фрукта', 'de': 'Fruchtrang', 'es': 'Rango de fruta', 'zh': '万妖果品阶'},
  'Highest rank (+50%)': {'ru': 'Высший ранг (+50%)', 'de': 'Höchster Rang (+50%)', 'es': 'Rango máximo (+50%)', 'zh': '最高品阶（+50%）'},
  'No. of fruits': {'ru': 'Кол-во фруктов', 'de': 'Anzahl Früchte', 'es': 'N.º de frutas', 'zh': '果实数量'},
  'Culti level': {'ru': 'Ур. совершенствования', 'de': 'Kultivierungsstufe', 'es': 'Nivel de cultivo', 'zh': '修炼等级'},
  'Quality level': {'ru': 'Ур. качества', 'de': 'Qualitätsstufe', 'es': 'Nivel de calidad', 'zh': '品质等级'},
  'Gush level': {'ru': 'Ур. потока', 'de': 'Schwall-Stufe', 'es': 'Nivel de oleada', 'zh': '灵涌等级'},
  'Extractor quality': {'ru': 'Качество извлекателя ауры', 'de': 'Aura-Extraktor-Qualität', 'es': 'Calidad de la Extractora de Aura', 'zh': '化灵台品质'},
  'Pill-effect source': {'ru': 'Источник эффекта пилюль', 'de': 'Quelle des Pilleneffekts', 'es': 'Fuente de efecto de píldora', 'zh': '丹药效果来源'},
  'Pill effect total': {'ru': 'Эффект пилюль всего', 'de': 'Pilleneffekt gesamt', 'es': 'Efecto de píldora total', 'zh': '丹药效果合计'},
  'Upgrade level': {'ru': 'Уровень улучшения', 'de': 'Aufwertungsstufe', 'es': 'Nivel de mejora', 'zh': '升级等级'},
  'varies': {'ru': 'варьируется', 'de': 'variiert', 'es': 'varía', 'zh': '视情况'},
  'info': {'ru': 'инфо', 'de': 'Info', 'es': 'info', 'zh': '信息'},
  'pill input': {'ru': 'вход пилюль', 'de': 'Pillen-Einsatz', 'es': 'entrada de píldoras', 'zh': '投入丹药'},
  // ---- results card ----------------------------------------------------------
  'Half-step breakthrough in': {'ru': 'Переход половины через', 'de': 'Halbschritt-Durchbruch in', 'es': 'Adelante de medio paso en', 'zh': '半步突破还需'},
  'Stage breakthrough in': {'ru': 'Переход стадии через', 'de': 'Bühnen-Durchbruch in', 'es': 'Adelante de etapa en', 'zh': '大境界突破还需'},
  'Target reached in': {'ru': 'Цель будет достигнута через', 'de': 'Ziel erreicht in', 'es': 'Objetivo alcanzado en', 'zh': '达成目标还需'},
  'Abode Aura (implied)': {'ru': 'Аура обители (расчетная)', 'de': 'Wohnsitz-Aura (impliziert)', 'es': 'Aura de la morada (implícita)', 'zh': '洞府灵气（推算）'},
  'Cultivation XP / day': {'ru': 'Опыт дао / день', 'de': 'Anbau-EXP / Tag', 'es': 'EXP de Cultivo / día', 'zh': '境界修为 / 天'},
  'Effective XP / day': {'ru': 'Эффективный опыт / день', 'de': 'Effektive EXP / Tag', 'es': 'EXP efectiva / día', 'zh': '有效经验 / 天'},
  'Pill XP / day': {'ru': 'Опыт пилюль / день', 'de': 'Pillen-EXP / Tag', 'es': 'EXP de píldoras / día', 'zh': '丹药经验 / 天'},
  'Daily XP share (pills+Respira / gem)': {
    'ru': 'Доля дневного опыта (пилюли+дыхание ци / самоцвет)',
    'de': 'Täglicher EXP-Anteil (Pillen+Atmung / Juwel)',
    'es': 'Parte de EXP diaria (píldoras+Inhala / gema)',
    'zh': '每日经验占比（丹药+吐纳 / 纳灵石）',
  },
  'Daily XP share (daily flat XP / gem)': {
    'ru': 'Доля дневного опыта (фиксированный опыт / самоцвет)',
    'de': 'Täglicher EXP-Anteil (fixe EXP / Juwel)',
    'es': 'Parte de EXP diaria (EXP fija / gema)',
    'zh': '每日经验占比（固定经验 / 纳灵石）',
  },
  'Ascension blessing (%)': {
    'ru': 'Благословение вознесения (%)',
    'de': 'Aufstiegssegen (%)',
    'es': 'Bendición de ascensión (%)',
    'zh': '飞升福泽 (%)',
  },
  'Blessing before Voidbreak Middle (%)': {
    'ru': 'Благословение до Преодоления (Средняя) (%)',
    'de': 'Segen vor Leerenbruch (Mitte) (%)',
    'es': 'Bendición antes de Ruptura del Vacío (Intermedio) (%)',
    'zh': '万象破虚中期前的福泽 (%)',
  },
  'Auto-fill from Stage': {
    'ru': 'Автозаполнение по ступени',
    'de': 'Automatisch aus Stufe füllen',
    'es': 'Autorrellenar según la etapa',
    'zh': '按境界自动填充',
  },
  'Respira Effect books (%)': {
    'ru': 'Книги эффекта дыхания ци (%)',
    'de': 'Atmungseffekt-Bücher (%)',
    'es': 'Libros de efecto de Inhala (%)',
    'zh': '吐纳效果典籍 (%)',
  },
  'Absorption ratio must exceed the blessing bonus.': {
    'ru': 'Коэффициент поглощения должен превышать бонус благословения.',
    'de': 'Die Absorptionsrate muss den Segensbonus übersteigen.',
    'es': 'El índice de absorción debe superar el bono de la bendición.',
    'zh': '吸收率必须高于福泽加成。',
  },
  'XP elixirs / day': {
    'ru': 'Эликсиров опыта / день',
    'de': 'EXP-Elixiere / Tag',
    'es': 'Elixires de EXP / día',
    'zh': '每日经验灵药',
  },
  'EXP per elixir': {
    'ru': 'Опыт за эликсир',
    'de': 'EXP pro Elixier',
    'es': 'EXP por elixir',
    'zh': '每个灵药的经验',
  },
  'Elixir effectiveness (%)': {
    'ru': 'Эффективность эликсира (%)',
    'de': 'Elixier-Wirksamkeit (%)',
    'es': 'Eficacia del elixir (%)',
    'zh': '灵药效果 (%)',
  },
  'Elixir XP / day': {
    'ru': 'Опыт с эликсиров / день',
    'de': 'Elixier-EXP / Tag',
    'es': 'EXP de elixires / día',
    'zh': '灵药经验 / 天',
  },
  'speed': {'ru': 'скорость', 'de': 'Tempo', 'es': 'velocidad', 'zh': '速度'},
  'Mythic pills / day': {'ru': 'Мифич. пилюли / день', 'de': 'Mythische Pillen / Tag', 'es': 'Píldoras míticas / día', 'zh': '超越仙品丹 / 天'},
  'Pearl XP / day': {'ru': 'Опыт жемчужины / день', 'de': 'Perlen-EXP / Tag', 'es': 'EXP de perla / día', 'zh': '逆尘珠经验 / 天'},
  'Respira XP / day': {'ru': 'Опыт дыхания ци / день', 'de': 'Atmungs-EXP / Tag', 'es': 'EXP de Inhala / día', 'zh': '吐纳经验 / 天'},
  'XP from fruits': {'ru': 'Опыт от фруктов', 'de': 'EXP aus Früchten', 'es': 'EXP de frutas', 'zh': '万妖果经验'},
  'Fruit time saved': {'ru': 'Экономия времени от фруктов', 'de': 'Durch Früchte gesparte Zeit', 'es': 'Tiempo ahorrado por frutas', 'zh': '果实节省时间'},
  'best': {'ru': 'лучш.', 'de': 'best', 'es': 'mejor', 'zh': '最佳'},
  'worst': {'ru': 'худш.', 'de': 'schlechtest', 'es': 'peor', 'zh': '最差'},
  // ---- absorption diagnostics -------------------------------------------------
  'Base absorption (grade)': {'ru': 'Базовое поглощение (ступень)', 'de': 'Basis-Absorption (Grad)', 'es': 'Absorción base (rango)', 'zh': '基础吸收率（品阶）'},
  'Implied Strive': {'ru': 'Расчетное Стремление', 'de': 'Impliziertes Streben', 'es': 'Esfuerzo implícito', 'zh': '推算奋起'},
  'over 120% cap (stale reading?)': {
    'ru': 'выше лимита 120% (устаревшее значение?)',
    'de': 'über der 120%-Grenze (veralteter Wert?)',
    'es': 'sobre el tope de 120% (¿lectura obsoleta?)',
    'zh': '超过120%上限（数据过期？）',
  },
  "below base; Strive can't be negative": {
    'ru': 'ниже базы; Стремление не может быть отрицательным',
    'de': 'unter der Basis; Streben kann nicht negativ sein',
    'es': 'bajo la base; el Esfuerzo no puede ser negativo',
    'zh': '低于基础值；奋起不能为负',
  },
  'Strive above 120% — normal in later realms (overcap); later cap tables not modeled.': {
    'ru': 'Стремление выше 120% — нормально в поздних мирах (сверх лимита); поздние таблицы лимитов не смоделированы.',
    'de': 'Streben über 120% — in späteren Reichen normal (Overcap); spätere Grenztabellen nicht modelliert.',
    'es': 'Esfuerzo sobre 120% — normal en reinos tardíos (sobre el tope); tablas de topes tardías no modeladas.',
    'zh': '奋起超过120%——在后期境界属正常（超上限）；后期上限表未建模。',
  },
};

/// Localize an engine-formatted duration string ("1D 12H 0M  (~1.2 yr)")
/// at display time. The engine's fmtDays stays canonical English — tests
/// and parity compare its exact output.
String trDuration(String s) {
  const suffixes = {
    'ru': ['д', 'ч', 'м', 'г'],
    'de': ['T', 'Std', 'Min', 'J'],
    'es': ['d', 'h', 'min', 'años'],
    'zh': ['天', '时', '分', '年'],
  };
  final suf = suffixes[currentLang];
  if (suf == null) return s;
  var out = s.replaceAllMapped(
      RegExp(r'(\d+)D (\d+)H (\d+)M'),
      (m) => currentLang == 'zh'
          ? '${m[1]}${suf[0]}${m[2]}${suf[1]}${m[3]}${suf[2]}'
          : '${m[1]}${suf[0]} ${m[2]}${suf[1]} ${m[3]}${suf[2]}');
  out = out.replaceAllMapped(
      RegExp(r'\(~([\d.]+) yr\)'),
      (m) => currentLang == 'zh' ? '(~${m[1]}${suf[3]})' : '(~${m[1]} ${suf[3]})');
  return out;
}
