from google import genai
import pandas as pd
import time
from dotenv import load_dotenv
import os

load_dotenv()  
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)
LABELS = ["Deep Learning", "Computer Vision", "Reinforcement Learning", "NLP", "Optimization"]

def classify_paper(title, abstract):
    prompt = (
        f"Classify the following research paper into one of these categories: {', '.join(LABELS)}. "
        "If it does not clearly fit into any of these, reply with 'Other'.\n\n"
        f"Title: {title}\n\nAbstract: {abstract}\n\nCategory:"
    )
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        classification = response.text.strip()
        print(f"Assigned category: {classification}")
        return classification
    except Exception as e:
        print(f"Gemini API error: {e}")
        return "Error"

def annotate_dataset(input_csv, output_csv):
    try:
        df = pd.read_csv(input_csv)
    except Exception as e:
        print(f"Error reading {input_csv}: {e}")
        return
    if "title" not in df.columns or "abstract" not in df.columns:
        print("Error: The CSV file must have 'title' and 'abstract' columns.")
        return
    annotations = []
    for idx, row in df.iterrows():
        title = row["title"]
        abstract = row["abstract"]
        print(f"\nAnnotating paper {idx + 1}/{len(df)}: {title}")
        label = classify_paper(title, abstract)
        annotations.append(label)
        time.sleep(2)
    df["Category"] = annotations
    try:
        df.to_csv(output_csv, index=False)
        print(f"\nAnnotated dataset saved to: {output_csv}")
    except Exception as e:
        print(f"Error saving annotated dataset: {e}")

if __name__ == "__main__":
    input_csv_file = "C:/Users/asfan/Downloads/neurips_data (2)/neurips_1999.csv"
    output_csv_file = "C:/Users/asfan/Downloads/neurips_data (2)/neurips_papers_annotated.csv"
    annotate_dataset(input_csv_file, output_csv_file)
