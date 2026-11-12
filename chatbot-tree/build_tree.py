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
    ["price_ca", "price_us", "pricing_payment"], [], origin="ui")

# payment methods: stated and approved by the owner in chat on 2026-11-12 (not yet a KB row)
OWNER = "owner-approved in chat 2026-11-12; not yet in the KB sheet"
add("pricing_payment", "pricing", "answer",
    {"ar": "ما طرق الدفع؟", "en": "What payment methods do you accept?", "fr": "Quels moyens de paiement acceptez-vous ?"},
    {"ar": "في كندا: الدفع عبر التحويل بالبريد الإلكتروني (Interac e-Transfer). في الولايات المتحدة: الدفع عبر PayPal أو Stripe.",
     "en": "In Canada: payment by email money transfer (Interac e-Transfer). In the United States: payment by PayPal or Stripe.",
     "fr": "Au Canada : paiement par virement par courriel (Interac e-Transfer). Aux États-Unis : paiement par PayPal ou Stripe."},
    ["price_ca", "price_us", {"to": "register", "preset": {"request": "CALLBACK"}}], [], origin="owner")
for l in LANGS:
    composed.append(("pricing_payment", l, OWNER))

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
    {"ar": "نفهم أن لكل طفل احتياجاً مختلفاً. اختر ما يصف حالة ابنك وسنوضح كيف نساعده.",
     "en": "We understand every child is different. Choose what describes your child and we will explain how we help.",
     "fr": "Chaque enfant est différent. Choisissez ce qui décrit votre enfant et nous expliquerons comment nous l’aidons."},
    ["help_struggle", "concern_focus", "help_motivation", "help_quality", "help_exams", "help_change", "followup_updates"], [], origin="ui")

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
# owner-stated approach (chat 2026-11-12): specialised tutors, patience, professionalism, progress tracking, appreciation, homework
HELP_TXT = {
    "struggle": {"ar": "نبدأ بفهم صف الطالب ومستواه، ثم يعمل معه مدرس متخصص بصبر وحرفية على نقاط ضعفه، مع واجب بعد الحصة ومتابعة لتقدمه وتقدير لكل تحسّن.",
                 "en": "We start by understanding the student’s grade and level, then a specialised tutor works with them patiently and professionally on their weak points, with homework after the lesson, progress follow-up and recognition of every improvement.",
                 "fr": "Nous commençons par comprendre le niveau de l’élève, puis un tuteur spécialisé travaille avec lui, avec patience et professionnalisme, sur ses points faibles, avec des devoirs après le cours, un suivi des progrès et une reconnaissance de chaque amélioration."},
    "motivation": {"ar": "لدينا مدرسون متخصصون يتعاملون بصبر وحرفية مع الطالب قليل الدافعية، فيشجعونه ويقدّرون تقدمه ويعطونه واجباً مناسباً بعد الحصة ليبقى مستمراً.",
                   "en": "We have specialised tutors who work patiently and professionally with students who lack motivation: they encourage the student, recognise progress and give suitable homework after each lesson to keep them going.",
                   "fr": "Nos tuteurs spécialisés travaillent avec patience et professionnalisme avec les élèves peu motivés : ils les encouragent, reconnaissent leurs progrès et donnent des devoirs adaptés après chaque cours pour maintenir l’élan."},
    "tutors": {"ar": "لدينا مدرسون متخصصون يتعاملون مع الطلاب بصبر وحرفية، ويتابعون تقدمهم ويقدّرون جهدهم، ويعطون واجباً بعد الحصة حسب الحاجة.",
               "en": "We have specialised tutors who work with students patiently and professionally, follow their progress, recognise their effort and give homework after the lesson as needed.",
               "fr": "Nos tuteurs sont spécialisés et travaillent avec les élèves avec patience et professionnalisme, suivent leurs progrès, reconnaissent leurs efforts et donnent des devoirs après le cours selon les besoins."},
}
HELP_LBL = {
    "struggle": {"ar": "ابني ضعيف أو يواجه صعوبة دراسية، كيف تساعدونه؟", "en": "My child is struggling at school. How do you help?", "fr": "Mon enfant a des difficultés scolaires. Comment l’aidez-vous ?"},
    "motivation": {"ar": "ابني قليل الدافعية، كيف تتعاملون معه؟", "en": "My child lacks motivation. How do you handle that?", "fr": "Mon enfant manque de motivation. Comment réagissez-vous ?"},
    "tutors": {"ar": "من هم المدرسون الذين سيتعاملون مع ابني؟", "en": "Who are the tutors who will work with my child?", "fr": "Qui sont les tuteurs qui travailleront avec mon enfant ?"},
}
HELP_FOLLOW = {"struggle": ["followup_assessment", "classes_tailored", "help_exams", "trial"],
               "motivation": ["concern_patient", "concern_tried", "trial", "register"],
               "tutors": ["classes_matching", "classes_tutor", "help_quality", "register"]}
for k in ("struggle", "motivation", "tutors"):
    add("help_" + k, "help", "answer", HELP_LBL[k], HELP_TXT[k], HELP_FOLLOW[k], [], origin="owner")
    for l in LANGS:
        composed.append(("help_" + k, l, OWNER))
# owner-stated quality assurance (chat 2026-11-12): comfort, liking the tutor, tutor change, quality supervisor, grades, real exams
QA_NODES = {
 "help_quality": (
  {"ar": "إزاي بتتأكدوا إن ابني مرتاح وبيتقدّم؟", "en": "How do you make sure my child is comfortable and progressing?", "fr": "Comment vous assurez-vous que mon enfant est à l’aise et progresse ?"},
  {"ar": "عندنا مراقب جودة بيتابع الحصص وبيتابع علامات الطالب. وبنتأكد إن الطالب مرتاح مع المدرّس وبيحبه، وإنه بيتقدّم فعلاً، ولو مش مرتاح بنقدر نغيّر المدرّس.",
   "en": "We have a quality supervisor who follows the lessons and tracks the student’s grades. We make sure the student is comfortable with the tutor and likes them, and that they are really progressing; if not, we can change the tutor.",
   "fr": "Nous avons un responsable qualité qui suit les cours et les notes de l’élève. Nous veillons à ce que l’élève soit à l’aise avec le tuteur et l’apprécie, et qu’il progresse réellement ; sinon, nous pouvons changer de tuteur."},
  ["help_change", "help_exams", "help_tutors", "trial"]),
 "help_change": (
  {"ar": "ينفع نغيّر المدرّس؟", "en": "Can we change the tutor?", "fr": "Peut-on changer de tuteur ?"},
  {"ar": "أيوه، لو الطالب مش مرتاح مع المدرّس أو مش بيحبه، إحنا بنقدر نغيّر المدرّس.",
   "en": "Yes. If the student is not comfortable with the tutor or does not like them, we can change the tutor.",
   "fr": "Oui. Si l’élève n’est pas à l’aise avec le tuteur ou ne l’apprécie pas, nous pouvons changer de tuteur."},
  ["policy_refund", "classes_matching", "trial", "register"]),
 "help_exams": (
  {"ar": "بتعملوا امتحانات لابني؟", "en": "Do you give my child exams?", "fr": "Donnez-vous des examens à mon enfant ?"},
  {"ar": "أيوه، بنتأكد إن الطالب بيتقدّم، وبنعمل له امتحانات حقيقية وأسئلة صعبة عشان يبقى جاهز للمدرسة ونساعده يتحسّن مستواه.",
   "en": "Yes. We make sure the student is progressing, and we give them real exams and challenging questions so they are ready for school and we help improve their level.",
   "fr": "Oui. Nous veillons à ce que l’élève progresse et nous lui proposons de vrais examens et des questions difficiles pour qu’il soit prêt pour l’école et que nous l’aidions à améliorer son niveau."},
  ["about_exam", "about_mentoring", "trial", "register"]),
}
for _k, (_lab, _txt, _fol) in QA_NODES.items():
    add(_k, "help", "answer", _lab, _txt, _fol, [], origin="owner")
    for l in LANGS:
        composed.append((_k, l, OWNER))
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
PH = "\u2066" + phone["content"] + "\u2069"   # isolate the number so it keeps its order inside Arabic text
WA = "https://wa.me/" + re.sub(r"\D", "", phone["content"])   # WhatsApp link built from the approved phone number
htxt = {
 "ar": f"تقدر تتواصل معانا على الواتساب على الرقم {PH}. فريق خدمة العملاء والدعم الفني والعمليات ممكن يحجزلك حصة ويجاوب على كل أسئلتك.\n"
       f"تحب تكلّم خدمة العملاء مباشرة؟ دوس على الرابط:\n{WA}\n"
       "ولو عندك تفاصيل عايز تشاركها، زي واجب أو أوراق عمل أو تمارين، أو عايز تحكي عن احتياجات طفلك، أو تغيّر المدرّس، أو عندك شكوى، أو عايز تعدّل أو تأجّل ميعاد، تقدر تتواصل معانا كتابةً أو بمكالمة على الواتساب.\n"
       f"{LBL['ar'][0]}: {email['content']}",
 "en": f"You can reach us on WhatsApp at {phone['content']}. Our customer service, technical support and operations team can book a lesson for you and answer all your questions.\n"
       f"To chat with customer service directly, use this link:\n{WA}\n"
       "If you have details to share, such as homework, worksheets or exercises, or you want to tell us more about your child’s needs, change the tutor, make a complaint, or change or postpone a lesson, you can contact us by text or by phone call on WhatsApp.\n"
       f"{LBL['en'][0]}: {email['content']}",
 "fr": f"Vous pouvez nous joindre sur WhatsApp au {phone['content']}. Notre équipe du service client, du support technique et des opérations peut réserver un cours pour vous et répondre à toutes vos questions.\n"
       f"Pour discuter directement avec le service client, utilisez ce lien :\n{WA}\n"
       "Si vous avez des informations à partager, comme des devoirs, des fiches de travail ou des exercices, ou si vous voulez nous parler des besoins de votre enfant, changer de tuteur, faire une réclamation ou modifier ou reporter un cours, vous pouvez nous contacter par message ou par appel sur WhatsApp.\n"
       f"{LBL['fr'][0]} : {email['content']}",
}
for l in LANGS:
    composed.append(("human", l, "WhatsApp contact text stated by the owner 2026-11-12; email line from COM-005; wa.me link built from COM-009"))
add("human", "root", "answer", UI["human"], htxt,
    [{"to": "register", "preset": {"request": "CALLBACK"}}], src(email, phone), origin="composed",
    persistent=True)

# ---------------------------------------------------------------- Arabic answers in Egyptian dialect, first-person voice (owner instruction 2026-11-12)
# Wording only: every fact, number and rule is unchanged from the approved text. Needs owner review of the dialect.
AR_EG = {
 "root": "أهلاً بيكم في Success Path Mentors. اختار اللي يهمّك وإحنا نوضّحلك.",
 "about": "إحنا بنقدّم دروس خصوصية فردية أونلاين لطلاب من الصف الأول لحد الصف الثاني عشر.",
 "about_online": "أيوه، كل الدروس عندنا فردية وبتتقدّم أونلاين.",
 "about_grades": "إحنا بنخدم الطلاب من الصف الأول لحد الصف الثاني عشر.",
 "about_curriculum": "إحنا بنقدّم دعم متوافق مع المناهج الكندية والأمريكية، على حسب صف الطالب واحتياجه.",
 "sub_001": "إحنا بنقدّم دروس رياضيات فردية أونلاين.",
 "sub_002": "إحنا بنقدّم دروس لغة إنجليزية فردية أونلاين.",
 "sub_003": "إحنا بنقدّم دروس علوم فردية على حسب الصف والمنهج.",
 "sub_004_ontario": "أيوه. إحنا في Success Path Mentors بندعم مادة الفيزياء للصف الحادي عشر على منهج أونتاريو في كندا. وبنقدر نظبّط الدروس مع منهج أونتاريو ومواد الطالب في المدرسة وواجباته واحتياجاته التعليمية. وبنختار المدرّس على حسب المادة والصف والمنهج واللغة واحتياجات الطالب، وبنأكّد إن المدرّس متاح قبل ما نعتمد الاختيار.",
 "sub_004": "إحنا بنقدّم دروس فيزياء فردية أونلاين للصفوف 9–12. وبندعم فيزياء الصف الحادي عشر على منهج أونتاريو في كندا، وبنقدر نظبّط الدروس مع منهج الطالب ومواد المدرسة والواجبات واحتياجاته التعليمية. وبنختار المدرّس على حسب المادة والصف والمنهج واللغة واحتياجات الطالب، وبنأكّد إن المدرّس متاح قبل ما نعتمد الاختيار.",
 "sub_005": "إحنا بنقدّم دروس كيمياء فردية لطلاب المرحلة الثانوية.",
 "sub_006": "إحنا بنقدّم دروس لغة فرنسية فردية أونلاين.",
 "sub_007": "إحنا بنقدّم دروس لغة عربية فردية أونلاين.",
 "sub_008": "إحنا بنقدّم دروس فردية في الدراسات الإسلامية.",
 "subjects": "اختار المادة اللي تهمّك.",
 "price_ca": "اختار الباقة.", "price_us": "اختار الباقة.",
 "price_ca_4": "إحنا بنقدّم باقة 4 حصص بسعر 110 دولار كندي (CAD).",
 "price_ca_8": "إحنا بنقدّم باقة 8 حصص بسعر 220 دولار كندي (CAD).",
 "price_ca_12": "إحنا بنقدّم باقة 12 حصة بسعر 280 دولار كندي (CAD).",
 "price_us_4": "إحنا بنقدّم باقة 4 حصص بسعر 110 دولار أمريكي (USD).",
 "price_us_8": "إحنا بنقدّم باقة 8 حصص بسعر 220 دولار أمريكي (USD).",
 "price_us_12": "إحنا بنقدّم باقة 12 حصة بسعر 280 دولار أمريكي (USD).",
 "pricing": "الطالب مقيم فين؟ سعر الباقة بيختلف على حسب البلد.",
 "pricing_payment": "بالنسبة للدفع: في كندا إحنا بنستقبل الدفع بالتحويل عن طريق الإيميل (Interac e-Transfer). وفي أمريكا بنستقبل الدفع عن طريق PayPal أو Stripe.",
 "trial": "أيوه، إحنا بنقدّم حصة تجريبية مجانية لكل طالب جديد ولكل مادة جديدة. الحصة دي بتساعدنا نفهم مستوى الطالب واحتياجاته ومدى ملاءمة المدرّس. وبننسّق الميعاد على حسب مواعيد الطالب والمدرّس.",
 "classes_duration": "الحصة عندنا مدتها 60 دقيقة.",
 "classes_frequency": "إحنا عادةً بننصح بحصة لحصتين في الأسبوع على حسب احتياج الطالب، والحد الأدنى حصة واحدة في الأسبوع عشان نحافظ على الاستمرارية.",
 "classes_homework": "المدرّس بيدّي الطالب واجب أو تدريب بعد كل حصة على حسب الحاجة، عشان نثبّت التعلّم ونتابع النقط اللي اتشرحت.",
 "classes_matching": "إحنا بنختار المدرّس على حسب المادة والصف والمنهج واحتياجات الطالب واللغة المفضلة، وبعدين بنأكّد التوفّر.",
 "classes_tech": "الحصص بتتعمل أساساً على Google Meet. وتقدر تستخدم كمبيوتر أو لابتوب أو تابلت أو موبايل، والأفضل شاشة أكبر زي اللابتوب أو الكمبيوتر، مع اتصال إنترنت ثابت.",
 "classes_booking": "الميعاد أو توفّر المدرّس محتاج تأكيد من الفريق عندنا. ابعتلنا اليوم والوقت والمنطقة الزمنية المناسبة ليك.",
 "classes_certificates": "إحنا حالياً مبنقدّمش شهادة رسمية بعد عدد معيّن من الحصص. لكن الفريق ممكن يوفّر تقرير عن تقدّم الطالب لو طلبته.",
 "followup_assessment": "إحنا بنعمل تقييم أولي مجاني عشان نفهم المستوى والفجوات والتحديات، مع حصة تجريبية مجانية لكل طالب جديد ولكل مادة جديدة. وبعد حوالي 4–6 حصص ممكن نعمل تقييم متابعة عشان نقيس التقدّم ونديّ ولي الأمر ملاحظاتنا.",
 "followup_updates": "إحنا بنقدّم تحديثات أسبوعية من المدرّس عن التحديات والفجوات والإنجازات والخطة والخطوات الجاية، مع إمكانية تقييم متابعة بعد حوالي 4–6 حصص ومشاركة الملاحظات مع ولي الأمر.",
 "help": "إحنا فاهمين إن كل طفل ليه احتياجه. اختار اللي يوصف حالة ابنك، وإحنا نوضّحلك بنساعده إزاي.",
 "classes": "اختار اللي عايز تعرفه.",
 "about_exam": "إحنا بنقدّم مراجعة موجّهة على حسب المنهج والفجوات ونوع التقييم.",
 "about_mentoring": "إحنا بنساعد في تنظيم الدراسة وتحديد الأهداف وبناء العادات ومتابعة التقدّم.",
 "classes_tutor": "إحنا فاهمين أهمية خبرة المدرّس. بنراعي الخبرة المناسبة للمادة والصف والمنهج واحتياجات الطالب، وبعدين الفريق بيأكّد المدرّس المتاح.",
 "classes_tailored": "إحنا بنبدأ بفهم صف الطالب ومستواه الحالي، عشان التوصية تبقى مناسبة لاحتياجاته الدراسية.",
 "help_struggle": "خليني أوضّحلك إحنا بنعمل إيه: بنبدأ نفهم صف الطالب ومستواه، وبعدين مدرّس متخصص بيشتغل معاه بصبر وحرفية على نقط ضعفه، مع واجب بعد الحصة ومتابعة لتقدّمه وتقدير لكل تحسّن بيحصل.",
 "help_motivation": "عندنا مدرّسين متخصصين بيتعاملوا بصبر وحرفية مع الطالب اللي دافعيته قليلة؛ بيشجّعوه وبيقدّروا تقدّمه وبيدّوه واجب مناسب بعد الحصة عشان يفضل مستمر.",
 "help_tutors": "عندنا مدرّسين متخصصين بيتعاملوا مع الطلاب بصبر وحرفية، وبيتابعوا تقدّمهم وبيقدّروا مجهودهم، وبيدّوا واجب بعد الحصة على حسب الحاجة.",
 "policy_cancellation": "سياستنا إنه ممكن تلغي حصة واحدة في الأسبوع وتعيد جدولتها في نفس الأسبوع.",
 "policy_reschedule": "سياستنا إنه ممكن تلغي حصة واحدة في الأسبوع وتعيد جدولتها في نفس الأسبوع.",
 "policy_absence": "في سياستنا، الإلغاء أو الغياب التاني في نفس الأسبوع بيتحسب من رصيد الحصص.",
 "policy_minimum": "الحد الأدنى المطلوب عندنا حصة واحدة في الأسبوع.",
 "policy_refund": "إحنا رضاكم وتقدّم الطالب أولويتنا. لو الطالب واجه مشكلة في ملاءمة المدرّس أو أسلوبه أو لهجته، أو حسّ بعدم الارتياح، من فضلك بلّغنا فوراً. هنراجع الحالة، وممكن نقترح تغيير المدرّس، أو حصص إضافية، أو خصم، أو تحويل الرصيد، أو استرداد كلي أو جزئي على حسب الحالة وبعد موافقة الفريق.",
 "policies": "اختار اللي عايز تعرفه.",
 "concern_price": "إحنا فاهمين إن الميزانية مهمة. عندنا باقات بتبدأ من 4 حصص، وبنختار على حسب الهدف من غير التزام زيادة.",
 "concern_online": "الأونلاين بيفيد لما تكون الحصة فردية والخطة مناسبة، مع تدريب ومتابعة.",
 "concern_tried": "إحنا فاهمين تحفّظك؛ بنحدّد سبب التعثّر وبنطابق الطالب مع مدرّس وخطة أنسب.",
 "concern_patient": "إحنا بناخد أسلوب التعلّم والشخصية في الاعتبار وإحنا بنختار المدرّس، وبعدين بنتابع الملاءمة.",
 "concern_timing": "إحنا بنجمع مواعيدكم المناسبة وبنتأكد من التوفّر؛ والميعاد بيبقى نهائي بعد تأكيد الأكاديمية.",
 "concern_focus": "إحنا فاهمين إن التركيز هو التحدي الأساسي. الحصة الفردية بتخلّي المدرّس يتابع طالب واحد بس ويظبّط الإيقاع والأسلوب على حسب استجابته.",
 "concern_inperson": "إحنا فاهمين إنكم بتفضّلوا الدروس الحضورية. حصصنا الفردية أونلاين بتقدّم تفاعل مباشر ومتابعة مخصصة، من غير ما انتباه المدرّس يتوزّع على طلاب تانيين.",
 "concerns": "إيه اللي شاغلك؟",
 "about_where": "إحنا بنقدّم دروس خصوصية أونلاين للطلاب في كندا، وفي الولايات المتحدة كمان.",
 "register": "هنسألك على كام معلومة بسيطة، خطوة خطوة، وبعدين تراجعها قبل ما نبعتها.",
}
for _sid in ("sub_001", "sub_002", "sub_004", "sub_005"):
    AR_EG[_sid + "_strands"] = "خليني أوضّحلك المحاور اللي بنشتغل عليها:\n" + nodes[_sid + "_strands"]["text"]["ar"]
AR_EG["sub_003_strands"] = "خليني أوضّحلك المحاور اللي بنشتغل عليها:\n" + nodes["sub_003_strands"]["text"]["ar"]
for _nid, _t in AR_EG.items():
    nodes[_nid]["text"]["ar"] = _t
    composed.append((_nid, "ar", "Arabic reworded to Egyptian dialect, first-person voice (owner instruction 2026-11-12); facts unchanged, owner to review"))

# owner correction 2026-11-12: updates from the tutor are weekly only (the KB row S-5 still says "daily or weekly" and must be fixed there)
_fu = nodes["followup_updates"]["text"]
_fu["en"] = _fu["en"].replace("Daily or weekly teacher updates", "Weekly teacher updates")
_fu["fr"] = _fu["fr"].replace("Mises à jour quotidiennes ou hebdomadaires du tuteur", "Mises à jour hebdomadaires du tuteur")
composed.append(("followup_updates", "all", "owner correction: weekly updates only; KB row S-5 to be corrected"))

# Arabic UI wording in Egyptian dialect
UI["pick"]["ar"] = "اختار من الاختيارات دي."
UI["back2"]["ar"] = "رجوع مرتين"
UI["fwd"]["ar"] = "قدّام"
UI["you_are_here"]["ar"] = "إنت هنا"
UI["human"]["ar"] = "كلّم الفريق"
UI["related"]["ar"] = "أسئلة ممكن تهمّك"
UI["next_step"]["ar"] = "الخطوة الجاية"
UI["greeting"]["ar"] = AR_EG["root"]

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


# ---------------------------------------------------------------- Arabic titles in Egyptian dialect (owner instruction 2026-11-12); EN/FR unchanged
EG_LABEL = {
 "about": "إنتوا مين وبتقدّموا إيه؟", "about_online": "هي الدروس أونلاين؟", "about_grades": "بتدرّسوا لأنهي صفوف؟",
 "about_where": "بتخدموا بلدي أو مدينتي؟", "about_curriculum": "بتدعموا أنهي مناهج؟",
 "subjects": "بتدرّسوا أنهي مواد وصفوف؟",
 "sub_004_ontario": "بتدعموا فيزياء الصف الحادي عشر على منهج أونتاريو؟",
 "pricing": "إيه الأسعار والباقات المتاحة؟", "price_ca": "الأسعار في كندا كام؟", "price_us": "الأسعار في أمريكا كام؟",
 "pricing_payment": "إيه طرق الدفع؟",
 "trial": "إزاي آخد الحصة التجريبية المجانية؟",
 "classes": "الحصص بتمشي إزاي؟", "classes_duration": "الحصة مدتها قد إيه؟", "classes_frequency": "بتنصحوا بكام حصة في الأسبوع؟",
 "classes_homework": "فيه واجب بعد الحصة؟", "classes_matching": "بتختاروا المدرّس إزاي؟",
 "classes_tech": "إيه الأجهزة والتقنية المطلوبة للحصص؟", "classes_booking": "الميعاد والمدرّس مأكّدين؟",
 "classes_certificates": "الطالب بياخد شهادة رسمية بعد ما يخلّص عشرين حصة؟",
 "classes_tutor": "بتراعوا أنهي خبرة في المدرّسين؟", "classes_tailored": "الحصص بتتظبط إزاي عشان تناسب الطالب؟",
 "followup_assessment": "فيه تقييم للطالب؟", "followup_updates": "ولي الأمر بيتابع تقدّم الطالب إزاي؟",
 "help": "إزاي بتساعدوا ابني يتحسّن وبتتابعوا تقدّمه؟",
 "help_struggle": "ابني ضعيف أو عنده صعوبة في الدراسة، بتساعدوه إزاي؟",
 "help_motivation": "ابني دافعيته قليلة، بتتعاملوا معاه إزاي؟",
 "help_tutors": "مين المدرّسين اللي هيتعاملوا مع ابني؟",
 "about_exam": "بتقدّموا تحضير للامتحانات؟", "about_mentoring": "بتقدّموا إرشاد أكاديمي وتنظيم للمذاكرة؟",
 "policies": "إزاي ألغي أو أغيّر ميعاد أو أسترد فلوسي؟",
 "policy_cancellation": "إيه سياسة الإلغاء؟", "policy_absence": "إيه اللي بيحصل لو غبت؟",
 "policy_minimum": "إيه الحد الأدنى للحصص؟", "policy_refund": "لو المدرّس أو الخدمة مناسبتناش، إيه اللي بيحصل؟",
 "policy_reschedule": "إزاي أغيّر ميعاد حصة؟",
 "concerns": "لو عندي تحفّظ أو قلق، أعمل إيه؟", "concern_price": "لو السعر عالي علينا؟",
 "concern_online": "هو الأونلاين فعّال؟", "concern_tried": "لو جرّبنا مدرّس والطالب ما اتحسّنش؟",
 "concern_patient": "عندكم مدرّس صبور يناسب ابننا؟", "concern_timing": "لو الوقت مش مناسب لنا؟",
 "concern_focus": "لو ابني مش بيركّز في الدروس أونلاين؟", "concern_inperson": "لو إحنا بنفضّل الدروس الحضورية؟",
 "register": "أسجّل إزاي دلوقتي؟", "human": "أتواصل مع مين وإزاي؟",
}
for _sid in sub_ids:
    EG_LABEL[_sid] = "بتدرّسوا " + nodes[_sid]["label"]["ar"].replace("هل تدرّسون ", "").rstrip("؟") + "؟"
    if _sid + "_strands" in nodes:
        EG_LABEL[_sid + "_strands"] = "إيه محاور المادة؟"
for _c in ("ca", "us"):
    for _n in sorted(pk):
        EG_LABEL[f"price_{_c}_{_n}"] = f"باقة {_n} {'حصة' if _n == 12 else 'حصص'} سعرها كام؟"
for _nid, _l in EG_LABEL.items():
    nodes[_nid]["label"]["ar"] = _l

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
          "- Teacher qualifications and vetting", "- Working hours of the team",
          "- EN/FR subject names for French, Arabic and Islamic Studies; FR names for Math, Science, Chemistry"]
open(f"{OUT}/tree_report.md", "w").write("\n".join(lines) + "\n")
print("OK nodes=", len(nodes), "sources=", len(used_sources), "gaps=", len(gaps), "composed=", len(composed))
