"""
Test to debug why tables aren't being detected
"""

test_table = """| Condición de análisis | Riesgo de daños económicos y ambientales | Riesgo de pérdida de vidas |
| :-------------------- | :------------------------------------- | :------------------------ |
|                       |                                        | Bajo    | Medio   | Alto   |
| Estática              | Bajo                                    | 1,20    | 1,30    | 1,40   |
|                       | Medio                                   | 1,30    | 1,40    | 1,50   |"""

table_lines = test_table.split('\n')

print("Total lines:", len(table_lines))
for i, line in enumerate(table_lines):
    print(f"Line {i}: {repr(line)}")

print("\n" + "="*70)
print("Filtering alignment rows...")
print("="*70)

rows = [r for r in table_lines if not all(c in '|-: ' for c in r if c != '|')]

print(f"\nRows after filtering: {len(rows)}")
for i, row in enumerate(rows):
    print(f"Row {i}: {repr(row)}")

print("\n" + "="*70)
print("Parsing rows...")
print("="*70)

parsed_rows = []
for row in rows:
    cells = [cell.strip() for cell in row.split('|')[1:-1]]
    parsed_rows.append(cells)
    print(f"Parsed: {cells} (len={len(cells)})")

# Find max columns
max_cols = max(len(row) for row in parsed_rows)
print(f"\nMax columns: {max_cols}")

# Remember original header length
original_header_cols = len(parsed_rows[0])
print(f"Original header columns: {original_header_cols}")

# Pad rows
for row in parsed_rows:
    while len(row) < max_cols:
        row.append('')

# Create header
header = parsed_rows[0]
if original_header_cols < max_cols:
    for i in range(original_header_cols, max_cols):
        header[i] = f'Unnamed_{i}'

print(f"\nFinal header: {header}")
print(f"Data rows: {len(parsed_rows)-1}")

import pandas as pd
df = pd.DataFrame(parsed_rows[1:], columns=header)
print("\nDataFrame:")
print(df)
