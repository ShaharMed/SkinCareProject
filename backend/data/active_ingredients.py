import pandas as pd
from Bio import Entrez
from transformers import pipeline
import json
import time
import os

Entrez.email = "Shaharmedina98@gmail.com"

try:
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
except Exception as e:
    print("⚠ בעיה בהורדת המודל - ודאי שיש אינטרנט ושהתקנת transformers + torch")
    raise e


class IngredientContext:
    def __init__(self, inci_name):
        self.inci_name = inci_name
        self.functions = []
        self.evidence = []
        self.skin_targets = []
        self.product_types = []
        self.timing = []
        self.safety_notes = []
        self.synergies = []
        self.conflicts = []

    def to_dict(self):
        # ממיר את רשימות למחרוזות מופרדות בפסיקים לשמירה ב-Excel
        return {
            "INCI Name": self.inci_name,
            "Functions": ", ".join(self.functions),
            "Evidence": " | ".join(self.evidence),
            "Skin Targets": ", ".join(self.skin_targets),
            "Product Types": ", ".join(self.product_types),
            "Timing": ", ".join(self.timing),
            "Safety Notes": ", ".join(self.safety_notes),
            "Synergies": ", ".join(self.synergies),
            "Conflicts": ", ".join(self.conflicts),
        }


def search_pubmed(term, max_results=5):
    try:
        handle = Entrez.esearch(db="pubmed", term=term, retmax=max_results)
        record = Entrez.read(handle)
        handle.close()
        return record["IdList"]
    except Exception as e:
        print(f"⚠ שגיאה בחיפוש PubMed עבור {term}: {e}")
        return []


def fetch_abstracts(id_list):
    abstracts = []
    if not id_list:
        return abstracts
    try:
        handle = Entrez.efetch(db="pubmed", id=",".join(id_list), rettype="medline", retmode="text")
        text = handle.read()
        handle.close()
        entries = text.split("\n\n")
        for entry in entries:
            lines = entry.split("\n")
            abstract = " ".join([line[5:] for line in lines if line.startswith("AB  ")])
            if abstract:
                abstracts.append(abstract)
    except Exception as e:
        print(f"⚠ שגיאה בשליפת תקצירים: {e}")
    return abstracts


def summarize_and_tag(context, abstracts):
    for abstract in abstracts:
        if len(abstract.strip()) < 100:
            continue
        try:
            summary = summarizer(abstract, max_length=150, min_length=40, do_sample=False)[0]['summary_text']
            context.evidence.append(summary)

            text = summary.lower()
            if "anti-inflammatory" in text:
                context.functions.append("Anti-inflammatory")
                context.skin_targets.append("Irritation")
            if "acne" in text:
                context.skin_targets.append("Acne-prone skin")
            if "hydration" in text or "moisture" in text:
                context.functions.append("Hydrating")
        except Exception as e:
            print(f"⚠ שגיאה בסיכום תקציר: {e}")
            continue
        time.sleep(1)


def process_all_ingredients(csv_path):
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"⚠ שגיאה בקריאת CSV: {e}")
        return

    results = []

    for inci_name in df["INCI Name"]:
        print(f"\n🔍 עיבוד רכיב: {inci_name}")
        context = IngredientContext(inci_name)
        ids = search_pubmed(inci_name + " skin")
        abstracts = fetch_abstracts(ids)
        summarize_and_tag(context, abstracts)
        results.append(context.to_dict())

    # שמירה לקובץ Excel אחד
    results_df = pd.DataFrame(results)
    output_filename = "ingredients_context.xlsx"
    results_df.to_excel(output_filename, index=False)
    print(f"\n✔ כל המידע נשמר בקובץ: {output_filename}")


if __name__ == "__main__":
    process_all_ingredients("active_ingredients.csv")
