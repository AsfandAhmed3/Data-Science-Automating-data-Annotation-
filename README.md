# 🤖 CleanData-Insights: Automating Research Paper Annotation with LLMs  

**`Leveraging Large Language Models for Smart Data Annotation`**  

---

## 📌 Project Overview  
This project automates the **annotation of research papers** using **Large Language Models (LLMs)**.  
Building on a previous assignment (scraping research papers from [NeurIPS](https://papers.nips.cc)), this project uses LLM APIs (such as **OpenAI ChatGPT**, **Google Gemini**, or other open-source models) to **classify papers into predefined research categories**.  

The pipeline transforms raw scraped research papers into a **labeled dataset**, enabling deeper analysis, trend tracking, and research insights.  

---

## 🧩 Features  

- 🔎 **Web Scraping Integration** – Scrapes research papers from NeurIPS.  
- 🏷️ **Automated Annotation** – Sends paper abstracts & titles to an LLM API.  
- 📂 **Five Research Categories** (e.g., NLP, Reinforcement Learning, Computer Vision, Deep Learning, Optimization).  
- 📊 **Structured Dataset** – Appends category labels to the dataset for downstream tasks.  
- 📝 **Blog & Knowledge Sharing** – Documented in a Medium article & shared on LinkedIn.  

---

## 🛠️ Tech Stack  

- **Language:** Python  
- **Libraries & Tools:**  
  - Requests / BeautifulSoup (for scraping)  
  - Pandas (data handling)  
  - LLM APIs (OpenAI, Google Gemini, or similar)  
  - JSON/CSV (data storage)  

---

## ⚙️ Workflow  

```mermaid
flowchart TD
    A[Scrape NeurIPS Papers] --> B[Extract Title & Abstract]
    B --> C[Send to LLM API]
    C --> D[Classify into One of 5 Labels]
    D --> E[Append Label to Dataset]
    E --> F[Save Final Annotated Dataset]
🚀 Setup & Usage
Clone the Repository

bash
Copy code
git clone https://github.com/AsfandAhmed3/Data-Science-Automating-data-Annotation.git
cd Data-Science-Automating-data-Annotation
Install Dependencies

bash
Copy code
pip install -r requirements.txt
Set API Key

Add your OpenAI / Gemini API key in .env file:

ini
Copy code
OPENAI_API_KEY=your_api_key_here
Run the Annotation Script

bash
Copy code
python annotate.py
📊 Example Output
Title	Abstract (truncated)	Category
"Attention is All You Need"	Transformers enable parallel learning	Natural Language Processing
"AlphaGo: Mastering Go with RL"	Deep RL framework with MCTS	Reinforcement Learning
"CNN for Image Recognition"	Convolutional approach for vision	Computer Vision

✨ Deliverables
✔️ Python Code – Well-documented script for the pipeline.
✔️ Annotated Dataset – With category labels.
✔️ Medium Blog – Explanation of approach & challenges.
✔️ LinkedIn Post – Experience sharing.

📢 Author
👤 Asfand Ahmed

💼 LinkedIn

📧 Email
