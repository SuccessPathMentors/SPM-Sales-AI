#!/usr/bin/env python3
"""Build the guided-question tree (tree.json) from the approved SPM knowledge-base snapshot.

Read-only: reads the xlsx snapshot, writes tree.json + tree_report.md next to this script.
Every answer text is copied verbatim from an ACTIVE KB row. Anything composed or
adapted is marked origin="composed" and listed in the report for owner approval.

Usage: python3 -I build_tree.py <kb.xlsx> <out_dir>
"""
import json, sys, re, collections
import openpyxl

KB, OUT = sys.argv[1], sys.argv[2]
LANGS = ["ar", "en", "fr"]

wb = openpyxl.load_workbook(KB, read_only=True, data_only=True)


def rows(name):
    r = list(wb[name].iter_rows(values_only=True))
    h = r[0]
    out = []
    for x in r[1:]:
        if not x or not x[0]:
            continue
        d = dict(zip(h, x))
        if str(d.get("status", "ACTIVE")).upper() == "ACTIVE":
            out.append(d)
    return out


FAQ, POL, PKG, SUB, COM, PATH, OBJ, SERV, FB, NUR = (rows(n) for n in
    ["FAQ", "POLICIES", "PACKAGES", "SUBJECTS", "COMPANY", "SUBJECT_PATHWAYS", "OBJECTIONS", "SERVICES", "FALLBACKS", "SALES_NURTURE"])

# Records that must never reach customers (test row, conversation-specific example, duplicates)
EXCLUDED = {"FAQ-UQ-39556": "test record", "FAQ-358": "conversation-specific example, not a general answer"}
used_sources = set()
gaps = []          # (node, lang, reason)
composed = []      # (node, lang, reason)
excluded_note = []


def by(rowsl, key, val, lang, langkey="language"):
    for r in rowsl:
        if r.get(key) == val and str(r.get(langkey)).lower() == lang and r.get(next(iter(r))) not in EXCLUDED:
            return r
    return None


def faq(cat, lang):
    return by(FAQ, "category", cat, lang)


def pol(kind, lang):
    return by(POL, "policy_type", kind, lang)


def com(cat, lang):
    return by(COM, "category", cat, lang)


nodes = collections.OrderedDict()


def add(nid, parent, kind, label, text=None, options=None, sources=None, origin="kb", **extra):
    """label/text are dicts lang->str (missing lang => node hidden in that language)."""
    nodes[nid] = dict(id=nid, parent=parent, kind=kind, label=label or {}, text=text or {},
                      options=options or [], sources=sources or [], origin=origin, **extra)
    return nid


def src(*recs):
    ids = [r[next(iter(r))] for r in recs if r]
    used_sources.update(ids)
    return ids


# ---------------------------------------------------------------- UI copy (wording of the interface, not facts)
UI = {
    "greeting": {"ar": "أهلاً بكم في Success Path Mentors. اختر ما يهمّكم.",
                 "en": "Welcome to Success Path Mentors. Choose what you would like to know.",
                 "fr": "Bienvenue chez Success Path Mentors. Choisissez ce qui vous intéresse."},
    "pick": {"ar": "اختر من الخيارات التالية.", "en": "Choose one of the options below.", "fr": "Choisissez l’une des options ci-dessous."},
    "home": {"ar": "الرئيسية", "en": "Home", "fr": "Accueil"},
    "back1": {"ar": "رجوع", "en": "Back", "fr": "Retour"},
    "back2": {"ar": "رجوع مستويين", "en": "Back 2 levels", "fr": "Retour de 2 niveaux"},
    "fwd": {"ar": "إلى الأمام", "en": "Forward", "fr": "Suivant"},
    "map": {"ar": "خريطة الأسئلة", "en": "Question map", "fr": "Carte des questions"},
    "you_are_here": {"ar": "أنت هنا", "en": "You are here", "fr": "Vous êtes ici"},
    "human": {"ar": "تواصل مع الفريق", "en": "Contact the team", "fr": "Contacter l’équipe"},
    "related": {"ar": "أسئلة قد تهمّك", "en": "You may also want to know", "fr": "Vous pourriez aussi vouloir savoir"},
    "next_step": {"ar": "الخطوة التالية", "en": "Next step", "fr": "Étape suivante"},
}

# ---------------------------------------------------------------- root and main menu
MAIN = [
    ("about",    {"ar": "من نحن وما خدماتنا؟", "en": "Who we are and what we offer", "fr": "Qui sommes-nous et que proposons-nous ?"}),
    ("subjects", {"ar": "المواد والصفوف", "en": "Subjects and grades", "fr": "Matières et niveaux"}),
    ("pricing",  {"ar": "الأسعار والباقات", "en": "Prices and packages", "fr": "Tarifs et forfaits"}),
    ("trial",    {"ar": "الحصة التجريبية المجانية", "en": "Free trial lesson", "fr": "Essai gratuit"}),
    ("classes",  {"ar": "كيف تسير الحصص؟", "en": "How lessons work", "fr": "Déroulement des cours"}),
    ("help",     {"ar": "كيف تساعدون ابني؟", "en": "How do you help my child?", "fr": "Comment aidez-vous mon enfant ?"}),
    ("policies", {"ar": "الإلغاء والغياب والاسترداد", "en": "Cancellation, absence and refunds", "fr": "Annulation, absence et remboursement"}),
    ("concerns", {"ar": "لديّ تحفظ أو قلق", "en": "I have a concern", "fr": "J’ai une réserve"}),
    ("register", {"ar": "سجّل الآن", "en": "Register now", "fr": "S’inscrire"}),
]
add("root", None, "menu", {"ar": "الرئيسية", "en": "Home", "fr": "Accueil"}, UI["greeting"],
    # ordered by real traffic (WU109_INTENT_SUMMARY): learning goal 24%, subjects/grades 20%, pricing 11%, registration ~10%
    ["help", "subjects", "pricing", "trial", "register", "classes", "concerns", "policies", "about"], origin="ui")

CTA_TRIAL = {"to": "trial"}
CTA_REG = {"to": "register"}

# ---------------------------------------------------------------- about
svc = {l: com("service", l) for l in LANGS}
add("about", "root", "menu", MAIN[0][1],
    {l: svc[l]["content"] for l in LANGS if svc[l]},
    ["about_online", "about_grades", "about_where", "about_curriculum"], src(*svc.values()))


def faq_leaf(nid, parent, cat, follow, label_override=None):
    rs = {l: faq(cat, l) for l in LANGS}
    lab = label_override or {l: rs[l]["question"] for l in LANGS if rs[l]}
    txt = {l: rs[l]["answer"] for l in LANGS if rs[l]}
    for l in LANGS:
        if not rs[l]:
            gaps.append((nid, l, f"no approved FAQ '{cat}' row in this language"))
    add(nid, parent, "answer", lab, txt, follow, src(*rs.values()))


faq_leaf("about_online", "about", "delivery", ["about_grades", "trial", "register"])
faq_leaf("about_grades", "about", "grades", ["subjects", "trial", "register"])
cur = {l: com("curriculum", l) for l in LANGS}
add("about_curriculum", "about",
    "answer",
    {"ar": "ما المناهج التي تدعمونها؟", "en": "Which curricula do you support?", "fr": "Quels programmes soutenez-vous ?"},
    {l: cur[l]["content"] for l in LANGS if cur[l]},
    ["subjects", "trial", "register"], src(*cur.values()))
nodes["about_curriculum"]["origin"] = "kb+ui-label"

# ---------------------------------------------------------------- subjects
EN_NAME = {"الرياضيات": "Mathematics", "اللغة الإنجليزية": "English", "العلوم": "General Science",
           "الفيزياء": "Physics", "الكيمياء": "Chemistry"}
FR_NAME = {"اللغة الإنجليزية": "Anglais", "الفيزياء": "Physique"}
PATH_AR_NAME = {"العلوم": "العلوم العامة"}   # SUBJECTS says "العلوم", SUBJECT_PATHWAYS says "العلوم العامة"

sub_ids = []
for s in SUB:
    if str(s["language"]).lower() != "ar":
        continue
    nid = "sub_" + s["record_id"].split("-")[1]
    sub_ids.append(nid)
    ar = s["subject"]
    label = {"ar": ar}
    if ar in EN_NAME: label["en"] = EN_NAME[ar]
    if ar in FR_NAME: label["fr"] = FR_NAME[ar]
    g1, g2 = int(float(s["grade_from"])), int(float(s["grade_to"]))
    text = {"ar": s["description"]}
    # EN/FR descriptions are assembled from the structured grade fields; flagged for approval.
    if "en" in label:
        text["en"] = f"{label['en']}: one-to-one online lessons for Grades {g1}–{g2}."
        composed.append((nid, "en", "description assembled from SUBJECTS structured fields"))
    if "fr" in label:
        text["fr"] = f"{label['fr']} : cours individuels en ligne de la {g1}{'re' if g1 == 1 else 'e'} à la {g2}e année."
        composed.append((nid, "fr", "description assembled from SUBJECTS structured fields"))
    for l in LANGS:
        if l not in label:
            gaps.append((nid, l, "no approved subject name in this language"))
    opts = []
    # strands
    pname = PATH_AR_NAME.get(ar, ar)
    strands = {}
    for p in PATH:
        pl = str(p["language"]).lower()
        pn = p["subject"]
        if pl == "ar" and pn == pname:
            strands.setdefault("ar", []).append(p)
        if pl == "en" and pn == EN_NAME.get(ar):
            strands.setdefault("en", []).append(p)
        if pl == "fr" and pn == FR_NAME.get(ar):
            strands.setdefault("fr", []).append(p)
    if strands:
        sid = nid + "_strands"
        stx = {l: "• " + "\n• ".join(p["strand"] for p in strands[l]) for l in strands}
        slabel = {"ar": "ما محاور المادة؟", "en": "What topics are covered?", "fr": "Quels sujets sont couverts ?"}
        add(sid, nid, "answer", slabel, stx, [nid.replace("_strands", ""), "trial", "register"],
            src(*[p for l in strands for p in strands[l]]), origin="kb+ui-label")
        opts.append(sid)
        for l in LANGS:
            if l not in strands:
                gaps.append((sid, l, "no approved topic list in this language"))
    if ar == "الفيزياء":
        # Ontario Grade 11 Physics: verbatim FAQ answers
        rs = {l: faq("curriculum_alignment", l) for l in LANGS}
        add(nid + "_ontario", nid, "answer",
            {l: rs[l]["question"] for l in LANGS if rs[l]},
            {l: rs[l]["answer"] for l in LANGS if rs[l]},
            [nid, "trial", "register"], src(*rs.values()))
        opts.append(nid + "_ontario")
    opts += [{"to": "pricing"}, {"to": "trial"}, {"to": "register", "preset": {"subject": nid}}]
    add(nid, "subjects", "answer", label, text, opts, src(s))
add("subjects", "root", "menu", MAIN[1][1],
    {"ar": "اختر المادة.", "en": "Choose a subject.", "fr": "Choisissez une matière."},
    ["about_grades"] + sub_ids, [], origin="ui")

# ---------------------------------------------------------------- pricing (country first, per decision D-009)
pk = {}
for p in PKG:
    pk.setdefault(int(p["class_count"]), {})[str(p["language"]).lower()] = p


def to_cad(text, lang):
    t = text.replace("USD", "CAD")
    if lang == "ar":
        t = t.replace("أمريكية", "كندية").replace("أمريكيًا", "كنديًا")
    return t


PKG_LABEL = {"ar": lambda n: f"باقة {n} {'حصة' if n == 12 else 'حصص'}",
             "en": lambda n: f"{n}-lesson package",
             "fr": lambda n: f"Forfait de {n} cours"}
CO = {"ca": {"ar": "كندا", "en": "Canada", "fr": "Canada"}, "us": {"ar": "الولايات المتحدة", "en": "United States", "fr": "États-Unis"}}
for c in ("ca", "us"):
    ids = []
    for n in sorted(pk):
        nid = f"price_{c}_{n}"
        ids.append(nid)
        txt = {}
        for l in LANGS:
            r = pk[n].get(l)
            if not r:
                gaps.append((nid, l, "no approved package row"))
                continue
            txt[l] = r["answer_text"] if c == "us" else to_cad(r["answer_text"], l)
            if c == "ca":
                composed.append((nid, l, "Canada price = package row with USD→CAD per decision D-009; live sheet must confirm"))
        add(nid, f"price_{c}", "answer", {l: PKG_LABEL[l](n) for l in LANGS}, txt,
            ["faq_frequency", "concern_price", {"to": "trial"}, {"to": "register"}],
            src(*pk[n].values()), origin="kb" if c == "us" else "composed")
    add(f"price_{c}", "pricing", "menu", CO[c],
        {"ar": "اختر الباقة.", "en": "Choose a package.", "fr": "Choisissez un forfait."}, ids, [], origin="ui")
add("pricing", "root", "menu", MAIN[2][1],
    {"ar": "أين يقيم الطالب؟ يختلف سعر الباقة بحسب البلد.", "en": "Where does the student live? The package price depends on the country.",
     "fr": "Où réside l’élève ? Le prix du forfait dépend du pays."},
    ["price_ca", "price_us"], [], origin="ui")

# ---------------------------------------------------------------- trial
rs = {l: faq("trial", l) for l in LANGS}
add("trial", "root", "answer", MAIN[3][1], {l: rs[l]["answer"] for l in LANGS if rs[l]},
    ["classes_duration", "classes_matching", {"to": "register", "preset": {"request": "FREE_TRIAL"}}], src(*rs.values()))
nodes["trial"]["origin"] = "kb+ui-label"

# ---------------------------------------------------------------- classes
faq_leaf("classes_duration", "classes", "lesson_duration", ["classes_frequency", "trial", "register"])
faq_leaf("classes_frequency", "classes", "lesson_frequency", ["pricing", "trial", "register"])
faq_leaf("classes_homework", "classes", "homework", ["classes_matching", "trial", "register"])
faq_leaf("classes_matching", "classes", "matching", ["classes_tutor", "trial", "register"])


def svc_leaf(nid, parent, num, label, follow):
    """Answer = verbatim 'description' of the ACTIVE SERVICES row S-<LANG>-<num>; label is interface wording."""
    rs = {l: by(SERV, "service_id", f"S-{l.upper()}-{num}", l) for l in LANGS}
    for l in LANGS:
        if not rs[l]:
            gaps.append((nid, l, f"no ACTIVE SERVICES row S-{l.upper()}-{num}"))
    add(nid, parent, "answer", label, {l: rs[l]["description"] for l in LANGS if rs[l]}, follow,
        src(*rs.values()), origin="kb+ui-label")


svc_leaf("classes_tech", "classes", 6,
         {"ar": "ما الأجهزة والتقنية المطلوبة للحصص؟", "en": "What equipment and technology do lessons require?",
          "fr": "De quel équipement a-t-on besoin pour les cours ?"},
         ["classes_duration", "trial", "register"])
fb = {l: by(FB, "scenario", "unconfirmed_booking", l) for l in LANGS}
for l in LANGS:
    if not fb[l]:
        gaps.append(("classes_booking", l, "no ACTIVE FALLBACKS unconfirmed_booking row"))
add("classes_booking", "classes", "answer",
    {"ar": "هل الموعد والمدرس مؤكدان؟", "en": "Are the tutor and lesson time confirmed?", "fr": "Le tuteur et l’horaire sont-ils confirmés ?"},
    {l: fb[l]["message"] for l in LANGS if fb[l]},
    [{"to": "register", "preset": {"request": "CALLBACK"}}, "classes_matching", "policy_reschedule"], src(*fb.values()), origin="kb+ui-label")
faq_leaf("classes_certificates", "help", "certificates", ["followup_updates", "register"])
svc_leaf("followup_assessment", "help", 2,
         {"ar": "هل يوجد تقييم للطالب؟", "en": "Is the student assessed?", "fr": "L’élève est-il évalué ?"},
         ["followup_updates", "trial", "register"])
svc_leaf("followup_updates", "help", 5,
         {"ar": "كيف يتابع ولي الأمر تقدم الطالب؟", "en": "How can parents follow the student’s progress?", "fr": "Comment les parents suivent-ils les progrès de l’élève ?"},
         ["followup_assessment", "classes_certificates", "register"])
add("help", "root", "menu", MAIN[5][1],
    {"ar": "اختر ما يهمّك.", "en": "Choose what matters to you.", "fr": "Choisissez ce qui vous intéresse."},
    ["classes_tailored", "followup_assessment", "about_mentoring", "about_exam", "followup_updates", "concern_tried"], [], origin="ui")
add("classes", "root", "menu", MAIN[4][1],
    {"ar": "اختر ما تريد معرفته.", "en": "Choose what you want to know.", "fr": "Choisissez ce que vous voulez savoir."},
    ["classes_duration", "classes_frequency", "classes_homework", "classes_matching", "classes_tech", "classes_booking"], [], origin="ui")

svc_leaf("about_exam", "help", 4,
         {"ar": "هل تقدمون التحضير للاختبارات؟", "en": "Do you help with exam preparation?", "fr": "Aidez-vous à préparer les examens ?"},
         ["subjects", "trial", "register"])
svc_leaf("about_mentoring", "help", 3,
         {"ar": "هل تقدمون إرشاداً أكاديمياً وتنظيماً للدراسة؟", "en": "Do you offer academic mentoring and study organization?",
          "fr": "Offrez-vous du mentorat scolaire et de l’aide à l’organisation ?"},
         ["subjects", "trial", "register"])


def nur_leaf(nid, parent, key, label, follow):
    r = next((x for x in NUR if x["nurture_key"] == key), None)
    txt = {l: r[f"fact_{l}"] for l in LANGS if r and r.get(f"fact_{l}")}
    for l in LANGS:
        if l not in txt:
            gaps.append((nid, l, f"no ACTIVE SALES_NURTURE '{key}' text"))
    add(nid, parent, "answer", label, txt, follow, src(r), origin="kb+ui-label")


nur_leaf("classes_tutor", "classes", "objection.tutor.tutor_experience",
         {"ar": "ما الخبرة التي تراعونها في المدرسين؟", "en": "What tutor experience do you look for?", "fr": "Quelle expérience recherchez-vous chez les tuteurs ?"},
         ["classes_matching", "trial", "register"])
nur_leaf("classes_tailored", "help", "personalized_assessment",
         {"ar": "كيف تُصمَّم الحصص لتناسب الطالب؟", "en": "How are lessons tailored to each student?", "fr": "Comment les cours sont-ils adaptés à chaque élève ?"},
         ["followup_assessment", "trial", "register"])
# pricing leaves point to the frequency answer (cross-link)
for n in pk:
    for c in ("ca", "us"):
        nodes[f"price_{c}_{n}"]["options"][0] = "classes_frequency"

# ---------------------------------------------------------------- policies
POL_LABEL = {
    "cancellation": {"ar": "ما سياسة الإلغاء؟", "en": "What is the cancellation policy?", "fr": "Quelle est la politique d’annulation ?"},
    "absence": {"ar": "ماذا يحدث عند الغياب؟", "en": "What happens if a lesson is missed?", "fr": "Que se passe-t-il en cas d’absence ?"},
    "minimum": {"ar": "ما الحد الأدنى للحصص؟", "en": "What is the minimum number of lessons?", "fr": "Quel est le nombre minimum de cours ?"},
    "refund": {"ar": "ماذا لو لم يناسبنا المدرس أو الخدمة؟", "en": "What if the tutor or service is not a good fit?", "fr": "Et si le tuteur ou le service ne convient pas ?"},
}
pids = []
for k in ("cancellation", "absence", "minimum", "refund"):
    rs = {l: pol(k, l) for l in LANGS}
    nid = "policy_" + k
    pids.append(nid)
    add(nid, "policies", "answer", POL_LABEL[k], {l: rs[l]["customer_answer"] for l in LANGS if rs[l]},
        [o for o in ["policy_absence", "policy_minimum", "policy_refund", "policy_cancellation"] if o != nid][:2] + ["register"],
        src(*rs.values()), origin="kb+ui-label")
# reschedule: the approved cancellation rule also covers rescheduling, so the same ACTIVE rows answer it directly
rs = {l: pol("cancellation", l) for l in LANGS}
add("policy_reschedule", "policies", "answer",
    {"ar": "كيف أغيّر موعد حصة؟", "en": "How do I reschedule a lesson?", "fr": "Comment déplacer un cours ?"},
    {l: rs[l]["customer_answer"] for l in LANGS if rs[l]},
    ["policy_absence", "classes_booking", {"to": "register", "preset": {"request": "CALLBACK"}}], src(*rs.values()), origin="kb+ui-label")
pids.insert(1, "policy_reschedule")
add("policies", "root", "menu", MAIN[6][1],
    {"ar": "اختر ما تريد معرفته.", "en": "Choose what you want to know.", "fr": "Choisissez ce que vous voulez savoir."},
    pids, [], origin="ui")

# ---------------------------------------------------------------- concerns (approved OBJECTIONS; #6 excluded)
cids = []
for n in range(1, 6):
    rs = {l: next((o for o in OBJ if o["objection_id"] == f"O-{l.upper()}-{n}"), None) for l in LANGS}
    nid = f"concern_{['','price','online','tried','patient','timing'][n]}"
    cids.append(nid)
    add(nid, "concerns", "answer", {l: rs[l]["objection"] for l in LANGS if rs[l]},
        {l: rs[l]["approved_response"] for l in LANGS if rs[l]},
        [{"to": "pricing"}, {"to": "trial"}, {"to": "register"}] if n == 1 else [{"to": "trial"}, {"to": "register"}],
        src(*rs.values()))
excluded_note.append(("O-AR/EN/FR-6", "'I need time to think' promises to send a summary; the tree cannot send one, so it is not offered"))
# approved SALES_NURTURE texts for the two most common online worries (focus is a real-traffic theme)
nur_leaf("concern_focus", "concerns", "objection.online.focus_concern",
         {"ar": "ماذا لو كان طفلي لا يركّز في الدروس أونلاين؟", "en": "What if my child cannot focus in online lessons?",
          "fr": "Et si mon enfant n’arrive pas à se concentrer en ligne ?"},
         ["concern_inperson", "trial", "register"])
nur_leaf("concern_inperson", "concerns", "objection.online.in_person_preference",
         {"ar": "ماذا لو كنا نفضّل الدروس الحضورية؟", "en": "What if we prefer in-person lessons?", "fr": "Et si nous préférons les cours en présentiel ?"},
         ["concern_focus", "trial", "register"])
nodes["concern_online"]["options"] = [{"to": "concern_focus"}, {"to": "concern_inperson"}, {"to": "trial"}, {"to": "register"}]
cids = [c for c in cids if c != "concern_tried"]   # reachable from "How do you help my child?" and listed here too
cids = ["concern_price", "concern_online", "concern_focus", "concern_tried", "concern_patient", "concern_timing"]
add("concerns", "root", "menu", MAIN[7][1],
    {"ar": "ما الذي يقلقكم؟", "en": "What is on your mind?", "fr": "Qu’est-ce qui vous préoccupe ?"}, cids, [], origin="ui")

# where do you serve (location.ask, INT-004): composed from the country-level LOCATIONS rows
LOCS = rows("LOCATIONS")
def loc_country(country, lang):
    return next((r["service_note"] for r in LOCS if r.get("country") == country and str(r.get("language")).lower() == lang
                 and not r.get("city") and (not r.get("region") or r.get("region") == lang)), None)
wtxt = {}
for l in LANGS:
    a, b = loc_country("Canada", l), loc_country("United States", l)
    if a and b:
        wtxt[l] = a + " " + b
        composed.append(("about_where", l, "two verbatim country-level LOCATIONS rows (Canada + United States) joined"))
    else:
        gaps.append(("about_where", l, "no ACTIVE country-level LOCATIONS rows in this language"))
add("about_where", "about", "answer",
    {"ar": "هل تخدمون بلدي أو مدينتي؟", "en": "Do you serve my country or city?", "fr": "Servez-vous mon pays ou ma ville ?"},
    wtxt, ["pricing", "trial", "register"], [], origin="composed")

# ---------------------------------------------------------------- register + human
add("register", "root", "form", MAIN[8][1],
    {"ar": "سنجمع بضع معلومات بسيطة، خطوة بخطوة، ثم تراجعونها قبل الإرسال.",
     "en": "We will collect a few details, one step at a time, and you review them before sending.",
     "fr": "Nous allons recueillir quelques informations, étape par étape, et vous les vérifiez avant l’envoi."},
    [], [], origin="ui")

email = com("contact", "ar")   # COM-005 (email value)
phone = com("contact", "en")   # COM-009 (phone value)
LBL = {"ar": ("البريد الإلكتروني", "الهاتف"), "en": ("Email", "Phone"), "fr": ("Courriel", "Téléphone")}
htxt = {l: f"{LBL[l][0]}: {email['content']}\n{LBL[l][1]}: {phone['content']}" for l in LANGS}
for l in LANGS:
    composed.append(("human", l, "contact lines assembled from COM-005 (email) and COM-009 (phone)"))
add("human", "root", "answer", UI["human"], htxt,
    [{"to": "register", "preset": {"request": "CALLBACK"}}], src(email, phone), origin="composed",
    persistent=True)

# ---------------------------------------------------------------- every title is a question (interface wording, not facts)
QLABEL = {
    "about": {"ar": "من أنتم وما الخدمات التي تقدمونها؟", "en": "Who are you and what do you offer?", "fr": "Qui êtes-vous et que proposez-vous ?"},
    "subjects": {"ar": "ما المواد والصفوف التي تدرّسونها؟", "en": "Which subjects and grades do you teach?", "fr": "Quelles matières et quels niveaux enseignez-vous ?"},
    "pricing": {"ar": "ما الأسعار والباقات المتاحة؟", "en": "What prices and packages are available?", "fr": "Quels sont les tarifs et forfaits disponibles ?"},
    "trial": {"ar": "كيف أحصل على الحصة التجريبية المجانية؟", "en": "How do I get the free trial lesson?", "fr": "Comment obtenir l’essai gratuit ?"},
    "classes": {"ar": "كيف تسير الحصص؟", "en": "How do lessons work?", "fr": "Comment se déroulent les cours ?"},
    "help": {"ar": "كيف تساعدون ابني على التحسّن وكيف تتابعون تقدمه؟", "en": "How do you help my child improve and track progress?", "fr": "Comment aidez-vous mon enfant à progresser et suivez-vous ses progrès ?"},
    "policies": {"ar": "كيف يمكن الإلغاء أو تغيير الموعد أو استرداد المبلغ؟", "en": "How can I cancel, reschedule or ask for a refund?", "fr": "Comment annuler, déplacer un cours ou demander un remboursement ?"},
    "concerns": {"ar": "ماذا لو كان لديّ تحفظ أو قلق؟", "en": "What if I have a concern?", "fr": "Et si j’ai une réserve ou une inquiétude ?"},
    "register": {"ar": "كيف أسجّل الآن؟", "en": "How do I register now?", "fr": "Comment m’inscrire maintenant ?"},
    "human": {"ar": "مع من أتواصل وكيف؟", "en": "Who can I contact, and how?", "fr": "Qui contacter et comment ?"},
    "price_ca": {"ar": "كم الأسعار في كندا؟", "en": "What are the prices in Canada?", "fr": "Quels sont les tarifs au Canada ?"},
    "price_us": {"ar": "كم الأسعار في الولايات المتحدة؟", "en": "What are the prices in the United States?", "fr": "Quels sont les tarifs aux États-Unis ?"},
    "concern_price": {"ar": "ماذا لو كان السعر مرتفعاً علينا؟", "en": "What if the price is too high for us?", "fr": "Et si le prix est trop élevé pour nous ?"},
    "concern_tried": {"ar": "ماذا لو جرّبنا مدرساً ولم يتحسن الطالب؟", "en": "What if we tried a tutor before and saw no improvement?", "fr": "Et si nous avons déjà essayé un tuteur sans amélioration ?"},
    "concern_patient": {"ar": "هل لديكم مدرس صبور يناسب طفلنا؟", "en": "Do you have a patient tutor for my child?", "fr": "Avez-vous un tuteur patient pour mon enfant ?"},
    "concern_timing": {"ar": "ماذا لو كان الوقت غير مناسب لنا؟", "en": "What if the timing does not work for us?", "fr": "Et si l’horaire ne nous convient pas ?"},
}
for c in ("ca", "us"):
    for n in sorted(pk):
        QLABEL[f"price_{c}_{n}"] = {"ar": f"كم سعر باقة {n} {'حصة' if n == 12 else 'حصص'}؟", "en": f"How much is the {n}-lesson package?",
                                   "fr": f"Combien coûte le forfait de {n} cours ?"}
SUB_Q = {"en": lambda n: f"Do you teach {n}?",
         "fr": lambda n: "Enseignez-vous " + {"Anglais": "l’anglais", "Physique": "la physique"}.get(n, n) + " ?"}
for nid in sub_ids:
    lab = nodes[nid]["label"]
    q = {"ar": f"هل تدرّسون {lab['ar']}؟"}
    for l in ("en", "fr"):
        if l in lab:
            q[l] = SUB_Q[l](lab[l])
    QLABEL[nid] = q
for nid, q in QLABEL.items():
    nodes[nid]["label"] = q
    if nodes[nid]["origin"] == "kb":
        nodes[nid]["origin"] = "kb+ui-label"

# ---------------------------------------------------------------- finish: normalise options, verify
for n in list(nodes.values()):
    norm = []
    for o in n["options"]:
        if isinstance(o, str):
            o = {"to": o}
        norm.append(o)
    n["options"] = norm

# register form schema (mirrors the R1 validator in Validated_Human_Handoff_FIXED.json)
TZ = {
    "ca": [("America/St_Johns", {"ar": "نيوفاوندلاند", "en": "Newfoundland", "fr": "Terre-Neuve"}),
           ("America/Halifax", {"ar": "الأطلسي (هاليفاكس)", "en": "Atlantic (Halifax)", "fr": "Atlantique (Halifax)"}),
           ("America/Toronto", {"ar": "الشرقي (تورنتو)", "en": "Eastern (Toronto)", "fr": "Est (Toronto)"}),
           ("America/Winnipeg", {"ar": "الأوسط (وينيبيغ)", "en": "Central (Winnipeg)", "fr": "Centre (Winnipeg)"}),
           ("America/Regina", {"ar": "ساسكاتشوان (ريجينا)", "en": "Saskatchewan (Regina)", "fr": "Saskatchewan (Regina)"}),
           ("America/Edmonton", {"ar": "الجبلي (إدمنتون)", "en": "Mountain (Edmonton)", "fr": "Montagnes (Edmonton)"}),
           ("America/Vancouver", {"ar": "الهادئ (فانكوفر)", "en": "Pacific (Vancouver)", "fr": "Pacifique (Vancouver)"})],
    "us": [("America/New_York", {"ar": "الشرقي (نيويورك)", "en": "Eastern (New York)", "fr": "Est (New York)"}),
           ("America/Chicago", {"ar": "الأوسط (شيكاغو)", "en": "Central (Chicago)", "fr": "Centre (Chicago)"}),
           ("America/Denver", {"ar": "الجبلي (دنفر)", "en": "Mountain (Denver)", "fr": "Montagnes (Denver)"}),
           ("America/Phoenix", {"ar": "أريزونا (فينيكس)", "en": "Arizona (Phoenix)", "fr": "Arizona (Phoenix)"}),
           ("America/Los_Angeles", {"ar": "الهادئ (لوس أنجلوس)", "en": "Pacific (Los Angeles)", "fr": "Pacifique (Los Angeles)"}),
           ("America/Anchorage", {"ar": "ألاسكا", "en": "Alaska", "fr": "Alaska"})],
}
REGISTER = {
    "request_types": [("FREE_TRIAL", {"ar": "حصة تجريبية مجانية", "en": "Free trial lesson", "fr": "Essai gratuit"}),
                      ("ENROLLMENT", {"ar": "تسجيل", "en": "Registration", "fr": "Inscription"}),
                      ("CONSULTATION", {"ar": "استشارة", "en": "Consultation", "fr": "Consultation"}),
                      ("CALLBACK", {"ar": "اتصال هاتفي", "en": "Phone call back", "fr": "Rappel téléphonique"})],
    "countries": [("Canada", "ca", CO["ca"]), ("United States", "us", CO["us"])],
    "timezones": {k: [(v, l) for v, l in lst] for k, lst in TZ.items()},
    "languages": [("Arabic", {"ar": "العربية", "en": "Arabic", "fr": "Arabe"}),
                  ("English", {"ar": "الإنجليزية", "en": "English", "fr": "Anglais"}),
                  ("French", {"ar": "الفرنسية", "en": "French", "fr": "Français"})],
    "grades": list(range(1, 13)),
    "confirmation_phrase": {"ar": "أؤكد صحة البيانات وأوافق على مشاركتها والتواصل معي",
                            "en": "I confirm the details are correct and consent to sharing them and being contacted",
                            "fr": "Je confirme que les informations sont correctes et j'accepte de les partager et d'être contacté"},
    "backend_contract": "Validated_Human_Handoff_FIXED.json / Validate Lead Payload (workflow swhmNa0Goo0uYm1k)",
}

tree = dict(meta=dict(source=KB.split("/")[-1], note="Built from the 2026-08-18 KB snapshot; live sheet re-verified 2026-11-12: content tabs identical to this snapshot.",
                      langs=LANGS), ui=UI, nodes=nodes, register=REGISTER)

# ---------------------------------------------------------------- integrity checks
errs = []
for nid, n in nodes.items():
    if n["parent"] and n["parent"] not in nodes:
        errs.append(f"{nid}: missing parent {n['parent']}")
    for o in n["options"]:
        if o["to"] not in nodes:
            errs.append(f"{nid}: option -> missing {o['to']}")
for nid, n in nodes.items():
    for o in n["options"]:
        pass
reach, stack = set(), ["root"]
while stack:
    x = stack.pop()
    if x in reach: continue
    reach.add(x)
    stack += [o["to"] for o in nodes[x]["options"]]
orph = [n for n in nodes if n not in reach and not nodes[n].get("persistent")]
if orph: errs.append(f"unreachable nodes: {orph}")
bad = [s for n in nodes.values() for s in n["sources"] if s in EXCLUDED]
if bad: errs.append(f"excluded records used: {bad}")
if errs:
    print("INTEGRITY ERRORS:"); [print(" ", e) for e in errs]; sys.exit(1)

json.dump(tree, open(f"{OUT}/tree.json", "w"), ensure_ascii=False, indent=1)

# ---------------------------------------------------------------- report
cov = collections.OrderedDict()
for nid, n in nodes.items():
    cov[nid] = {l: (l in n["text"] or n["kind"] == "form") and (l in n["label"] or nid == "root") for l in LANGS}
lines = ["# Tree build report", "",
         f"Source: {tree['meta']['source']}", f"Nodes: {len(nodes)}  |  KB records used: {len(used_sources)}", "",
         "## Excluded from customers", *[f"- {k}: {v}" for k, v in EXCLUDED.items()],
         *[f"- {k}: {v}" for k, v in excluded_note], "",
         "## Composed text that needs owner approval"]
seen = set()
for n, l, why in composed:
    if (n, why) in seen: continue
    seen.add((n, why)); lines.append(f"- {n} ({why})")
lines += ["", "## Language gaps (node hidden in that language until approved text exists)"]
bylang = collections.defaultdict(list)
for n, l, why in gaps: bylang[l].append(f"{n}: {why}")
for l in LANGS:
    lines.append(f"### {l}: {len(bylang[l])}")
    lines += [f"- {x}" for x in bylang[l]]
lines += ["", "## Not found in the KB (not invented)",
          "- Payment methods and how to pay", "- Teacher qualifications and vetting", "- Working hours of the team",
          "- EN/FR subject names for French, Arabic and Islamic Studies; FR names for Math, Science, Chemistry"]
open(f"{OUT}/tree_report.md", "w").write("\n".join(lines) + "\n")
print("OK nodes=", len(nodes), "sources=", len(used_sources), "gaps=", len(gaps), "composed=", len(composed))
