import fitz

def check_toc():
    files = ["fazail-e-amal-virtues-of-deeds.pdf", "easy-good-deeds.pdf"]
    
    for filename in files:
        if not os.path.exists(filename):
            print(f"Skipping {filename} (not found)")
            continue
            
        print(f"\nChecking ToC for: {filename}")
        try:
            doc = fitz.open(filename)
            toc = doc.get_toc()
            
            print(f"ToC has {len(toc)} entries.")
            for item in toc[:20]:
                print(item)
            
            # Check deep struct
            print("  Searching for 'Salaat'...")
            count = 0
            for item in toc:
                if "Salaat" in item[1] or "Prayer" in item[1]:
                    print(f"  {item}")
                    count += 1
            if count == 0:
                print("  No 'Salaat' entries found.")
                
        except Exception as e:
            print(f"Error reading {filename}: {e}")

if __name__ == "__main__":
    import os
    check_toc()
