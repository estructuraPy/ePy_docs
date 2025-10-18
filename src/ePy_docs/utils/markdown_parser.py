"""Utilidades para parsear elementos de archivos Markdown/Quarto."""

import re
import pandas as pd
from typing import List, Tuple, Optional


def extract_markdown_tables(content: str) -> List[Tuple[pd.DataFrame, Optional[str], int, int]]:
    """
    Extrae todas las tablas en formato Markdown de un contenido de texto.
    
    Args:
        content: Contenido del archivo Markdown/Quarto
        
    Returns:
        Lista de tuplas (dataframe, caption, start_line, end_line)
    """
    tables = []
    lines = content.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Buscar inicio de tabla Markdown (línea con pipes |)
        if '|' in line and line.startswith('|'):
            caption = None
            start_line = i
            
            # Verificar si hay un caption antes de la tabla
            if i > 0:
                prev_line = lines[i-1].strip()
                # Buscar formato ": Caption text" o "Table X: Caption"
                if prev_line.startswith(':') or 'Table' in prev_line or 'Tabla' in prev_line:
                    caption = prev_line.lstrip(':').strip()
                    start_line = i - 1
            
            # Extraer todas las líneas de la tabla
            table_lines = []
            while i < len(lines) and '|' in lines[i]:
                table_lines.append(lines[i])
                i += 1
            
            end_line = i - 1
            
            # Parsear la tabla
            if len(table_lines) >= 2:  # Al menos header + separador
                df = _parse_markdown_table(table_lines)
                if df is not None and not df.empty:
                    tables.append((df, caption, start_line, end_line))
            
            continue
        
        i += 1
    
    return tables


def _parse_markdown_table(table_lines: List[str]) -> Optional[pd.DataFrame]:
    """
    Convierte líneas de tabla Markdown en DataFrame.
    
    Args:
        table_lines: Lista de líneas que forman la tabla
        
    Returns:
        DataFrame o None si no se puede parsear
    """
    try:
        # Limpiar líneas
        cleaned_lines = []
        for line in table_lines:
            # Remover pipes al inicio y final, split por pipes
            line = line.strip()
            if line.startswith('|'):
                line = line[1:]
            if line.endswith('|'):
                line = line[:-1]
            cleaned_lines.append(line)
        
        # Primera línea son headers
        headers = [h.strip() for h in cleaned_lines[0].split('|')]
        
        # Segunda línea es el separador (ignorar)
        if len(cleaned_lines) < 2:
            return None
        
        # Resto son datos
        data_rows = []
        for line in cleaned_lines[2:]:
            if line.strip():  # Ignorar líneas vacías
                row = [cell.strip() for cell in line.split('|')]
                # Asegurar que tenga el mismo número de columnas
                if len(row) == len(headers):
                    data_rows.append(row)
        
        if not data_rows:
            return None
        
        # Crear DataFrame
        df = pd.DataFrame(data_rows, columns=headers)
        
        # Intentar convertir columnas numéricas
        for col in df.columns:
            try:
                # Intentar conversión a numérico (sin deprecated errors='ignore')
                numeric_series = pd.to_numeric(df[col].str.replace(',', '.'))
                df[col] = numeric_series
            except (ValueError, AttributeError):
                # Si falla, dejar como está (puede ser texto)
                pass
        
        return df
    
    except Exception as e:
        print(f"⚠️ Error parsing markdown table: {e}")
        return None


def remove_tables_from_content(content: str, tables_info: List[Tuple]) -> str:
    """
    Remueve las tablas del contenido original.
    
    Args:
        content: Contenido original
        tables_info: Lista de tuplas (df, caption, start_line, end_line)
        
    Returns:
        Contenido sin las tablas
    """
    lines = content.split('\n')
    
    # Ordenar tablas por línea de inicio (de atrás hacia adelante para no alterar índices)
    sorted_tables = sorted(tables_info, key=lambda x: x[2], reverse=True)
    
    for _, _, start_line, end_line in sorted_tables:
        # Remover líneas de la tabla
        del lines[start_line:end_line + 1]
        # Agregar un marcador donde estaba la tabla
        lines.insert(start_line, f"<!-- TABLE_PLACEHOLDER_{start_line} -->")
    
    return '\n'.join(lines)
