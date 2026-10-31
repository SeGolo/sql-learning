"""Mindset reading: Oleg Khomiak's framework of sins and virtues (five episodes), in English, Ukrainian and Czech.
Reading cards only (k='lesson'): no drills. side = text shown in the right panel next to the card.
Also feeds the Czech reading module (czread): Czech text in the card, English in the right panel.
Row = (domain, sin, sin explanation, virtue, virtue explanation)."""

SRC = 'Oleg Khomiak (Олег Хомяк), five episodes.'

LANG = {
'EN': dict(name='English', head=('Domain', 'Sin — shadow side', 'Virtue — pivot point'),
  core='Sin is not a list of forbidden acts, it is a distortion of intention arising from inner woundedness. Virtue is a state of wholeness.',
  rows=[
    ('Root', 'Worthlessness', 'acting from emptiness and lack', 'Highest good', 'acting from fullness and meaning'),
    ('Orientation', 'Acting from fear', 'following rules to avoid punishment', 'Acting from meaning', 'you act because you understand why, not from fear'),
    ('Intention', 'Distorted motive', 'good act with corrupt purpose', 'Pure intention', 'act and motive match completely'),
    ('Thought', 'Sinful thought', '6 stages: appear → focus → curiosity → enjoyment → desire → action', 'Pure mind', 'watching what arises without attaching'),
    ('Attention', 'Misdirected attention', 'curiosity toward darkness forms a bond', 'Attention on good', 'continuous inner orientation toward highest good'),
    ('Shadow', 'Dark side', 'the part of yourself you refuse to see', 'Integration', 'owning the shadow so it works for you'),
    ('Trauma', 'Frozen pain', 'fixation in pain, root of all compensation', 'Going into the wound', 'the exit is through the pain, not around it'),
    ('Truth', 'Deception', 'sacred words used to hide opposite intent', 'Honesty', 'no gap between stated and real purpose'),
    ('Love', 'Dependency', 'wanting to possess, lust disguised as love', 'True love', 'wanting to give, not to take'),
    ('Power', 'Control', 'owning people instead of relating to them', 'Respect', 'recognising the other as a free subject'),
    ('Temptation', 'Temptation', 'something promises to fill your specific wound', 'Discernment', 'feeling the difference between real and bait'),
    ('Energy', 'Chronic hatred', 'artificial, sustained, drains and blinds you', 'Cold clarity', 'focused strength without emotional noise'),
    ('Immunity', 'Vulnerability', 'your wounds are the doors others enter through', 'Spiritual immunity', 'no hook inside = nothing to grab onto'),
    ('Ideology', 'False good', 'ideology replacing highest good', 'Highest good', 'non-dual, no opponent, the place where all are equal'),
    ('Wholeness', 'Fragmentation', 'living as a victim or a rebel', 'Integrity', 'full author of your life, without projections'),
  ]),
'UK': dict(name='Українська', head=('Сфера', 'Гріх — тіньова сторона', 'Чеснота — точка зростання'),
  core='Гріх — це не список заборонених дій, це викривлення наміру, що виникає з внутрішньої рани. Чеснота — це стан цілісності.',
  rows=[
    ('Корінь', 'Нікчемність', 'дія з порожнечі та нестачі', 'Благо', 'дія з повноти та смислу'),
    ('Орієнтація', 'Дія зі страху', 'дотримання правил зі страху покарання', 'Дія зі смислу', 'дієш, тому що розумієш чому, а не зі страху'),
    ('Намір', 'Викривлений намір', 'добрий вчинок, корумпована мета', 'Чистий намір', 'вчинок і мотив збігаються повністю'),
    ('Думка', 'Гріховна думка', '6 стадій: виникнення → увага → цікавість → насолода → бажання → дія', 'Чистота розуму', 'спостерігати за тим, що виникає, без прилипання'),
    ('Увага', 'Увага до темного', 'цікавість до темряви формує зв\'язок', 'Увага на благо', 'постійна внутрішня орієнтація на найвище благо'),
    ('Тінь', 'Темна сторона', 'частина себе, яку ти відмовляєшся бачити', 'Інтеграція', 'прийняти тінь, щоб вона працювала на тебе'),
    ('Травма', 'Застиглий біль', 'фіксація в болі, корінь усіх компенсацій', 'Занурення в рану', 'вихід крізь біль, а не навколо нього'),
    ('Правда', 'Обман', 'священні слова для приховування протилежного наміру', 'Чесність', 'жодного розриву між словом і справжнім наміром'),
    ('Любов', 'Залежність', 'прагнення володіти, жага, замаскована під любов', 'Справжня любов', 'прагнення давати, а не брати'),
    ('Влада', 'Контроль', 'володіти людьми замість будувати стосунки', 'Повага', 'визнання іншого як вільного суб\'єкта'),
    ('Спокуса', 'Спокуса', 'щось обіцяє заповнити твою конкретну рану', 'Розрізнення', 'відчути різницю між справжнім і наживкою'),
    ('Енергія', 'Хронічна ненависть', 'штучна, тривала, виснажує та осліплює', 'Холодна ясність', 'зосереджена сила без емоційного шуму'),
    ('Імунітет', 'Вразливість', 'твої рани — двері для маніпуляції', 'Духовний імунітет', 'жодного гачка всередині = нема за що зачепитись'),
    ('Ідеологія', 'Псевдо-благо', 'ідеологія, що замінює найвище благо', 'Найвище благо', 'без противника, місце, де всі рівні'),
    ('Цілісність', 'Розщепленість', 'жити в ролі жертви або бунтаря', 'Цілісність', 'повний автор свого життя, без проєкцій'),
  ]),
'CZ': dict(name='Čeština', head=('Oblast', 'Hřích — stínová strana', 'Ctnost — bod obratu'),
  core='Hřích není seznam zakázaných činů, je to zkreslení záměru vzniklé z vnitřního zranění. Ctnost je stav celistvosti.',
  rows=[
    ('Základ', 'Bezcennost', 'jednání z prázdnoty a nedostatku', 'Nejvyšší dobro', 'jednání z plnosti a smyslu'),
    ('Orientace', 'Jednání ze strachu', 'dodržování pravidel ze strachu z trestu', 'Jednání ze smyslu', 'jednáš, protože rozumíš proč, ne ze strachu'),
    ('Záměr', 'Pokřivený záměr', 'dobrý skutek, korumpovaný motiv', 'Čistý záměr', 'skutek a motiv jsou v úplném souladu'),
    ('Myšlenka', 'Hříšná myšlenka', '6 fází: vznik → pozornost → zvědavost → potěšení → touha → čin', 'Čistota mysli', 'pozorovat, co vyvstává, bez lpění'),
    ('Pozornost', 'Pozornost k temnotě', 'zvědavost vůči temnotě vytváří pouto', 'Pozornost upnutá k dobru', 'trvalá vnitřní orientace k nejvyššímu dobru'),
    ('Stín', 'Temná strana', 'část sebe, kterou odmítáš vidět', 'Integrace', 'přijmout stín, aby pracoval pro tebe'),
    ('Trauma', 'Zmrzlá bolest', 'fixace v bolesti, kořen všech kompenzací', 'Sestup do rány', 'východ vede skrze bolest, ne kolem ní'),
    ('Pravda', 'Podvod', 'posvátná slova ke skrytí opačného záměru', 'Čestnost', 'žádná mezera mezi slovem a skutečným záměrem'),
    ('Láska', 'Závislost', 'touha vlastnit, chtíč maskovaný jako láska', 'Pravá láska', 'touha dávat, ne brát'),
    ('Moc', 'Ovládání', 'vlastnit lidi místo vztahovat se k nim', 'Úcta', 'uznání druhého jako svobodného subjektu'),
    ('Pokušení', 'Pokušení', 'něco slibuje zaplnit tvoji konkrétní ránu', 'Rozlišování', 'cítit rozdíl mezi skutečným a návnadou'),
    ('Energie', 'Chronická nenávist', 'umělá, trvalá, vyčerpává a zaslepuje', 'Chladná jasnost', 'soustředěná síla bez emočního hluku'),
    ('Imunita', 'Zranitelnost', 'tvoje rány jsou dveřmi pro manipulaci', 'Duchovní imunita', 'žádný háček uvnitř = není se čeho chytit'),
    ('Ideologie', 'Pseudo-dobro', 'ideologie nahrazující nejvyšší dobro', 'Nejvyšší dobro', 'bez protivníka, místo, kde jsou si všichni rovni'),
    ('Celistvost', 'Rozštěpenost', 'žití v roli oběti nebo rebela', 'Celistvost', 'plný autor svého života, bez projekcí'),
  ]),
}


def card(lang):
    L = LANG[lang]
    rows = ''.join(f'<tr><td>{d}</td><td><b>{s}</b> — {se}</td><td><b>{v}</b> — {ve}</td></tr>' for d, s, se, v, ve in L['rows'])
    return (f'<p><b>{L["core"]}</b></p>'
            f'<table><thead><tr>{"".join(f"<th>{h}</th>" for h in L["head"])}</tr></thead><tbody>{rows}</tbody></table>'
            f'<p><small>{SRC}</small></p>')


def lesson(t, g, p, side):
    return dict(t=t, d='Easy', g=g, p=p, side=side, h='', s='', o=False, k='lesson', a='', b='Done — mark as read')


def questions():
    g = 'Khomiak · sins and virtues'
    side = ''.join(f'<p><b>{LANG[x]["name"]}:</b> {LANG[x]["core"]}</p>' for x in ('EN', 'UK', 'CZ'))
    return [lesson(f'Khomiak: sins and virtues ({LANG[x]["name"]})', g, card(x), side) for x in ('EN', 'UK', 'CZ')]


def cz_reading():
    return [lesson('Čtení: Chomjak — hříchy a ctnosti', '1 · Chomjak: hříchy a ctnosti',
                   '<p><i>Read the Czech text. The English version is in the right panel.</i></p>' + card('CZ'),
                   '<h4>English</h4>' + card('EN'))]
