import json
import csv

def save_as_json(data_str, filename):
    data = json.loads(data_str)
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def save_as_csv(data_str, filename):
    data = json.loads(data_str)
    headers = ["nazwa", "netto", "vat_stawka", "vat_kwota", "brutto"]
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for item in data.get("pozycje", []):
            writer.writerow({
                "nazwa": item.get("nazwa"),
                "netto": item.get("netto"),
                "vat_stawka": item.get("vat_stawka"),
                "vat_kwota": item.get("vat_kwota"),
                "brutto": item.get("brutto")
            })
