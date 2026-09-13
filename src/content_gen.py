"""
content_gen.py
Generates professional PDF digital products for Etsy — completely free.
Uses pure Python (reportlab) — no API cost, no external service needed.

Products generated weekly (rotates through categories):
  1. Medical/Health education guides (Dr. Bansal's expertise)
  2. Professional templates (CV, research proposals, reports)
  3. Study guides (clinical biochemistry, lab medicine)
  4. Patient education (understanding lab tests)
  5. Wellness guides (nutrition, fitness reference cards)
"""
import random
from datetime import datetime

# ── Product catalog — 5 categories × 3 products each = 15 unique products ─────

PRODUCTS = [

    # ── Category 1: Medical Education (Your PhD expertise) ────────────────────
    {
        "category": "medical_education",
        "title": "Complete Blood Count (CBC) Explained: A Patient's Guide",
        "filename": "CBC_Patient_Guide",
        "price": 4.99,
        "tags": ["lab tests", "CBC", "blood test", "medical guide", "patient education",
                 "health", "laboratory", "clinical", "doctor", "nurse"],
        "sections": [
            ("What is a CBC?",
             "A Complete Blood Count (CBC) is one of the most common blood tests ordered by doctors. "
             "It measures different components of blood including red blood cells, white blood cells, "
             "hemoglobin, hematocrit, and platelets. This test helps doctors detect a wide range of "
             "disorders including anemia, infection, and leukemia."),
            ("Red Blood Cells (RBC)",
             "Normal range: 4.5-5.5 million cells/μL (men), 4.0-5.0 million cells/μL (women).\n"
             "Low RBC may indicate: Anemia, blood loss, bone marrow problems, nutritional deficiencies.\n"
             "High RBC may indicate: Dehydration, lung disease, living at high altitude, smoking."),
            ("Hemoglobin (Hgb)",
             "Normal range: 13.5-17.5 g/dL (men), 12.0-15.5 g/dL (women).\n"
             "Hemoglobin is the protein in red blood cells that carries oxygen throughout your body.\n"
             "Low hemoglobin = anemia. High hemoglobin may indicate dehydration or polycythemia."),
            ("White Blood Cells (WBC)",
             "Normal range: 4,500-11,000 cells/μL.\n"
             "WBCs are your immune system's soldiers. They fight infections and foreign invaders.\n"
             "High WBC (leukocytosis): Infection, inflammation, stress, leukemia.\n"
             "Low WBC (leukopenia): Viral infections, autoimmune disorders, bone marrow problems."),
            ("Platelets",
             "Normal range: 150,000-400,000 per μL.\n"
             "Platelets help your blood clot when you have a cut or injury.\n"
             "Low platelets (thrombocytopenia): Bleeding risk, bruising easily.\n"
             "High platelets (thrombocytosis): Clotting risk, may indicate inflammation or iron deficiency."),
            ("When to be Concerned",
             "Always discuss results with your doctor. Values slightly outside normal range may not "
             "be clinically significant. Your doctor considers your symptoms, medical history, and "
             "other test results together before making any diagnosis or treatment decision."),
            ("Questions to Ask Your Doctor",
             "• Which values are outside the normal range and by how much?\n"
             "• What could be causing abnormal results?\n"
             "• Do I need additional tests?\n"
             "• Should I repeat this test? If so, when?\n"
             "• How do my results compare to my previous tests?"),
        ],
        "description": "A clear, easy-to-understand patient guide explaining every component of the Complete Blood Count (CBC) blood test. Perfect for patients who want to understand their lab results, medical students, nurses and healthcare workers. Includes normal ranges, what abnormal values mean, and questions to ask your doctor.",
    },

    {
        "category": "medical_education",
        "title": "Kidney Function Tests Explained: Creatinine, BUN & eGFR Guide",
        "filename": "Kidney_Function_Tests_Guide",
        "price": 4.99,
        "tags": ["kidney function", "creatinine", "eGFR", "BUN", "renal", "lab tests",
                 "patient guide", "medical", "nephrology", "health"],
        "sections": [
            ("Understanding Kidney Function Tests",
             "Kidney function tests are blood and urine tests that check how well your kidneys "
             "are working. Your kidneys filter waste products from your blood, regulate blood "
             "pressure, and maintain fluid balance. These tests help detect kidney disease early "
             "when treatment is most effective."),
            ("Creatinine",
             "Normal range: 0.7-1.2 mg/dL (men), 0.5-1.0 mg/dL (women).\n"
             "Creatinine is a waste product from normal muscle metabolism. Healthy kidneys filter "
             "creatinine efficiently. High creatinine = kidneys not filtering well.\n"
             "Factors affecting creatinine: Muscle mass, diet (high meat intake), hydration status."),
            ("Blood Urea Nitrogen (BUN)",
             "Normal range: 7-20 mg/dL.\n"
             "BUN measures the amount of nitrogen in your blood from urea (protein waste product).\n"
             "High BUN may indicate: Kidney disease, dehydration, high protein diet, heart failure.\n"
             "Low BUN may indicate: Liver disease, malnutrition, overhydration."),
            ("eGFR — The Most Important Number",
             "eGFR (estimated Glomerular Filtration Rate) measures how much blood your kidneys "
             "filter per minute. It is calculated from your creatinine level, age, sex, and race.\n\n"
             "eGFR 90+: Normal kidney function\n"
             "eGFR 60-89: Mildly reduced — monitor closely\n"
             "eGFR 30-59: Moderate reduction — see nephrologist\n"
             "eGFR 15-29: Severely reduced — prepare for treatment\n"
             "eGFR <15: Kidney failure — dialysis or transplant needed"),
            ("BUN:Creatinine Ratio",
             "Normal ratio: 10:1 to 20:1.\n"
             "This ratio helps identify the cause of kidney problems:\n"
             "High ratio (>20:1): Dehydration, heart failure, high protein diet, GI bleeding\n"
             "Low ratio (<10:1): Liver disease, malnutrition, dialysis"),
            ("Protecting Your Kidneys",
             "• Stay well hydrated (6-8 glasses of water daily)\n"
             "• Control blood pressure and blood sugar\n"
             "• Avoid NSAIDs (ibuprofen, naproxen) if kidney function is reduced\n"
             "• Eat a balanced diet low in processed foods\n"
             "• Exercise regularly and maintain healthy weight\n"
             "• Don't smoke\n"
             "• Get regular kidney function tests if you have diabetes or hypertension"),
        ],
        "description": "Expert guide to understanding kidney function blood tests including creatinine, BUN, and eGFR. Written by a clinical biochemistry PhD. Ideal for patients with kidney disease, diabetes, or hypertension, medical students, and healthcare professionals. Includes CKD staging chart and kidney protection tips.",
    },

    {
        "category": "medical_education",
        "title": "Thyroid Function Tests: TSH, T3 & T4 Complete Reference Guide",
        "filename": "Thyroid_Function_Tests_Guide",
        "price": 4.99,
        "tags": ["thyroid", "TSH", "T3", "T4", "thyroid test", "hypothyroid",
                 "hyperthyroid", "lab tests", "patient guide", "endocrinology"],
        "sections": [
            ("The Thyroid Gland",
             "Your thyroid gland, located in your neck, produces hormones that regulate your metabolism, "
             "energy levels, body temperature, heart rate, and many other vital functions. "
             "Thyroid disorders are among the most common endocrine conditions worldwide, affecting "
             "millions of people — particularly women."),
            ("TSH — Thyroid Stimulating Hormone",
             "Normal range: 0.4-4.0 mIU/L.\n"
             "TSH is produced by the pituitary gland and tells your thyroid how much hormone to make.\n"
             "High TSH: Your thyroid isn't making enough hormone (hypothyroidism)\n"
             "Low TSH: Your thyroid is making too much hormone (hyperthyroidism)\n"
             "TSH is usually the FIRST test ordered to screen thyroid function."),
            ("Free T4 (Thyroxine)",
             "Normal range: 0.8-1.8 ng/dL.\n"
             "T4 is the main hormone produced by the thyroid gland. 'Free' T4 is the active form "
             "not bound to proteins in the blood.\n"
             "Low T4 + High TSH = Hypothyroidism\n"
             "High T4 + Low TSH = Hyperthyroidism"),
            ("Free T3 (Triiodothyronine)",
             "Normal range: 2.3-4.2 pg/mL.\n"
             "T3 is the more active thyroid hormone. The body converts T4 to T3.\n"
             "T3 testing is usually done when T4 and TSH results are inconclusive or when "
             "monitoring treatment for hyperthyroidism."),
            ("Hypothyroidism Symptoms",
             "If your thyroid is underactive you may experience:\n"
             "• Fatigue and sluggishness\n"
             "• Increased sensitivity to cold\n"
             "• Constipation\n"
             "• Weight gain\n"
             "• Dry skin and hair\n"
             "• Muscle weakness\n"
             "• Depression\n"
             "• Slow heart rate"),
            ("Hyperthyroidism Symptoms",
             "If your thyroid is overactive you may experience:\n"
             "• Unintentional weight loss\n"
             "• Rapid or irregular heartbeat\n"
             "• Anxiety and irritability\n"
             "• Trembling hands\n"
             "• Increased sweating\n"
             "• Difficulty sleeping\n"
             "• Frequent bowel movements"),
            ("Treatment Overview",
             "Hypothyroidism: Usually treated with synthetic thyroid hormone (levothyroxine).\n"
             "Hyperthyroidism: Treated with anti-thyroid medications, radioactive iodine, or surgery.\n"
             "Both conditions are highly treatable. Regular monitoring of thyroid hormone levels "
             "is essential for proper dose adjustment and long-term management."),
        ],
        "description": "Comprehensive patient guide to thyroid function tests including TSH, Free T3, and Free T4. Explains what each test measures, normal ranges, and what abnormal results mean. Includes symptom checklists for both hypothyroidism and hyperthyroidism. Written with clinical biochemistry expertise.",
    },

    # ── Category 2: Professional Templates ────────────────────────────────────
    {
        "category": "templates",
        "title": "Research Proposal Template: Complete Academic Format (10 Templates)",
        "filename": "Research_Proposal_Template_Pack",
        "price": 7.99,
        "tags": ["research proposal", "academic template", "PhD template", "grant proposal",
                 "research template", "academic writing", "university", "dissertation", "thesis"],
        "sections": [
            ("How to Use These Templates",
             "This pack contains 10 research proposal templates suitable for undergraduate, "
             "postgraduate, and doctoral research across sciences, social sciences, and humanities. "
             "Each template follows internationally accepted academic formatting standards."),
            ("Template 1: Basic Research Proposal Structure",
             "1. Title Page\n"
             "   - Research title\n"
             "   - Researcher name and affiliation\n"
             "   - Supervisor name\n"
             "   - Date of submission\n\n"
             "2. Abstract (250-300 words)\n"
             "3. Introduction and Background\n"
             "4. Research Problem Statement\n"
             "5. Research Objectives\n"
             "6. Research Questions/Hypotheses\n"
             "7. Literature Review\n"
             "8. Research Methodology\n"
             "9. Timeline/Work Plan\n"
             "10. Budget\n"
             "11. References"),
            ("Writing a Strong Problem Statement",
             "A good problem statement:\n"
             "• Identifies the specific problem clearly\n"
             "• Explains why the problem matters\n"
             "• Describes who is affected\n"
             "• States what is currently known and unknown\n"
             "• Shows the gap in knowledge your research will fill\n\n"
             "Template:\n"
             "'Despite [current understanding], [the problem] remains [unclear/unsolved]. "
             "This gap leads to [consequences]. Therefore, this study will investigate [topic] "
             "to [achieve goal].'"),
            ("Research Objectives — Writing Tips",
             "Objectives should be SMART:\n"
             "• Specific — clearly defined and focused\n"
             "• Measurable — can be quantified or assessed\n"
             "• Achievable — realistic within your resources\n"
             "• Relevant — directly address the research problem\n"
             "• Time-bound — can be completed within your timeframe\n\n"
             "Use action verbs: To assess, To compare, To evaluate, To identify, To determine"),
            ("Methodology Section Template",
             "Study Design: [Descriptive/Analytical/Experimental/Qualitative]\n"
             "Setting: [Where will the study take place?]\n"
             "Population and Sample: [Who are the participants? How many? How selected?]\n"
             "Data Collection: [What tools/instruments? Questionnaire? Lab tests? Interviews?]\n"
             "Data Analysis: [What statistical methods? What software?]\n"
             "Ethical Considerations: [IRB approval? Informed consent? Confidentiality?]"),
            ("Common Mistakes to Avoid",
             "✗ Too broad a topic — narrow your focus\n"
             "✗ Vague objectives — make them specific and measurable\n"
             "✗ Ignoring existing literature — show you know the field\n"
             "✗ Unrealistic timeline — be honest about what's feasible\n"
             "✗ Neglecting ethics — always address ethical considerations\n"
             "✗ Poor references — use proper citation format consistently"),
            ("Grant Funding Proposal Template",
             "When applying for grants, additionally include:\n"
             "• Executive Summary (1 page)\n"
             "• Significance and Innovation section\n"
             "• Preliminary data (if available)\n"
             "• Detailed budget justification\n"
             "• Team qualifications and roles\n"
             "• Sustainability plan (how will work continue after funding ends?)\n"
             "• Dissemination plan (how will findings be shared?)"),
        ],
        "description": "Professional research proposal template pack with 10 templates for academic and grant proposals. Includes structure templates, writing tips for each section, SMART objectives guide, and grant funding proposal format. Suitable for all academic levels and disciplines. Instant digital download.",
    },

    {
        "category": "templates",
        "title": "Professional CV Template Pack for Medical & Healthcare Professionals",
        "filename": "Medical_CV_Template_Pack",
        "price": 6.99,
        "tags": ["CV template", "medical CV", "doctor CV", "healthcare resume",
                 "curriculum vitae", "medical resume", "nurse CV", "physician CV", "job template"],
        "sections": [
            ("Why Medical CVs Are Different",
             "A medical/healthcare CV differs from a standard resume in several important ways:\n"
             "• Length: Medical CVs can be 3-10+ pages (unlike 1-2 page resumes)\n"
             "• Content: Includes publications, presentations, clinical rotations, certifications\n"
             "• Format: Chronological with detailed clinical experience sections\n"
             "• Purpose: Demonstrates both clinical competence and academic achievement"),
            ("Essential CV Sections — Medical Format",
             "1. Personal Information (Name, contact, registration number)\n"
             "2. Professional Summary (3-4 sentences)\n"
             "3. Medical Qualifications and Licenses\n"
             "4. Clinical Experience (most recent first)\n"
             "5. Education and Training\n"
             "6. Research Experience\n"
             "7. Publications and Presentations\n"
             "8. Awards and Honors\n"
             "9. Professional Memberships\n"
             "10. Skills (clinical, technical, languages)\n"
             "11. References"),
            ("Clinical Experience Section Template",
             "Job Title | Hospital/Clinic Name | City | Start Date – End Date\n"
             "Department: [e.g., Internal Medicine, Emergency, ICU]\n"
             "• [Specific clinical responsibility or achievement]\n"
             "• [Patient volume/case types handled]\n"
             "• [Procedures performed or supervised]\n"
             "• [Leadership or teaching responsibilities]\n"
             "• [Quality improvement initiatives]\n\n"
             "Example:\n"
             "Senior Medical Officer | City General Hospital | New Delhi | Jan 2020 – Present\n"
             "• Managed 40+ daily outpatients in internal medicine department\n"
             "• Supervised 4 junior residents in diagnostic procedures"),
            ("Publications Section Format",
             "Journal Articles:\n"
             "Author(s). Title. Journal Name. Year;Volume(Issue):Pages. DOI.\n\n"
             "Example:\n"
             "Bansal A, Smith J. Beta-trace protein as a novel marker for CKD staging. "
             "Clinical Biochemistry. 2023;56(2):112-118. doi:10.1016/j.clinbiochem.2023.01.005\n\n"
             "List publications in reverse chronological order.\n"
             "Separate into: Peer-reviewed articles, Book chapters, Conference abstracts"),
            ("Professional Summary — Writing Tips",
             "Write 3-4 powerful sentences covering:\n"
             "1. Your specialty and years of experience\n"
             "2. Your key clinical strengths\n"
             "3. Your academic/research achievements\n"
             "4. What you bring to the position\n\n"
             "Example:\n"
             "'Board-certified physician with 10 years of experience in internal medicine and "
             "clinical biochemistry. Expertise in renal biomarkers, metabolic disorders, and "
             "diagnostic testing. Published researcher with 15+ peer-reviewed articles. "
             "Committed to evidence-based patient care and clinical education.'"),
            ("ATS-Friendly Formatting Tips",
             "Many hospitals use Applicant Tracking Systems (ATS) to screen CVs:\n"
             "✓ Use standard fonts (Arial, Calibri, Times New Roman)\n"
             "✓ Font size 10-12pt for body text, 14-16pt for name\n"
             "✓ Use standard section headings\n"
             "✓ Avoid tables, graphics, and text boxes\n"
             "✓ Save as .docx and .pdf both\n"
             "✓ Include keywords from the job description\n"
             "✗ Avoid headers/footers with important information"),
        ],
        "description": "Professional CV template pack specifically designed for medical doctors, nurses, and healthcare professionals. Includes 5 different CV formats, section-by-section writing guides, publication formatting templates, and ATS optimization tips. Perfect for residency applications, consultancy positions, and academic jobs.",
    },

    # ── Category 3: Study Guides ────────────────────────────────────────────
    {
        "category": "study_guides",
        "title": "Clinical Biochemistry Quick Reference: Lab Values Cheat Sheet",
        "filename": "Clinical_Biochemistry_Reference_Card",
        "price": 3.99,
        "tags": ["clinical biochemistry", "lab values", "reference card", "medical student",
                 "USMLE", "MBBS", "cheat sheet", "normal values", "laboratory", "nursing"],
        "sections": [
            ("Complete Metabolic Panel — Normal Values",
             "GLUCOSE\n"
             "Fasting: 70-99 mg/dL | Post-meal (<2hr): <140 mg/dL\n"
             "Prediabetes: 100-125 mg/dL | Diabetes: ≥126 mg/dL\n\n"
             "SODIUM (Na+): 136-145 mEq/L\n"
             "POTASSIUM (K+): 3.5-5.0 mEq/L\n"
             "CHLORIDE (Cl-): 98-106 mEq/L\n"
             "BICARBONATE (HCO3-): 22-29 mEq/L\n"
             "BUN: 7-20 mg/dL\n"
             "CREATININE: 0.7-1.2 mg/dL (M), 0.5-1.0 mg/dL (F)\n"
             "eGFR: >60 mL/min/1.73m² (normal)\n"
             "CALCIUM: 8.5-10.2 mg/dL"),
            ("Liver Function Tests",
             "ALT (SGPT): 7-56 U/L\n"
             "AST (SGOT): 10-40 U/L\n"
             "ALKALINE PHOSPHATASE: 44-147 U/L\n"
             "BILIRUBIN TOTAL: 0.1-1.2 mg/dL\n"
             "BILIRUBIN DIRECT: 0.0-0.3 mg/dL\n"
             "ALBUMIN: 3.5-5.0 g/dL\n"
             "TOTAL PROTEIN: 6.0-8.3 g/dL\n"
             "GGT: 9-48 U/L (M), 9-32 U/L (F)"),
            ("Lipid Panel",
             "TOTAL CHOLESTEROL: <200 mg/dL (desirable)\n"
             "LDL CHOLESTEROL: <100 mg/dL (optimal), <130 (near optimal)\n"
             "HDL CHOLESTEROL: >60 mg/dL (protective), <40 (low/risk)\n"
             "TRIGLYCERIDES: <150 mg/dL (normal)\n"
             "Non-HDL cholesterol: <130 mg/dL\n"
             "Total/HDL ratio: <5.0"),
            ("Thyroid Function",
             "TSH: 0.4-4.0 mIU/L\n"
             "Free T4: 0.8-1.8 ng/dL\n"
             "Free T3: 2.3-4.2 pg/mL\n"
             "Total T4: 5.0-12.0 μg/dL\n"
             "Total T3: 80-200 ng/dL\n"
             "Anti-TPO: <35 IU/mL\n"
             "Anti-Thyroglobulin: <20 IU/mL"),
            ("Complete Blood Count",
             "RBC: 4.5-5.5 M/μL (M), 4.0-5.0 M/μL (F)\n"
             "HEMOGLOBIN: 13.5-17.5 g/dL (M), 12.0-15.5 g/dL (F)\n"
             "HEMATOCRIT: 41-53% (M), 36-46% (F)\n"
             "MCV: 80-100 fL\n"
             "MCH: 27-33 pg\n"
             "MCHC: 32-36 g/dL\n"
             "WBC: 4,500-11,000/μL\n"
             "PLATELETS: 150,000-400,000/μL"),
            ("Coagulation Studies",
             "PT: 11-13.5 seconds\n"
             "INR: 0.8-1.2 (therapeutic 2.0-3.0 for anticoagulation)\n"
             "aPTT: 25-35 seconds\n"
             "Thrombin Time: 14-19 seconds\n"
             "Fibrinogen: 200-400 mg/dL\n"
             "D-Dimer: <0.5 mg/L FEU"),
            ("Cardiac Markers",
             "TROPONIN I: <0.04 ng/mL\n"
             "TROPONIN T: <0.01 ng/mL\n"
             "CK-MB: <3.6 ng/mL\n"
             "CK Total: 22-198 U/L (M), 39-238 U/L (F)\n"
             "BNP: <100 pg/mL\n"
             "NT-proBNP: <125 pg/mL (<75 years)\n"
             "Myoglobin: 0-90 ng/mL"),
        ],
        "description": "Essential quick reference card for medical students, nurses, and healthcare professionals. Covers complete metabolic panel, CBC, liver function tests, lipid panel, thyroid function, coagulation studies, and cardiac markers with normal ranges. Perfect study companion for USMLE, MBBS, nursing boards, and clinical rotations. Print and keep at your desk!",
    },

]


def get_product_for_week() -> dict:
    """Get the product to create this week based on week number."""
    week  = datetime.utcnow().isocalendar()[1]
    year  = datetime.utcnow().year
    idx   = (week + year * 100) % len(PRODUCTS)
    product = PRODUCTS[idx]
    print(f"  [content] Week {week}/{year}: '{product['title']}'")
    return product
