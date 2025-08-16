import re

# Read the file
with open('src/ePy_docs/components/tables.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Define the pattern to match the try/except block
try_except_pattern = r'''(        # Integrate source into caption if provided
        if source:
            )try:(.*?)except:(.*?)(\n\n        # Create table markdown)'''

# Define the replacement
replacement = r'''\1if 'source' not in table_config:
                raise ValueError("Missing 'source' configuration in tables.json")
            source_config = table_config['source']
            
            if 'enable_source' not in source_config:
                raise ValueError("Missing 'enable_source' in source configuration")
            if source_config['enable_source']:
                if 'source_format' not in source_config:
                    raise ValueError("Missing 'source_format' in source configuration")
                source_text = source_config['source_format'].format(source=source)
                if table_caption:
                    table_caption = f"{table_caption} {source_text}"
                else:
                    table_caption = source_text\4'''

# Apply the replacement with DOTALL flag to match newlines
content = re.sub(try_except_pattern, replacement, content, flags=re.DOTALL)

# Write back
with open('src/ePy_docs/components/tables.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ Try/except fallbacks eliminados en ambas funciones')
