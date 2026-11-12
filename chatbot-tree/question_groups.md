# مجموعات الأسئلة (Batch D) وربطها بالشجرة

المصدر: `SPM_Intent_Curation_Batch_D_WU45_WU60_Operations_Registration.xlsx`
(16 نية، 8,224 جملة نشطة، 514 لكل نية: 282 EN + 152 AR + 80 FR).

**ملاحظة مهمة:** هذا الملف بيانات تدريب مُنسّقة/مولّدة (مصدرها "SPM Synthetic Expansion v2" و"Batch D curated")، وعدد الجمل متساوٍ بين النوايا بالتصميم. لا يدل على تكرار الأسئلة الحقيقي. لذلك استُخدم لتحديد **مجموعات الأسئلة**، وتُرتَّب الشجرة بحسب رحلة العميل لا بحسب التكرار.

القاعدة: لا يُكتب أي نص جديد. كل جواب منقول حرفياً من صف ACTIVE في قاعدة المعرفة. ما لا جواب معتمد له يبقى خارج الشجرة ويُحوَّل إلى الفريق.

| WU | النية | عقدة الشجرة | مصدر الجواب المعتمد |
|---|---|---|---|
| 45 | reschedule | `policy_reschedule` (جديد) | POLICIES: cancellation (POL-001/005/009) |
| 46 | cancel_lesson | `policy_cancellation` | POLICIES: cancellation |
| 47 | missed_lesson | `policy_absence` | POLICIES: absence |
| 48 | online_class_how_it_works | `about_online` | FAQ: delivery |
| 49 | technology_requirements | `classes_tech` (جديد) | SERVICES: S-AR/EN/FR-6 |
| 50 | lesson_duration | `classes_duration` | FAQ: lesson_duration |
| 51 | lesson_frequency | `classes_frequency` | FAQ: lesson_frequency |
| 52 | assessment | `followup_assessment` (جديد) | SERVICES: S-AR/EN/FR-2 |
| 53 | progress_tracking | `followup_updates` (جديد) | SERVICES: S-AR/EN/FR-5 |
| 54 | parent_reporting | `followup_updates` + `classes_certificates` | SERVICES: S-5، FAQ: certificates |
| 55 | curriculum_alignment | `about_curriculum` + `sub_004_ontario` | COMPANY: curriculum، FAQ: curriculum_alignment |
| 56 | materials_homework | `classes_homework` | FAQ: homework |
| 57 | registration | `register` | نموذج التسجيل (يُحوَّل لصفحة التسجيل في الموقع) |
| 58 | ready_to_register | `register` | نفسه |
| 59 | contact_share | `register` / `human` | يُجمَع عبر التسجيل بعد التحقق |
| 60 | booking_confirmation | `classes_booking` (جديد) | FALLBACKS: unconfirmed_booking (FB-007/008/009) |

## ضوابط ACTION_FACT_GATES التي تلتزم بها الشجرة
- لا تقول "تم تغيير/إلغاء الموعد" ولا "تم التسجيل" ولا "الحجز مؤكد": الشجرة تشرح السياسة وتحوّل للفريق/التسجيل فقط.
- لا وعود بالتعويض أو بنتائج دراسية أو علامات؛ التقدّم يُعرض كآلية لا كنتيجة.
- مدة الحصة وعدد الحصص من FAQ المعتمد فقط.

## نقاط تحتاج تأكيد المالك
1. صف S-5 يذكر "تحديثات يومية أو أسبوعية من المدرس": هل هو التزام فعلي؟
2. صف S-6 يحدد Google Meet كمنصة رئيسية للحصص.
3. تسميات الأزرار الجديدة (سؤال العميل) صياغتها من الواجهة وليست من الشيت.
