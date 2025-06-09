import os
import generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

import json
import google.generativeai as genai

def extract_invoice_data_from_bytes(pdf_bytes):
    prompt = (
        "Wyciągnij dane z faktury PDF i zwróć w formacie JSON z polami: numer faktury, "
        "data wystawienia, data sprzedaży/wykonania usługi, sprzedawca, adres sprzedawcy, "
        "nr konta, termin płatności, nazwa usługi/towaru, kwota netto, stawka VAT, kwota VAT, "
        "kwota brutto, kwota do zapłaty. Jeśli czegoś brakuje, wpisz null."
    )
    try:
        # Zakładam, że Gemini API w pythonie pozwala przekazać prompt i plik (bytes) jako content listę
        response = genai.models.generate(
            model="models/gemini-1.5-pro-latest",
            prompt=[prompt, pdf_bytes],
            temperature=0,
            max_output_tokens=512,
        )
        text = response['candidates'][0]['content']
        data = json.loads(text)
        return data
    except json.JSONDecodeError:
        print("⚠️ Nie udało się sparsować JSON z odpowiedzi Gemini AI")
        print("Odpowiedź Gemini:", text)
        return None
    except Exception as e:
        print(f"⚠️ Błąd podczas ekstrakcji danych: {e}")
        return None

