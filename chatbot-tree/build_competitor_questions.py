#!/usr/bin/env python3
"""Competitor FAQ question inventory -> competitor_questions.xlsx (questions only, own wording; no competitor answers copied)."""
import sys, openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
OUT = sys.argv[1]
IN, ADD, NEED = "في الشجرة", "أُضيف الآن", "يحتاج إجابة معتمدة"
# (group, ar, en, fr, competitors, status, tree node / note)
R = [
("التعريف والخدمات","من أنتم وما الخدمات التي تقدمونها؟","Who are you and what do you offer?","Qui êtes-vous et que proposez-vous ?","PP, TD",IN,"about"),
("التعريف والخدمات","ما المواد التي تدرّسونها؟","Which subjects do you teach?","Quelles matières enseignez-vous ?","TD, PP, SS",IN,"subjects"),
("التعريف والخدمات","ما الصفوف التي تدرّسونها؟","Which grades do you teach?","Quels niveaux enseignez-vous ?","SS, TD",IN,"about_grades"),
("التعريف والخدمات","ما المناهج التي تدعمونها؟","Which curricula do you support?","Quels programmes soutenez-vous ?","TD",IN,"about_curriculum"),
("التعريف والخدمات","هل تقدمون التحضير للاختبارات؟","Do you help with exam preparation?","Aidez-vous à préparer les examens ?","TD",ADD,"about_exam"),
("التعريف والخدمات","هل تقدمون إرشاداً أكاديمياً وتنظيماً للدراسة؟","Do you offer academic mentoring and study organization?","Offrez-vous du mentorat scolaire et de l’aide à l’organisation ?","TD",ADD,"about_mentoring"),
("التعريف والخدمات","هل الدروس أونلاين؟ وهل هي فردية أم جماعية؟","Are lessons online, and are they one-to-one or group?","Les cours sont-ils en ligne, individuels ou en groupe ?","TD, SS, OL, PR",IN,"about_online"),
("التعريف والخدمات","هل يمكن الحصول على مادة غير مذكورة في الموقع؟","Can I get tutoring in a subject that is not listed?","Puis-je obtenir un cours dans une matière non listée ?","TD",NEED,"لا يوجد صف معتمد"),
("الأسعار والدفع","كم تكلفة الدروس؟","How much does tutoring cost?","Combien coûte le tutorat ?","SS, PP, TD, VT",IN,"pricing"),
("الأسعار والدفع","ما طرق الدفع المقبولة؟","Which payment methods do you accept?","Quels modes de paiement acceptez-vous ?","SS, PP, PR",NEED,"لا يوجد صف معتمد"),
("الأسعار والدفع","متى وكيف يتم خصم المبلغ؟","When and how am I charged?","Quand et comment suis-je facturé ?","PR, PP",NEED,"لا يوجد صف معتمد"),
("الأسعار والدفع","هل أحصل على إيصال؟ وهل تُضاف ضريبة؟","Do I get a receipt, and is tax added?","Reçoit-on un reçu et les taxes s’ajoutent-elles ?","SS, PR",NEED,"لا يوجد صف معتمد"),
("الأسعار والدفع","هل توجد خطط دفع أو تقسيط؟","Are payment plans available?","Existe-t-il des plans de paiement ?","TD",NEED,"لا يوجد صف معتمد"),
("الأسعار والدفع","هل توجد خصومات أو برنامج إحالة؟","Are there discounts or a referral program?","Y a-t-il des rabais ou un programme de parrainage ?","PR",NEED,"RULE-011: لا خصومات دون صف معتمد"),
("البدء والتجربة","كيف أسجّل الآن؟","How do I register now?","Comment m’inscrire maintenant ?","OL, SS, TD, PP, PR",IN,"register"),
("البدء والتجربة","كيف أحصل على الحصة التجريبية المجانية؟","How do I get the free trial lesson?","Comment obtenir l’essai gratuit ?","PR, PP",IN,"trial"),
("البدء والتجربة","كيف تعرفون احتياج الطالب؟ وهل يوجد تقييم؟","How do you find out what my child needs? Is there an assessment?","Comment déterminez-vous les besoins de mon enfant ? Y a-t-il une évaluation ?","SS, TD, PR",IN,"followup_assessment"),
("البدء والتجربة","ماذا يحدث في الحصة التجريبية؟","What happens in the trial lesson?","Que se passe-t-il pendant l’essai ?","PR",NEED,"trial يجيب جزئياً فقط"),
("البدء والتجربة","ما علامات أن طفلي يحتاج إلى دروس؟","What signs show my child could benefit from tutoring?","Quels signes montrent que mon enfant bénéficierait du tutorat ?","SS",NEED,"لا يوجد صف معتمد"),
("الحصص","كم مدة الحصة؟","How long is each lesson?","Combien de temps dure un cours ?","SS",IN,"classes_duration"),
("الحصص","كم حصة تنصحون بها أسبوعياً؟","How many lessons per week do you recommend?","Combien de cours par semaine recommandez-vous ?","SS, TD",IN,"classes_frequency"),
("الحصص","ما المواعيد المتاحة؟ وهل الوقت مرن؟","When are tutors available? Is scheduling flexible?","Quelles sont les disponibilités ? L’horaire est-il flexible ?","OL, SS, TD",IN,"classes_booking, concern_timing"),
("الحصص","كيف تختارون المدرس؟","How do you choose the tutor?","Comment choisissez-vous le tuteur ?","VT, PP, PR, TD",IN,"classes_matching"),
("الحصص","ما الخبرة التي تراعونها في المدرسين؟","What tutor experience do you look for?","Quelle expérience recherchez-vous chez les tuteurs ?","VT, OL, PP, TD, PR",ADD,"classes_tutor"),
("الحصص","هل المدرسون خاضعون لفحص خلفية؟ وما معايير السلامة؟","Are tutors background-checked? What safety measures exist?","Les tuteurs sont-ils vérifiés ? Quelles mesures de sécurité ?","TD, PP, VT",NEED,"لا يوجد صف معتمد"),
("الحصص","كيف تُصمَّم الحصص لتناسب الطالب؟","How are lessons tailored to each student?","Comment les cours sont-ils adaptés à chaque élève ?","TD",ADD,"classes_tailored"),
("الحصص","ما الأجهزة والتقنية المطلوبة؟","What equipment and technology do lessons require?","De quel équipement a-t-on besoin ?","PP, PR",ADD,"classes_tech"),
("الحصص","هل يوجد واجب بعد الحصة؟","Is there homework after lessons?","Y a-t-il des devoirs après les cours ?","TD",IN,"classes_homework"),
("الحصص","هل تُسجَّل الحصص؟","Are sessions recorded?","Les séances sont-elles enregistrées ?","PP",NEED,"لا يوجد صف معتمد"),
("الحصص","ماذا لو لم يحضر المدرس؟","What if my tutor does not show up?","Que faire si mon tuteur ne se présente pas ?","VT, PP",NEED,"لا يوجد صف معتمد"),
("الحصص","ما دوري كولي أمر؟","What is my role as a parent?","Quel est mon rôle de parent ?","SS",NEED,"لا يوجد صف معتمد"),
("المتابعة والنتائج","كيف تتم متابعة تقدم الطالب وتقارير ولي الأمر؟","How is progress tracked, and how do parents get updates?","Comment les progrès sont-ils suivis et communiqués aux parents ?","OL, TD, PR",ADD,"followup_updates"),
("المتابعة والنتائج","متى أرى النتائج؟","How soon will I see results?","Dans combien de temps verra-t-on des résultats ?","OL, SS, TD",NEED,"RULE-WU99-020: لا ضمان للنتائج؛ يحتاج صياغة معتمدة"),
("المتابعة والنتائج","هل يحصل الطالب على شهادة؟","Does the student get a certificate?","L’élève reçoit-il un certificat ?","PR",IN,"classes_certificates"),
("المتابعة والنتائج","كيف أقيّم المدرس أو أرسل ملاحظات؟","How can I rate my tutor or give feedback?","Comment évaluer mon tuteur ou donner un avis ?","VT, PP",NEED,"لا يوجد صف معتمد"),
("السياسات","ما سياسة الإلغاء؟","What is the cancellation policy?","Quelle est la politique d’annulation ?","OL, VT, PP, TD, PR",IN,"policy_cancellation"),
("السياسات","كيف أغيّر موعد حصة؟","How do I reschedule a lesson?","Comment déplacer un cours ?","VT, TD, PR",ADD,"policy_reschedule"),
("السياسات","ماذا يحدث عند الغياب أو الإلغاء المتأخر؟","What happens if I miss or cancel late?","Que se passe-t-il en cas d’absence ou d’annulation tardive ?","VT",IN,"policy_absence"),
("السياسات","كيف أسترد المبلغ إن لم يناسبنا المدرس أو الخدمة؟","How do I get a refund if the tutor or service is not a fit?","Comment être remboursé si le tuteur ou le service ne convient pas ?","PR, PP, VT",IN,"policy_refund"),
("السياسات","هل يمكنني تغيير المدرس؟","Can I switch tutors?","Puis-je changer de tuteur ?","VT, PP, PR, TD",IN,"policy_refund"),
("السياسات","هل لديكم ضمان رضا؟","Do you have a satisfaction guarantee?","Offrez-vous une garantie de satisfaction ?","PP",NEED,"RULE-011: لا ضمانات دون صف معتمد"),
("التحفظات","ماذا لو لم يعجب طفلي أو وجد صعوبة؟","What if my child dislikes it or struggles?","Et si mon enfant n’aime pas ou a des difficultés ?","OL",IN,"concern_tried"),
("التحفظات","هل التعلم أونلاين فعّال؟","Is online learning effective?","L’apprentissage en ligne est-il efficace ?","—",IN,"concern_online"),
("التحفظات","هل يمكن دعم طلاب لديهم صعوبات تعلّم؟","Can students with learning difficulties get help?","Les élèves ayant des difficultés d’apprentissage peuvent-ils être aidés ?","SS, TD",NEED,"قرار المالك"),
("التواصل","مع من أتواصل وكيف؟","Who can I contact, and how?","Qui contacter et comment ?","TD, PP, VT",IN,"human"),
]
SRC = [("OL","Oxford Learning","https://oxfordlearning.com/tutoring-faqs"),
       ("VT","Varsity Tutors (Help Center, 1-on-1)","https://member-services.varsitytutors.com/hc/en-us/categories/15408070452635-1-on-1-Tutoring"),
       ("SS","Success Scolaire (Canada)","https://www.successcolaire.ca/en/faq"),
       ("PP","++tutors","https://plusplustutors.com/faqs"),
       ("TD","Tutor Doctor","https://www.tutordoctor.co.uk/?p=319"),
       ("PR","Preply (Help for students)","https://help.preply.com/en/collections/3328581-help-for-students")]
wb = openpyxl.Workbook(); ws = wb.active; ws.title = "الأسئلة"
H = ["#","المجموعة","السؤال (عربي)","Question (EN)","Question (FR)","المنافسون الذين يسألونه","الحالة","عقدة الشجرة / ملاحظة"]
ws.append(H)
for i, r in enumerate(R, 1): ws.append([i, *r])
fill = {IN: "E3F1E5", ADD: "DCE8FA", NEED: "FBE9D0"}
for row in ws.iter_rows(min_row=2):
    row[6].fill = PatternFill("solid", fgColor=fill[row[6].value])
    for c in row: c.alignment = Alignment(wrap_text=True, vertical="top")
for c in ws[1]: c.font = Font(bold=True, color="FFFFFF"); c.fill = PatternFill("solid", fgColor="1D5FB8")
for col, w in zip("ABCDEFGH", (5, 18, 42, 42, 42, 20, 20, 34)): ws.column_dimensions[col].width = w
ws.freeze_panes = "A2"; ws.sheet_view.rightToLeft = True
ws2 = wb.create_sheet("بحاجة لإجابة معتمدة"); ws2.append(H[:6] + ["ملاحظة"]); ws2.sheet_view.rightToLeft = True
for i, r in enumerate(R, 1):
    if r[5] == NEED: ws2.append([i, *r[:5], r[6]])
for col, w in zip("ABCDEFG", (5, 18, 42, 42, 42, 20, 34)): ws2.column_dimensions[col].width = w
for row in ws2.iter_rows():
    for c in row: c.alignment = Alignment(wrap_text=True, vertical="top")
for c in ws2[1]: c.font = Font(bold=True)
ws3 = wb.create_sheet("المصادر"); ws3.append(["الرمز", "المنافس", "الصفحة"])
for s in SRC: ws3.append(list(s))
ws3.append([]); ws3.append(["ملاحظة", "الأسئلة مصاغة بكلماتنا من محتوى صفحات الأسئلة الشائعة لكل منافس؛ لم تُنسخ إجاباتهم."])
ws3.column_dimensions["B"].width = 40; ws3.column_dimensions["C"].width = 90
wb.save(OUT)
import collections; print(len(R), collections.Counter(r[5] for r in R))
