import io
import os
import pdfplumber
from dotenv import load_dotenv
from openai import OpenAI  # zakładam, że masz pakiet openai z DeepSeek API

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)

def extract_invoice_data_from_bytes(pdf_bytes: bytes) -> dict:
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    except Exception as e:
        print(f"❌ Błąd podczas ekstrakcji tekstu z PDF: {e}")
        return {}

    prompt = f"""
Oto treść faktury. Wyodrębnij i zwróć w formacie JSON następujące pola:
- numer faktury jako "numer faktury" - typ danych str
- nazwa sprzedawcy jako "sprzedawca" - typ danych str
- nazwa nabywcy jako "nabywca" - typ danych str
- data wystawienia jako "data wystawienia" - typ danych str (format: YYYY-MM-DD)
- data sprzedaży jako "data sprzedaży" - typ danych str (format: YYYY-MM-DD)
- kwota brutto jako "kwota brutto" - typ danych float (usuń inne znaki typu "PLN", "zł")
- kwota netto jako "kwota netto" - typ danych float (usuń inne znaki typu "PLN", "zł")
- kwota VAT jako "kwota VAT" - typ danych float (usuń inne znaki typu "PLN", "zł")
- numer konta bankowego jako "konto bankowe" - typ danych str

Tekst faktury:
{text}
"""

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        content = response.choices[0].message.content
        # Zakładam, że odpowiedź zawiera JSON - wydobądź go z tekstu
        json_start = content.find("{")
        json_end = content.rfind("}") + 1
        import json
        data = json.loads(content[json_start:json_end])
        return data
    except Exception as e:
        print(f"❌ Błąd podczas przetwarzania przez DeepSeek: {e}")
        return {}
