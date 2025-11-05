# DocumentWriter API - Complete Reference

## Initialization

```python
from ePy_docs import DocumentWriter

writer = DocumentWriter(
    document_type: str = "report",  # 'report', 'paper', 'book', 'presentations'
    layout_style: str = None,       # Layout name or None for default
    project_file: str = None,       # Custom project config file
    language: str = None,            # 'en', 'es', 'fr', etc.
    columns: int = None              # Number of columns (1, 2, or 3)
)
```

## Content Methods

### Headers
- `add_h1(text)` - Top-level header
- `add_h2(text)` - Second-level header  
- `add_h3(text)` - Third-level header
- `add_h4(text)` - Fourth-level header
- `add_h5(text)` - Fifth-level header
- `add_h6(text)` - Sixth-level header

### Text
- `add_text(content)` - Add paragraph with markdown support
- `add_content(content)` - Add raw content without processing

### Lists
- `add_list(items, ordered=False)` - Generic list
- `add_unordered_list(items)` - Bullet list
- `add_ordered_list(items)` - Numbered list

## Tables

### Basic Table
```python
writer.add_table(
    df: pd.DataFrame,
    title: str = None,
    show_figure: bool = True,
    columns: Union[float, List[float], None] = None,
    # Additional parameters:
    max_rows_per_table: Union[int, List[int]] = None,  # Split large tables
    hide_columns: Union[str, List[str]] = None,         # Hide columns
    filter_by: Dict[str, Any] = None,                   # Filter rows
    sort_by: Union[str, List[str]] = None,              # Sort by columns
    width_inches: float = None                          # Override width
)
```

### Colored Table with Highlighting
```python
writer.add_colored_table(
    df: pd.DataFrame,
    title: str = None,
    show_figure: bool = True,
    columns: Union[float, List[float], None] = None,
    # Color highlighting parameters:
    highlight_columns: Union[str, List[str]] = None,    # Columns to highlight
    palette_name: str = None,                           # Color palette
    pallete_name: str = None,                           # Alias (accepts typo)
    # Additional parameters (same as add_table):
    max_rows_per_table: Union[int, List[int]] = None,
    hide_columns: Union[str, List[str]] = None,
    filter_by: Dict[str, Any] = None,
    sort_by: Union[str, List[str]] = None,
    width_inches: float = None
)
```

**Available Palettes:**
- Colors: `blues`, `reds`, `greens`, `oranges`, `purples`
- Neutral: `minimal` (B&W), `monochrome` (grays), `neutrals`
- Professional: `professional`, `scientific`, `technical`, `corporate`
- Status: `status_positive`, `status_negative`, `status_warning`, `status_info`

## Figures

### Matplotlib Plots
```python
writer.add_plot(
    fig,                                               # Matplotlib figure
    title: str = None,
    caption: str = None,
    source: str = None,
    columns: Union[float, List[float], None] = None,
    palette_name: str = None                           # Restrict colors to palette
)
```

### Images
```python
writer.add_image(
    path: str,                                         # File path or URL
    caption: str = None,
    width: str = None,                                 # Deprecated
    columns: Union[float, List[float], None] = None,
    alt_text: str = None,                              # Accessibility
    responsive: bool = True                            # Responsive HTML
)
```

## Equations

```python
# Block equation
writer.add_equation(
    latex_code: str,                                   # LaTeX without delimiters
    caption: str = None,
    label: str = None                                  # For cross-references
)

# Inline equation
writer.add_inline_equation(latex_code: str)
```

## Callouts

### Generic Callout
```python
writer.add_callout(
    content: str,
    type: str = "note",                                # See types below
    title: str = None
)
```

### Shortcut Methods
- `add_note(content, title=None)` - Blue, general info
- `add_tip(content, title=None)` - Green, helpful suggestions
- `add_warning(content, title=None)` - Yellow/Orange, cautions
- `add_error(content, title=None)` - Red, error messages
- `add_success(content, title=None)` - Green, success messages
- `add_caution(content, title=None)` - Orange, important warnings
- `add_important(content, title=None)` - Purple/Red, critical info
- `add_information(content, title=None)` - Blue, informational
- `add_recommendation(content, title=None)` - Green, recommended actions
- `add_advice(content, title=None)` - Blue, advisory content
- `add_risk(content, title=None)` - Red, risk assessment

## Code Chunks

```python
# Display only (not executed)
writer.add_chunk(
    code: str,
    language: str = 'python',
    eval: bool = False,
    echo: bool = True,
    output: bool = False
)

# Executable (runs during generation)
writer.add_chunk_executable(
    code: str,
    language: str = 'python',
    eval: bool = True,
    echo: bool = True,
    output: bool = True
)
```

## Cross-References

```python
# Reference to table/figure/equation
writer.add_reference(
    ref_type: str,                                     # 'table', 'figure', 'equation'
    ref_id: str,                                       # Label assigned to element
    custom_text: str = None
)

# Citation from bibliography
writer.add_citation(
    citation_key: str,                                 # Key from .bib file
    page: str = None                                   # Page number(s)
)
```

## File Import

```python
# Import Markdown file
writer.add_markdown_file(
    file_path: str,
    fix_image_paths: bool = True,
    convert_tables: bool = True
)

# Import Quarto file
writer.add_quarto_file(
    file_path: str,
    include_yaml: bool = False,                        # Strip YAML frontmatter
    fix_image_paths: bool = True,
    convert_tables: bool = True
)
```

**Note:** Spacers are automatically added before and after imported content to prevent markdown rendering issues.

## Generation

```python
result = writer.generate(
    markdown: bool = False,                            # Generate .md
    html: bool = True,                                 # Generate .html
    pdf: bool = True,                                  # Generate .pdf
    qmd: bool = True,                                  # Generate .qmd
    tex: bool = False,                                 # Generate .tex
    output_filename: str = None                        # Base filename
)

# Returns dict with paths:
# {
#     'html': '/path/to/file.html',
#     'pdf': '/path/to/file.pdf',
#     'qmd': '/path/to/file.qmd',
#     ...
# }
```

## Properties (Read-only)

- `writer.document_type` - Document type ('report', 'paper', etc.)
- `writer.layout_style` - Current layout style
- `writer.output_dir` - Output directory path
- `writer.language` - Document language
- `writer.table_counter` - Current table number
- `writer.figure_counter` - Current figure number
- `writer.note_counter` - Current note number
- `writer.content_buffer` - List of content strings
- `writer.generated_images` - List of generated image paths

## Method Chaining

All add_* methods return `self`, enabling method chaining:

```python
(writer
    .add_h1("Title")
    .add_text("Introduction")
    .add_table(df, title="Results")
    .add_plot(fig, palette_name='blues')
    .generate(output_filename="Report"))
```

## Column Width Specification

For tables and figures, `columns` parameter accepts:

- `None` - Uses full page width (default)
- `float` - Number of columns to span (e.g., `1.0`, `1.5`, `2.0`)
- `List[float]` - Specific widths in inches for different document types

Example:
```python
writer.add_table(df, columns=2.0)  # Span 2 columns
writer.add_plot(fig, columns=1.5)  # Span 1.5 columns
```
