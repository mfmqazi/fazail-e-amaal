import fitz

PDF_FILE = "fazail-e-amal-virtues-of-deeds.pdf"

BOOKS = [
    "STORIES OF THE SAHAABAH",
    "VIRTUES OF THE HOLY QUR",
    "VIRTUES OF SALAAT",
    "VIRTUES OF ZIKR",
    "VIRTUES OF TABLIGH",
    "VIRTUES OF RAMADHAAN",
    "MUSLIM DEGENERATION",
    "SIX FUNDAMENTALS"
]

def map_all_starts():
    doc = fitz.open(PDF_FILE)
    found = {}
    for i in range(len(doc)):
        text = doc[i].get_text().upper()
        for b in BOOKS:
            if b in text:
                if b not in found:
                    found[b] = []
                found[b].append(i)
                
    for b in BOOKS:
        nums = found.get(b, [])
        if nums:
            print(f"{b}: First={nums[0]}, Last={nums[-1]}, Instances={len(nums)}")
        else:
            print(f"{b}: NOT FOUND")

map_all_starts()
