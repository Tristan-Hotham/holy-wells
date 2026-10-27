"""Name reader for wells in Britain, Ireland and the Isle of Man.

Three readings of each well name:
  language(name, nation, unit) -> language layer of the 'well' word
  saint(name)                   -> (key, how) or (None, None)
  folk(name)                    -> list of folk-practice name types

Rules (also documented on the page and in the README):
- Language is read from the generic word only: English 'well'/'wells'
  (also 'Ladywell', 'Holywell' written as one word); Welsh 'ffynnon'; Irish
  'tobar'/'tobair'/'tiobraid'/'tipra' (Gaelic spelling) or 'tober'/'tobber'/
  'tubber'/'tubbrid' (anglicised spelling, as on the Ordnance Survey maps of
  Ireland); Scottish Gaelic 'tobar'/'fuaran' when the well is in Scotland;
  Cornish 'venton'/'fenton'/'fenten' when the well is in Cornwall; Manx
  'chibbyr'/'chibber'. A name with none of these words is 'other'.
- Saints are read only where the name says so plainly: 'St X's Well',
  'Saint X', 'Ffynnon Sant X', or a known name form directly after the generic
  word (Tobar Phádraig, Toberbride, Ffynnon Fair, Tobar Mhoire). A name after
  'St' that is not in the table becomes its own key as written. Name forms
  after Tober/Tobar/Ffynnon are read only from the fixed table below, so
  'Tobermore' or 'Ffynnon Wen' stay unread rather than guessed.
- 'Lady Well', 'Our Lady's Well', 'Ladywell' and 'Virgin' are Mary.
  'Holy Well', 'Holywell', 'Trinity', 'Christ', 'Sunday' are kept as their
  own non-saint religious keys.
"""
import re, unicodedata


def norm(s):
    s = (s or "").replace("’", "'").replace("‘", "'").replace("`", "'")
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c)).lower().strip()


# English (and Latin-alphabet) name forms after 'St' -> key
ALIAS = {
    "mary": "Mary", "marys": "Mary", "maries": "Mary",
    "bridget": "Brigid", "brigid": "Brigid", "brigit": "Brigid", "bride": "Brigid", "brides": "Brigid", "bridgid": "Brigid", "bridgit": "Brigid",
    "brighid": "Brigid", "brigids": "Brigid", "bridgets": "Brigid", "breeda": "Brigid", "brigida": "Brigid", "briget": "Brigid", "bridget's": "Brigid",
    "patrick": "Patrick", "patricks": "Patrick", "padraig": "Patrick",
    "columba": "Colmcille", "columcille": "Colmcille", "colmcille": "Colmcille", "columbkille": "Colmcille", "columkille": "Colmcille", "colmkille": "Colmcille", "columb": "Colmcille", "colum": "Colmcille",
    "kieran": "Ciaran", "ciaran": "Ciaran", "kieran's": "Ciaran", "keiran": "Ciaran", "kiaran": "Ciaran", "kyran": "Ciaran", "kyrans": "Ciaran", "kierans": "Ciaran", "piran": "Piran", "perran": "Piran",
    "anne": "Anne", "ann": "Anne", "anna": "Anne", "annes": "Anne", "anns": "Anne",
    "helen": "Helen", "helena": "Helen", "helens": "Helen", "elen": "Helen", "helen": "Helen", "ellen": "Helen",
    "winifred": "Winifred", "winefride": "Winifred", "winifrede": "Winifred", "winifreds": "Winifred", "gwenfrewi": "Winifred",
    "catherine": "Catherine", "katherine": "Catherine", "catharine": "Catherine", "kathrine": "Catherine", "catherines": "Catherine",
    "margaret": "Margaret", "margarets": "Margaret", "john": "John", "johns": "John", "james": "James", "jame": "James",
    "peter": "Peter", "peters": "Peter", "paul": "Paul", "andrew": "Andrew", "andrews": "Andrew", "michael": "Michael", "michaels": "Michael",
    "david": "David", "davids": "David", "dewi": "David", "non": "Non", "nons": "Non", "cuthbert": "Cuthbert", "cuthberts": "Cuthbert",
    "chad": "Chad", "chads": "Chad", "aidan": "Aidan", "oswald": "Oswald", "oswalds": "Oswald", "ninian": "Ninian", "ninians": "Ninian",
    "mungo": "Kentigern", "kentigern": "Kentigern", "brendan": "Brendan", "brendans": "Brendan", "declan": "Declan", "declans": "Declan",
    "fintan": "Fintan", "fintans": "Fintan", "finbarr": "Finbarr", "finbar": "Finbarr", "fionnbarra": "Finbarr", "kevin": "Kevin", "kevins": "Kevin",
    "colman": "Colman", "colmans": "Colman", "molua": "Molua", "mochuda": "Mochuda", "carthage": "Mochuda", "moling": "Moling", "molings": "Moling",
    "gobnait": "Gobnait", "gobnet": "Gobnait", "gobinet": "Gobnait", "senan": "Senan", "senans": "Senan", "fechin": "Fechin", "feichin": "Fechin",
    "cronan": "Cronan", "ronan": "Ronan", "enda": "Enda", "ita": "Ita", "laserian": "Laserian", "molaise": "Laserian", "canice": "Canice",
    "flannan": "Flannan", "mel": "Mel", "kilian": "Kilian", "ailbe": "Ailbe", "munchin": "Munchin", "manchan": "Manchan", "fiacre": "Fiachra", "fiachra": "Fiachra",
    "brigid's": "Brigid", "martin": "Martin", "martins": "Martin", "lawrence": "Lawrence", "laurence": "Lawrence", "thomas": "Thomas", "stephen": "Stephen",
    "agnes": "Agnes", "edmund": "Edmund", "alkelda": "Alkelda", "hilda": "Hilda", "wilfrid": "Wilfrid", "wilfred": "Wilfrid", "bede": "Bede",
    "augustine": "Augustine", "augustines": "Augustine", "george": "George", "georges": "George", "nicholas": "Nicholas", "leonard": "Leonard",
    "cybi": "Cybi", "beuno": "Beuno", "seiriol": "Seiriol", "tegla": "Tegla", "dyfnog": "Dyfnog", "teilo": "Teilo", "madron": "Madron", "keyne": "Keyne",
    "cleer": "Cleer", "clether": "Clether", "neot": "Neot", "nectan": "Nectan", "ia": "Ia", "euny": "Euny", "maughold": "Maughold", "fillan": "Fillan",
    "maelrubha": "Maelrubha", "moluag": "Moluag", "medana": "Medana", "triduana": "Triduana", "queran": "Ciaran", "ciarain": "Ciaran",
    "mullins": "Moling", "corcoran": "Corcoran", "brigeds": "Brigid", "bridgets'": "Brigid", "olave": "Olaf", "olaf": "Olaf", "bartholomew": "Bartholomew",
    "barbara": "Barbara", "boniface": "Boniface", "ethelbert": "Ethelbert", "edith": "Edith", "frideswide": "Frideswide", "osyth": "Osyth", "walstan": "Walstan",
    "withburga": "Withburga", "eanswythe": "Eanswythe", "mungos": "Kentigern", "joseph": "Joseph", "luke": "Luke", "mark": "Mark", "matthew": "Matthew",
    "kenelm": "Kenelm", "edward": "Edward", "botolph": "Botolph", "werburgh": "Werburgh", "plegmund": "Plegmund", "mabyn": "Mabyn", "uny": "Euny",
    "brannoc": "Brannock", "brannock": "Brannock", "petroc": "Petroc", "gundred": "Gundred", "ninians'": "Ninian", "mochua": "Mochua", "dympna": "Dympna",
    "attracta": "Attracta", "ultan": "Ultan", "brides": "Brigid", "kenneth": "Canice", "colmcilles": "Colmcille", "bridgit's": "Brigid", "lachtain": "Lachtain", "mogue": "Mogue", "aedan": "Aidan",
}
# fixed forms after an Irish or Scottish Gaelic 'tobar/tober...' (spaced, hyphenated or joined) -> key
GAELIC = {
    "mhuire": "Mary", "muire": "Mary", "mhoire": "Mary", "moire": "Mary", "na maighdine": "Mary",
    "bhride": "Brigid", "bride": "Brigid", "bhrid": "Brigid", "bhrighde": "Brigid", "breeda": "Brigid", "breedia": "Brigid", "breedy": "Brigid", "breda": "Brigid", "bridget": "Brigid", "brigid": "Brigid", "bhrighid": "Brigid",
    "phadraig": "Patrick", "phadraic": "Patrick", "padraig": "Patrick", "patrick": "Patrick", "phatraic": "Patrick",
    "chiarain": "Ciaran", "kieran": "Ciaran", "keeran": "Ciaran", "ciaran": "Ciaran", "kerrin": "Ciaran",
    "cholmcille": "Colmcille", "colmcille": "Colmcille", "columbkille": "Colmcille", "columkille": "Colmcille", "colmkille": "Colmcille", "chaluim chille": "Colmcille", "chalum chille": "Colmcille",
    "bhreanainn": "Brendan", "brendan": "Brendan", "declan": "Declan", "fintan": "Fintan", "fhionntain": "Fintan", "kevin": "Kevin", "chaoimhin": "Kevin",
    "molua": "Molua", "mochuda": "Mochuda", "moling": "Moling", "gobnait": "Gobnait", "gobnet": "Gobnait", "senan": "Senan", "fechin": "Fechin", "feichin": "Fechin",
    "cronan": "Cronan", "ronan": "Ronan", "enda": "Enda", "colman": "Colman", "finbarr": "Finbarr", "mhichil": "Michael", "michael": "Michael",
    "murry": "Mary", "murray": "Mary", "reendoney": "Sunday", "reendowney": "Sunday", "eendoney": "Sunday", "adoney": "Sunday", "doney": "Sunday",
    "macduagh": "Mac Duagh", "mac duagh": "Mac Duagh", "araght": "Attracta", "arraght": "Attracta", "mochulla": "Mochulla", "mochuille": "Mochulla",
    "ultan": "Ultan", "mogue": "Mogue", "feheen": "Fechin", "brighde": "Brigid", "bhrighde": "Brigid",
    "eoin": "John", "sheain": "John", "john": "John", "martin": "Martin", "mhartain": "Martin", "mhaolrubha": "Maelrubha", "fillan": "Fillan",
}
# fixed forms after Welsh 'ffynnon' (with soft mutation) -> key
WELSH = {
    "fair": "Mary", "mair": "Mary", "ddewi": "David", "dewi": "David", "wenfrewi": "Winifred", "gwenfrewi": "Winifred", "gybi": "Cybi", "cybi": "Cybi",
    "non": "Non", "beuno": "Beuno", "elen": "Helen", "helen": "Helen", "fihangel": "Michael", "mihangel": "Michael", "degla": "Tegla", "tegla": "Tegla",
    "ddyfnog": "Dyfnog", "dyfnog": "Dyfnog", "seiriol": "Seiriol", "badrig": "Patrick", "badrick": "Patrick", "deilo": "Teilo", "teilo": "Teilo",
    "gwenfaen": "Gwenfaen", "fyllin": "Myllin", "fred": "Brigid", "ffraid": "Brigid", "sanffraid": "Brigid", "santffraid": "Brigid", "eilian": "Eilian",
    "cristiolus": "Cristiolus", "dyfrig": "Dyfrig", "gwynwy": "Gwynwy", "cynfarch": "Cynfarch", "tudno": "Tudno", "trillo": "Trillo", "fyw": "Wyw",
    "beris": "Peris", "peris": "Peris", "elian": "Eilian", "ddeiniol": "Deiniol", "deiniol": "Deiniol", "gadfan": "Cadfan", "cadfan": "Cadfan",
    "dydecho": "Tydecho", "tydecho": "Tydecho", "drillo": "Trillo", "ddyfrig": "Dyfrig", "gwenllian": None, "wen": None,
}
# names read as a saint even without 'St' when written as '<Name>'s Well' (distinctly saints' names only, so 'John's Well' is not read)
POSS = {"Brigid", "Patrick", "Colmcille", "Ciaran", "Brendan", "Declan", "Fintan", "Finbarr", "Kevin", "Molua", "Mochuda", "Moling", "Gobnait", "Senan",
        "Fechin", "Cronan", "Enda", "Laserian", "Canice", "Flannan", "Kentigern", "Ninian", "Cuthbert", "Winifred", "Cybi", "Beuno", "Ultan", "Attracta",
        "Piran", "Keyne", "Madron", "Alkelda", "Chad", "Aidan", "Oswald", "Mogue", "Columba"}
MARY_RX = re.compile(r"\b(our lady|lady'?s?|ladye|ladywell|virgin)\b")
HOLY_RX = re.compile(r"\b(holy ?wells?|holywell|haly ?well|halliwell|halywell|holy\b|sacred well|blessed well|tobar beannaithe|tobar beannaighthe)\b")
TRIN_RX = re.compile(r"\btrinity\b")
CHRIST_RX = re.compile(r"\b(christ'?s?|jesus|our lord'?s?|saviour'?s?|corpus christi)\b")
SUNDAY_RX = re.compile(r"\bsunday'?s?\b|\bdomhnaigh\b")
CLERIC_RX = re.compile(r"\b(priest'?s?|monk'?s?|friar'?s?|nun'?s?|bishop'?s?|abbot'?s?|abbey|chapel|canon'?s?|hermit'?s?|pope'?s?|cross)\b")
ST_RX = re.compile(r"\b(?:st|saint|sts|ste|sanct|sant|santes|naomh)\b\.?\s+([a-z][a-z'\-]+)")


def gaelic_rest(n):
    m = re.match(r"^(?:tobar|tobair|tober|tobber|tubber|tubbrid|tiobraid|fuaran|chibbyr|chibber)[\s\-]*(?:an\s+|na\s+|a\s+)?(.*)$", n)
    return m.group(1) if m else None


def saint(name):
    """Return (key, how) where how is 'st', 'gaelic', 'welsh', 'mary', 'religious' ; or (None, None)."""
    n = norm(name)
    if not n: return None, None
    m = ST_RX.search(n)
    if m:
        w0 = m.group(1).strip("'-")
        w1 = w0[:-2] if w0.endswith("'s") else w0.rstrip("'")
        for cand in (w0, w1, w1[:-1] if w1.endswith("s") else None):
            if cand and cand in ALIAS: return ALIAS[cand], "st"
        if len(w1) >= 2 and w1 not in ("well", "wells", "the", "of", "and"): return w1.capitalize(), "st"
    rest = gaelic_rest(n)
    if rest is not None:
        r = rest.strip()
        for form in sorted(GAELIC, key=len, reverse=True):
            if r == form or r.startswith(form + " ") or r.startswith(form + "'") or (r.startswith(form) and len(form) >= 5 and n.startswith(("tober", "tobber", "tubber"))):
                return GAELIC[form], "gaelic"
    m = re.search(r"\bffynnon[\s\-]+(?:sant |santes |sanct )?([a-z]+)", n)
    if m and m.group(1) in WELSH and WELSH[m.group(1)]:
        return WELSH[m.group(1)], "welsh"
    m = re.match(r"^([a-z]+)'?s'? wells?$", n)
    if m and ALIAS.get(m.group(1)) in POSS: return ALIAS[m.group(1)], "st"
    if MARY_RX.search(n): return "Mary", "mary"
    if re.search(r"\ball saints\b|\ball hallows\b", n): return "All Saints", "religious"
    if TRIN_RX.search(n): return "Trinity", "religious"
    if CHRIST_RX.search(n): return "Christ", "religious"
    if SUNDAY_RX.search(n): return "Sunday", "religious"
    if HOLY_RX.search(n): return "Holy (no saint named)", "religious"
    return None, None


FOLK = [
    ("wishing", re.compile(r"\bwishing\b")),
    ("rag or clootie", re.compile(r"\b(rag|rags|clootie|cloutie|clooty|cloot|clout)\b")),
    ("pin", re.compile(r"\bpin\b|\bpins\b|\bpin ?well")),
    ("cursing", re.compile(r"\bcursing\b|\bcurse\b")),
    ("eye", re.compile(r"\beyes?\b|\beye ?well|\bsore eye")),
    ("wart", re.compile(r"\bwarts?\b|\bwart ?well")),
    ("fever or ague", re.compile(r"\b(fever|ague)\b")),
]


def folk(name):
    n = norm(name)
    return [k for k, rx in FOLK if rx.search(n)]


def language(name, nation, unit=""):
    n = norm(name)
    if not n: return "unnamed"
    if re.search(r"\bffynnon\b|\bffynhonnau\b", n): return "Welsh"
    if re.search(r"\b(chibbyr|chibber)\b", n): return "Manx"
    if unit == "Cornwall" and re.search(r"\b(venton|fenton|fenten)\b", n): return "Cornish"
    if re.search(r"^(tobar|tobair|tiobraid|tipra|fuaran)\b|\b(tobar|tobair|fuaran)\b", n):
        return "Scottish Gaelic" if nation == "Scotland" else "Irish (Gaelic spelling)"
    if re.search(r"^(tober|tobber|tubber|tubbrid|tubrid|tobbar)|\b(tober|tobber|tubber)[a-z]*\b", n):
        return "Irish (anglicised)" if nation != "Scotland" else "Scottish Gaelic"
    if re.search(r"\bwells?\b|ladywell|holywell|halliwell|well$", n): return "English"
    return "other"
