import re

def _is_figure_block_start(line):
    pattern = r':::\s*\{#fig-[\w-]+[^}]*\}'
    result = bool(re.match(pattern, line.strip()))
    print(f'Testing line: {repr(line)}')
    print(f'Pattern: {pattern}')
    print(f'Result: {result}')
    return result

# Test our lines  
test_lines = [
    '::: {#fig-CS layout-ncol="2" layout-nrow="1"}',
    '![Propuesta 1](files/viga_reforzada_propuesta_1.png){#fig-round height="4cm"}',
    '![Propuesta 2](files/viga_reforzada_propuesta_2.png){#fig-rect height="4cm"}'
]

for line in test_lines:
    _is_figure_block_start(line)
    print('---')