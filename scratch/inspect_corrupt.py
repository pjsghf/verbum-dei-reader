import re

def main():
    with open('extracted_josue.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    corrupt_patterns = [
        "ApƷ", "BƘŃ", "Bǔsqu", "Cġǂp", "DƖs", "ExƋ", "EƷ", "EǇs", "FƖǇ", "Jǔsu", "Orġ", "OŃ", "PrĢ", "SƖst", "Tǔt", "ÚƷ", "ÚǇ", "úƖ"
    ]
    
    with open('scratch/context_output.txt', 'w', encoding='utf-8') as out:
        for idx, line in enumerate(lines):
            for pat in corrupt_patterns:
                if pat in line:
                    out.write(f"Line {idx+1}: {line.strip()}\n")
                    break

if __name__ == '__main__':
    main()
