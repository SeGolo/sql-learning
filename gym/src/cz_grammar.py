"""Czech grammar, A1 (phase 1). Each topic = one lesson card (theory) + drills.
Drill = (prompt, accepted answers, hint, why, difficulty). '___' marks the gap.
Answers are checked case-insensitively, diacritics strictly."""

def T(*rows, head=None):
    h = f"<thead><tr>{''.join(f'<th>{c}</th>' for c in head)}</tr></thead>" if head else ''
    return f"<table>{h}<tbody>{''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows)}</tbody></table>"

TOPICS = []
def topic(name, lesson, drills):
    TOPICS.append((name, lesson, drills))

# ---------------------------------------------------------------- 1
topic('1 · být a mít', f'''
<p><b>být</b> (to be) and <b>mít</b> (to have) are the two most used verbs. Learn both by heart: everything else builds on them.</p>
{T(('já','jsem','mám'),('ty','jsi','máš'),('on / ona / ono','je','má'),('my','jsme','máme'),('vy','jste','máte'),('oni','jsou','mají'), head=('person','být','mít'))}
<p><b>Negative</b> = <i>ne</i> + verb, written as one word: <i>nejsem, nejsi, nejsme, nejste, nejsou</i> · <i>nemám, nemáš…</i></p>
<p>Exception to remember: <b>je → není</b> (never „neje“).</p>
<p>Examples: <i>Jsem analytik.</i> · <i>Máme dotaz.</i> · <i>Petr dnes není v kanceláři.</i></p>
<p><b>Typical mistakes:</b> „oni jsí“ (→ <i>oni jsou</i>), „on neje doma“ (→ <i>není</i>), „oni mají“ written „oni maji“ (diacritics: <i>mají</i>).</p>''', [
    ('Já ___ analytik. (být)', ['jsem'], 'Person: já → 1st singular of být.', 'já + být → <b>jsem</b>.', 'Easy'),
    ('Ty ___ dnes doma? (být)', ['jsi'], 'Person: ty → 2nd singular.', 'ty + být → <b>jsi</b>.', 'Easy'),
    ('Petr ___ v kanceláři. (být)', ['je'], 'Petr = on → 3rd singular.', 'on + být → <b>je</b>.', 'Easy'),
    ('My ___ kolegové. (být)', ['jsme'], 'Person: my → 1st plural.', 'my + být → <b>jsme</b>.', 'Easy'),
    ('Vy ___ z Brna? (být)', ['jste'], 'Person: vy → 2nd plural (also polite „you“).', 'vy + být → <b>jste</b>.', 'Easy'),
    ('Oni ___ na schůzce. (být)', ['jsou'], 'Person: oni → 3rd plural.', 'oni + být → <b>jsou</b>.', 'Easy'),
    ('Jana dnes ___ doma. (být, negative)', ['není'], 'Negative of „je“ is irregular.', 'je → <b>není</b> (not „neje“).', 'Medium'),
    ('Já ___ čas. (mít)', ['mám'], 'Person: já → 1st singular of mít.', 'já + mít → <b>mám</b>.', 'Easy'),
    ('Ty ___ auto? (mít)', ['máš'], 'Person: ty.', 'ty + mít → <b>máš</b>.', 'Easy'),
    ('Firma ___ nový web. (mít)', ['má'], 'Firma = ona → 3rd singular.', 'ona + mít → <b>má</b>.', 'Easy'),
    ('My ___ dotaz. (mít)', ['máme'], 'Person: my.', 'my + mít → <b>máme</b>.', 'Easy'),
    ('Oni ___ hodně práce. (mít)', ['mají'], 'Person: oni → 3rd plural, long í.', 'oni + mít → <b>mají</b>.', 'Medium'),
    ('Dnes ___ čas. (já, mít, negative)', ['nemám'], 'Negative = ne + verb, one word.', 'ne + mám → <b>nemám</b>.', 'Medium'),
    ('Vy ___ hlad? (mít)', ['máte'], 'Person: vy.', 'vy + mít → <b>máte</b>.', 'Easy'),
])

# ---------------------------------------------------------------- 2
topic('2 · rod podstatných jmen', f'''
<p>Every Czech noun has a <b>gender</b>: masculine, feminine or neuter. The ending of the nominative usually tells you which. <i>ten / ta / to</i> = „the / this“.</p>
{T(('masculine','consonant','<b>ten</b> počítač, ten stůl, ten den, ten e-mail'),('feminine','-a, -e, some consonants','<b>ta</b> firma, ta práce, ta kancelář'),('neuter','-o, -í, -e','<b>to</b> auto, to nádraží, to moře'), head=('gender','typical ending','examples'))}
<p>Watch the exceptions: some feminines end in a consonant (<i>ta kancelář, ta noc, ta věc</i>), and <i>-e</i> can be feminine (<i>ta práce</i>) or neuter (<i>to moře</i>) — learn these with <i>ta / to</i>.</p>
<p><b>Typical mistakes:</b> „ten kancelář“ (→ <i>ta</i>), „ta auto“ (→ <i>to</i>).</p>''', [
    ('___ počítač je nový. (ten / ta / to)', ['ten'], 'Ends in a consonant.', 'počítač → consonant → masculine → <b>ten</b>.', 'Easy'),
    ('___ firma je velká. (ten / ta / to)', ['ta'], 'Ends in -a.', 'firma → -a → feminine → <b>ta</b>.', 'Easy'),
    ('___ okno je otevřené. (ten / ta / to)', ['to'], 'Ends in -o.', 'okno → -o → neuter → <b>to</b>.', 'Easy'),
    ('___ kancelář je malá. (ten / ta / to)', ['ta'], 'Exception: consonant, but not masculine.', 'kancelář is a <b>feminine</b> noun ending in a consonant → <b>ta</b>.', 'Medium'),
    ('___ tabulka má deset řádků. (ten / ta / to)', ['ta'], 'Ends in -a.', 'tabulka → -a → feminine → <b>ta</b>.', 'Easy'),
    ('___ heslo je špatně. (ten / ta / to)', ['to'], 'Ends in -o.', 'heslo → -o → neuter → <b>to</b>.', 'Easy'),
    ('___ den byl dlouhý. (ten / ta / to)', ['ten'], 'Ends in a consonant.', 'den → consonant → masculine → <b>ten</b>.', 'Easy'),
    ('___ práce je zajímavá. (ten / ta / to)', ['ta'], 'Ends in -e — here feminine.', 'práce → -e, feminine → <b>ta</b>.', 'Medium'),
    ('___ nádraží je daleko. (ten / ta / to)', ['to'], 'Ends in -í.', 'nádraží → -í → neuter → <b>to</b>.', 'Medium'),
    ('___ číslo je správné. (ten / ta / to)', ['to'], 'Ends in -o.', 'číslo → -o → neuter → <b>to</b>.', 'Easy'),
    ('___ e-mail je důležitý. (ten / ta / to)', ['ten'], 'Ends in a consonant.', 'e-mail → consonant → masculine → <b>ten</b>.', 'Easy'),
    ('___ schůzka začíná v deset. (ten / ta / to)', ['ta'], 'Ends in -a.', 'schůzka → -a → feminine → <b>ta</b>.', 'Easy'),
    ('___ moře je studené. (ten / ta / to)', ['to'], 'Ends in -e — here neuter.', 'moře → -e, neuter → <b>to</b>.', 'Medium'),
])

# ---------------------------------------------------------------- 3
topic('3 · přítomný čas', f'''
<p>Personal pronouns: <i>já, ty, on / ona / ono, my, vy, oni</i>. They are often left out, because the verb ending already shows the person (<i>Pracuji.</i> = I work).</p>
<p>Present tense has three main patterns. Find the pattern from the <b>on/ona</b> form:</p>
{T(('já','dělám','mluvím','pracuji / pracuju'),('ty','děláš','mluvíš','pracuješ'),('on / ona','dělá','mluví','pracuje'),('my','děláme','mluvíme','pracujeme'),('vy','děláte','mluvíte','pracujete'),('oni','dělají','mluví','pracují / pracujou'), head=('person','-á (dělat)','-í (mluvit)','-e (pracovat)'))}
<p>Useful irregular <b>-e</b> verbs: <i>psát → píšu, píšeš, píše… oni píšou</i> · <i>číst → čtu, čteš, čte</i> · <i>pít → piju, piješ, pije</i>.</p>
<p>Verbs in <b>-ovat</b> always go <i>-uji / -uju, -uješ, -uje…</i>: <i>analyzovat → analyzuji</i>.</p>
<p><b>Typical mistakes:</b> „oni mluvijí“ (→ <i>mluví</i>), „já pracuju“ is fine in speech, <i>pracuji</i> in writing; „on píšé“ (→ <i>píše</i>).</p>''', [
    ('Já ___ v bance. (pracovat)', ['pracuji', 'pracuju'], '-ovat verb → -uji / -uju.', 'pracovat → já <b>pracuji</b> (spoken: pracuju).', 'Easy'),
    ('Ty ___ česky? (mluvit)', ['mluvíš'], '-í pattern.', 'mluvit → ty <b>mluvíš</b>.', 'Easy'),
    ('Ona ___ kávu. (pít)', ['pije'], 'Irregular -e verb.', 'pít → ona <b>pije</b>.', 'Medium'),
    ('My ___ v Praze. (bydlet)', ['bydlíme'], '-í pattern.', 'bydlet → my <b>bydlíme</b>.', 'Easy'),
    ('Vy ___ SQL? (znát)', ['znáte'], '-á pattern.', 'znát → vy <b>znáte</b>.', 'Easy'),
    ('Oni ___ e-maily. (psát)', ['píšou', 'píší'], 'Irregular: psát → píš-.', 'psát → oni <b>píšou</b> (formal: píší).', 'Medium'),
    ('Co ___ ? (ty, dělat)', ['děláš'], '-á pattern, person ty.', 'dělat → ty <b>děláš</b>.', 'Easy'),
    ('Petr ___ noviny. (číst)', ['čte'], 'Irregular: číst → čt-.', 'číst → on <b>čte</b>.', 'Medium'),
    ('My ___ česky. (mluvit)', ['mluvíme'], '-í pattern.', 'mluvit → my <b>mluvíme</b>.', 'Easy'),
    ('Oni ___ v kanceláři. (pracovat)', ['pracují', 'pracujou'], '-ovat verb, oni.', 'pracovat → oni <b>pracují</b> (spoken: pracujou).', 'Medium'),
    ('Já ___ data. (analyzovat)', ['analyzuji', 'analyzuju'], '-ovat → -uji / -uju.', 'analyzovat → já <b>analyzuji</b>.', 'Medium'),
    ('Ty ___ rychle. (psát)', ['píšeš'], 'Irregular: psát → píš-.', 'psát → ty <b>píšeš</b>.', 'Medium'),
    ('Vy ___ dobře. (vařit)', ['vaříte'], '-í pattern.', 'vařit → vy <b>vaříte</b>.', 'Easy'),
    ('Oni ___ česky. (mluvit)', ['mluví'], '-í pattern: oni has the same form as on.', 'mluvit → oni <b>mluví</b> (not „mluvijí“).', 'Medium'),
])

# ---------------------------------------------------------------- 4
topic('4 · otázky a zápor', f'''
<p><b>Yes/no questions</b> keep normal word order; only the intonation rises: <i>Máš čas?</i> · <i>Pracuješ dnes?</i></p>
<p><b>Question words:</b></p>
{T(('kdo','who'),('co','what'),('kde','where'),('kdy','when'),('jak','how'),('proč','why'),('kolik','how much / many'),('odkud / kam','from where / where to'), head=('Czech','English'))}
<p><b>Negative:</b> <i>ne</i> is joined to the verb: <i>nemám, nepracuji, nemluvím</i>. Remember <b>je → není</b>.</p>
<p><b>Double negative is correct in Czech:</b> <i>Nikdo nic nemá.</i> (Nobody has anything.) · <i>Nikdy nepracuji v neděli.</i> Words: <i>nikdo, nic, nikdy, nikde</i> + negative verb.</p>
<p><b>Typical mistakes:</b> „ne mám“ (→ <i>nemám</i>), „Nikdo nic má“ (→ <i>nemá</i>).</p>''', [
    ('Já ___ česky dobře. (mluvit, negative)', ['nemluvím'], 'ne + verb, one word.', 'ne + mluvím → <b>nemluvím</b>.', 'Easy'),
    ('On dnes ___ v kanceláři. (být, negative)', ['není'], 'Irregular negative of „je“.', 'je → <b>není</b>.', 'Easy'),
    ('___ bydlíš? — V Brně.', ['kde'], 'The answer is a place.', 'Place → <b>Kde</b>?', 'Easy'),
    ('___ je to? — To je Petr.', ['kdo'], 'The answer is a person.', 'Person → <b>Kdo</b>?', 'Easy'),
    ('___ děláš? — Pracuji.', ['co'], 'The answer is an activity / thing.', 'Thing / activity → <b>Co</b>?', 'Easy'),
    ('___ to stojí? — 200 korun.', ['kolik'], 'The answer is an amount.', 'Amount → <b>Kolik</b>?', 'Easy'),
    ('___ se máš? — Dobře.', ['jak'], 'The answer is „how“.', 'Manner → <b>Jak</b>?', 'Easy'),
    ('___ přijdeš? — Zítra.', ['kdy'], 'The answer is a time.', 'Time → <b>Kdy</b>?', 'Easy'),
    ('___ nepracuješ? — Protože jsem nemocný.', ['proč'], 'The answer starts with „protože“.', 'Reason → <b>Proč</b>?', 'Easy'),
    ('Nikdo to ___ . (vědět, negative)', ['neví'], 'nikdo needs a negative verb.', 'vědět → on ví → negative <b>neví</b>; double negative is correct.', 'Medium'),
    ('Já ___ nemám. (nothing)', ['nic'], 'Negative pronoun for „nothing“.', '„nothing“ = <b>nic</b>, with a negative verb: <i>Nic nemám.</i>', 'Medium'),
    ('My ___ nepracujeme v neděli. (never)', ['nikdy'], 'Negative adverb of time.', '„never“ = <b>nikdy</b> + negative verb.', 'Medium'),
    ('Oni dnes ___ . (pracovat, negative)', ['nepracují', 'nepracujou'], 'ne + oni form.', 'ne + pracují → <b>nepracují</b>.', 'Medium'),
])

# ---------------------------------------------------------------- 5
topic('5 · přídavná jména (1. pád)', f'''
<p>Adjectives agree with the noun's gender. There are two types.</p>
{T(('hard (-ý)','nový počítač','nová firma','nové auto'),('soft (-í)','moderní počítač','moderní firma','moderní auto'), head=('type','masculine','feminine','neuter'))}
<p><b>Hard</b> adjectives change: <b>-ý / -á / -é</b>. <b>Soft</b> adjectives (ending in <b>-í</b>) stay the same for all genders.</p>
<p>So first find the noun's gender (topic 2), then pick the ending.</p>
<p><b>Typical mistakes:</b> „nový kancelář“ (kancelář is feminine → <i>nová kancelář</i>), „moderná firma“ (soft → <i>moderní</i>).</p>''', [
    ('To je ___ počítač. (nový)', ['nový'], 'počítač = masculine.', 'masculine + hard → <b>nový</b>.', 'Easy'),
    ('To je ___ kancelář. (nový)', ['nová'], 'kancelář = feminine (exception!).', 'feminine + hard → <b>nová</b>.', 'Medium'),
    ('To je ___ auto. (nový)', ['nové'], 'auto = neuter.', 'neuter + hard → <b>nové</b>.', 'Easy'),
    ('___ firma má sto lidí. (velký)', ['velká'], 'firma = feminine.', 'feminine → <b>velká</b>.', 'Easy'),
    ('To je ___ okno. (velký)', ['velké'], 'okno = neuter.', 'neuter → <b>velké</b>.', 'Easy'),
    ('To je ___ tabulka. (dlouhý)', ['dlouhá'], 'tabulka = feminine.', 'feminine → <b>dlouhá</b>.', 'Easy'),
    ('Dnes je ___ den. (dobrý)', ['dobrý'], 'den = masculine.', 'masculine → <b>dobrý</b>.', 'Easy'),
    ('Praha je ___ město. (krásný)', ['krásné'], 'město = neuter.', 'neuter → <b>krásné</b>.', 'Easy'),
    ('To je ___ kancelář. (moderní)', ['moderní'], 'Soft adjective (-í).', 'soft adjectives keep <b>-í</b> in all genders → <b>moderní</b>.', 'Medium'),
    ('To je ___ práce. (zajímavý)', ['zajímavá'], 'práce = feminine.', 'feminine → <b>zajímavá</b>.', 'Medium'),
    ('To číslo je ___ . (správný)', ['správné'], 'číslo = neuter.', 'neuter → <b>správné</b>.', 'Easy'),
    ('Jana je ___ kolegyně. (český)', ['česká'], 'kolegyně = feminine.', 'feminine → <b>česká</b>.', 'Medium'),
    ('To je ___ e-mail. (důležitý)', ['důležitý'], 'e-mail = masculine.', 'masculine → <b>důležitý</b>.', 'Easy'),
])

# ---------------------------------------------------------------- 6
topic('6 · přivlastňovací zájmena (1. pád)', f'''
<p>Possessives agree with the gender of the <b>thing owned</b>, not of the owner.</p>
{T(('můj','moje / má','moje / mé'),('tvůj','tvoje / tvá','tvoje / tvé'),('náš','naše','naše'),('váš','vaše','vaše'), head=('masculine','feminine','neuter'))}
<p>The short forms (<i>má, mé, tvá, tvé</i>) are a bit more formal; both are correct.</p>
<p><b>his / her / their never change:</b> <i>jeho</i> (his), <i>její</i> (her), <i>jejich</i> (their): <i>jeho žena, jeho auto · její manžel, její auto · jejich dům</i>.</p>
<p><b>Typical mistakes:</b> „můj sestra“ (→ <i>moje sestra</i>), „jeho“ for a woman owner (→ <i>její</i>).</p>''', [
    ('To je ___ kolega. (můj)', ['můj'], 'kolega = masculine (a man).', 'masculine → <b>můj</b>.', 'Easy'),
    ('To je ___ sestra. (můj)', ['moje', 'má'], 'sestra = feminine.', 'feminine → <b>moje</b> (or má).', 'Easy'),
    ('To je ___ auto. (můj)', ['moje', 'mé'], 'auto = neuter.', 'neuter → <b>moje</b> (or mé).', 'Easy'),
    ('Kde je ___ telefon? (tvůj)', ['tvůj'], 'telefon = masculine.', 'masculine → <b>tvůj</b>.', 'Easy'),
    ('___ firma je velká. (náš)', ['naše'], 'firma = feminine.', 'feminine → <b>naše</b>.', 'Easy'),
    ('___ šéf je dnes tady. (náš)', ['náš'], 'šéf = masculine.', 'masculine → <b>náš</b>.', 'Easy'),
    ('To je ___ kancelář? (váš)', ['vaše'], 'kancelář = feminine.', 'feminine → <b>vaše</b>.', 'Medium'),
    ('To je Petr a to je ___ žena. (his)', ['jeho'], 'his never changes.', '„his“ = <b>jeho</b> for every gender.', 'Easy'),
    ('To je Jana a to je ___ manžel. (her)', ['její'], 'her never changes.', '„her“ = <b>její</b> for every gender.', 'Medium'),
    ('___ tým je nejlepší. (váš)', ['váš'], 'tým = masculine.', 'masculine → <b>váš</b>.', 'Easy'),
    ('To je ___ dítě? (tvůj)', ['tvoje', 'tvé'], 'dítě = neuter.', 'neuter → <b>tvoje</b> (or tvé).', 'Medium'),
    ('To jsou Novákovi a to je ___ dům. (their)', ['jejich'], 'their never changes.', '„their“ = <b>jejich</b>.', 'Easy'),
])

# ---------------------------------------------------------------- 7
topic('7 · čísla 1–100', f'''
<p><b>1 and 2 change with gender:</b> <i>jeden</i> muž / <i>jedna</i> žena / <i>jedno</i> auto · <i>dva</i> muži / <i>dvě</i> ženy / <i>dvě</i> auta.</p>
{T(('1 jeden/jedna/jedno','11 jedenáct','10 deset'),('2 dva/dvě','12 dvanáct','20 dvacet'),('3 tři','13 třináct','30 třicet'),('4 čtyři','14 čtrnáct','40 čtyřicet'),('5 pět','15 patnáct','50 padesát'),('6 šest','16 šestnáct','60 šedesát'),('7 sedm','17 sedmnáct','70 sedmdesát'),('8 osm','18 osmnáct','80 osmdesát'),('9 devět','19 devatenáct','90 devadesát'),('','','100 sto'), head=('1–9','11–19','tens'))}
<p>21–99: <i>dvacet jedna</i> (or <i>jedenadvacet</i>), <i>třicet pět</i>, <i>čtyřicet dva</i>…</p>
<p><b>Typical mistakes:</b> „čtyřnáct“ (→ <i>čtrnáct</i>), „pětdesát“ (→ <i>padesát</i>), „devětdesát“ (→ <i>devadesát</i>), „dva ženy“ (→ <i>dvě</i>).</p>''', [
    ('Mám ___ sestry. (2)', ['dvě'], 'sestra = feminine.', 'feminine → <b>dvě</b>.', 'Medium'),
    ('V týmu jsou ___ muži. (2)', ['dva'], 'muž = masculine.', 'masculine → <b>dva</b>.', 'Easy'),
    ('Pracuji tady ___ let. (12)', ['dvanáct'], '10 + 2.', '12 = <b>dvanáct</b>.', 'Easy'),
    ('Máme ___ zákazníků. (15)', ['patnáct'], 'Watch the spelling: pat-.', '15 = <b>patnáct</b> (not „pětnáct“).', 'Medium'),
    ('Je mu ___ let. (40)', ['čtyřicet'], '4 × 10.', '40 = <b>čtyřicet</b>.', 'Easy'),
    ('Stojí to ___ korun. (50)', ['padesát'], 'Irregular spelling.', '50 = <b>padesát</b> (not „pětdesát“).', 'Medium'),
    ('Tabulka má ___ řádků. (90)', ['devadesát'], 'Irregular spelling.', '90 = <b>devadesát</b>.', 'Medium'),
    ('Máme ___ firmu. (1)', ['jednu'], 'firma = feminine; after „Máme“ the form is accusative.', 'feminine, accusative: jedna → <b>jednu</b> (see topic 8).', 'Hard'),
    ('Je tam ___ auto. (1)', ['jedno'], 'auto = neuter.', 'neuter → <b>jedno</b>.', 'Easy'),
    ('Mám ___ počítač. (1)', ['jeden'], 'počítač = masculine inanimate.', 'masculine → <b>jeden</b>.', 'Easy'),
    ('Je mi ___ let. (21)', ['dvacet jedna', 'jedenadvacet'], 'Two ways to say it.', '21 = <b>dvacet jedna</b> or <b>jedenadvacet</b>.', 'Medium'),
    ('Tabulka má ___ sloupců. (14)', ['čtrnáct'], 'Watch the spelling.', '14 = <b>čtrnáct</b> (not „čtyřnáct“).', 'Medium'),
    ('Mám ___ e-mailů. (19)', ['devatenáct'], '9 + teen.', '19 = <b>devatenáct</b>.', 'Medium'),
    ('Zaplatil jsem ___ korun. (100)', ['sto'], 'One hundred.', '100 = <b>sto</b>.', 'Easy'),
])

# ---------------------------------------------------------------- 8
topic('8 · 4. pád (akuzativ)', f'''
<p>The <b>accusative</b> (4. pád) is the direct object: <i>koho? co?</i> — after verbs like <i>mít, vidět, hledat, potřebovat, znát, pít, číst</i>.</p>
{T(('masculine animate (people, animals)','-a / -u','Petr → <b>Petra</b>, bratr → <b>bratra</b>, kolega → <b>kolegu</b>'),('masculine inanimate','no change','počítač → <b>počítač</b>'),('feminine -a','-u','káva → <b>kávu</b>, kniha → <b>knihu</b>'),('feminine -e / consonant','-i / no change','práce → <b>práci</b>, kancelář → <b>kancelář</b>'),('neuter','no change','auto → <b>auto</b>'), head=('gender','ending','examples'))}
<p><b>Adjectives</b> follow: <i>nového</i> kolegu (m. animate) · <i>nový</i> počítač (m. inanimate) · <i>novou</i> práci (f) · <i>nové</i> auto (n).</p>
<p><b>Typical mistakes:</b> „Mám bratr“ (→ <i>bratra</i>), „Piju káva“ (→ <i>kávu</i>), „Hledám nový kolega“ (→ <i>nového kolegu</i>).</p>''', [
    ('Mám ___ . (bratr)', ['bratra'], 'Masculine animate.', 'bratr (person) → <b>bratra</b>.', 'Easy'),
    ('Piju ___ . (káva)', ['kávu'], 'Feminine -a.', 'káva → <b>kávu</b>.', 'Easy'),
    ('Hledám ___ . (kolega)', ['kolegu'], 'Masculine animate ending in -a.', 'kolega → <b>kolegu</b>.', 'Medium'),
    ('Mám ___ . (nový počítač)', ['nový počítač'], 'Masculine inanimate.', 'inanimate → no change: <b>nový počítač</b>.', 'Medium'),
    ('Čtu ___ . (kniha)', ['knihu'], 'Feminine -a.', 'kniha → <b>knihu</b>.', 'Easy'),
    ('Máme nové ___ . (auto)', ['auto'], 'Neuter.', 'neuter → no change: <b>auto</b>.', 'Easy'),
    ('Znáš ___ ? (Petr)', ['Petra'], 'Masculine animate.', 'Petr → <b>Petra</b>.', 'Easy'),
    ('Mám novou ___ . (práce)', ['práci'], 'Feminine -e.', 'práce → <b>práci</b>.', 'Medium'),
    ('Potřebuju ___ . (tabulka)', ['tabulku'], 'Feminine -a.', 'tabulka → <b>tabulku</b>.', 'Easy'),
    ('Mám ___ . (sestra)', ['sestru'], 'Feminine -a.', 'sestra → <b>sestru</b>.', 'Easy'),
    ('Vidím ___ . (pan Novák)', ['pana Nováka'], 'Both words: masculine animate.', 'pan Novák → <b>pana Nováka</b>.', 'Medium'),
    ('Mám ___ . (nová práce)', ['novou práci'], 'Feminine adjective + noun.', 'nová práce → <b>novou práci</b>.', 'Hard'),
    ('Hledáme ___ . (dobrý analytik)', ['dobrého analytika'], 'Masculine animate adjective + noun.', 'dobrý analytik → <b>dobrého analytika</b>.', 'Hard'),
])

# ---------------------------------------------------------------- 9
topic('9 · modální slovesa', f'''
<p><b>chtít</b> (want), <b>moct</b> (can), <b>muset</b> (must) + <b>infinitive</b>: <i>Chci pracovat.</i> · <i>Můžu se zeptat?</i> · <i>Musím odejít.</i></p>
{T(('já','chci','můžu / mohu','musím'),('ty','chceš','můžeš','musíš'),('on / ona','chce','může','musí'),('my','chceme','můžeme','musíme'),('vy','chcete','můžete','musíte'),('oni','chtějí','můžou / mohou','musí'), head=('person','chtít','moct','muset'))}
<p>The second verb stays in the <b>infinitive</b> (-t): <i>Chci mluvit česky</i> — not „chci mluvím“.</p>
<p><b>Typical mistakes:</b> „já chcu“ (→ <i>chci</i>), „oni chcou“ (→ <i>chtějí</i>), „musím pracuju“ (→ <i>musím pracovat</i>).</p>''', [
    ('Já ___ kávu. (chtít)', ['chci'], 'Irregular: já form.', 'chtít → já <b>chci</b>.', 'Easy'),
    ('Ty ___ jít s námi? (chtít)', ['chceš'], 'ty form.', 'chtít → ty <b>chceš</b>.', 'Easy'),
    ('Oni ___ pracovat doma. (chtít)', ['chtějí'], 'Irregular oni form.', 'chtít → oni <b>chtějí</b> (not „chcou“).', 'Medium'),
    ('___ se zeptat? (já, moct)', ['můžu', 'mohu'], 'já form; two variants.', 'moct → já <b>můžu</b> (formal: mohu).', 'Medium'),
    ('Ona ___ přijít zítra. (moct)', ['může'], 'ona form.', 'moct → ona <b>může</b>.', 'Easy'),
    ('My ___ začít. (moct)', ['můžeme'], 'my form.', 'moct → my <b>můžeme</b>.', 'Easy'),
    ('Oni ___ zůstat. (moct)', ['můžou', 'mohou'], 'oni form; two variants.', 'moct → oni <b>můžou</b> (formal: mohou).', 'Medium'),
    ('Já ___ dnes pracovat. (muset)', ['musím'], '-í pattern.', 'muset → já <b>musím</b>.', 'Easy'),
    ('Vy ___ počkat. (muset)', ['musíte'], 'vy form.', 'muset → vy <b>musíte</b>.', 'Easy'),
    ('Oni ___ odejít. (muset)', ['musí'], 'oni = same as on.', 'muset → oni <b>musí</b>.', 'Medium'),
    ('Ty ___ to udělat dnes. (muset)', ['musíš'], 'ty form.', 'muset → ty <b>musíš</b>.', 'Easy'),
    ('Chci ___ česky. (mluvit)', ['mluvit'], 'After a modal verb → infinitive.', 'modal + <b>infinitive</b>: Chci <b>mluvit</b>.', 'Medium'),
    ('Musím ___ e-mail. (napsat)', ['napsat'], 'After a modal verb → infinitive.', 'modal + <b>infinitive</b>: Musím <b>napsat</b>.', 'Medium'),
])

# ---------------------------------------------------------------- 10
topic('10 · kde? v / na + 6. pád', f'''
<p><b>Where?</b> = <i>v</i> (in) or <i>na</i> (on, at) + the <b>locative</b> (6. pád). Before some consonant groups <i>v</i> becomes <b>ve</b>: <i>ve škole, ve městě</i>.</p>
{T(('feminine -a','-e / -ě (k→c, h→z, r→ř)','Praha → v <b>Praze</b>, škola → ve <b>škole</b>, pošta → na <b>poště</b>, tabulka → v <b>tabulce</b>'),('feminine -e / consonant','-i','práce → v <b>práci</b>, kancelář → v <b>kanceláři</b>'),('masculine','-u / -ě','obchod → v <b>obchodě</b>, počítač → v <b>počítači</b>'),('neuter -o','-ě / -u','Brno → v <b>Brně</b>, město → ve <b>městě</b>, auto → v <b>autě</b>'),('neuter -í','no change','nádraží → na <b>nádraží</b>'), head=('noun type','ending','examples'))}
<p><b>v or na?</b> Most places take <i>v</i>; learn the <i>na</i> ones as fixed phrases: <i>na poště, na nádraží, na schůzce, na úřadě, na Slovensku</i>.</p>
<p><b>Typical mistakes:</b> „v Praha“ (→ <i>v Praze</i>), „v pošta“ (→ <i>na poště</i>), „ve Brno“ (→ <i>v Brně</i>).</p>''', [
    ('Bydlím v ___ . (Praha)', ['Praze'], 'Feminine -a; h changes.', 'Praha → h→z + e → v <b>Praze</b>.', 'Medium'),
    ('Pracuji v ___ . (Brno)', ['Brně'], 'Neuter -o → -ě.', 'Brno → v <b>Brně</b>.', 'Medium'),
    ('Jsem v ___ . (kancelář)', ['kanceláři'], 'Feminine consonant → -i.', 'kancelář → v <b>kanceláři</b>.', 'Medium'),
    ('Jsem na ___ . (pošta)', ['poště'], 'Feminine -a → -ě; uses „na“.', 'pošta → na <b>poště</b>.', 'Medium'),
    ('Děti jsou ve ___ . (škola)', ['škole'], 'Feminine -a → -e.', 'škola → ve <b>škole</b>.', 'Easy'),
    ('Jsem v ___ . (práce)', ['práci'], 'Feminine -e → -i.', 'práce → v <b>práci</b>.', 'Easy'),
    ('Čekám na ___ . (nádraží)', ['nádraží'], 'Neuter -í.', 'nádraží → no change: na <b>nádraží</b>.', 'Easy'),
    ('Jsme na ___ . (schůzka)', ['schůzce'], 'Feminine -ka → k changes.', 'schůzka → k→c + e → na <b>schůzce</b>.', 'Hard'),
    ('Data jsou v ___ . (tabulka)', ['tabulce'], 'Feminine -ka → k changes.', 'tabulka → k→c + e → v <b>tabulce</b>.', 'Hard'),
    ('Bydlím ve ___ . (město)', ['městě'], 'Neuter -o → -ě.', 'město → ve <b>městě</b>.', 'Medium'),
    ('Jsem v ___ . (obchod)', ['obchodě'], 'Masculine → -ě.', 'obchod → v <b>obchodě</b>.', 'Medium'),
    ('Data jsou v ___ . (databáze)', ['databázi'], 'Feminine -e → -i.', 'databáze → v <b>databázi</b>.', 'Medium'),
    ('Sedím v ___ . (auto)', ['autě'], 'Neuter -o → -ě.', 'auto → v <b>autě</b>.', 'Medium'),
])

# ---------------------------------------------------------------- 11
topic('11 · množné číslo (1. pád)', f'''
<p>Plural nominative (1. pád) — what you say after <i>dva / dvě / tři / čtyři</i> and for „the … are“.</p>
{T(('masculine animate','-i / -ové','student → <b>studenti</b>, zákazník → <b>zákazníci</b> (k→c), kolega → <b>kolegové</b>'),('masculine inanimate','-y / -e','stůl → <b>stoly</b>, e-mail → <b>e-maily</b>, počítač → <b>počítače</b>'),('feminine -a','-y','firma → <b>firmy</b>, tabulka → <b>tabulky</b>'),('feminine -e / consonant','-e','práce → <b>práce</b>, kancelář → <b>kanceláře</b>'),('neuter -o','-a','auto → <b>auta</b>, číslo → <b>čísla</b>'), head=('gender','ending','examples'))}
<p>Soft consonants (<i>č, ř, š, ž, j, c</i>) usually take <b>-e</b>, hard ones <b>-y</b>.</p>
<p><b>Typical mistakes:</b> „dva studenty“ (→ <i>studenti</i>), „dvě auty“ (→ <i>auta</i>), „zákazníki“ (→ <i>zákazníci</i>).</p>''', [
    ('jeden student – dva ___', ['studenti'], 'Masculine animate.', 'student → <b>studenti</b>.', 'Easy'),
    ('jedna firma – dvě ___', ['firmy'], 'Feminine -a.', 'firma → <b>firmy</b>.', 'Easy'),
    ('jedno auto – dvě ___', ['auta'], 'Neuter -o.', 'auto → <b>auta</b>.', 'Easy'),
    ('jeden stůl – dva ___', ['stoly'], 'Masculine inanimate; ů → o.', 'stůl → <b>stoly</b>.', 'Medium'),
    ('jeden počítač – dva ___', ['počítače'], 'Masculine inanimate, soft č.', 'počítač → soft → <b>počítače</b>.', 'Medium'),
    ('jedna tabulka – dvě ___', ['tabulky'], 'Feminine -a.', 'tabulka → <b>tabulky</b>.', 'Easy'),
    ('jedno číslo – dvě ___', ['čísla'], 'Neuter -o.', 'číslo → <b>čísla</b>.', 'Easy'),
    ('jedna kancelář – dvě ___', ['kanceláře'], 'Feminine consonant.', 'kancelář → <b>kanceláře</b>.', 'Medium'),
    ('jedna schůzka – dvě ___', ['schůzky'], 'Feminine -a.', 'schůzka → <b>schůzky</b>.', 'Easy'),
    ('jeden kolega – dva ___', ['kolegové'], 'Masculine animate ending in -a.', 'kolega → <b>kolegové</b>.', 'Medium'),
    ('jeden e-mail – dva ___', ['e-maily'], 'Masculine inanimate, hard l.', 'e-mail → <b>e-maily</b>.', 'Easy'),
    ('jedno okno – dvě ___', ['okna'], 'Neuter -o.', 'okno → <b>okna</b>.', 'Easy'),
    ('jeden zákazník – dva ___', ['zákazníci'], 'Masculine animate; k changes.', 'zákazník → k→c → <b>zákazníci</b>.', 'Hard'),
])

# ---------------------------------------------------------------- 12
topic('12 · minulý čas', f'''
<p>Past tense = <b>l-form</b> of the verb (+ <i>jsem / jsi</i> for <i>já / ty</i>, + <i>jsme / jste</i> for <i>my / vy</i>). The 3rd person has no helper verb.</p>
{T(('já','byl jsem','byla jsem'),('ty','byl jsi','byla jsi'),('on / ona','byl','byla'),('my','byli jsme','byly jsme (only women)'),('vy','byli jste','byly jste'),('oni','byli','byly (only women / things)'), head=('person','man / masculine','woman / feminine'))}
<p>Endings: <b>-l</b> (m), <b>-la</b> (f), <b>-lo</b> (n), <b>-li</b> (m. plural), <b>-ly</b> (f. plural).</p>
<p>Irregular l-forms: <i>být → byl · mít → měl · jít → šel / šla · číst → četl · jíst → jedl · moct → mohl · chtít → chtěl · psát → psal · pít → pil</i>.</p>
<p><b>Word order:</b> <i>jsem / jsi</i> go to the second position: <i>Včera <b>jsem</b> byl doma.</i> · <i>Byl <b>jsem</b> doma.</i> (never first).</p>
<p><b>Typical mistakes:</b> „Jsem byl“ at the start (→ <i>Byl jsem</i>), „on byl jsem“ (3rd person has no jsem), „ona byl“ (→ <i>byla</i>).</p>''', [
    ('Včera ___ doma. (já, man, být)', ['jsem byl'], '„Včera“ is first, so „jsem“ comes second.', 'já (man) → <b>jsem byl</b>: Včera jsem byl doma.', 'Medium'),
    ('Včera ___ doma. (já, woman, být)', ['jsem byla'], 'Feminine l-form.', 'já (woman) → <b>jsem byla</b>.', 'Medium'),
    ('Petr ___ v práci. (být)', ['byl'], '3rd person: no jsem.', 'on → <b>byl</b>.', 'Easy'),
    ('Jana ___ e-mail. (psát)', ['psala'], 'Feminine l-form, 3rd person.', 'ona + psát → <b>psala</b>.', 'Easy'),
    ('My ___ na schůzce. (být)', ['jsme byli'], 'my + jsme + plural l-form.', 'my → <b>jsme byli</b>.', 'Medium'),
    ('___ včera čas? (ty, man, mít)', ['měl jsi'], 'Question starts with the verb; jsi second.', 'mít → měl; ty → <b>Měl jsi</b>?', 'Hard'),
    ('Oni ___ do kina. (jít)', ['šli'], 'Irregular: jít → šel.', 'jít → oni <b>šli</b>.', 'Hard'),
    ('Ona ___ kávu. (pít)', ['pila'], 'Feminine l-form.', 'pít → ona <b>pila</b>.', 'Easy'),
    ('___ knihu. (já, man, číst)', ['četl jsem'], 'Irregular l-form; jsem second.', 'číst → četl → <b>Četl jsem</b> knihu.', 'Hard'),
    ('___ dotaz? (vy, mít)', ['měli jste'], 'Plural l-form; jste second.', 'mít → měli → <b>Měli jste</b> dotaz?', 'Hard'),
    ('To auto ___ nové. (být)', ['bylo'], 'auto = neuter.', 'neuter → <b>bylo</b>.', 'Medium'),
    ('Kolegové ___ přijít. (chtít)', ['chtěli'], 'Masculine plural, irregular stem.', 'chtít → chtěl → plural <b>chtěli</b>.', 'Medium'),
    ('___ dlouho pracovat. (já, woman, muset)', ['musela jsem'], 'Feminine l-form; jsem second.', 'muset → musela → <b>Musela jsem</b>.', 'Hard'),
])


def questions():
    out = []
    for name, lesson, drills in TOPICS:
        out.append(dict(t='Lesson: ' + name.split(' · ', 1)[1], d='Easy', g=name, p=lesson.strip(), h='', s='', o=False, k='lesson', a=''))
        for prompt, answers, hint, why, diff in drills:
            title = prompt.replace('___', '…')
            if prompt.startswith('___'):   # gap opens the sentence -> show the answer capitalised (checking ignores case)
                answers = [x[0].upper() + x[1:] for x in answers]
            out.append(dict(t=title[:46], d=diff, g=name, p=prompt, h=hint, s='', o=False, k='cz', a=answers, w=why))
    return out
