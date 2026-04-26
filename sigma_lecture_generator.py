import random
from textwrap import fill

TITLE = "Sigma Metrics in Clinical Laboratory Quality"

SECTIONS = [
"historical evolution of quality control",
"six sigma principles in laboratory medicine",
"sigma calculation using TEa, bias and CV",
"Westgard rules and sigma interpretation",
"method validation and verification",
"clinical risk and patient safety",
"automation and digital laboratories",
"future of sigma metrics in precision medicine"
]

def paragraph(topic):
    base = f"""
    {topic.capitalize()} is a critical component of modern clinical laboratory
    practice. In high-throughput hospital laboratories, analytical errors can
    directly influence patient diagnosis and treatment decisions. Sigma metrics
    provide a quantitative framework to evaluate assay performance using total
    allowable error, analytical bias, and coefficient of variation.

    When laboratories adopt sigma-based thinking, quality control becomes risk-
    driven rather than schedule-driven. This transition allows laboratories to
    optimize QC frequency, reduce reagent waste, and improve turnaround time.
    Ultimately, sigma metrics transform quality from a compliance activity into
    a patient-safety strategy.
    """
    return fill(base, 90)

def generate_lecture():
    lecture = []
    lecture.append(fill(f"""
    Welcome to this PhD Masterclass on {TITLE}.
    This session explains how sigma metrics revolutionized laboratory quality,
    risk management, and clinical decision reliability across modern hospitals.
    """, 90))

    for topic in SECTIONS:
        for _ in range(2):   # two paragraphs per section
            lecture.append(paragraph(topic))

    lecture.append(fill("""
    In conclusion, sigma metrics are not merely statistical tools. They represent
    a complete philosophy of laboratory excellence focused on minimizing risk,
    maximizing efficiency, and protecting patient outcomes.
    """, 90))

    script = "\n\n".join(lecture)

    with open("lecture_script.txt","w") as f:
        f.write(script)

    print("Word count:", len(script.split()))

if __name__ == "__main__":
    generate_lecture()
