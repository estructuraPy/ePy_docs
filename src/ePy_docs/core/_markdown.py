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
    
    Args:
        file_path: Path to markdown file
        fix_image_paths: Whether to fix image paths
        convert_tables: Whether to convert tables
        output_dir: Output directory
        figure_counter: Current figure counter
        writer_instance: DocumentWriter instance
    """
    # Read markdown file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add to writer
    if writer_instance:
        writer_instance.add_content(content)
