test_content = '''---
title: "Test Figure Blocks"
---

# Test Document

This is a test of the Quarto figure block processing.

::: {#fig-CS layout-ncol="2" layout-nrow="1"}

![Propuesta 1](files/viga_reforzada_propuesta_1.png){#fig-round height="4cm"}

![Propuesta 2](files/viga_reforzada_propuesta_2.png){#fig-rect height="4cm"}

Propuestas de reforzamiento
:::

Regular text continues here.
'''

with open('debug_final_test.qmd', 'w', encoding='utf-8') as f:
    f.write(test_content)

# Now read and show it
with open('debug_final_test.qmd', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        print(f'Line {i}: {repr(line)}')