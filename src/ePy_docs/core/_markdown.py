"""
Markdown Processing Module

Handles:
- Markdown file reading and parsing
- Markdown content extraction
- Markdown to QMD conversion
"""

from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path


# =============================================================================
# MARKDOWN READING
# =============================================================================

def read_markdown_file(file_path: Path) -> str:
    """
    Read markdown file content.
    
    Args:
        file_path: Path to markdown file
        
    Returns:
        Markdown content as string
        
    Raises:
        FileNotFoundError: If file doesn't exist
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Markdown file not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return content


# =============================================================================
# MARKDOWN PARSING
# =============================================================================

def extract_frontmatter(content: str) -> Tuple[Optional[Dict[str, Any]], str]:
    """
    Extract YAML frontmatter from markdown content.
    
    Args:
        content: Markdown content
        
    Returns:
        Tuple of (frontmatter_dict, body_content)
        Returns (None, content) if no frontmatter found
    """
    import yaml
    
    lines = content.split('\n')
    
    # Check if starts with ---
    if not lines or lines[0].strip() != '---':
        return None, content
    
    # Find closing ---
    closing_idx = None
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            closing_idx = i
            break
    
    if closing_idx is None:
        return None, content
    
    # Extract YAML content
    yaml_content = '\n'.join(lines[1:closing_idx])
    body_content = '\n'.join(lines[closing_idx + 1:])
    
    try:
        frontmatter = yaml.safe_load(yaml_content)
        return frontmatter, body_content
    except yaml.YAMLError:
        # If YAML parsing fails, return original content
        return None, content


def parse_markdown_sections(content: str) -> List[Dict[str, str]]:
    """
    Parse markdown content into sections based on headings.
    
    Args:
        content: Markdown content
        
    Returns:
        List of sections, each with {'level': int, 'title': str, 'content': str}
    """
    import re
    
    lines = content.split('\n')
    sections = []
    current_section = None
    
    for line in lines:
        # Check if line is a heading
        heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
        
        if heading_match:
            # Save previous section if exists
            if current_section is not None:
                sections.append(current_section)
            
            # Start new section
            level = len(heading_match.group(1))
            title = heading_match.group(2).strip()
            current_section = {
                'level': level,
                'title': title,
                'content': ''
            }
        else:
            # Add line to current section
            if current_section is not None:
                current_section['content'] += line + '\n'
            else:
                # Content before first heading
                if sections == [] and line.strip():
                    sections.append({
                        'level': 0,
                        'title': '',
                        'content': line + '\n'
                    })
    
    # Add last section
    if current_section is not None:
        sections.append(current_section)
    
    return sections


# =============================================================================
# MARKDOWN TO QMD CONVERSION
# =============================================================================

def convert_markdown_to_qmd(
    md_path: Path,
    output_path: Path,
    add_yaml: bool = True,
    yaml_config: Optional[Dict[str, Any]] = None
) -> Path:
    """
    Convert markdown file to Quarto QMD format.
    
    Args:
        md_path: Path to input markdown file
        output_path: Path to output QMD file
        add_yaml: Whether to add YAML frontmatter
        yaml_config: Custom YAML configuration (if add_yaml=True)
        
    Returns:
        Path to created QMD file
    """
    import yaml
    
    # Read markdown content
    content = read_markdown_file(md_path)
    
    # Extract existing frontmatter
    frontmatter, body = extract_frontmatter(content)
    
    # Merge with provided yaml_config
    if add_yaml:
        if yaml_config:
            # Start with provided config
            final_yaml = yaml_config.copy()
            # Merge with existing frontmatter
            if frontmatter:
                final_yaml.update(frontmatter)
        else:
            # Use existing frontmatter or create minimal config
            final_yaml = frontmatter if frontmatter else {
                'title': md_path.stem.replace('_', ' ').title()
            }
        
        # Generate YAML string
        yaml_str = yaml.dump(final_yaml, default_flow_style=False, sort_keys=False)
        
        # Create QMD content
        qmd_content = f'''---
{yaml_str}---

{body}
'''
    else:
        # No YAML, just copy content
        qmd_content = body
    
    # Write to output file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(qmd_content)
    
    return output_path


# =============================================================================
# MARKDOWN UTILITIES
# =============================================================================

def validate_markdown_file(file_path: Path) -> bool:
    """
    Validate that file is a markdown file.
    
    Args:
        file_path: Path to file
        
    Returns:
        True if valid markdown file
        
    Raises:
        ValueError: If not a markdown file
    """
    valid_extensions = ['.md', '.markdown', '.qmd']
    
    if file_path.suffix.lower() not in valid_extensions:
        raise ValueError(
            f"Not a markdown file: {file_path}\n"
            f"Valid extensions: {', '.join(valid_extensions)}"
        )
    
    return True


def count_words(content: str) -> int:
    """
    Count words in markdown content (excluding code blocks).
    
    Args:
        content: Markdown content
        
    Returns:
        Word count
    """
    import re
    
    # Remove code blocks
    content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
    content = re.sub(r'`[^`]+`', '', content)
    
    # Remove markdown syntax
    content = re.sub(r'[#*_\[\](){}]', '', content)
    
    # Count words
    words = content.split()
    return len(words)


# =============================================================================
# MARKDOWN FILE PROCESSING FOR WRITER
# =============================================================================

def process_markdown_file(
    file_path: str,
    fix_image_paths: bool = True,
    convert_tables: bool = True,
    output_dir: str = None,
    figure_counter: int = 1,
    writer_instance = None
) -> None:
    """
    Process markdown file and add to writer.
    
    Automatically processes:
    - Markdown tables: Converts to styled image tables
    - Images: Extracts caption from markdown and adds as figure
    - Text content: Preserves as-is
    
    Args:
        file_path: Path to markdown file
        fix_image_paths: Whether to fix image paths
        convert_tables: Whether to convert tables to styled images
        output_dir: Output directory
        figure_counter: Current figure counter
        writer_instance: DocumentWriter instance
    """
    import re
    import os
    from pathlib import Path
    
    # Read markdown file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if not writer_instance:
        return
    
    # Detect if writer_instance is the wrapper or the core
    # If it has _core attribute, it's the wrapper; otherwise it's the core itself
    core = writer_instance._core if hasattr(writer_instance, '_core') else writer_instance
    
    # Add spacer before imported content
    core.content_buffer.append("\n\n")
    
    # Process content if conversion is enabled
    if convert_tables or fix_image_paths:
        # Split content into blocks (tables, images, text)
        lines = content.split('\n')
        i = 0
        current_block = []
        
        while i < len(lines):
            line = lines[i]
            
            # Detect markdown table
            if convert_tables and '|' in line and i + 1 < len(lines) and '|' in lines[i + 1]:
                # Save any accumulated text
                if current_block:
                    core.content_buffer.append('\n'.join(current_block) + '\n\n')
                    current_block = []
                
                # Extract table
                table_lines = [line]
                i += 1
                while i < len(lines) and ('|' in lines[i] or lines[i].strip() == ''):
                    if '|' in lines[i]:
                        table_lines.append(lines[i])
                    i += 1
                
                # Try to convert table to DataFrame
                try:
                    import pandas as pd
                    import io
                    
                    # Parse markdown table
                    table_text = '\n'.join(table_lines)
                    print(f"DEBUG: Table detected with {len(table_lines)} lines")
                    for idx, tline in enumerate(table_lines):
                        print(f"  Line {idx}: {repr(tline)}")
                    
                    # Remove alignment row (e.g., |---|---|) - be more specific
                    rows = []
                    for r in table_lines:
                        # Skip lines that are only alignment characters
                        cleaned = r.replace('|', '').replace(' ', '').replace('\t', '')
                        if cleaned and not all(c in '-:' for c in cleaned):
                            rows.append(r)
                    
                    print(f"DEBUG: After filtering alignment rows: {len(rows)} rows")
                    for idx, row in enumerate(rows):
                        print(f"  Row {idx}: {repr(row)}")
                    
                    if len(rows) >= 2:  # At least header + 1 data row
                        # Parse table - handle tables with varying column counts
                        parsed_rows = []
                        for row in rows:
                            cells = [cell.strip() for cell in row.split('|')[1:-1]]
                            parsed_rows.append(cells)
                        
                        # Find maximum number of columns across all rows
                        max_cols = max(len(row) for row in parsed_rows)
                        
                        # Remember original header length before padding
                        original_header_cols = len(parsed_rows[0]) if parsed_rows else 0
                        
                        # Pad rows with fewer columns with empty strings
                        for row in parsed_rows:
                            while len(row) < max_cols:
                                row.append('')
                        
                        # Use first row as header, but if header has fewer columns than data,
                        # generate additional column names
                        header = parsed_rows[0]
                        if original_header_cols < max_cols:
                            # Replace empty padded columns with unnamed columns
                            for i in range(original_header_cols, max_cols):
                                header[i] = f'Unnamed_{i}'
                        
                        df = pd.DataFrame(parsed_rows[1:], columns=header)
                        print(f"DEBUG: DataFrame created successfully: {df.shape}")
                        print(f"DEBUG: Columns: {list(df.columns)}")
                        
                        # Look for caption in previous lines
                        caption = None
                        if i > len(table_lines):
                            for prev_line in reversed(lines[max(0, i - len(table_lines) - 5):i - len(table_lines)]):
                                if prev_line.strip().startswith(':') or 'Table' in prev_line or 'Tabla' in prev_line:
                                    caption = prev_line.strip().lstrip(':').strip()
                                    break
                        
                        # Add as styled table (show_figure=True to save as image with proper counter)
                        print(f"DEBUG: Adding table to document with caption: {caption}")
                        core.add_table(df, title=caption, show_figure=True)
                        print("DEBUG: Table added successfully - should be converted to image")
                        continue
                except Exception as e:
                    print(f"DEBUG: Exception during table parsing: {e}")
                    import traceback
                    traceback.print_exc()
                    # If parsing fails, add as raw markdown
                    core.content_buffer.append('\n'.join(table_lines) + '\n\n')
                    continue
            
            # Detect markdown image: ![alt](path)
            elif fix_image_paths and line.strip().startswith('!['):
                # Save any accumulated text
                if current_block:
                    core.content_buffer.append('\n'.join(current_block) + '\n\n')
                    current_block = []
                
                # Extract image
                match = re.match(r'!\[(.*?)\]\((.*?)\)', line.strip())
                if match:
                    alt_text = match.group(1)
                    image_path = match.group(2)
                    
                    # Fix path if relative
                    if not image_path.startswith('http') and not os.path.isabs(image_path):
                        base_dir = Path(file_path).parent
                        image_path = str(base_dir / image_path)
                    
                    # DEBUG
                    # print(f"DEBUG: Processing image: {image_path}, exists: {os.path.exists(image_path)}")
                    
                    # Look for caption in next line
                    caption = alt_text if alt_text else None
                    if i + 1 < len(lines) and lines[i + 1].strip().startswith(':'):
                        caption = lines[i + 1].strip().lstrip(':').strip()
                        i += 1
                    
                    # Add as figure if image exists
                    # Calculate width based on document columns to prevent overflow
                    if os.path.exists(image_path):
                        try:
                            # Get document type and layout from writer
                            document_type = getattr(core, 'document_type', 'report')
                            layout_style = getattr(core, 'layout_style', 'classic')
                            
                            # Calculate appropriate width spanning all columns
                            from ePy_docs.core._columns import calculate_content_width, get_width_string
                            from ePy_docs.core._config import load_layout
                            
                            try:
                                layout_config = load_layout(layout_style)
                                # Get default columns for this document type
                                default_columns = 1
                                if document_type in layout_config:
                                    columns_config = layout_config[document_type].get('columns', {})
                                    default_columns = columns_config.get('default', 1)
                                
                                # Calculate width spanning all columns
                                width_inches = calculate_content_width(
                                    document_type=document_type,
                                    layout_columns=default_columns,
                                    columns=default_columns  # Span full width
                                )
                                width_str = get_width_string(width_inches)
                            except Exception:
                                # Fallback to safe default (6.5in fits most standard pages)
                                width_str = '6.5in'
                            
                            core.add_image(image_path, caption=caption, width=width_str)
                            i += 1
                            continue
                        except Exception as ex:
                            # print(f"DEBUG: Exception adding image: {ex}")
                            pass
                    
                    # If image doesn't exist or fails, add as raw markdown
                    core.content_buffer.append(line + '\n')
                    i += 1
                    continue
                else:
                    current_block.append(line)
            
            else:
                current_block.append(line)
            
            i += 1
        
        # Add remaining text
        if current_block:
            core.content_buffer.append('\n'.join(current_block))
    else:
        # No conversion, add raw content
        core.content_buffer.append(content)
    
    # Add trailing spacer for next content
    core.content_buffer.append("\n\n")
