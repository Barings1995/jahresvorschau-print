#!/usr/bin/env python3
"""Jahresvorschau Print – baut die neutrale Fassung aus der Web-Fassung.

Aufruf (aus diesem Ordner):  python3 bauen.py

Liest  ../Jahresvorschau Web/index.html  (wird nicht veraendert)
und schreibt  Jahresvorschau_Print.html  (leer, ohne Daten).

Jeder Eingriff ist ein woertlicher Austausch mit gezaehlter Fundstelle. Aendert
sich die Web-Fassung an einer dieser Stellen, bricht der Lauf mit einer Meldung
ab, statt still eine halbe Datei zu erzeugen. Dann wird der betroffene Austausch
hier nachgezogen. So lassen sich Verbesserungen der Web-Fassung spaeter mit
einem erneuten Lauf uebernehmen, statt sie zweimal von Hand einzubauen.

Was die Print-Fassung anders macht:
  * keine Datenbank, keine Anmeldung: die Tabellen stehen in der Datei selbst
    (Block <script id="tabellen">); dbAnfrage() arbeitet auf ihnen und
    versteht dieselben Pfade wie die Datenbank, der uebrige Code bleibt gleich
  * Sichern in dieselbe Datei (Chrome/Edge), sonst als Download
  * Fachbereich frei waehlbar, statt fest "Onkologie" - und mehrere
    Fachbereiche in einer Datei, umgeschaltet im Kopf; jeder fuehrt eigene
    Tabellen (Jahrgaenge, Titel, Ausgaben, Sicherungspunkte)
  * leerer Start mit Begruessung
  * weitere Rubriken je Titel (etwa CME-Beitraege)
  * "Weitere Rubriken" im Inhaltsfilter nur, wenn es sie gibt
  * Kongresse wie in der Datenpflege: eine Textzeile je Kongress an der
    Ausgabe, ohne Trennung Auslage/Bericht ("(Bericht)" steht im Text), ohne
    Kongressmatrix und ohne Kongressliste
  * Kontakt je Fachbereich (Name, Funktion, Telefon, E-Mail) im Kopf und im
    PDF unter dem Logo
  * Titelcover je Titel und Jahrgang als Leiste ueber der Uebersicht, nur fuer
    die gewaehlten Titel
  * ohne die Onkologie-Schreibweisen der Kongresse und ohne die Ausgaben fuer
    die Datenpflege der Angebotswerkzeuge
"""
import hashlib, pathlib, re, sys

HIER = pathlib.Path(__file__).resolve().parent
QUELLE = HIER.parent / 'Jahresvorschau Web' / 'index.html'
ZIEL = HIER / 'Jahresvorschau_Print.html'

roh = QUELLE.read_bytes()
md5 = hashlib.md5(roh).hexdigest()
s = roh.decode('utf-8')


def rep(alt, neu, anzahl=1):
    global s
    n = s.count(alt)
    if n != anzahl:
        sys.exit(f'Abbruch: erwartet {anzahl}x, gefunden {n}x:\n{alt[:160]}')
    s = s.replace(alt, neu)


def rep_re(muster, neu, anzahl=1, flags=re.S):
    global s
    treffer = re.findall(muster, s, flags)
    if len(treffer) != anzahl:
        sys.exit(f'Abbruch: Muster erwartet {anzahl}x, gefunden {len(treffer)}x:\n{muster[:160]}')
    s = re.sub(muster, lambda m: neu, s, flags=flags)


# ── Kopf ────────────────────────────────────────────────────────────────────
rep('<title>Jahresvorschau Onkologie/Print · Springer Medizin</title>',
    '<title>Jahresvorschau Print · Springer Medizin</title>\n'
    f'<meta name="jahresvorschau-fassung" content="Print 3 · gebaut aus der Web-Fassung {md5}">')
rep_re(r'<meta name="description" content="Jahresvorschau 2026 der Springer-Medizin-Onkologie-Printtitel:[^"]*">',
       '<meta name="description" content="Jahresvorschau der Printtitel eines Fachbereichs: '
       'Erscheinungstermine, Anzeigenschluss, Kongresse und Themen – '
       'filter- und durchsuchbar.">')
rep('<script src="konfiguration.js"></script>',
    "<script>/* Print-Fassung: keine Datenbank */ const SUPABASE_URL = '', SUPABASE_ANON_KEY = '';</script>")

# Ohne Anmeldung: Anmeldemaske und Netzhinweis fallen weg.
rep_re(r'<!-- Anmeldung\. Ohne Sitzung.*?<div id="netzhinweis" hidden></div>\n', '')

# Fachbereich statt "Onkologie"
rep('<span class="accent">Onkologie/Print</span>',
    '<span class="fach-wrap"><button type="button" class="fach-wahl" id="fachWahl" '
    'aria-haspopup="true" aria-expanded="false" onclick="toggleFach(event)" title="Fachbereich wechseln">'
    '<span class="accent" id="fachKopf">Print</span></button>'
    '<div class="export-menu fach-menu" id="fachMenu" role="menu"></div></span>')
# Der Jahrgang daneben wird dasselbe Klappmenue, mit "Jahrgang anlegen" darin.
# Die Kennung yearSel sitzt am aeusseren Behaelter: die HTML-Kopie ersetzt ihn
# im Ganzen durch festen Text (baueKopie), samt Menue.
rep('<select class="hero-year" id="yearSel" aria-label="Jahrgang wählen" onchange="waehleJahrgang(this.value)"></select>',
    '<span class="jahr-wrap" id="yearSel"><button type="button" class="hero-year jahr-wahl" id="jahrWahl" '
    'aria-haspopup="true" aria-expanded="false" onclick="toggleJahr(event)" title="Jahrgang wechseln oder anlegen">'
    '<span id="jahrKopf"></span></button>'
    '<div class="export-menu fach-menu" id="jahrMenu" role="menu"></div></span>')
rep('''  s.innerHTML = jahrgaenge().map(y=>
    `<option value="${y}"${y===jahr?' selected':''}>${y}</option>`).join('');''',
    '''  const k=document.getElementById('jahrKopf');
  if(k) k.textContent = jahr;''')
rep_re(r'\n        <button class="ex-item" role="menuitem" onclick="jahrgangAnlegen\(\)">.*?</button>', '')
rep('Jahresvorschau <span>Onkologie/Print</span> ${jahrgang()}',
    'Jahresvorschau <span>${esc(fachKopf())}</span> ${jahrgang()}')
rep('`Jahresvorschau_Onkologie-Print_${jahrgang()}`', '`Jahresvorschau_${dateiFach()}Print_${jahrgang()}`')
rep('`Jahresvorschau Onkologie/Print ${jahrgang()}`', '`Jahresvorschau ${fachKopf()} ${jahrgang()}`', 2)

# Die Schreibweisen-Tabelle der Onkologie-Kongresse entfaellt.
rep_re(r'const KONGRESSE = \[\n.*?\n\];', 'const KONGRESSE = [\n];')

# Texte, die von der Datenbank sprechen oder die Onkologie voraussetzen
rep('Der Jahrgang wird in der Datenbank ersetzt', 'Der Jahrgang wird ersetzt')
rep('Ausgaben und Sicherungspunkten aus der Datenbank</span>', 'Ausgaben und Sicherungspunkten aus der Datei</span>')
# Der Warnkasten beim Excel-Laden nennt den Sicherungspunkt, der vorher entsteht
rep("""<div class="pr-warn-kopf">Beim Übernehmen gehen Angaben verloren</div>${fehlt}</div>""",
    """<div class="pr-warn-kopf">Beim Übernehmen gehen Angaben verloren</div>${fehlt}<br>"""
    """Der bisherige Stand bleibt als Sicherungspunkt »Vor dem Laden aus Excel« erhalten.</div>""")
# Sicherungspunkt auch aus einem nicht gezeigten Fachbereich (vor dem Uebernehmen)
rep('''function jahrgangAlsBlock(y){
  const jetzt = !y || y===jahrgang();
  const stand = jetzt ? standText() : ((DATEN[y] && DATEN[y].stand) || '');
  const titel = jetzt ? JOURNALS   : ((DATEN[y] && DATEN[y].titel) || []);''',
    '''function jahrgangAlsBlock(y, daten){
  const jetzt = !daten && (!y || y===jahrgang());
  const d = daten || DATEN[y];
  const stand = jetzt ? standText() : ((d && d.stand) || '');
  const titel = jetzt ? JOURNALS   : ((d && d.titel) || []);''')
rep('`Jahrgang ${y} wird in die Datenbank geschrieben …`', '`Jahrgang ${y} wird übernommen …`')
rep('Dieser Jahrgang wird aus der Datenbank entfernt', 'Dieser Jahrgang wird aus der Datei entfernt')
rep("' wird aus der Datenbank entfernt.</p>'", "' wird entfernt.</p>'")
rep('''<span class="hinweis">H&ouml;chstens zwei Eintr&auml;ge; ein zweiter kommt
        in der Regel nur in der &Auml;rzte Zeitung ONKOLOGIE UND H&Auml;MATOLOGIE
        vor</span>''', '<span class="hinweis">H&ouml;chstens zwei Eintr&auml;ge</span>')
rep("  return 'Der Zugriff ist fehlgeschlagen: ' + roh;", '  return roh;')

# Ausgaben fuer die Datenpflege der Angebotswerkzeuge entfallen.
rep_re(r'\s*<button class="ex-item" role="menuitem" onclick="datenpflegeExport\(\)">.*?</button>', '')
rep_re(r"\n    \$\{neu \? '' : `<button type=\"button\" class=\"bearb-zu\" onclick=\"dpZeileKopieren\(\)\".*?</button>`\}", '')

# ── Kongresse als Text an der Ausgabe (seit Print 3) ───────────────────────
# Wie in der Datenpflege: ein Feld "Kongresse", eine Zeile je Kongress, von Hand
# eingetragen. Keine eigenen Kongresssaetze, keine Trennung Auslage/Bericht -
# ein seltener Bericht steht als "(Bericht)" im Text. Dafuer bleibt die
# Fassung auf dem Freitextweg der Web-Fassung (KONG_TABELLEN bleibt false):
# Kongressmatrix ("Nach Kongress") und Kongressliste entfallen.
rep("""async function vielleicht(pfad){
  try{ const r = await dbAnfrage(pfad); KONG_TABELLEN = true; return r; }
  catch(fehler){ return []; }
}""", """async function vielleicht(pfad){ return []; }   // Print: Kongresse nur als Text""")
rep("      a: a.auslagen || [], b: a.berichte || [],",
    "      a: kongresseZusammen(a.auslagen, a.berichte), b: [],")
rep("function zeigtB(){ return modus.size===0 || modus.has('bericht'); }",
    "function zeigtB(){ return false; }   // Print: Berichte stehen mit im Feld \"Kongresse\"")
rep('''<button class="mode-btn"        data-mode="auslage" onclick="setModus('auslage')">Auslagen</button>''',
    '''<button class="mode-btn"        data-mode="auslage" onclick="setModus('auslage')">Kongresse</button>''')
rep('''\n      <button class="mode-btn"        data-mode="bericht" onclick="setModus('bericht')">Berichte</button>''', '')
rep("const MODUS_TEXT = {auslage:'Kongressauslagen',", "const MODUS_TEXT = {auslage:'Kongresse',")
rep('''\n      <button class="view-btn"        data-view="kongress" onclick="setView('kongress')">Kongressliste</button>''', '')
# Aufgeklappte Monatsliste: Die Zeile hat schon eine Linie ueber dem Detail;
# der erste Block bringt deshalb keine eigene mit (sonst doppelte Linie).
rep(".ldetail .thema{border-top-color:var(--surface3)}\n",
    ".ldetail .thema{border-top-color:var(--surface3)}\n"
    ".ldetail>.thema:first-child{margin-top:0;padding-top:0;border-top:none}\n")
# Kongresse sehen in den Kacheln aus wie Themen und weitere Rubriken: ohne
# Symbol, gleiche Beschriftung, ein Eintrag je Zeile. Das Dreieck trennte in
# der Web-Fassung Auslagen von Berichten; diese Trennung gibt es hier nicht.
rep("""function kongBlock(liste,q,art){
  if(!liste.length)return'';
  const items=liste.map(t=>{
    const hit=q&&t.toLowerCase().includes(q.toLowerCase());
    return`<li class="ci${hit?' hit':''}">${hl(t,q)}</li>`;
  }).join('');
  const kopf = art==='auslage'
    ? `<div class="ctype auslage"><svg width="10" height="10" viewBox="0 0 10 10"><polygon points="0,0 10,5 0,10" fill="currentColor"/></svg>Kongressauslagen</div>`
    : `<div class="ctype bericht"><svg width="9" height="9" viewBox="0 0 10 10"><rect width="10" height="10" fill="currentColor" rx="1"/></svg>Kongressberichte</div>`;
  return`<div class="cs">${kopf}<ul class="clist">${items}</ul></div>`;
}""", """function kongBlock(liste,q){
  if(!liste.length) return '';
  const wort = liste.length>1 ? 'Kongresse' : 'Kongress';
  return `<div class="thema"><div class="tlbl">${wort}</div>`
    + liste.map(t=>`<div class="ttxt">${hl(t,q)}</div>`).join('')
    + '</div>';
}""")
rep("      if(zeigtA()) kong+=iss.a.map(n=>zeile(kongressText(n),'au','Auslage')).join('');",
    "      if(zeigtA()) kong+=iss.a.map(n=>`<div>${hl(kongressText(n),q)}</div>`).join('');")
rep('<div class="bearb-umschalter">${btn(\'ausgabe\',\'Nach Ausgabe\')}${btn(\'kongress\',\'Nach Kongress\')}</div>', '')
rep("""    ${zeilenGruppe('a','Kongressauslagen','Diese Ausgabe liegt auf dem Kongress aus')}
    ${zeilenGruppe('b','Kongressberichte','Über den Kongress wird berichtet')}""",
    """    ${zeilenGruppe('a','Kongresse','Ein Kongress je Zeile')}""")
rep('placeholder="Name des Kongresses"', 'placeholder="Kongress"')
rep("  const kAnzahl = (DATEN[vorlage] ? (DATEN[vorlage].kongresse||[]).length : 0);",
    "  const kAnzahl = 0;   // Print: Kongresse stehen als Text an den Heften")
# Excel: eine Spalte "Kongresse"; aeltere Dateien mit zwei Spalten bleiben lesbar.
rep("""  'Ein-/Durchhefter und Beilagen (EH)','Auflage','Themenschwerpunkte',
  'Kongressauslagen','Kongressberichte'];""", """  'Ein-/Durchhefter und Beilagen (EH)','Auflage','Themenschwerpunkte',
  'Kongresse'];""")
rep("""    spalte['Themenschwerpunkte']=spalte['Schwerpunkt'];
""", """    spalte['Themenschwerpunkte']=spalte['Schwerpunkt'];
  // Bis Print 2 standen Auslagen und Berichte in zwei Spalten.
  if(spalte['Kongresse']===undefined && spalte['Kongressauslagen']!==undefined)
    spalte['Kongresse']=spalte['Kongressauslagen'];
""")
rep("""      a:ausListenZelle(g('Kongressauslagen')),
      b:ausListenZelle(g('Kongressberichte'))};""",
    """      a:kongresseZusammen(ausListenZelle(g('Kongresse')),
        spalte['Kongressberichte']!==undefined ? ausListenZelle(g('Kongressberichte')) : []),
      b:[]};""")
rep("  if(zeigeA){ kopf1.push('Kongressauslagen'); breiten1.push(46); }",
    "  if(zeigeA){ kopf1.push('Kongresse'); breiten1.push(46); }")
rep("""  const kopf2=['Kongress','Zeitraum','Ort','Art','Titel','Heft',""",
    """  const kopf2=['Kongress','Zeitraum','Ort','Titel','Heft',""")
rep("  const breiten2=[52,15,20,10,40,7,13,13,13,16,9];", "  const breiten2=[52,15,20,40,7,13,13,13,16,9];")
# Kein zweites Blatt »Kongresse«: Die Spalte im Blatt »Ausgaben« zeigt jeden
# Kongress schon beim Heft, und Zeitraum und Ort liessen sich aus dem Freitext
# nicht verlaesslich herauslesen (Marcus, 10.10.2026). Die Zeilen werden noch
# gebaut, aber nicht mehr ausgegeben; baueXlsx kennt den Fall ohne zweites Blatt.
rep("    blatt2:   eintraege.length ? blattXml(breiten2,vorspann,kopf2,zeilen2) : null,",
    "    blatt2:   null,")
rep("Tabelle mit einer Zeile je Ausgabe, zweites Blatt je Kongress</span>",
    "Tabelle mit einer Zeile je Ausgabe</span>")
# Der Menuepunkt heisst »Aus Excel-Vorlage laden«, denn die Vorlage ist der
# uebliche Weg in dieser Fassung (Marcus, 11.10.2026). Austausch weiter unten,
# nach dem Einsetzen der Excel-Vorlage, das diesen Wortlaut als Anker nutzt.
# Die Erklaerung unter »Aus Excel laden« bleibt einzeilig, damit das Menue
# kurz bleibt; was eingelesen wird, sagt das Fenster danach (Marcus, 11.10.2026). Laeuft nach dem Austausch »in der Datenbank« weiter oben.
rep("Erwartet das Blatt &raquo;Ausgaben&laquo; dieses Werkzeugs, ausgegeben ohne Suche und Filter, mit einem vollst&auml;ndigen Jahrgang. Der Jahrgang wird ersetzt",
    "Ersetzt den Jahrgang")
rep("    const z=[{w:e.k.lang},{w:kongressZeitraum(e.k)},{w:e.k.ort||''},{w:e.art},",
    "    const z=[{w:e.k.lang},{w:kongressZeitraum(e.k)},{w:e.k.ort||''},")

# Bericht vor dem Laden aus Excel: beim ersten Befuellen ist der Jahrgang leer,
# und die Kennfarbe vergibt diese Fassung selbst.
rep("""      const vorher=DATEN[y]
        ? `ersetzt den vorhandenen Jahrgang mit""",
    """      const vorher=(DATEN[y] && DATEN[y].titel.some(j=>j.issues.length))
        ? `ersetzt den vorhandenen Jahrgang mit""")
rep("Farbe und vollständiger Name fehlen dafür.</div>`);",
    "Die Kennfarbe lässt sich danach unter »Bearbeiten« setzen.</div>`);")

# ── Bedienung: Inhaltsfilter, Sichern, Fachbereich ─────────────────────────
rep('''<button class="mode-btn"        data-mode="thema"   onclick="setModus('thema')">Themenschwerpunkte</button>''',
    '''<button class="mode-btn"        data-mode="thema"   onclick="setModus('thema')">Themenschwerpunkte</button>
      <button class="mode-btn"        data-mode="rubrik"  onclick="setModus('rubrik')" hidden>Weitere Rubriken</button>''')
rep("bericht:'Kongressberichte',thema:'Themenschwerpunkte'};",
    "bericht:'Kongressberichte',thema:'Themenschwerpunkte',rubrik:'Weitere Rubriken'};")
rep("['auslage','bericht','thema'].filter(k=>modus.has(k))", "['auslage','bericht','thema','rubrik'].filter(k=>modus.has(k))")
rep('  if(modus.size===3) modus.clear();', '  if(modus.size && modus.size===sichtbareArten().length) modus.clear();')
rep('''    <div class="daten-wrap">
      <button class="daten-btn" id="datenBtn"''',
    '''    <span class="sicher-offen" id="sicherOffen" hidden>Nicht gesichert</span>
    <button type="button" class="daten-btn sichern-btn" id="sichernBtn" hidden
            onclick="dateiSichern()" title="Änderungen in diese Datei schreiben"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><path d="M17 21v-8H7v8"/><path d="M7 3v5h8"/></svg>Sichern</button>
    <span class="sicher-stand" id="sicherStand" hidden
          title="Änderungen werden automatisch in dieser Datei gespeichert, solange sie geöffnet ist. Nach dem erneuten Öffnen ist bei der ersten Änderung einmalig »Sichern« zu wählen.">Automatisch gesichert</span>
    <div class="daten-wrap">
      <button class="daten-btn" id="datenBtn"''')
s = re.sub(r'(<span class="ex-t" id="kongUmstellenText">Kongresse umstellen</span>.*?</button>)',
           lambda m: m.group(1) + '''
        <button class="ex-item" role="menuitem" onclick="fachbereichAendern()">
          <span class="ex-t">Fachbereich umbenennen</span>
          <span class="ex-d">Der Name steht im Kopf, im Druck, in Excel und im Dateinamen der Ausgaben</span>
        </button>
        <button class="ex-item" id="fachWegBtn" role="menuitem" onclick="fachbereichEntfernen()" hidden>
          <span class="ex-t" id="fachWegText">Fachbereich entfernen</span>
          <span class="ex-d">Mit allen Jahrgängen und Sicherungspunkten aus dieser Datei</span>
        </button>''', s, count=1, flags=re.S)
if 'fachbereichAendern()">' not in s:
    sys.exit('Abbruch: Menüpunkt Fachbereich nicht eingesetzt')
# Kongresse sind hier nur Text an der Ausgabe: den Schritt der Web-Fassung, der
# daraus eigene Kongresssaetze macht, gibt es nicht. Ohne den Knopf laeuft der
# Verweis darauf ins Leere (if(ku)), die Funktion bleibt ungenutzt stehen.
rep_re(r'\n        <button class="ex-item" id="kongUmstellenBtn".*?</button>', '')
rep("&Ouml;ffnet die Arbeitsansicht: Ausgaben, Titel und Kongresse anlegen, &auml;ndern und entfernen",
    "&Ouml;ffnet die Arbeitsansicht: Ausgaben und Titel anlegen, &auml;ndern und entfernen", 2)
s, n = re.subn(r'(<span class="ex-t">Aus Excel laden</span>.*?</button>)',
               lambda m: m.group(1) + '''
        <button class="ex-item" role="menuitem" onclick="excelVorlage()">
          <span class="ex-t">Excel-Vorlage</span>
          <span class="ex-d">Leere Tabelle mit Erklärung der Spalten, zum ersten Befüllen</span>
        </button>
        <button class="ex-item" role="menuitem" onclick="altDatenKlick()">
          <span class="ex-t">Aus anderer HTML-Datei übernehmen</span>
          <span class="ex-d">Etwa beim Wechsel auf eine neuere Fassung oder zum Zusammenführen</span>
        </button>''', s, count=1, flags=re.S)
if n != 1:
    sys.exit('Abbruch: Menüpunkt Excel-Vorlage nicht eingesetzt')


rep('<input type="file" id="datenDatei" accept=".xlsx" style="display:none" onchange="datenDateiGewaehlt(event)">',
    '<input type="file" id="datenDatei" accept=".xlsx" style="display:none" onchange="datenDateiGewaehlt(event)">\n'
    '      <input type="file" id="altDatei" accept=".html,.htm" style="display:none" onchange="altDateiGewaehlt(event)">')
rep('#netzhinweis[hidden]{display:none}\n</style>',
    '''#netzhinweis[hidden]{display:none}
/* Print-Fassung: Arten im Inhaltsfilter, die der Jahrgang nicht fuehrt, und
   der Knopf "Sichern", solange nichts ungesichert ist, stehen nicht da. Der
   Knopf traegt dann den Abstand nach links, den sonst "Daten" traegt. */
.mode-btn[hidden],.sichern-btn[hidden]{display:none}
.sichern-btn{margin-left:auto}
.sichern-btn:not([hidden])~.daten-wrap{margin-left:0}
/* Ungesichertes: links der Stand in Orange mit Kreis-Ausrufezeichen, rechts
   der helle Knopf - gebaut
   wie "Automatisch gesichert", das an derselben Stelle steht. */
.sicher-offen{display:flex;align-items:center;gap:6px;margin-left:auto;font-size:.78rem;font-weight:600;color:var(--accent);white-space:nowrap}
.sicher-offen[hidden]{display:none}
.sicher-offen::before{content:"";width:13px;height:13px;flex:none;background:var(--accent);-webkit-mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23000' stroke-width='2.2' stroke-linecap='round'%3E%3Ccircle cx='12' cy='12' r='10'/%3E%3Cpath d='M12 7v6M12 16.5v.5'/%3E%3C/svg%3E") center/contain no-repeat;mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23000' stroke-width='2.2' stroke-linecap='round'%3E%3Ccircle cx='12' cy='12' r='10'/%3E%3Cpath d='M12 7v6M12 16.5v.5'/%3E%3C/svg%3E") center/contain no-repeat}
.sicher-offen:not([hidden])+.sichern-btn{margin-left:0}
/* Schreibt die Datei von selbst (Chrome/Edge), steht an Stelle des Knopfs ein
   ruhiger Hinweis ohne Rahmen; er ist kein Knopf und tut nichts. */
.sicher-stand{display:flex;align-items:center;gap:6px;margin-left:auto;font-size:.78rem;color:var(--muted);cursor:default;white-space:nowrap}
.sicher-stand[hidden]{display:none}
.sicher-stand::before{content:"✓";color:var(--navy);font-weight:700;font-family:system-ui,-apple-system,'Segoe UI',sans-serif}
.sicher-stand.laeuft::before{content:"…"}
.sicher-stand:not([hidden])~.daten-wrap{margin-left:0}
/* Fachbereich im Titel: wie der Jahrgang daneben ein Teil des Namens, der
   sich aufklappen laesst. Das Menue liegt links unter dem Namen und setzt die
   Schrift der Titelzeile fuer sich zurueck. */
.fach-wrap,.jahr-wrap{position:relative;display:inline-block}
.jahr-wrap:has(#jahrKopf:empty){display:none}
.fach-wahl{font:inherit;letter-spacing:inherit;color:inherit;background-color:transparent;border:none;border-radius:4px;padding:0 19px 0 4px;margin-left:-4px;cursor:pointer;transition:background-color .15s;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 12 12' fill='none' stroke='%23ee7d11' stroke-width='1.8'%3E%3Cpath d='M2.5 4.5 6 8l3.5-3.5'/%3E%3C/svg%3E");background-repeat:no-repeat;background-position:right 4px center;background-size:12px}
.fach-wahl:hover,.fach-wahl[aria-expanded="true"],.jahr-wahl[aria-expanded="true"]{background-color:rgba(255,255,255,.16)}
.fach-menu{left:0;right:auto;min-width:280px;font:400 14px/1.4 'Source Sans 3',Arial,Helvetica,sans-serif;letter-spacing:normal;text-wrap:wrap}
.fach-menu .ex-item.aktiv{background:var(--navy-faint);cursor:default}
.fach-menu .ex-item.aktiv .ex-t::after{content:" ✓";color:var(--accent);font-family:system-ui,-apple-system,'Segoe UI',sans-serif}
.leerstart{grid-column:1/-1;max-width:520px;margin:48px auto;text-align:center;color:var(--muted)}
.leerstart h3{color:var(--navy);font-size:1.05rem;margin-bottom:8px}
.leerstart button{margin-top:14px}
.leerstart .export-btn{display:inline-flex}
@media print{.sichern-btn,.sicher-stand,.sicher-offen{display:none!important}}
</style>''')

# ── Kontakt im Kopf ─────────────────────────────────────────────────────────
# Am Bildschirm rechts im dunklen Kopf ueber dem Stand, im PDF rechts unter dem
# Logo. Beide Stellen stehen fest im HTML, damit die HTML-Kopie den Kontakt
# als Text mitnimmt; gefuellt werden sie von kontaktZeigen().
rep('''  document.body.classList.toggle('bearbmodus', bearbOffen);
  standFeldModus();''', '''  document.body.classList.toggle('bearbmodus', bearbOffen);
  standFeldModus();
  kontaktZeigen();''')
rep('''      <span class="hero-stamp">Stand <span class="stand-feld" id="standFeld"></span></span>''',
    '''      <div class="hero-rechts">
        <div class="hero-kontakt" id="heroKontakt"></div>
        <span class="hero-stamp">Stand <span class="stand-feld" id="standFeld"></span></span>
      </div>''')
rep('''    <div class="eh-logo" id="exportlogo"></div>''',
    '''    <div class="eh-rechts">
      <div class="eh-logo" id="exportlogo"></div>
      <div class="eh-kontakt" id="ehKontakt"></div>
    </div>''')
rep('''.leerstart{grid-column:1/-1;''', '''/* Kontakt rechts im Kopf, ueber dem Stand. Der Stand gibt seinen Abstand nach
   links an den gemeinsamen Behaelter ab. */
.hero-rechts{margin-left:auto;align-self:center;flex:none;display:flex;flex-direction:column;align-items:flex-end;gap:6px;text-align:right}
.hero-rechts .hero-stamp{margin-left:0;align-self:auto}
.hero-kontakt{font-size:.75rem;line-height:1.5;color:rgba(255,255,255,.75)}
.hero-kontakt:empty{display:none}
.hero-kontakt b{color:#fff;font-weight:600}
.hero-kontakt a{color:#B3DCF5;text-decoration:none}
.hero-kontakt a:hover{text-decoration:underline}
/* Arbeitsansicht: gepunktete Linie wie am beschreibbaren Stand */
.hk-knopf{font:inherit;color:inherit;text-align:right;background:none;border:none;border-bottom:1px dotted rgba(255,255,255,.35);border-radius:0;padding:0;cursor:pointer}
.hk-knopf:hover{border-bottom-color:var(--accent)}
.hk-knopf.leer{color:rgba(255,255,255,.6)}
@media(max-width:640px){.hero-kontakt{display:none}}
.eh-kontakt{display:none}
@media print{
  .eh-rechts{flex:none;display:flex;flex-direction:column;align-items:flex-end}
  .eh-kontakt{display:block;margin-top:6px;font-size:7.5pt;line-height:1.45;color:var(--muted);text-align:right;white-space:nowrap}
  .eh-kontakt:empty{display:none}
  .eh-kontakt b{color:var(--navy);font-weight:600}
}
.leerstart{grid-column:1/-1;''')

# ── Datenblock der Datei ────────────────────────────────────────────────────
rep('''let DATEN = {};
let OHNE_DATENBANK = false;
</script>
''', '''let DATEN = {};
let OHNE_DATENBANK = false;
</script>

<script id="tabellen">
// Die Heftplanung dieser Datei, in derselben Form wie die Tabellen der
// Datenbank-Fassung. "Sichern" schreibt diesen Block im Ganzen neu.
// Je Fachbereich ein Satz Tabellen; AKTIV ist der zuletzt gezeigte.
let BEREICHE = [];
let AKTIV = 0;
</script>
''')

# Die HTML-Kopie traegt nur den gezeigten Jahrgang (#daten) - die Tabellen
# mit allen Jahrgaengen und Sicherungspunkten bleiben in der Arbeitsdatei.
rep('''  // Der Stand wandert als Text mit, ist in der Kopie aber nicht mehr aenderbar.''',
    '''  // Die Kopie zeigt den Kontakt immer in der Leseform, auch aus der Arbeitsansicht.
  const hk = klon.querySelector('#heroKontakt');
  if(hk) hk.innerHTML = kontaktHtml(kontaktJetzt(), true);
  const tb = klon.querySelector('#tabellen');
  if(tb) tb.textContent = '\\nlet BEREICHE = ' + sicheresJson([{name:FACHBEREICH, kontakt:kontaktJetzt(), tabellen:null}]) + ';\\nlet AKTIV = 0;\\n';
  // Die Kopie zeigt einen Fachbereich: der Name steht dort als fester Text.
  const fw = klon.querySelector('.fach-wrap');
  if(fw){
    const fest = document.createElement('span');
    fest.className = 'accent'; fest.id = 'fachKopf';
    fest.textContent = fachKopf();
    fw.replaceWith(fest);
  }

  // Der Stand wandert als Text mit, ist in der Kopie aber nicht mehr aenderbar.''')
rep("['.export-wrap','.daten-wrap','.daten-dialog','.hero-konto','.bm-etikett','#anmeldung','#netzhinweis']",
    "['.export-wrap','.daten-wrap','.daten-dialog','.hero-konto','.bm-etikett','#anmeldung','#netzhinweis','#sichernBtn','#sicherStand','#sicherOffen']")

# ── Daten lesen: Rubriken je Titel, Inhalte je Ausgabe ─────────────────────
rep("""      color: 'var(--j' + t.id + ')', hex: t.hex, issues: []""",
    """      color: 'var(--j' + t.id + ')', hex: t.hex, issues: [],
      rubriken: (t.rubriken || []).map(r=>({id:r.id, name:r.name}))""")
rep("""      t: [a.sonderthema, a.thema].map(w=>(w||'').trim()).filter(Boolean)
    });""", """      t: [a.sonderthema, a.thema].map(w=>(w||'').trim()).filter(Boolean),
      r: Object.assign({}, a.inhalte || {})   // Rubrik-Kennung -> Text
    });""")

# Ganze Jahrgaenge schreiben (Excel, Sicherungspunkt, Vorjahr): Rubriken mit.
rep("hex:t.hex||'#00285a'})))});", "hex:t.hex||'#00285a', rubriken:t.rubriken||[]})))});", 2)
rep("auslagen:iss.a||[], berichte:iss.b||[]})));", "auslagen:iss.a||[], berichte:iss.b||[], inhalte:iss.r||{}})));")
rep("    id:j.id, kurz:j.short, voll:j.full, auflage:j.auflage, hex:j.hex,\n",
    "    id:j.id, kurz:j.short, voll:j.full, auflage:j.auflage, hex:j.hex, rubriken:j.rubriken||[],\n")
rep("      a:iss.a.map(kongressText), b:iss.b.map(kongressText) }))",
    "      a:iss.a.map(kongressText), b:iss.b.map(kongressText), r:iss.r||{} }))")
rep("      id:t.id, short:t.kurz, full:t.voll, auflage:t.auflage, hex:t.hex,\n",
    "      id:t.id, short:t.kurz, full:t.voll, auflage:t.auflage, hex:t.hex, rubriken:t.rubriken||[],\n")
rep("    if(t) return {id:t.id,short:t.short,full:t.full,color:t.color,hex:t.hex};",
    "    if(t) return {id:t.id,short:t.short,full:t.full,color:t.color,hex:t.hex,\n"
    "                  rubriken:(t.rubriken||[]).map(r=>({id:r.id,name:r.name}))};")
rep("""      const t=stamm || {id:naechsteTitelId()+unbekannt.size-1,short:kurz,full:kurz,
                        color:'var(--muted)',hex:'#4a6080'};""",
    """      const neueId=naechsteTitelId()+unbekannt.size-1;
      const t=stamm || {id:neueId,short:kurz,full:kurz,
                        color:'var(--muted)',hex:farbeFuer(neueId),rubriken:[]};""")
# Excel-Eingang: Spalte "Weitere Rubriken", eine Zeile je Rubrik "Name: Text".
rep("""    T.issues.push(iss);
  }""", """    T.issues.push(iss);
    if(spalte['Weitere Rubriken']!==undefined){
      iss.r={};
      ausListenZelle(g('Weitere Rubriken')).forEach(z=>{
        const m=/^([^:]+):\\s*(.*)$/.exec(z);
        if(!m || !m[2].trim()) return;
        const name=m[1].trim();
        if(!T.rubriken) T.rubriken=[];
        let r=T.rubriken.find(x=>x.name===name);
        if(!r){ r={id:neueRubrikId(), name}; T.rubriken.push(r); }
        iss.r[r.id]=m[2].trim();
      });
    }
  }""")

# ── Anzeige ─────────────────────────────────────────────────────────────────
rep("function zeigeThema(){ return modus.size===0 || modus.has('thema'); }",
    """function zeigeThema(){ return modus.size===0 || modus.has('thema'); }
function zeigeRubrik(){ return modus.size===0 || modus.has('rubrik'); }

// ── Weitere Rubriken (Print-Fassung) ──
// Ein Titel fuehrt eine eigene Liste von Rubriken {id, name}, etwa
// "CME-Beitrag"; die Ausgabe haelt je Kennung ihren Text (iss.r). Angezeigt
// wird, was einen Text hat, unter dem Namen der Rubrik.
function titelVon(iss){ return JOURNALS.find(j=>j.issues.includes(iss)); }
function rubrikEintraege(iss){
  const j = titelVon(iss);
  if(!j) return [];
  const r = iss.r || {};
  return (j.rubriken||[]).map(x=>({name:x.name, text:String(r[x.id]||'').trim()}))
                         .filter(e=>e.text);
}
function neueRubrikId(){
  return 'r' + Date.now().toString(36) + Math.random().toString(36).slice(2,6);
}
function rubrikInhalte(r){
  const aus = {};
  Object.entries(r||{}).forEach(([k,w])=>{ const t=String(w||'').trim(); if(t) aus[k]=t; });
  return aus;
}
function rubrikBloecke(iss,q){
  return rubrikEintraege(iss).map(e=>`<div class="thema"><div class="tlbl">${esc(e.name)}</div>`
    + `<div class="ttxt">${hl(e.text,q)}</div></div>`).join('');
}

// Weitere Rubriken stehen im Inhaltsfilter nur, wenn der Jahrgang welche
// fuehrt: ein Schalter, der immer ins Leere fuehrt, saehe aus wie ein Fehler.
// Eine Art, die wegfaellt, faellt auch aus der Auswahl.
function hatRubriken(){ return JOURNALS.some(j=>j.issues.some(iss=>rubrikEintraege(iss).length)); }
function sichtbareArten(){
  return [...document.querySelectorAll('.mode-btn')]
    .filter(b=>b.dataset.mode!=='all' && !b.hidden).map(b=>b.dataset.mode);
}
function inhaltsArtenPruefen(){
  const da = {rubrik:hatRubriken()};
  document.querySelectorAll('.mode-btn').forEach(b=>{
    const k=b.dataset.mode;
    if(!(k in da)) return;
    b.hidden = !da[k];
    if(!da[k]) modus.delete(k);
  });
  if(modus.size && modus.size===sichtbareArten().length) modus.clear();
  document.querySelectorAll('.mode-btn').forEach(b=>{
    const k=b.dataset.mode;
    b.classList.toggle('active', k==='all' ? modus.size===0 : modus.has(k));
  });
}""")
rep("  if(zeigeThema()) f.push(...iss.t);\n",
    "  if(zeigeThema()) f.push(...iss.t);\n  if(zeigeRubrik()) f.push(...rubrikEintraege(iss).map(e=>e.text));\n")
rep("             || (modus.has('thema')   && iss.t.length>0);",
    "             || (modus.has('thema')   && iss.t.length>0)\n"
    "             || (modus.has('rubrik')  && rubrikEintraege(iss).length>0);")
rep("  return a+b+(zeigeThema() ? themaBlock(iss,q) : '');",
    "  return a+b+(zeigeThema() ? themaBlock(iss,q) : '')+(zeigeRubrik() ? rubrikBloecke(iss,q) : '');")
rep("  {k:'t',      t:'Themenschwerpunkte'},\n",
    "  {k:'t',      t:'Themenschwerpunkte'},\n  {k:'r',      t:'Weitere Rubriken'},\n")
rep("    if(s.k==='t')    return zeigeThema();\n",
    "    if(s.k==='t')    return zeigeThema();\n    if(s.k==='r')    return zeigeRubrik() && hatRubriken();\n")
rep("    case 't':       return`<td class=\"t-thema\">${themaZelle(iss,q)}</td>`;\n",
    "    case 't':       return`<td class=\"t-thema\">${themaZelle(iss,q)}</td>`;\n"
    "    case 'r': {\n"
    "      // Rubrikname links, Text rechts an einer gemeinsamen Kante je Zelle:\n"
    "      // die Namen sind verschieden lang, ein fester Einzug passte nur zu einem.\n"
    "      const re = rubrikEintraege(iss);\n"
    "      return`<td class=\"t-kong\">${re.length ? `<div class=\"kr\">${re.map(e=>\n"
    "        `<b>${esc(e.name)}</b><span>${hl(e.text,q)}</span>`).join('')}</div>` : '–'}</td>`;\n"
    "    }\n")
rep("  if(k==='t')      return it.iss.t.join(' ');\n",
    "  if(k==='t')      return it.iss.t.join(' ');\n"
    "  if(k==='r')      return rubrikEintraege(it.iss).map(e=>e.text).join(' ');\n")
rep("  if(zeigeT){ kopf1.push('Themenschwerpunkte'); breiten1.push(46); }\n",
    "  if(zeigeT){ kopf1.push('Themenschwerpunkte'); breiten1.push(46); }\n"
    "  const zeigeR = zeigeRubrik() && hatRubriken();\n"
    "  if(zeigeR){ kopf1.push('Weitere Rubriken'); breiten1.push(46); }\n")
rep("    if(zeigeT) z.push({w:themaText(iss),s:3});\n",
    "    if(zeigeT) z.push({w:themaText(iss),s:3});\n"
    "    if(zeigeR) z.push({w:rubrikEintraege(iss).map(e=>e.name+': '+e.text).join('\\n'),s:3});\n")
rep("""  bearbAnzeige();
  const q = document.getElementById('q').value.trim();""",
    """  bearbAnzeige();
  // Eine leere Datei zeigt bei jedem Zeichnen die Startseite, auch nach
  // einem Klick auf die Schalter oben - sonst verschwaende sie ohne Rueckweg.
  if(DATEN && !Object.keys(DATEN).length) return leerAnsicht();
  inhaltsArtenPruefen();
  const q = document.getElementById('q').value.trim();""")

# ── Bearbeiten: Rubriken am Titel, Felder an der Ausgabe ───────────────────
rep("      a: kongAusIssue(iss.a), b: kongAusIssue(iss.b) }, still);",
    "      a: kongAusIssue(iss.a), b: kongAusIssue(iss.b), r: Object.assign({}, iss.r||{}) }, still);")
rep("    { id:null, heft:'', et:'', as:'', du:'', eh:'', t:[], a:[], b:[] });",
    "    { id:null, heft:'', et:'', as:'', du:'', eh:'', t:[], a:[], b:[], r:{} });")
rep("      auflage:String(t.auflage||0), hex:t.hex||'#00285a' }, still);",
    "      auflage:String(t.auflage||0), hex:t.hex||'#00285a',\n"
    "      rubriken:(t.rubriken||[]).map(r=>({id:r.id, name:r.name})) }, still);")
rep("    { id:naechsteTitelId(), short:'', full:'', auflage:'0', hex:'#00285a' });",
    "    { id:naechsteTitelId(), short:'', full:'', auflage:'0', hex:farbeFuer(naechsteTitelId()), rubriken:[] });")
rep("""    berichte: kongAlsText(entwurf.b)
  };""", """    berichte: kongAlsText(entwurf.b),
    inhalte: rubrikInhalte(entwurf.r)
  };""")
rep("  iss.t = entwurf.t.map(w=>w.trim()).filter(Boolean);\n",
    "  iss.t = entwurf.t.map(w=>w.trim()).filter(Boolean);\n  iss.r = rubrikInhalte(entwurf.r);\n")
rep("    ${themenGruppe()}\n", "    ${themenGruppe()}\n\n    ${rubrikGruppe()}\n")
rep("""    ${bearbFussHtml(neu ? 'Anlegen' : 'Speichern', neu ? '' :
      `<button type="button" class="bearb-loeschen" onclick="titelEntfernen()">""",
    """    ${titelRubrikenGruppe()}

    ${bearbFussHtml(neu ? 'Anlegen' : 'Speichern', neu ? '' :
      `<button type="button" class="bearb-loeschen" onclick="titelEntfernen()">""")
rep("function zeilenGruppe(art, beschriftung, hinweis){",
    """// Je Rubrik des Titels ein Feld. Ein Titel ohne Rubriken zeigt hier nichts.
function rubrikGruppe(){
  const t = JOURNALS.find(j=>j.id===bearbAuswahl.titelId);
  const liste = (t && t.rubriken) || [];
  if(!liste.length) return '';
  return `<div class="bearb-gruppe">
    <span class="bearb-feld">Weitere Rubriken
      <span class="hinweis">Festgelegt am Titel; ein leeres Feld erscheint nirgends</span></span>
    ${liste.map(r=>`<label class="bearb-feld">${esc(r.name)}
       <input type="text" value="${escA((entwurf.r||{})[r.id]||'')}"
              oninput="bearbRubrikText('${r.id}',this.value)"></label>`).join('')}
  </div>`;
}
function bearbRubrikText(id, wert){
  if(!entwurf) return;
  if(!entwurf.r) entwurf.r = {};
  if(wert) entwurf.r[id] = wert; else delete entwurf.r[id];
  bearbStand('Nicht gespeichert', '');
}

function titelRubrikenGruppe(){
  const zeilen = entwurf.rubriken.map((r,i)=>
    `<div class="bearb-zeile">
       <input type="text" data-art="rubriken" value="${escA(r.name)}"
              placeholder="Name der Rubrik, etwa CME-Beitrag"
              oninput="bearbRubrikName(${i},this.value)">
       <button type="button" class="bearb-weg" title="Rubrik entfernen"
               onclick="bearbRubrikWeg(${i})"><svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12"/></svg></button>
     </div>`).join('');
  return `<div class="bearb-gruppe">
    <span class="bearb-feld">Weitere Rubriken
      <span class="hinweis">Inhalte je Ausgabe neben den Themenschwerpunkten,
        etwa CME-Beiträge. Jede Rubrik erhält im Formular der Ausgaben ein
        eigenes Feld und erscheint unter ihrem Namen in den Ansichten, im Druck
        und in Excel</span></span>
    ${zeilen || '<p class="bearb-leerhinweis">Keine Rubriken.</p>'}
    <button type="button" class="bearb-zu" onclick="bearbRubrikZu()">Rubrik hinzufügen</button>
  </div>`;
}
function bearbRubrikName(i, wert){
  if(!entwurf || !entwurf.rubriken[i]) return;
  entwurf.rubriken[i].name = wert;
  bearbStand('Nicht gespeichert', '');
}
function bearbRubrikZu(){
  if(!entwurf) return;
  entwurf.rubriken.push({id:neueRubrikId(), name:''});
  bearbFormNeu();
  const felder = document.querySelectorAll('.bearb-zeile input[data-art="rubriken"]');
  const letztes = felder[felder.length-1];
  if(letztes) letztes.focus();
}
function bearbRubrikWeg(i){
  if(!entwurf) return;
  entwurf.rubriken.splice(i,1);
  bearbFormNeu();
}

function zeilenGruppe(art, beschriftung, hinweis){""")

# Titel speichern: Rubriken mit; eine entfernte Rubrik nimmt ihre Eintraege mit.
rep("""async function titelSpeichern(){
  const warNeu = !!bearbAuswahl.neu;
  bearbArbeitet(warNeu ? 'Wird angelegt …' : 'Wird gespeichert …');
  try{
    const j = jahrgang();
    const feld = { kurz: entwurf.short.trim(), voll: entwurf.full.trim(),
                   auflage: Number(entwurf.auflage)||0, hex: entwurf.hex };""",
    """async function titelSpeichern(){
  const warNeu = !!bearbAuswahl.neu;
  const rubriken = entwurf.rubriken.map(r=>({id:r.id, name:r.name.trim()})).filter(r=>r.name);
  const vorher = warNeu ? null : JOURNALS.find(x=>x.id===entwurf.id);
  const bleibt = new Set(rubriken.map(r=>r.id));
  const weg = vorher ? (vorher.rubriken||[]).filter(r=>!bleibt.has(r.id)) : [];
  const betroffen = vorher ? vorher.issues.filter(iss=>
    weg.some(r=>String((iss.r||{})[r.id]||'').trim())) : [];
  if(betroffen.length && !await frage('Rubrik entfernen?',
    '<p>' + weg.map(r=>'»'+esc(r.name)+'«').join(', ') + ' hat Einträge in <b>' +
    betroffen.length + '</b> Ausgabe' + (betroffen.length===1?'':'n') +
    '. Sie werden mit entfernt.</p>', 'Entfernen')) return;
  bearbArbeitet(warNeu ? 'Wird angelegt …' : 'Wird gespeichert …');
  try{
    const j = jahrgang();
    const feld = { kurz: entwurf.short.trim(), voll: entwurf.short.trim(),
                   auflage: Number(entwurf.auflage)||0, hex: entwurf.hex, rubriken };""")
rep("""        auflage:feld.auflage, color:'var(--j'+entwurf.id+')', hex:feld.hex,
        issues:[] });""", """        auflage:feld.auflage, color:'var(--j'+entwurf.id+')', hex:feld.hex,
        rubriken:feld.rubriken, issues:[] });""")
rep("      t.short=feld.kurz; t.full=feld.voll; t.auflage=feld.auflage; t.hex=feld.hex;\n",
    """      t.short=feld.kurz; t.full=feld.voll; t.auflage=feld.auflage; t.hex=feld.hex;
      t.rubriken=feld.rubriken;
      for(const iss of betroffen){
        const r = Object.assign({}, iss.r||{});
        weg.forEach(x=>delete r[x.id]);
        await dbAnfrage('/rest/v1/ausgabe?id=eq.' + encodeURIComponent(iss.id),
          { method:'PATCH', headers:{ Prefer:'return=minimal' },
            body: JSON.stringify({ inhalte: r }) });
        iss.r = r;
      }
""")
rep("    entwurf.short=feld.kurz; entwurf.full=feld.voll;\n",
    "    entwurf.short=feld.kurz; entwurf.full=feld.voll;\n"
    "    entwurf.rubriken=feld.rubriken.map(r=>({id:r.id, name:r.name}));\n")

# Ein Namensfeld am Titel (seit Print 3): Kurzname und vollstaendiger Name
# zusammengelegt. Der vollstaendige Name wurde nirgends gezeigt; gespeichert
# wird er weiter, mit demselben Wortlaut wie der Name.
rep("""    <label class="bearb-feld">Kurzname
      <input type="text" value="${escA(entwurf.short)}"
             oninput="bearbFeld('short',this.value)">
      <span class="hinweis">So steht der Titel überall: in allen Ansichten, im
        Bearbeiten-Menü, im Druck und in den Ausgaben</span></label>
    <label class="bearb-feld">Vollständiger Name
      <input type="text" value="${escA(entwurf.full)}"
             oninput="bearbFeld('full',this.value)">
      <span class="hinweis">Wird zurzeit nirgends angezeigt und nur
        gespeichert</span></label>
""", """    <label class="bearb-feld">Name
      <input type="text" value="${escA(entwurf.short)}"
             oninput="bearbFeld('short',this.value)">
      <span class="hinweis">So steht der Titel überall: in allen Ansichten, im
        Bearbeiten-Menü, im Druck und in den Ausgaben</span></label>
""")
rep("    return !!entwurf.short.trim() && !!entwurf.full.trim();",
    "    return !!entwurf.short.trim();")

# ── Datenschicht: die Tabellen der Datei statt der Datenbank ───────────────
rep('async function dbAnfrage(pfad, einstellungen = {}, mitSitzung = true){',
    'async function dbAnfrageNetz(pfad, einstellungen = {}, mitSitzung = true){')
rep("""// ─── Datenschicht ───────────────────────────────────────────────────────────""",
    r"""// ─── Datenschicht der Print-Fassung ─────────────────────────────────────────
// Statt einer Datenbank stehen die Tabellen im Block <script id="tabellen">
// dieser Datei. dbAnfrage() versteht dieselben Pfade, die das Werkzeug an die
// Datenbank richtete (/rest/v1/<tabelle>?spalte=eq.wert&order=…&limit=…),
// samt Vorgabewerten, Schluesseln, Bezuegen und dem Loeschen abhaengiger
// Zeilen. Der uebrige Code bleibt dadurch wortgleich mit der Web-Fassung.
const TAB_REGELN = {
  jahrgang:         { schluessel:['jahr'], vorgabe:()=>({stand:''}) },
  titel:            { schluessel:['jahr','id'],
                      vorgabe:()=>({auflage:0, hex:'#00285a', rubriken:[]}),
                      braucht:[['jahrgang',{jahr:'jahr'}]] },
  ausgabe:          { schluessel:['id'], kennung:true,
                      vorgabe:()=>({erscheinung:null, anzeigenschluss:null,
                        druckunterlagen:null, anlieferung:null, thema:'',
                        sonderthema:'', auslagen:[], berichte:[], inhalte:{}}),
                      braucht:[['titel',{jahr:'jahr', id:'titel_id'}]] },
  kongress:         { schluessel:['id'], kennung:true,
                      vorgabe:()=>({kurz:'', von:null, bis:null, unscharf:'',
                        ort:'', erwartet:[], dach:true}),
                      braucht:[['jahrgang',{jahr:'jahr'}]] },
  kongress_ausgabe: { schluessel:['kongress_id','ausgabe_id','art'], vorgabe:()=>({}),
                      braucht:[['kongress',{id:'kongress_id'}],['ausgabe',{id:'ausgabe_id'}]] },
  sicherung:        { schluessel:['id'], kennung:true,
                      vorgabe:()=>({bezeichnung:'', erstellt_am:new Date().toISOString()}) }
};
// Was beim Loeschen mitgeht: [abhaengige Tabelle, {Spalte dort: Spalte hier}]
const TAB_KASKADE = {
  jahrgang: [['titel',{jahr:'jahr'}], ['kongress',{jahr:'jahr'}]],
  titel:    [['ausgabe',{jahr:'jahr', titel_id:'id'}]],
  ausgabe:  [['kongress_ausgabe',{ausgabe_id:'id'}]],
  kongress: [['kongress_ausgabe',{kongress_id:'id'}]]
};
function tabKopie(x){ return x==null ? x : JSON.parse(JSON.stringify(x)); }
function neueKennung(){
  if(window.crypto && crypto.randomUUID) return crypto.randomUUID();
  return 'xxxxxxxx-xxxx-4xxx-8xxx-xxxxxxxxxxxx'
    .replace(/x/g, ()=>(Math.random()*16|0).toString(16));
}
function tabFilter(params){
  const f = [];
  for(const [k,v] of params){
    if(k==='select' || k==='order' || k==='limit') continue;
    if(!v.startsWith('eq.')) throw new Error('Nicht unterstützte Abfrage: ' + k + '=' + v);
    f.push([k, v.slice(3)]);
  }
  return z => f.every(([k,w]) => String(z[k]) === w);
}
function tabOrdnen(zeilen, order){
  if(!order) return zeilen;
  const teile = order.split(',').map(t=>{ const [sp,r] = t.split('.'); return [sp, r==='desc'?-1:1]; });
  return zeilen.sort((a,b)=>{
    for(const [sp,r] of teile){
      const x=a[sp], y=b[sp];
      if(x===y) continue;
      if(x==null) return 1;
      if(y==null) return -1;
      return (x<y ? -1 : 1) * r;
    }
    return 0;
  });
}
function tabLoeschen(name, treffer){
  const tab = TABELLEN[name];
  treffer.forEach(z=>{ const i = tab.indexOf(z); if(i>=0) tab.splice(i,1); });
  (TAB_KASKADE[name]||[]).forEach(([kind, bez])=>{
    const mit = (TABELLEN[kind]||[]).filter(k=>treffer.some(p=>
      Object.entries(bez).every(([kc,pc])=>String(k[kc])===String(p[pc]))));
    if(mit.length) tabLoeschen(kind, mit);
  });
}
async function dbAnfrage(pfad, einstellungen = {}){
  const m = /^\/rest\/v1\/([a-z_]+)(?:\?(.*))?$/.exec(pfad);
  if(!m || !TAB_REGELN[m[1]]) throw new Error('Diese Fassung arbeitet ohne Datenbank.');
  // Eine leere Datei, die ohne den Begruessungsdialog gleich aus Excel
  // befuellt wird, bekommt hier ihren ersten (noch namenlosen) Fachbereich.
  if(!TABELLEN && !OHNE_DATENBANK && !BEREICHE.length){
    BEREICHE.push({name:'', tabellen:leereTabellen()});
    bereichSetzen(0);
  }
  if(!TABELLEN) throw new Error('Diese Kopie enthält nur die Anzeige.');
  const name = m[1], regel = TAB_REGELN[name];
  const tab = TABELLEN[name] || (TABELLEN[name] = []);
  const params = new URLSearchParams(m[2] || '');
  const methode = (einstellungen.method || 'GET').toUpperCase();
  const passt = tabFilter(params);
  const zurueck = /return=representation/.test(
    (einstellungen.headers && einstellungen.headers.Prefer) || '');

  if(methode==='GET'){
    let z = tabOrdnen(tab.filter(passt).map(tabKopie), params.get('order'));
    const grenze = parseInt(params.get('limit'), 10);
    if(grenze > 0) z = z.slice(0, grenze);
    return z;
  }
  const koerper = einstellungen.body ? JSON.parse(einstellungen.body) : null;
  if(methode==='POST'){
    const neu = (Array.isArray(koerper) ? koerper : [koerper]).map(z=>{
      const zeile = Object.assign(regel.vorgabe(), tabKopie(z));
      if(regel.kennung && !zeile.id) zeile.id = neueKennung();
      return zeile;
    });
    // Erst alles pruefen, dann schreiben: eine Anfrage gilt ganz oder gar nicht.
    const schl = z => regel.schluessel.map(k=>String(z[k])).join('|');
    const da = new Set(tab.map(schl));
    neu.forEach(z=>{
      const k = schl(z);
      if(da.has(k)) throw new Error('Diesen Eintrag gibt es bereits (' + name + ' ' + k + ').');
      da.add(k);
      (regel.braucht||[]).forEach(([el, bez])=>{
        if(!(TABELLEN[el]||[]).some(p=>Object.entries(bez).every(([pc,kc])=>String(p[pc])===String(z[kc]))))
          throw new Error('Der Bezug fehlt (' + name + ' → ' + el + ').');
      });
    });
    tab.push(...neu);
    dateiGeaendert();
    return zurueck ? neu.map(tabKopie) : null;
  }
  if(methode==='PATCH'){
    const treffer = tab.filter(passt);
    treffer.forEach(z=>Object.assign(z, tabKopie(koerper)));
    if(treffer.length) dateiGeaendert();
    return zurueck ? treffer.map(tabKopie) : null;
  }
  if(methode==='DELETE'){
    const treffer = tab.filter(passt);
    if(treffer.length){ tabLoeschen(name, treffer); dateiGeaendert(); }
    return null;
  }
  throw new Error('Nicht unterstützte Anfrage: ' + methode);
}

// ── Sichern ──
// In Chrome und Edge wird beim ersten Sichern die Datei gewaehlt; danach
// schreibt jede Aenderung von selbst in dieselbe Datei. Andere Browser kennen
// diesen Weg nicht - dort entsteht bei jedem Sichern eine neue Datei im
// Download-Ordner. Ungesichertes meldet der Knopf "Sichern" und das Verlassen
// der Seite; schreibt die Datei von selbst, steht dort "Automatisch gesichert".
let dateiHandle = null, ungesichert = false, aenderungen = 0,
    schreibZeit = null, schreibFehler = false, downloadErklaert = false;

function dateiGeaendert(){
  ungesichert = true;
  aenderungen++;
  if(dateiHandle && !schreibFehler){
    clearTimeout(schreibZeit);
    schreibZeit = setTimeout(()=>dateiSchreiben().catch(()=>{}), 400);
  }
  sichernAnzeigen();
}
function sichernAnzeigen(){
  const b = document.getElementById('sichernBtn');
  if(!b) return;
  const selbst = !!dateiHandle && !schreibFehler;
  b.hidden = !ungesichert || selbst;
  const o = document.getElementById('sicherOffen');
  if(o) o.hidden = b.hidden;
  const h = document.getElementById('sicherStand');
  if(!h) return;
  h.hidden = !selbst;
  h.textContent = ungesichert ? 'Wird gesichert …' : 'Automatisch gesichert';
  h.classList.toggle('laeuft', ungesichert);
}
function dateiName(){
  try{
    const n = decodeURIComponent(location.pathname.split('/').pop() || '');
    if(/\.html?$/i.test(n)) return n;
  }catch(e){}
  return 'Jahresvorschau_Print.html';
}
// Ein Abzug des Dokuments wie bei der HTML-Kopie, aber mit allen Bedienteilen
// und den Tabellen aller Jahrgaenge.
function dateiInhalt(){
  const klon = neutralerKlon();
  const tb = klon.querySelector('#tabellen');
  tb.textContent = '\n// Die Heftplanung dieser Datei, je Fachbereich ein Satz Tabellen. '
    + '"Sichern" schreibt diesen Block im Ganzen neu.\n'
    + 'let BEREICHE = ' + sicheresJson(BEREICHE) + ';\n'
    + 'let AKTIV = ' + AKTIV + ';\n';
  const fm = klon.querySelector('#fachMenu');
  if(fm) fm.innerHTML = '';
  ['#fachWahl','#jahrWahl'].forEach(k=>{
    const w = klon.querySelector(k);
    if(w) w.setAttribute('aria-expanded','false');
  });
  const jm = klon.querySelector('#jahrMenu');
  if(jm) jm.innerHTML = '';
  const sb = klon.querySelector('#sichernBtn');
  if(sb) sb.setAttribute('hidden','');
  ['#sicherStand','#sicherOffen'].forEach(k=>{
    const e = klon.querySelector(k);
    if(e) e.setAttribute('hidden','');
  });
  klon.querySelectorAll('.daten-dialog').forEach(d=>{ if(d.id!=='ladeDialog') d.remove(); });
  const ld = klon.querySelector('#ladeDialog');
  if(ld) ld.classList.remove('offen');
  // Was nur die gerade offene Ansicht betrifft, beginnt beim Oeffnen neu.
  const ps = klon.querySelector('#pagestyle');
  if(ps) ps.textContent = '';
  const rs = klon.querySelector('#results');
  if(rs) rs.className = 'grid';
  return '<!DOCTYPE html>\n' + klon.outerHTML;
}
async function dateiSchreiben(){
  const stand = aenderungen;
  const html = dateiInhalt();
  try{
    if(dateiHandle){
      const w = await dateiHandle.createWritable();
      await w.write(new Blob([html], {type:'text/html'}));
      await w.close();
    }else{
      const url = URL.createObjectURL(new Blob([html], {type:'text/html;charset=utf-8'}));
      const a = document.createElement('a');
      a.href = url; a.download = dateiName();
      document.body.appendChild(a); a.click(); a.remove();
      setTimeout(()=>URL.revokeObjectURL(url), 4000);
      if(!downloadErklaert){
        downloadErklaert = true;
        dialogZeigen('Gesichert als neue Datei',
          '<p>Dieser Browser kann nicht in die geöffnete Datei zurückschreiben. '
          + 'Der Stand liegt deshalb als neue Datei »' + esc(dateiName()) + '« im '
          + 'Download-Ordner.</p><p>Weitergearbeitet wird mit dieser neuen Datei; '
          + 'die bisherige kann durch sie ersetzt werden. In Chrome und Edge entfällt '
          + 'dieser Umweg.</p>');
      }
    }
    schreibFehler = false;
    if(stand === aenderungen) ungesichert = false;
  }catch(fehler){
    schreibFehler = true;
    throw fehler;
  }finally{
    sichernAnzeigen();
  }
}
// Beim ersten Mal, dass die Datei von selbst weiterschreibt, sagt ein Fenster
// einmal, was das heisst. Gemerkt wird das im Browser; ohne ihn kommt es eben
// noch einmal.
const AUTOSICHERN_ERKLAERT = 'jahresvorschau.autosichern-erklaert';
function autoSichernErklaeren(){
  try{ if(localStorage.getItem(AUTOSICHERN_ERKLAERT)) return; }catch(e){}
  dialogZeigen('Automatisches Sichern aktiviert',
    '<p>Weitere Änderungen werden ab sofort automatisch in dieser Datei gespeichert. '
    + 'Ein erneutes Sichern ist nicht erforderlich; der aktuelle Status wird oben als '
    + '»Automatisch gesichert« angezeigt.</p>'
    + '<p>Dies gilt, solange die Datei geöffnet ist. Nach dem erneuten Öffnen ist bei der '
    + 'ersten Änderung einmalig »Sichern« zu wählen; anschließend erfolgt das Speichern '
    + 'wieder automatisch.</p>');
  try{ localStorage.setItem(AUTOSICHERN_ERKLAERT, '1'); }catch(e){}
}
async function dateiSichern(){
  if(OHNE_DATENBANK) return;
  try{
    const neuGewaehlt = !dateiHandle && !!window.showSaveFilePicker;
    if((!dateiHandle || schreibFehler) && window.showSaveFilePicker){
      dateiHandle = await window.showSaveFilePicker({
        suggestedName: dateiName(),
        types: [{description:'Jahresvorschau', accept:{'text/html':['.html']}}]
      });
      schreibFehler = false;
    }
    await dateiSchreiben();
    if(neuGewaehlt) autoSichernErklaeren();
  }catch(fehler){
    if(fehler && fehler.name==='AbortError') return;      // Auswahl abgebrochen
    dialogZeigen('Sichern nicht möglich', '<p>' + esc(fehlertext(fehler)) + '</p>');
  }
}
window.addEventListener('beforeunload', e=>{
  if(ungesichert && !OHNE_DATENBANK){ e.preventDefault(); e.returnValue = ''; }
});
document.addEventListener('keydown', e=>{
  if(OHNE_DATENBANK) return;
  if((e.metaKey || e.ctrlKey) && !e.altKey && e.key.toLowerCase()==='s'){
    e.preventDefault();
    dateiSichern();
  }
});

// ── Kennfarben ──
// Neue Titel bekommen der Reihe nach eine eigene Farbe; geaendert wird sie im
// Titelformular. Vorn die vier Farben des Brand Hubs, dahinter Ergaenzungen.
const TITELFARBEN = ['#00285a','#0176c3','#ee7d11','#25855a','#8a5a9e','#afca00','#c0600a','#4a6080'];
function farbeFuer(id){ return TITELFARBEN[(Math.max(1, id|0) - 1) % TITELFARBEN.length]; }

// ── Excel-Vorlage ──
// Eine leere Tabelle in genau der Form, die "Aus Excel laden" erwartet: Blatt
// "Ausgaben" mit Vorspann (darin "Vollstaendiger Jahrgang", sonst gilt die
// Datei als Auszug) und den Spaltenkoepfen der Excel-Ausgabe. Vorbelegt ist je
// vorhandenem Titel eine Zeile mit Jahrgang, Titel und Auflage - ohne Heft
// wird sie beim Laden uebergangen und stoert also nicht. Davor ein Blatt
// "Hinweise", das jede Spalte erklaert.
const VORLAGE_KOPF = ['Jahrgang','Titel','Heft','Erscheinungstermin (ET)','Anzeigenschluss (AS)',
  'Druckunterlagen (DU)','Ein-/Durchhefter und Beilagen (EH)','Auflage','Themenschwerpunkte',
  'Weitere Rubriken','Kongresse'];
function vorlageJahr(){
  if(jahr && DATEN[jahr]) return jahr;
  const d = new Date();
  return String(d.getFullYear() + (d.getMonth() >= 6 ? 1 : 0));
}
function vorlageHinweise(y){
  const F=(w,s)=>({w,s});
  return [
    F(`Vorlage für die Jahresvorschau ${fachKopf()} ${y}`,4),
    F('So wird die Vorlage befüllt und eingelesen',5),
    F('',0),
    F('Ablauf',6),
    F('1. Im Blatt »Ausgaben« eine Zeile je Ausgabe eintragen.',0),
    F('2. Die Datei speichern, als Excel-Arbeitsmappe (.xlsx).',0),
    F('3. In der Jahresvorschau »Daten → Aus Excel-Vorlage laden« wählen und diese Datei angeben.',0),
    F('Vor dem Übernehmen zeigt das Werkzeug, was es gefunden hat. Das Laden ersetzt den Jahrgang',0),
    F('im Ganzen; steht dort schon etwas, entsteht vorher ein Sicherungspunkt.',0),
    F('',0),
    F('Die drei Zeilen über den Spaltenköpfen und die Spaltenköpfe selbst bleiben unverändert –',5),
    F('an ihnen erkennt das Werkzeug die Vorlage. Die Reihenfolge der Spalten ist dagegen frei.',5),
    F('',0),
    F('Die Spalten',6),
    F('Jahrgang – vierstellig, etwa ' + y + '. Pflicht.',0),
    F('Titel – der Name des Titels, in jeder Zeile gleich geschrieben. Neue Titel entstehen beim Laden;',0),
    F('   die Kennfarbe wird danach in der Jahresvorschau unter »Bearbeiten« gesetzt.',0),
    F('Heft – eine Nummer, auch ein Doppelheft wie »1–2«, oder eine Bezeichnung wie »Sonderheft«. Pflicht.',0),
    F('   Zeilen ohne Titel oder ohne Heft werden übergangen.',0),
    F('Erscheinungstermin (ET) – Pflicht, als Datum, etwa 12.02.' + y + '.',0),
    F('Anzeigenschluss, Druckunterlagen, Ein-/Durchhefter und Beilagen – Datum wie oben.',0),
    F('Auflage – eine Zahl; einmal je Titel genügt.',0),
    F('Themenschwerpunkte – höchstens zwei, jeder in einer eigenen Zeile innerhalb der Zelle.',0),
    F('Weitere Rubriken – je Eintrag eine Zeile »Rubrik: Text«, etwa »CME-Beitrag: Kardiale Amyloidose',0),
    F('   erkennen«. Die Rubrik entsteht beim Laden am jeweiligen Titel. Die Spalte darf leer bleiben.',0),
    F('Kongresse – je Kongress eine Zeile innerhalb der Zelle.',0),
    F('',0),
    F('Mehrere Einträge in einer Zelle',6),
    F('Zeilenumbruch innerhalb einer Zelle: Alt+Eingabe unter Windows, Ctrl+Option+Eingabe auf dem Mac.',0),
    F('',0),
    F('Termine, Themen, Rubriken und Kongresse lassen sich nach dem Laden jederzeit auch einzeln',5),
    F('in der Jahresvorschau unter »Daten → Bearbeiten« ändern.',5)
  ];
}
// zusatz: weitere Zeilen, nur fuer Pruefungen
function vorlageXlsx(zusatz){
  const y = vorlageJahr();
  const titel = (DATEN[y] && DATEN[y].titel) || [];
  const zeilen = titel.length
    ? titel.map(t=>[{w:y},{w:t.short},{w:''},{w:''},{w:''},{w:''},{w:''},{w:t.auflage||'',t:'n'}])
    : [[{w:y}]];
  (zusatz||[]).forEach(z=>zeilen.push(z));
  const vorspann = [
    [`Jahresvorschau ${fachKopf()} ${y} – Vorlage zum Befüllen`,4],
    ['Vollständiger Jahrgang · eine Zeile je Ausgabe · Erklärung im Blatt »Hinweise«',0],
    ['Die Zeilen bis einschließlich der Spaltenköpfe bleiben unverändert',5]
  ];
  // Die vier Terminspalten tragen das Datumsformat schon vorab: ein
  // eingetipptes Datum steht dann als 12.02.2027 da, nicht als Zahl.
  let blatt = blattXml([9,34,8,13,13,13,16,9,40,40,52], vorspann, VORLAGE_KOPF, zeilen);
  [4,5,6,7].forEach(i=>{
    blatt = blatt.replace(`<col min="${i}" max="${i}" width="`, `<col min="${i}" max="${i}" style="2" width="`);
  });
  const NS='http://schemas.openxmlformats.org/officeDocument/2006/relationships';
  const teile=[
    {name:'[Content_Types].xml', text:
      `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>`+
      `<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">`+
      `<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>`+
      `<Default Extension="xml" ContentType="application/xml"/>`+
      `<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>`+
      `<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>`+
      `<Override PartName="/xl/worksheets/sheet2.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>`+
      `<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>`+
      `</Types>`},
    {name:'_rels/.rels', text:
      `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>`+
      `<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">`+
      `<Relationship Id="rId1" Type="${NS}/officeDocument" Target="xl/workbook.xml"/>`+
      `</Relationships>`},
    // "Hinweise" steht vorn, damit der Weg beim Oeffnen zuerst dasteht;
    // eingelesen wird das Blatt "Ausgaben" ueber seinen Namen.
    {name:'xl/workbook.xml', text:
      `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>`+
      `<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="${NS}">`+
      `<sheets><sheet name="Hinweise" sheetId="1" r:id="rId1"/>`+
      `<sheet name="Ausgaben" sheetId="2" r:id="rId2"/></sheets></workbook>`},
    {name:'xl/_rels/workbook.xml.rels', text:
      `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>`+
      `<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">`+
      `<Relationship Id="rId1" Type="${NS}/worksheet" Target="worksheets/sheet1.xml"/>`+
      `<Relationship Id="rId2" Type="${NS}/worksheet" Target="worksheets/sheet2.xml"/>`+
      `<Relationship Id="rId9" Type="${NS}/styles" Target="styles.xml"/>`+
      `</Relationships>`},
    {name:'xl/styles.xml', text:XLSX_STYLES},
    {name:'xl/worksheets/sheet1.xml', text:hinweisBlattXml(vorlageHinweise(y))},
    {name:'xl/worksheets/sheet2.xml', text:blatt}
  ];
  const enc=new TextEncoder();
  return zipBauen(teile.map(t=>({name:t.name,bytes:enc.encode(t.text)})));
}
function excelVorlage(){
  schliesseDaten();
  const bytes = vorlageXlsx();
  const url = URL.createObjectURL(new Blob([bytes],
    {type:'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'}));
  const a = document.createElement('a');
  a.href = url; a.download = `Jahresvorschau_${dateiFach()}Print_${vorlageJahr()}_Vorlage.xlsx`;
  document.body.appendChild(a); a.click(); a.remove();
  setTimeout(()=>URL.revokeObjectURL(url), 4000);
}

// ── Fachbereiche ──
// Eine Datei kann mehrere Fachbereiche fuehren, jeder mit eigenem Satz
// Tabellen (Jahrgaenge, Titel, Ausgaben, Kongresse, Sicherungspunkte).
// TABELLEN und FACHBEREICH zeigen auf den gerade gewaehlten - dbAnfrage() und
// alles darueber wissen von den anderen nichts. PDF, Excel und HTML-Kopie
// gelten darum immer dem gezeigten Fachbereich.
let TABELLEN = null, FACHBEREICH = '';
function leereTabellen(){
  const t = {};
  Object.keys(TAB_REGELN).forEach(n=>{ t[n] = []; });
  return t;
}
function bereichSetzen(i){
  AKTIV = BEREICHE.length ? Math.min(Math.max(0, i|0), BEREICHE.length - 1) : 0;
  const b = BEREICHE[AKTIV];
  TABELLEN = b ? b.tabellen : null;
  FACHBEREICH = b ? b.name : '';
}
// Im Menue stehen die Fachbereiche nach dem Alphabet; der gewaehlte bleibt.
function bereicheOrdnen(){
  const b = BEREICHE[AKTIV];
  BEREICHE.sort((x,y)=>x.name.localeCompare(y.name, 'de'));
  if(b) bereichSetzen(BEREICHE.indexOf(b));
}
function nameGleich(a, b){
  return String(a).trim().toLocaleLowerCase('de') === String(b).trim().toLocaleLowerCase('de');
}
// ausser: der Fachbereich, der umbenannt wird; null beim Anlegen.
function bereichNamePruefen(name, ausser){
  const andere = BEREICHE.filter(b=>b!==ausser);
  if(!andere.length) return '';
  if(!name) return 'Bei mehreren Fachbereichen braucht jeder einen Namen.';
  if(!ausser && andere.some(b=>!b.name))
    return 'Der bisherige Fachbereich hat noch keinen Namen. Er wird zuerst unter '
      + '»Daten → Fachbereich umbenennen« benannt.';
  if(andere.some(b=>nameGleich(b.name, name)))
    return 'Einen Fachbereich »' + name + '« gibt es in dieser Datei schon.';
  return '';
}
function mehrzahl(n, ein, mehr){ return n + ' ' + (n===1 ? ein : mehr); }
function bereichUmfang(t){
  const jahre = t.jahrgang.map(j=>j.jahr).sort();
  const titel = new Set(t.titel.map(x=>x.kurz)).size;
  return mehrzahl(titel, 'Titel', 'Titel') + ' · '
    + (jahre.length===1 ? 'Jahrgang ' : 'Jahrgänge ') + jahre.join(', ');
}

// Klappmenue am Namen im Kopf
function fachMenuBauen(){
  const m = document.getElementById('fachMenu');
  if(!m) return;
  m.innerHTML = '<div class="exf-kopf">Fachbereich</div>'
    + BEREICHE.map((b,i)=>`<button type="button" class="ex-item${i===AKTIV?' aktiv':''}" role="menuitemradio"
        aria-checked="${i===AKTIV}" onclick="bereichWechseln(${i})">
        <span class="ex-t">${esc(b.name || 'ohne Namen')}</span>
        <span class="ex-d">${esc(bereichUmfang(b.tabellen))}</span></button>`).join('')
    + `<button type="button" class="ex-item" role="menuitem" onclick="fachbereichNeu()">
        <span class="ex-t">Fachbereich hinzufügen</span>
        <span class="ex-d">Mit eigenen Titeln, Jahrgängen und Kongressen. PDF, Excel und
          HTML-Kopie enthalten immer nur den gezeigten Fachbereich</span></button>`;
}
function toggleFach(ev){
  if(ev) ev.stopPropagation();
  const m = document.getElementById('fachMenu'), b = document.getElementById('fachWahl');
  if(!m) return;
  const auf = m.classList.contains('open');
  schliesseExport(); schliesseDaten(); schliesseJahr();
  if(!auf) fachMenuBauen();
  m.classList.toggle('open', !auf);
  b.setAttribute('aria-expanded', String(!auf));
}
function schliesseFach(){
  const m = document.getElementById('fachMenu'), b = document.getElementById('fachWahl');
  if(!m) return;
  m.classList.remove('open');
  b.setAttribute('aria-expanded', 'false');
}
document.addEventListener('click', e=>{
  if(!e.target.closest('.fach-wrap')) schliesseFach();
  if(!e.target.closest('.jahr-wrap')) schliesseJahr();
});
document.addEventListener('keydown', e=>{ if(e.key==='Escape'){ schliesseFach(); schliesseJahr(); } });

// Jahrgang im Kopf: wie der Fachbereich ein Klappmenue. Gewechselt und
// angelegt wird hier; umbenannt und entfernt wird ueber das Menue "Daten".
function jahrMenuBauen(){
  const m = document.getElementById('jahrMenu');
  if(!m) return;
  m.innerHTML = '<div class="exf-kopf">Jahrgang</div>'
    + jahrgaenge().map(y=>{
      const t = DATEN[y].titel;
      const hefte = t.reduce((n,j)=>n+j.issues.length, 0);
      return `<button type="button" class="ex-item${y===jahr?' aktiv':''}" role="menuitemradio"
        aria-checked="${y===jahr}" onclick="jahrWechseln('${escA(y)}')">
        <span class="ex-t">${esc(y)}</span>
        <span class="ex-d">${mehrzahl(t.length,'Titel','Titel')} · ${mehrzahl(hefte,'Ausgabe','Ausgaben')}</span></button>`;
    }).join('')
    + `<button type="button" class="ex-item" role="menuitem" onclick="schliesseJahr(); jahrgangAnlegen()">
        <span class="ex-t">Jahrgang anlegen</span>
        <span class="ex-d">Legt ein weiteres Jahr an, auf Wunsch mit den Titeln des
          gezeigten Jahrgangs. Die Hefte kommen einzeln dazu</span></button>`;
}
function toggleJahr(ev){
  if(ev) ev.stopPropagation();
  const m = document.getElementById('jahrMenu'), b = document.getElementById('jahrWahl');
  if(!m) return;
  const auf = m.classList.contains('open');
  schliesseExport(); schliesseDaten(); schliesseFach();
  if(!auf) jahrMenuBauen();
  m.classList.toggle('open', !auf);
  b.setAttribute('aria-expanded', String(!auf));
}
function schliesseJahr(){
  const m = document.getElementById('jahrMenu'), b = document.getElementById('jahrWahl');
  if(!m) return;
  m.classList.remove('open');
  b.setAttribute('aria-expanded', 'false');
}
function jahrWechseln(y){
  schliesseJahr();
  if(y!==jahr) waehleJahrgang(y);
}

// Der Wechsel selbst ist keine Aenderung der Heftplanung. Kann die Datei von
// selbst geschrieben werden, merkt sie sich den gezeigten Fachbereich gleich;
// sonst mit dem naechsten Sichern.
function stillMitschreiben(){
  if(!dateiHandle || schreibFehler) return;
  clearTimeout(schreibZeit);
  schreibZeit = setTimeout(()=>dateiSchreiben().catch(()=>{}), 400);
}
async function bereichZeigen(){
  entwurf = null; entwurfRein = null; bearbAuswahl = null;
  activeJ.clear(); modus.clear();
  DATEN = TABELLEN ? await datenHolen() : {};
  kopfFachbereich();
  if(!Object.keys(DATEN).length){ bearbOffen = false; return leerStart(); }
  starteAnsicht();
  if(bearbOffen) sicherungenHolen();
  render();
}
async function bereichWechseln(i){
  schliesseFach();
  if(i===AKTIV) return;
  if(!await bearbFrei()) return;
  bereichSetzen(i);
  await bereichZeigen();
  stillMitschreiben();
}
async function fachbereichNeu(){
  schliesseFach();
  if(!await bearbFrei()) return;
  ersterStart(BEREICHE.length > 0);
}
async function fachbereichEntfernen(){
  schliesseDaten();
  if(BEREICHE.length < 2) return;
  if(!await bearbFrei()) return;
  const b = BEREICHE[AKTIV], t = b.tabellen;
  const ok = await frage('Fachbereich entfernen?',
    `<p>Der Fachbereich »${esc(b.name || 'ohne Namen')}« wird aus dieser Datei entfernt: `
    + `${esc(bereichUmfang(t))}, ${mehrzahl(t.ausgabe.length,'Ausgabe','Ausgaben')} und `
    + `${mehrzahl(t.sicherung.length,'Sicherungspunkt','Sicherungspunkte')}.</p>`
    + `<p>Ein Sicherungspunkt entsteht dabei nicht. Die übrigen Fachbereiche bleiben unverändert.</p>`,
    'Entfernen');
  if(!ok) return;
  BEREICHE.splice(AKTIV, 1);
  bereichSetzen(0);
  bearbOffen = false;
  await bereichZeigen();
  dateiGeaendert();
}

// ── Aus aelterer Datei uebernehmen ──
// Eine neue Fassung dieser Datei kommt leer. Ihr Inhalt wird hier aus der
// bisherigen Datei geholt: der Block <script id="tabellen"> wird gelesen,
// nicht ausgefuehrt - die fremde Datei bleibt Text. Jeder Fachbereich dort
// ersetzt den gleichnamigen hier oder kommt neu dazu; so lassen sich auch
// mehrere Dateien zu einer zusammenfuehren. Felder, die eine aeltere Fassung
// noch nicht kannte, bekommen ihre Vorgabewerte (TAB_REGELN) - an dieser
// Stelle setzt jede kuenftige Umstellung des Datenaufbaus an. Gelesen wird
// auch die erste Fassung mit nur einem Fachbereich (TABELLEN/FACHBEREICH).
let altErgebnis = null;
async function altDatenKlick(){
  schliesseDaten();
  if(!await bearbFrei()) return;
  document.getElementById('altDatei').click();
}
// Inhaltsvergleich unabhaengig von der Reihenfolge der Felder
function kanon(x){
  if(Array.isArray(x)) return '[' + x.map(kanon).join(',') + ']';
  if(x && typeof x==='object')
    return '{' + Object.keys(x).sort().map(k=>JSON.stringify(k) + ':' + kanon(x[k])).join(',') + '}';
  return JSON.stringify(x);
}
function altDatenLesen(text){
  const doc = new DOMParser().parseFromString(text, 'text/html');
  const sk = doc.getElementById('tabellen');
  if(!sk) throw new Error('Diese Datei ist keine Jahresvorschau Print.\n\nErwartet wird eine '
    + 'Datei, die mit dieser Jahresvorschau gesichert wurde.');
  const mNeu = /let BEREICHE = ([\s\S]*?);\nlet AKTIV = /.exec(sk.textContent);
  const mAlt = /let TABELLEN = ([\s\S]*?);\nlet FACHBEREICH = ([\s\S]*?);\n/.exec(sk.textContent);
  let roh;
  if(mNeu) roh = JSON.parse(mNeu[1]);
  else if(mAlt) roh = [{name: JSON.parse(mAlt[2]), tabellen: JSON.parse(mAlt[1])}];
  if(!Array.isArray(roh)) throw new Error('Die Daten in dieser Datei sind nicht lesbar.');
  if(roh.some(b=>!b || !b.tabellen)) throw new Error('Diese Datei ist eine HTML-Kopie zum Ansehen.\n\n'
    + 'Sie enthält nur einen Jahrgang und keine bearbeitbaren Daten. Übernommen werden '
    + 'kann nur aus der Arbeitsdatei, mit der gearbeitet und gesichert wurde.');
  const bereiche = roh.map(b=>{
    const tabellen = {};
    Object.keys(TAB_REGELN).forEach(name=>{
      tabellen[name] = (Array.isArray(b.tabellen[name]) ? b.tabellen[name] : [])
        .map(z=>Object.assign(TAB_REGELN[name].vorgabe(), z));
    });
    return {name: String(b.name || '').trim(), kontakt: kontaktLesen(b.kontakt),
      tabellen: kongresseAlsText(tabellen)};
  }).filter(b=>b.tabellen.jahrgang.length);
  const fassung = doc.querySelector('meta[name="jahresvorschau-fassung"]');
  return { bereiche, fassung: fassung ? fassung.getAttribute('content') : '' };
}
async function altDateiGewaehlt(ev){
  const datei = ev.target.files[0];
  ev.target.value = '';
  if(!datei) return;
  try{
    const erg = altDatenLesen(await datei.text());
    if(!erg.bereiche.length) throw new Error('Die gewählte Datei enthält noch keinen Jahrgang.');
    const plan = erg.bereiche.map(q=>({q, ziel: BEREICHE.find(b=>nameGleich(b.name, q.name)) || null}));
    if(plan.every(p=>p.ziel && kanon(p.ziel.tabellen)===kanon(p.q.tabellen)) && plan.every(p=>p.ziel.name===p.q.name)
       && plan.every(p=>!kontaktDa(p.q.kontakt) || kanon(kontaktLesen(p.ziel.kontakt))===kanon(p.q.kontakt)))
      throw new Error('Die gewählte Datei enthält genau den Stand, der hier schon steht.');
    // Ein Fachbereich ohne einen einzigen Titel ist ein angefangener leerer
    // Start - er weicht dem Uebernommenen, statt leer daneben stehen zu bleiben.
    const leere = BEREICHE.filter(b=>!b.tabellen.titel.length && !plan.some(p=>p.ziel===b));
    const bleiben = BEREICHE.filter(b=>!leere.includes(b) && !plan.some(p=>p.ziel===b));
    plan.forEach(p=>{ p.gleich = !!p.ziel && kanon(p.ziel.tabellen)===kanon(p.q.tabellen); });
    const teile = plan.map(({q, ziel, gleich})=>{
      const t = q.tabellen;
      const zeilen = t.jahrgang.map(j=>j.jahr).sort().map(y=>{
        const n = tab => t[tab].filter(x=>x.jahr===y).length;
        return `<tr><td>${esc(y)}</td><td>${mehrzahl(n('titel'),'Titel','Titel')} · `
          + `${mehrzahl(n('ausgabe'),'Ausgabe','Ausgaben')} · `
          + `${mehrzahl(n('sicherung'),'Sicherungspunkt','Sicherungspunkte')}</td></tr>`;
      }).join('');
      const art = gleich ? 'steht hier schon genau so' : ziel ? 'ersetzt den vorhandenen' : 'kommt neu dazu';
      return `<div class="pr-jahr"><b>${esc(q.name || 'ohne Namen')}</b> – ${art}</div>`
        + `<table class="pr-tab"><tbody>${zeilen}</tbody></table>`;
    });
    const ersetzt = plan.filter(p=>p.ziel && !p.gleich && p.ziel.tabellen.ausgabe.length).map(p=>p.ziel);
    const warn = ersetzt.length
      ? `<div class="pr-warn"><div class="pr-warn-kopf">Vorhandener Inhalt wird ersetzt</div>`
        + ersetzt.map(b=>`»${esc(b.name || 'ohne Namen')}« mit ${mehrzahl(b.tabellen.ausgabe.length,'Ausgabe','Ausgaben')}`).join(', ')
        + '.' + (plan.some(({q, ziel, gleich})=>ziel && !gleich && ziel.tabellen.jahrgang.some(j=>q.tabellen.jahrgang.some(n=>n.jahr===j.jahr)))
          ? ` Der bisherige Stand bleibt als Sicherungspunkt »Vor dem Übernehmen« erhalten.` : '')
        + plan.filter(p=>p.ziel && !p.gleich).map(({q, ziel})=>{
            const da = new Set(q.tabellen.jahrgang.map(j=>j.jahr));
            const weg = ziel.tabellen.jahrgang.map(j=>j.jahr).filter(y=>!da.has(y)).sort();
            return weg.length ? ` Die gewählte Datei enthält für »${esc(ziel.name || 'ohne Namen')}« `
              + `${weg.length > 1 ? 'die Jahrgänge' : 'den Jahrgang'} ${weg.map(esc).join(', ')} nicht; `
              + `${weg.length > 1 ? 'sie entfallen' : 'er entfällt'}.` : '';
          }).join('') + `</div>` : '';
    const rest = (bleiben.length ? `<div class="pr-hinw">Unverändert bleiben: `
        + bleiben.map(b=>esc(b.name || 'ohne Namen')).join(', ') + '.</div>' : '')
      + (leere.length ? `<div class="pr-hinw">Entfällt, weil noch ohne Titel: `
        + leere.map(b=>b.name ? '»' + esc(b.name) + '«' : 'der angefangene Fachbereich ohne Namen').join(', ') + '.</div>' : '');
    const herkunft = erg.fassung ? `<div class="pr-hinw">Herkunft: ${esc(erg.fassung)}</div>` : '';
    altErgebnis = {plan, leere};
    dialogZeigen('Geprüft: ' + datei.name, warn + teile.join('') + rest + herkunft,
      ersetzt.length ? 'Trotzdem übernehmen' : 'Übernehmen', altUebernehmen, !!ersetzt.length);
  }catch(e){
    altErgebnis = null;
    dialogZeigen('Die Datei wurde nicht übernommen',
      '<div class="pr-fehler">' + esc(String(e.message||e)).replace(/\n/g,'<br>') + '</div>');
  }
}
async function altUebernehmen(){
  if(!altErgebnis) return dialogSchliessen();
  const {plan, leere} = altErgebnis;
  ladeKnoepfe(true);
  try{
    // Was ersetzt wird, bleibt im neuen Bestand als Sicherungspunkt
    // "Vor dem Übernehmen" erreichbar - je Jahrgang, den es dort weiter gibt.
    // Punkte von hier, die der neue Bestand nicht kennt, kommen mit.
    const vorher = [];
    for(const p of plan){
      if(!p.ziel || p.gleich) continue;
      const jahre = new Set(p.q.tabellen.jahrgang.map(j=>j.jahr));
      bereichSetzen(BEREICHE.indexOf(p.ziel));
      const daten = await datenHolen();
      vorher.push({ p,
        bloecke: Object.keys(daten).filter(y=>jahre.has(y) && daten[y].titel.length)
          .map(y=>[y, jahrgangAlsBlock(y, daten[y])]),
        alte: p.ziel.tabellen.sicherung.filter(s=>jahre.has(s.jahr)
          && !p.q.tabellen.sicherung.some(n=>n.id===s.id)) });
    }
    plan.forEach(({q, ziel})=>{
      if(ziel){
        ziel.tabellen = q.tabellen; ziel.name = q.name;
        // Ein Kontakt, den die andere Datei nicht fuehrt, bleibt stehen.
        if(kontaktDa(q.kontakt)) ziel.kontakt = q.kontakt;
      }
      else BEREICHE.push(q);
    });
    for(const {p, bloecke, alte} of vorher){
      p.q.tabellen.sicherung.push(...alte);
      bereichSetzen(BEREICHE.indexOf(p.ziel));
      for(const [y, block] of bloecke)
        await dbAnfrage('/rest/v1/sicherung', {
          method:'POST', headers:{ Prefer:'return=minimal' },
          body: JSON.stringify({ jahr: y, bezeichnung: 'Vor dem Übernehmen', inhalt: block })
        });
    }
    BEREICHE = BEREICHE.filter(b=>!leere.includes(b));
    // Gezeigt wird danach der erste uebernommene Fachbereich.
    bereichSetzen(BEREICHE.indexOf(plan[0].ziel || plan[0].q));
    bereicheOrdnen();
    bearbOffen = false;
    altErgebnis = null;
    dialogSchliessen();
    await bereichZeigen();
    dateiGeaendert();
    // Uebernommen ist erst, was in der Datei steht. Der Knopf ist ein Klick
    // des Benutzers - nur so darf der Browser nach dem Speicherort fragen.
    if(!dateiHandle)
      dialogZeigen('Übernommen', '<p>Der Inhalt wurde in diese Datei übernommen, ist jedoch '
        + 'noch nicht gesichert. Mit »Sichern« wird er dauerhaft gespeichert.</p><p>Anschließend '
        + 'wird ausschließlich mit dieser Datei weitergearbeitet; die ältere Datei wird nicht mehr '
        + 'benötigt.</p>', 'Sichern',
        ()=>{ dialogSchliessen(); dateiSichern(); });
  }catch(fehler){ ladeStand(fehlertext(fehler), true); ladeKnoepfe(false); }
}

// ── Name des Fachbereichs ──
function fachKopf(){ return FACHBEREICH ? FACHBEREICH + '/Print' : 'Print'; }
function dateiFach(){
  return FACHBEREICH ? FACHBEREICH.trim().replace(/[\\/:*?"<>|\s]+/g,'-') + '-' : '';
}
function kopfFachbereich(){
  const e = document.getElementById('fachKopf');
  if(e) e.textContent = fachKopf();
  document.title = 'Jahresvorschau ' + fachKopf() + ' · Springer Medizin';
  const wb = document.getElementById('fachWegBtn');
  if(wb) wb.hidden = BEREICHE.length < 2;
  const wt = document.getElementById('fachWegText');
  if(wt) wt.textContent = FACHBEREICH ? `Fachbereich »${FACHBEREICH}« entfernen` : 'Fachbereich entfernen';
  kontaktZeigen();
}
async function fachbereichAendern(){
  schliesseDaten();
  const b = BEREICHE[AKTIV];
  if(!b) return ersterStart();
  const neu = await eingabe('Fachbereich umbenennen',
    'Der Name steht im Kopf, im Druck, in Excel und im Dateinamen der Ausgaben.'
    + (BEREICHE.length < 2 ? ' Bleibt das Feld leer, heißt es nur »Jahresvorschau Print«.' : ''),
    'Fachbereich', FACHBEREICH, 'Übernehmen');
  if(neu===null) return;
  const name = neu.trim();
  const fehler = bereichNamePruefen(name, b);
  if(fehler) return dialogZeigen('Nicht umbenannt', '<p>' + esc(fehler) + '</p>');
  if(name === b.name) return;
  b.name = name;
  bereicheOrdnen();
  kopfFachbereich();
  dateiGeaendert();
  render();
}

// ── Kontakt des Fachbereichs ──
// Ein Kontakt gilt fuer den ganzen Fachbereich und liegt darum am Eintrag in
// BEREICHE, nicht in den Tabellen eines Jahrgangs. Er steht nicht neben den
// Inhalten, sondern im Kopf: am Bildschirm oben rechts ueber dem Stand, im PDF
// rechts unter dem Logo. Sind alle Felder leer, steht nichts da.
const KONTAKT_FELDER = ['name', 'funktion', 'tel', 'mail'];
function kontaktLesen(k){
  const r = {};
  KONTAKT_FELDER.forEach(f=>{ r[f] = String((k && k[f]) || '').trim(); });
  return r;
}
function kontaktDa(k){ return !!k && KONTAKT_FELDER.some(f=>String(k[f] || '').trim()); }
function kontaktJetzt(){ return kontaktLesen(BEREICHE[AKTIV] && BEREICHE[AKTIV].kontakt); }
function kontaktHtml(k, link){
  if(!kontaktDa(k)) return '';
  const z1 = [k.name ? '<b>' + esc(k.name) + '</b>' : '', esc(k.funktion)].filter(Boolean).join(', ');
  const mail = k.mail ? (link ? `<a href="mailto:${escA(k.mail)}">${esc(k.mail)}</a>` : esc(k.mail)) : '';
  const z2 = [k.tel ? 'Tel. ' + esc(k.tel) : '', mail].filter(Boolean).join(' · ');
  return 'Kontakt: ' + [z1, z2].filter(Boolean).join('<br>');
}
// In der Arbeitsansicht ist der Kontakt im Kopf ein Knopf, der das Fenster
// zum Eintragen oeffnet - gepflegt wird er dort, wo er zu sehen ist; einen
// eigenen Punkt im Menue »Daten« hat er nicht (Marcus, 11.10.2026). Fehlt er, steht dort nur in der Arbeitsansicht der Hinweis
// »Kontakt eintragen«. Lesen, HTML-Kopie und PDF bleiben davon unberuehrt.
function kontaktZeigen(){
  const k = kontaktJetzt();
  const h = document.getElementById('heroKontakt');
  if(h) h.innerHTML = (typeof bearbOffen!=='undefined' && bearbOffen && BEREICHE[AKTIV])
    ? `<button type="button" class="hk-knopf${kontaktDa(k) ? '' : ' leer'}" onclick="kontaktAendern()"
        title="Kontakt für den ganzen Fachbereich ändern">${kontaktHtml(k, false) || 'Kontakt eintragen'}</button>`
    : kontaktHtml(k, true);
  const e = document.getElementById('ehKontakt');
  if(e) e.innerHTML = kontaktHtml(k, false);
}
function kontaktAendern(){
  schliesseDaten();
  const b = BEREICHE[AKTIV];
  if(!b) return ersterStart();
  const k = kontaktLesen(b.kontakt);
  const feld = (id, text, wert, art, hinweis) => `<label class="dlg-feld">${text}
       <input type="${art}" id="${id}" value="${escA(wert)}" placeholder="${escA(hinweis)}"></label>`;
  dialogZeigen(FACHBEREICH ? `Kontakt für ${FACHBEREICH}` : 'Kontakt',
    feld('ktName', 'Name', k.name, 'text', 'Vorname Nachname')
    + feld('ktFunktion', 'Funktion', k.funktion, 'text', 'etwa Sales Manager')
    + feld('ktTel', 'Telefon', k.tel, 'tel', 'etwa +49 6221 487-0000')
    + feld('ktMail', 'E-Mail', k.mail, 'email', 'vorname.nachname@springer.com')
    + `<div class="pr-hinw">Der Kontakt gilt für alle Titel und Jahrgänge dieses Fachbereichs. `
    + `Er steht oben rechts im Kopf, in der HTML-Kopie und im PDF unter dem Logo. `
    + `Leere Felder werden weggelassen; sind alle leer, erscheint kein Kontakt.</div>`,
    'Übernehmen', kontaktUebernehmen);
  const f = document.getElementById('ktName');
  if(f) f.focus();
}
function kontaktUebernehmen(){
  const b = BEREICHE[AKTIV];
  if(!b) return dialogSchliessen();
  const wert = id => (document.getElementById(id).value || '').trim();
  const neu = kontaktLesen({name: wert('ktName'), funktion: wert('ktFunktion'),
    tel: wert('ktTel'), mail: wert('ktMail')});
  dialogSchliessen();
  if(kanon(neu)===kanon(kontaktLesen(b.kontakt))) return;
  if(kontaktDa(neu)) b.kontakt = neu; else delete b.kontakt;
  kontaktZeigen();
  dateiGeaendert();
}

// ── Start ──
async function starteDatei(){
  bereichSetzen(AKTIV);
  DATEN = TABELLEN ? await datenHolen() : {};
  kopfFachbereich();
  if(!Object.keys(DATEN).length) return leerAnsicht();
  starteAnsicht();
}
// Eine leere Datei begruesst mit der Startseite; der Dialog fuer Fachbereich
// und ersten Jahrgang oeffnet sich beim Oeffnen der Datei nicht von selbst,
// sondern ueber »Beginnen« (leerStart nur nach einem Wechsel ins Leere).
function leerStart(){
  leerAnsicht();
  ersterStart();
}
function leerAnsicht(){
  const jk = document.getElementById('jahrKopf');
  if(jk) jk.textContent = '';
  const res = document.getElementById('results');
  if(res) res.innerHTML = `<div class="leerstart"><h3>Noch keine Heftplanung</h3>
    <p>Angelegt werden zuerst der Fachbereich und ein Jahrgang, danach die Titel
      und ihre Ausgaben.</p>
    <button type="button" class="export-btn" onclick="ersterStart()">Beginnen</button>
    <p><button type="button" class="bearb-zu" onclick="altDatenKlick()">Aus anderer HTML-Datei übernehmen</button></p></div>`;
}
// neu: ein weiterer Fachbereich neben den vorhandenen
function ersterStart(neu){
  const jetzt = new Date();
  const vorschlag = String(jetzt.getFullYear() + (jetzt.getMonth() >= 6 ? 1 : 0));
  dialogZeigen(neu ? 'Fachbereich hinzufügen' : 'Neue Jahresvorschau',
    `<label class="dlg-feld">Fachbereich
       <input type="text" id="ersFach" value="${neu ? '' : escA(FACHBEREICH)}"></label>
     <label class="dlg-feld">Jahrgang
       <input type="text" id="ersJahr" inputmode="numeric" maxlength="4" value="${escA(vorschlag)}"></label>
     <div class="pr-stand">${neu
       ? 'Liegt der Fachbereich schon in einer anderen Datei dieser Jahresvorschau vor, wird er von dort übernommen:'
       : 'Liegt schon eine ältere Datei dieser Jahresvorschau vor, etwa bei einer neuen Fassung, wird ihr Inhalt übernommen statt neu angelegt:'}
       <button type="button" class="bearb-zu" onclick="dialogSchliessen(); altDatenKlick()">Aus anderer HTML-Datei übernehmen</button></div>
     <div class="pr-hinw">${neu
       ? 'Der neue Fachbereich bekommt eigene Titel, Jahrgänge und Kongresse; gewechselt wird über seinen Namen im Kopf.'
       : 'Der Fachbereich steht im Kopf, im Druck und im Dateinamen der Ausgaben und lässt sich später im Menü »Daten« umbenennen. Weitere Fachbereiche kommen über seinen Namen im Kopf dazu.'}
       Danach werden die Titel und ihre Ausgaben angelegt – einzeln unter »Daten → Bearbeiten«
       oder auf einen Schlag über »Daten → Excel-Vorlage« und »Aus Excel-Vorlage laden«.</div>`,
    'Anlegen', ()=>ersterStartAusfuehren(!!neu));
  const f = document.getElementById('ersFach');
  if(f) f.focus();
}
async function ersterStartAusfuehren(neu){
  const y = (document.getElementById('ersJahr').value || '').trim();
  const name = (document.getElementById('ersFach').value || '').trim();
  if(!/^\d{4}$/.test(y))
    return ladeStand('Das Jahr wird vierstellig erwartet, etwa ' + new Date().getFullYear() + '.', true);
  const anlegen = neu || !BEREICHE.length;
  const b = anlegen ? {name, tabellen: leereTabellen()} : BEREICHE[AKTIV];
  const fehler = (neu && !name) ? 'Der neue Fachbereich braucht einen Namen.'
    : bereichNamePruefen(name, anlegen ? null : b);
  if(fehler) return ladeStand(fehler, true);
  const vorher = BEREICHE[AKTIV];
  ladeKnoepfe(true);
  try{
    if(anlegen){ BEREICHE.push(b); bereichSetzen(BEREICHE.length - 1); }
    else b.name = name;
    bereicheOrdnen();
    await dbAnfrage('/rest/v1/jahrgang', {method:'POST',
      headers:{Prefer:'return=minimal'}, body: JSON.stringify({jahr:y, stand:''})});
    dialogSchliessen();
    bearbOffen = true;
    await bereichZeigen();
    bearbNeuerTitel();
  }catch(fehler){
    if(anlegen){
      BEREICHE = BEREICHE.filter(x=>x!==b);
      bereichSetzen(Math.max(0, BEREICHE.indexOf(vorher)));
      kopfFachbereich();
    }
    ladeStand(fehlertext(fehler), true); ladeKnoepfe(false);
  }
}
// ── Kongresse als Text ──
// Seit Print 3 stehen die Kongresse einer Ausgabe nur noch als Textliste in
// ausgabe.auslagen, ein Eintrag je Zeile; ein Bericht traegt "(Bericht)" am
// Ende. Was eine aeltere Fassung als Bericht oder als eigenen Kongresssatz
// mit Zuordnung fuehrte, wird beim Oeffnen und beim Uebernehmen dahin
// umgeschrieben - verloren geht dabei nichts.
function kongresseZusammen(a, b){
  return (a||[]).map(t=>String(t).trim()).filter(Boolean).concat((b||[])
    .map(t=>String(t).trim()).filter(Boolean)
    .map(t=>/\(Bericht\)$/.test(t) ? t : t + ' (Bericht)'));
}
function kongresseAlsText(t){
  const kong = t.kongress || [], zu = t.kongress_ausgabe || [];
  const nachId = new Map(kong.map(k=>[k.id, k]));
  const umgestellt = new Set(kong.map(k=>String(k.jahr)));
  (t.ausgabe || []).forEach(a=>{
    if(umgestellt.has(String(a.jahr))){
      const eigene = zu.filter(z=>z.ausgabe_id===a.id)
        .map(z=>({k:nachId.get(z.kongress_id), art:z.art})).filter(x=>x.k)
        .sort((x,y)=>kongVergleich(kongSchluessel(x.k, a.jahr), kongSchluessel(y.k, a.jahr)));
      a.auslagen = eigene.filter(x=>x.art!=='bericht').map(x=>kongressAus(x.k));
      a.berichte = eigene.filter(x=>x.art==='bericht').map(x=>kongressAus(x.k));
    }
    a.auslagen = kongresseZusammen(a.auslagen, a.berichte);
    a.berichte = [];
  });
  t.kongress = []; t.kongress_ausgabe = [];
  return t;
}
BEREICHE.forEach(b=>{ if(b && b.tabellen) kongresseAlsText(b.tabellen); });
bereichSetzen(AKTIV);

// ─── Datenschicht ───────────────────────────────────────────────────────────""")

rep("""window.addEventListener('offline', ()=>
  netzhinweis('Keine Netzverbindung – der angezeigte Stand bleibt sichtbar, Änderungen sind nicht möglich.'));
window.addEventListener('online', ()=> netzhinweis(''));
""", '')
rep('else               starteArbeitsfassung();', 'else               starteDatei();')

# Menuepunkt »Aus Excel-Vorlage laden« (siehe oben) und der Verweis darauf
# beim Anlegen eines Jahrgangs
rep('<span class="ex-t">Aus Excel laden</span>', '<span class="ex-t">Aus Excel-Vorlage laden</span>')
rep('Jahrgang ist über »Aus Excel laden« schneller angelegt.', 'Jahrgang ist über »Aus Excel-Vorlage laden« schneller angelegt.')

# ── Titelcover (11.10.2026) ────────────────────────────────────────────────
# Je Titel und Jahrgang ein Cover (titel.cover, verkleinertes JPEG als
# data-URL). Es steht als Leiste ueber der Uebersicht, ueber die ganze Breite
# in gleich breite Felder geteilt, nur fuer die gewaehlten Titel mit Cover.
# Bis 3 Felder (hoch) bzw. 5 (quer) stehen Cover und Text nebeneinander,
# darueber untereinander; hoechstens 6 bzw. 9 Spalten, sonst ausgeglichen
# auf mehrere Reihen. Sicherungspunkte fuehren das Cover nicht (die Datei
# bliebe sonst bei jedem Punkt um alle Bilder schwerer); beim Zuruecksetzen
# und beim Laden aus Excel bleibt das Cover des Titels stehen. Ein neuer
# Jahrgang uebernimmt die Cover nicht - sie gehoeren zum Jahrgang.
rep("vorgabe:()=>({auflage:0, hex:'#00285a', rubriken:[]}),",
    "vorgabe:()=>({auflage:0, hex:'#00285a', rubriken:[], cover:''}),")
rep("      rubriken: (t.rubriken || []).map(r=>({id:r.id, name:r.name}))",
    "      cover: t.cover || '',\n      rubriken: (t.rubriken || []).map(r=>({id:r.id, name:r.name}))")
rep("""  await dbAnfrage('/rest/v1/titel?jahr=eq.'+encodeURIComponent(y),
    {method:'DELETE', headers:{Prefer:'return=minimal'}});
  await dbAnfrage('/rest/v1/titel',
    {method:'POST', headers:{Prefer:'return=minimal'},
     body: JSON.stringify(titel.map(t=>({jahr:y, id:t.id, kurz:t.short, voll:t.full,
       auflage:t.auflage||0, hex:t.hex||'#00285a', rubriken:t.rubriken||[]})))});""",
"""  // Excel und Sicherungspunkte fuehren kein Cover: das bisherige bleibt.
  const coverVorher = new Map((await dbAnfrage('/rest/v1/titel?jahr=eq.'+encodeURIComponent(y)))
    .map(t=>[String(t.id), t.cover || '']));
  await dbAnfrage('/rest/v1/titel?jahr=eq.'+encodeURIComponent(y),
    {method:'DELETE', headers:{Prefer:'return=minimal'}});
  await dbAnfrage('/rest/v1/titel',
    {method:'POST', headers:{Prefer:'return=minimal'},
     body: JSON.stringify(titel.map(t=>({jahr:y, id:t.id, kurz:t.short, voll:t.full,
       auflage:t.auflage||0, hex:t.hex||'#00285a', rubriken:t.rubriken||[],
       cover: t.cover!==undefined ? (t.cover||'') : (coverVorher.get(String(t.id)) || '')})))});""")
rep("      auflage:String(t.auflage||0), hex:t.hex||'#00285a',",
    "      auflage:String(t.auflage||0), hex:t.hex||'#00285a', cover:t.cover||'',")
rep("hex:farbeFuer(naechsteTitelId()), rubriken:[] });",
    "hex:farbeFuer(naechsteTitelId()), cover:'', rubriken:[] });")
rep("auflage: Number(entwurf.auflage)||0, hex: entwurf.hex, rubriken };",
    "auflage: Number(entwurf.auflage)||0, hex: entwurf.hex, cover: entwurf.cover||'', rubriken };")
rep("rubriken:feld.rubriken, issues:[] });", "rubriken:feld.rubriken, cover:feld.cover, issues:[] });")
rep("t.rubriken=feld.rubriken;", "t.rubriken=feld.rubriken; t.cover=feld.cover;")
rep("    ${titelRubrikenGruppe()}", """    <div class="bearb-gruppe">
      <span class="bearb-feld">Titelcover
        <span class="hinweis">Gilt für diesen Jahrgang; erscheint über der Übersicht,
          im Druck und in der HTML-Kopie. JPG oder PNG, wird verkleinert gespeichert</span></span>
      <div class="cv-wahl">
        ${entwurf.cover ? `<img class="cv-vorschau" src="${escA(entwurf.cover)}" alt="">`
                        : '<div class="cv-leer">Kein Cover</div>'}
        <div class="cv-knoepfe">
          <button type="button" class="bearb-zu" onclick="coverWaehlen()">${entwurf.cover ? 'Anderes Bild wählen …' : 'Bild wählen …'}</button>
          ${entwurf.cover ? '<button type="button" class="bearb-zu" onclick="coverWeg()">Cover entfernen</button>' : ''}
        </div>
      </div>
    </div>

    ${titelRubrikenGruppe()}""")
rep('<div class="stats" id="stats"></div>',
    '<div class="stats" id="stats"></div>\n  <div class="cover-leiste" id="coverLeiste"></div>')
rep("function setzeExportKopf(q,zahlen){", "function setzeExportKopf(q,zahlen){\n  coverLeiste();")
rep(".hero-kontakt:empty{display:none}", """.hero-kontakt:empty{display:none}
/* Titelcover: Leiste ueber der Uebersicht, gleich breite Felder (--cl), mittig */
/* Cover 160 px hoch neben dem Text, 140 px untereinander; bei vielen Spalten auf die Feldbreite verkleinert */
.cover-leiste{display:grid;grid-template-columns:repeat(var(--cl,1),minmax(0,1fr));gap:10px;margin:0 0 16px}
.cover-leiste:empty,body.bearbmodus .cover-leiste{display:none}
.cl-feld{display:flex;flex-direction:column;align-items:center;justify-content:flex-start;gap:8px;
  text-align:center;background:var(--surface);border:1px solid var(--surface3);border-radius:8px;padding:12px 10px;min-width:0}
.cl-feld img{display:block;width:auto;height:auto;max-height:140px;max-width:100%;border:1px solid #d5dbe5;border-radius:2px}
.cover-leiste.neben .cl-feld img{max-height:160px;max-width:45%}
.cl-name{font-weight:700;color:var(--navy);font-size:.8rem;line-height:1.25}
.cl-info{font-size:.7rem;color:var(--muted);margin-top:3px;line-height:1.45}
.cl-info span{display:block}
.cover-leiste.neben .cl-feld{flex-direction:row;justify-content:center;align-items:center;gap:14px;text-align:left;padding:12px 16px}
.cover-leiste.neben .cl-name{font-size:.9rem}
.cover-leiste.neben .cl-info{font-size:.75rem}
.cover-leiste.neben .cl-info span{display:inline}
.cover-leiste.neben .cl-info span+span::before{content:" · "}
/* Auflage und Hefte brechen nie in sich um. Ist das Feld schmaler, als
   "120.000 Expl. · 12 Hefte 2027" neben dem Cover braucht (gut 310 px),
   stehen beide fest in zwei Zeilen - gemessen am Feld, also auch im Druck. */
.cl-feld{container-type:inline-size}
.cl-info span{white-space:nowrap}
@container (max-width:320px){
  .cover-leiste.neben .cl-info span{display:block}
  .cover-leiste.neben .cl-info span+span::before{content:none}}
@media(max-width:640px){.cover-leiste{display:none}}
@media print{.cover-leiste{gap:3mm;margin-bottom:4mm}
  .cl-feld{break-inside:avoid;-webkit-print-color-adjust:exact;print-color-adjust:exact}}
.cv-wahl{display:flex;align-items:center;gap:14px;margin-top:6px}
.cv-vorschau{display:block;height:96px;width:auto;max-width:96px;border:1px solid #d5dbe5;border-radius:2px}
.cv-leer{width:72px;height:96px;border:1px dashed var(--surface3);border-radius:2px;display:flex;align-items:center;
  justify-content:center;text-align:center;font-size:.7rem;color:var(--muted)}
.cv-knoepfe{display:flex;flex-direction:column;align-items:flex-start;gap:4px}""")
# Die Kopie baut die Leiste beim Oeffnen selbst; die gezeichnete Leiste aus
# dem Klon trueg jedes Bild sonst ein zweites Mal in die Datei.
rep("  // Die Kopie zeigt den Kontakt immer in der Leseform, auch aus der Arbeitsansicht.",
    """  const cl = klon.querySelector('#coverLeiste');
  if(cl){ cl.innerHTML = ''; cl.removeAttribute('style'); cl.className = 'cover-leiste'; }
  // Die Kopie zeigt den Kontakt immer in der Leseform, auch aus der Arbeitsansicht.""")
rep("// ── Kontakt des Fachbereichs ──", """// ── Titelcover ──
// Die Leiste zeigt die gewaehlten Titel, soweit sie ein Cover haben. Das
// Raster richtet sich nach der Breite: am Schirm ab 1300 px wie quer, im
// Druck nach dem gewaehlten Format (beforeprint), sonst wie hoch.
let coverImDruck = false;
function coverLeiste(){
  const el = document.getElementById('coverLeiste');
  if(!el) return;
  const ts = JOURNALS.filter(j=>j.cover && (activeJ.size===0 || activeJ.has(j.id)));
  el.innerHTML = ts.map(j=>{
    const n = j.issues.length;
    const aufl = Number(j.auflage) ? '<span>' + Number(j.auflage).toLocaleString('de-DE') + ' Expl.</span>' : '';
    return `<div class="cl-feld"><img src="${escA(j.cover)}" alt=""><div class="cl-text">`
      + `<div class="cl-name">${esc(j.short)}</div>`
      + `<div class="cl-info">${aufl}<span>${n} Heft${n===1?'':'e'} ${esc(jahrgang())}</span></div></div></div>`;
  }).join('');
  coverRaster();
}
function coverRaster(){
  const el = document.getElementById('coverLeiste');
  const n = el ? el.children.length : 0;
  if(!n) return;
  const quer = coverImDruck ? (druckFormat || empfohlenesFormat())==='landscape'
                            : window.innerWidth >= 1300;
  const mx = quer ? 9 : 6;
  let c = Math.min(n, mx);
  if(n > mx){ const reihen = Math.ceil(n / mx); c = Math.ceil(n / reihen); }
  el.style.setProperty('--cl', c);
  el.classList.toggle('neben', c <= (quer ? 5 : 3));
}
window.addEventListener('resize', ()=>{ if(!coverImDruck) coverRaster(); });
window.addEventListener('beforeprint', ()=>{ coverImDruck = true; coverRaster(); });
window.addEventListener('afterprint', ()=>{ coverImDruck = false; coverRaster(); });
// Verkleinert auf hoechstens 300 x 400 px, als JPEG - so bleibt die Datei
// leicht, und fuer den Druck in Leistengroesse reicht es.
function coverWaehlen(){
  const ein = document.createElement('input');
  ein.type = 'file'; ein.accept = 'image/*';
  ein.onchange = ()=>{
    const datei = ein.files && ein.files[0];
    if(!datei) return;
    const leser = new FileReader();
    leser.onload = ()=>{
      const bild = new Image();
      bild.onload = ()=>{
        const f = Math.min(1, 300 / bild.naturalWidth, 400 / bild.naturalHeight);
        const w = Math.max(1, Math.round(bild.naturalWidth * f)), h = Math.max(1, Math.round(bild.naturalHeight * f));
        const c = document.createElement('canvas'); c.width = w; c.height = h;
        const x = c.getContext('2d');
        x.fillStyle = '#fff'; x.fillRect(0, 0, w, h);
        x.drawImage(bild, 0, 0, w, h);
        if(!entwurf) return;
        entwurf.cover = c.toDataURL('image/jpeg', 0.85);
        bearbFormNeu();
        bearbStand('Nicht gespeichert', '');
      };
      bild.onerror = ()=> bearbStand('Das Bild lässt sich nicht lesen. Erwartet wird ein JPG oder PNG.', 'schlecht');
      bild.src = leser.result;
    };
    leser.readAsDataURL(datei);
  };
  ein.click();
}
function coverWeg(){
  if(!entwurf) return;
  entwurf.cover = '';
  bearbFormNeu();
  bearbStand('Nicht gespeichert', '');
}

// ── Kontakt des Fachbereichs ──""")

# Tabelle: Themenschwerpunkte, Weitere Rubriken und Kongresse gleich breit.
# Die Web-Fassung kennt nur Kongresse als breite Textspalte (40 %); hier trug
# "Weitere Rubriken" dieselbe Klasse, und die Themen blieben bei 200 px stehen.
# Die Klasse tx2/tx3 zaehlt die sichtbaren Textspalten; mit nur einer bleibt
# alles wie in Web (Bildschirm 40 %, Druck 42 %).
rep("  return`<div class=\"tabwrap\"><table class=\"tab\"><thead>",
    "  const tx = spalten.filter(s=>s.k==='t'||s.k==='r'||s.k==='kong').length;\n"
    "  return`<div class=\"tabwrap\"><table class=\"tab${tx>1?' tx'+tx:''}\"><thead>")
rep(".t-thema{min-width:200px}", """.t-thema{min-width:200px}
table.tab.tx2 td.t-thema,table.tab.tx2 td.t-kong{width:37.5%}
table.tab.tx3 td.t-thema,table.tab.tx3 td.t-kong{width:25%}
@media screen{table.tab.tx2 td.t-kong,table.tab.tx3 td.t-kong{min-width:200px}}
.t-kong .kr{display:grid;grid-template-columns:max-content minmax(0,1fr);column-gap:6px;align-items:baseline}
@media print{.t-kong .kr{column-gap:5px}.t-kong .kr b{font-size:6pt}}""")

ZIEL.write_text(s, encoding='utf-8')
print(f'{ZIEL.name}: {len(s.encode("utf-8")):,} Bytes, MD5 {hashlib.md5(s.encode("utf-8")).hexdigest()}')
print(f'Grundlage: {QUELLE.parent.name}/{QUELLE.name}, MD5 {md5}')
