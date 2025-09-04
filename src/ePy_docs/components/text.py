"""
🎨 REINO TEXT - Centralización Absoluta de Tipografía y Texto
================================================================================

📋 ARQUITECTURA SIN BACKWARD COMPATIBILITY:
   - font_families: 20 fuentes + brand obligatoria (Helvética configurable)
   - layout_styles: 8 estilos exactos (academic, technical, corporate, minimal, classic, scientific, professional, creative)
   - Integración brand -> corporate siempre
   - ⚠️ CERO fallbacks - errores inmediatos y transparentes
   - 📡 Caché centralizado vía _load_cached_files únicamente

🔐 FUNCIONES LEGÍTIMAS:
   - resolve_font_reference(): Resolver referencias de fuente
   - resolve_layout_style_typography(): Resolver tipografía por layout_style
   - get_typography_config(): Configuración de tipografía específica
   - validate_text_system_integrity(): Auditoría completa del sistema
   
🚫 PROHIBIDO: Cualquier función legacy, wraps innecesarios, fallbacks
"""

import os
import json
from typing import Dict, Any, List, Tuple
from ePy_docs.components.setup import _load_cached_files

def _load_text_config(sync_files: bool = False) -> Dict[str, Any]:
    """🔧 CARGAR CONFIGURACIÓN DE TEXTO
    
    Usa exclusivamente _load_cached_files para mantener consistencia
    con la arquitectura centralizada.
    
    ⚠️ SIN FALLBACKS: Configuración exacta o falla
    
    Args:
        sync_files: Si True, fuerza recarga desde archivos
        
    Returns:
        Configuración completa de texto
        
    Raises:
        FileNotFoundError: Si text.json no existe
        json.JSONDecodeError: Si el JSON es inválido
        KeyError: Si faltan secciones críticas
    """
    from pathlib import Path
    
    # Construir ruta absoluta al archivo text.json
    components_dir = Path(__file__).parent
    text_json_path = components_dir / "text.json"
    
    if not text_json_path.exists():
        raise FileNotFoundError(f"VIOLACIÓN CRÍTICA: text.json no encontrado en {text_json_path}")
    
    config = _load_cached_files(str(text_json_path), sync_files)
    
    # Validación de arquitectura
    required_sections = ['font_families', 'layout_styles']
    for section in required_sections:
        if section not in config:
            raise KeyError(f"VIOLACIÓN CRÍTICA: Sección '{section}' faltante en text.json")
    
    # Validación de brand obligatoria
    if 'brand' not in config['font_families']:
        raise KeyError("VIOLACIÓN CRÍTICA: Fuente 'brand' obligatoria faltante en font_families")
    
    # Validar layout_styles exactos
    required_layouts = {'academic', 'technical', 'corporate', 'minimal', 'classic', 'scientific', 'professional', 'creative'}
    available_layouts = set(config['layout_styles'].keys())
    
    missing_layouts = required_layouts - available_layouts
    if missing_layouts:
        raise KeyError(f"VIOLACIÓN CRÍTICA: Layout_styles faltantes: {missing_layouts}")
    
    return config

def resolve_font_reference(font_name: str, sync_files: bool = False) -> Dict[str, Any]:
    """🎯 RESOLVER REFERENCIA DE FUENTE
    
    Obtiene la configuración completa de una fuente específica.
    
    ⚠️ SIN FALLBACKS: Fuente exacta o falla
    
    Args:
        font_name: Nombre de la fuente (ej: 'brand', 'serif_academic', etc.)
        sync_files: Si True, fuerza recarga desde archivos
        
    Returns:
        Diccionario con configuración de la fuente:
        {
            'primary': str,    # Nombre de fuente primaria
            'fallback': str,   # Stack de fallback CSS
            'weights': list,   # Pesos disponibles
            'styles': list     # Estilos disponibles
        }
        
    Raises:
        KeyError: Si la fuente no existe
        ValueError: Si la configuración de fuente es inválida
    """
    config = _load_text_config(sync_files)
    
    if font_name not in config['font_families']:
        available_fonts = list(config['font_families'].keys())
        raise KeyError(f"VIOLACIÓN CRÍTICA: Font '{font_name}' no encontrada. Disponibles: {available_fonts}")
    
    font_config = config['font_families'][font_name]
    
    # Validar estructura de fuente
    required_keys = ['primary', 'fallback', 'weights', 'styles']
    for key in required_keys:
        if key not in font_config:
            raise ValueError(f"VIOLACIÓN CRÍTICA: Clave '{key}' faltante en fuente '{font_name}'")
    
    return font_config.copy()

def resolve_layout_style_typography(layout_name: str, element_type: str, sync_files: bool = False) -> Dict[str, Any]:
    """🎯 RESOLVER TIPOGRAFÍA POR LAYOUT_STYLE - Reino TEXT
    
    Obtiene la configuración tipográfica específica para un elemento
    en un layout_style determinado.
    
    ⚠️ SIN FALLBACKS: Configuración exacta o falla transparentemente
    
    Args:
        layout_name: Nombre del layout_style (academic, technical, etc.)
        element_type: Tipo de elemento (h1, h2, h3, normal, caption, etc.)
        sync_files: Si True, fuerza recarga desde archivos
        
    Returns:
        Configuración tipográfica tal como está en text.json
        
    Raises:
        KeyError: Si layout_name o element_type no existen
    """
    config = _load_text_config(sync_files)
    
    # Validar layout_name
    if layout_name not in config['layout_styles']:
        available_layouts = list(config['layout_styles'].keys())
        raise KeyError(f"VIOLACIÓN CRÍTICA: Layout '{layout_name}' no encontrado. Disponibles: {available_layouts}")
    
    layout_config = config['layout_styles'][layout_name]
    
    # Validar existencia de typography
    if 'typography' not in layout_config:
        raise KeyError(f"VIOLACIÓN CRÍTICA: Sección 'typography' faltante en layout '{layout_name}'")
    
    typography = layout_config['typography']
    
    # Validar element_type
    if element_type not in typography:
        available_elements = list(typography.keys())
        raise KeyError(f"VIOLACIÓN CRÍTICA: Elemento '{element_type}' no encontrado en {layout_name}. Disponibles: {available_elements}")
    
    # Devolver configuración tal como está - sin transformaciones
    return typography[element_type].copy()

def get_typography_config(layout_name: str, sync_files: bool = False) -> Dict[str, Dict[str, Any]]:
    """📋 OBTENER CONFIGURACIÓN TIPOGRÁFICA COMPLETA
    
    Retorna toda la configuración tipográfica de un layout_style.
    
    ⚠️ SIN FALLBACKS: Configuración exacta o falla
    
    Args:
        layout_name: Nombre del layout_style
        sync_files: Si True, fuerza recarga desde archivos
        
    Returns:
        Diccionario completo con configuración de todos los elementos tipográficos
        
    Raises:
        KeyError: Si el layout_name no existe
    """
    config = _load_text_config(sync_files)
    
    if layout_name not in config['layout_styles']:
        available_layouts = list(config['layout_styles'].keys())
        raise KeyError(f"VIOLACIÓN CRÍTICA: Layout '{layout_name}' no encontrado. Disponibles: {available_layouts}")
    
    layout_config = config['layout_styles'][layout_name]
    
    if 'typography' not in layout_config:
        raise KeyError(f"VIOLACIÓN CRÍTICA: Sección 'typography' faltante en layout '{layout_name}'")
    
    return layout_config['typography'].copy()

def get_text_config(sync_files: bool = False) -> Dict[str, Any]:
    """🤝 TRATADO COMERCIAL OFICIAL - Reino TEXT
    
    Esta es la ÚNICA función autorizada para que otros reinos
    obtengan recursos del Reino TEXT. Respeta la soberanía del
    gobernante y protege al pueblo (text.json).
    
    Args:
        sync_files: Si usar archivos sincronizados o del paquete
        
    Returns:
        Configuración completa del Reino TEXT
    """
    return _load_text_config(sync_files)

def get_available_fonts(sync_files: bool = False) -> List[str]:
    """📋 OBTENER FUENTES DISPONIBLES
    
    ⚠️ SIN FALLBACKS: Lista exacta o falla
    
    Returns:
        Lista de nombres de fuentes disponibles
    """
    config = _load_text_config(sync_files)
    return list(config['font_families'].keys())

def get_available_layout_styles(sync_files: bool = False) -> List[str]:
    """📋 OBTENER LAYOUT_STYLES DISPONIBLES
    
    ⚠️ SIN FALLBACKS: Lista exacta o falla
    
    Returns:
        Lista de layout_styles disponibles
    """
    config = _load_text_config(sync_files)
    return list(config['layout_styles'].keys())

def get_font_weights(font_name: str, sync_files: bool = False) -> List[str]:
    """📋 OBTENER PESOS DE UNA FUENTE
    
    ⚠️ SIN FALLBACKS: Lista exacta o falla
    
    Args:
        font_name: Nombre de la fuente
        
    Returns:
        Lista de pesos disponibles para la fuente
    """
    font_config = resolve_font_reference(font_name, sync_files)
    return font_config['weights'].copy()

def get_font_styles(font_name: str, sync_files: bool = False) -> List[str]:
    """📋 OBTENER ESTILOS DE UNA FUENTE
    
    ⚠️ SIN FALLBACKS: Lista exacta o falla
    
    Args:
        font_name: Nombre de la fuente
        
    Returns:
        Lista de estilos disponibles para la fuente
    """
    font_config = resolve_font_reference(font_name, sync_files)
    return font_config['styles'].copy()

def build_css_font_stack(font_name: str, sync_files: bool = False) -> str:
    """🎨 CONSTRUIR STACK CSS DE FUENTE
    
    Genera el string CSS completo para usar una fuente con fallbacks.
    
    ⚠️ SIN FALLBACKS INTERNOS: Fuente exacta o falla
    
    Args:
        font_name: Nombre de la fuente
        sync_files: Si True, fuerza recarga desde archivos
        
    Returns:
        String CSS font-family completo
        
    Example:
        "Helvetica, Arial, sans-serif"
        "Times New Roman, serif"
    """
    font_config = resolve_font_reference(font_name, sync_files)
    primary = font_config['primary']
    fallback = font_config['fallback']
    
    # Construir stack CSS
    if ',' in fallback:
        # Fallback ya tiene múltiples fuentes
        return f'"{primary}", {fallback}'
    else:
        # Fallback es genérico
        return f'"{primary}", {fallback}'

def _get_current_layout_config(sync_files: bool = False) -> Dict[str, Any]:
    """Get the configuration for the current active layout.
    
    Args:
        sync_files: Whether to reload files from disk before getting config
        
    Returns:
        Dictionary containing the current layout's configuration including text and headers
    """
    # Import here to avoid circular imports
    from ePy_docs.components.pages import get_current_layout
    
    # Get the current layout name
    current_layout = get_current_layout()
    
    # Load text configuration
    text_config = _load_text_config(sync_files=sync_files)
    
    # Validate layout exists
    if current_layout not in text_config.get('layout_styles', {}):
        available_layouts = list(text_config.get('layout_styles', {}).keys())
        raise KeyError(f"Layout '{current_layout}' not found. Available layouts: {available_layouts}")
    
    # Get layout configuration
    layout_config = text_config['layout_styles'][current_layout]
    
    # Return configuration in the expected format
    return {
        'text': layout_config.get('typography', {}),
        'headers': layout_config.get('typography', {})
    }

class TextFormatter:
    """Text formatting utilities for consistent text formatting across the system."""
    
    @staticmethod
    def format_field(label: str, value: str, sync_files: bool = False) -> str:
        """Format a label-value pair with consistent styling.
        
        Args:
            label: The field label
            value: The field value
            sync_files: Whether to reload configuration
            
        Returns:
            Formatted string for the field
        """
        if not value:
            return ""
            
        # Simple formatting for now - can be enhanced with layout-specific styling
        return f"**{label}**: {value}"

def validate_text_system_integrity(sync_files: bool = False) -> Dict[str, Any]:
    """🔍 VALIDAR INTEGRIDAD COMPLETA DEL SISTEMA DE TEXTO
    
    Audita todo el sistema buscando inconsistencias, referencias rotas,
    o violaciones de la arquitectura.
    
    ⚠️ SIN FALLBACKS: Reporta TODOS los problemas sin ocultarlos
    
    Returns:
        Reporte completo de validación
    """
    report = {
        'valid': True,
        'violations': [],
        'warnings': [],
        'statistics': {}
    }
    
    try:
        config = _load_text_config(sync_files)
        
        # Estadísticas básicas
        report['statistics'] = {
            'total_fonts': len(config['font_families']),
            'total_layout_styles': len(config['layout_styles']),
            'brand_font_exists': 'brand' in config['font_families']
        }
        
        # Validar todas las referencias de fuentes en layout_styles
        broken_font_references = []
        missing_elements = []
        
        for layout_name, layout in config['layout_styles'].items():
            if 'typography' not in layout:
                missing_elements.append({
                    'layout': layout_name,
                    'missing': 'typography',
                    'error': 'Typography section missing'
                })
                continue
                
            typography = layout['typography']
            required_elements = {'h1', 'h2', 'h3', 'body', 'caption', 'code'}
            available_elements = set(typography.keys())
            
            missing_typo_elements = required_elements - available_elements
            if missing_typo_elements:
                missing_elements.append({
                    'layout': layout_name,
                    'missing': 'typography_elements',
                    'elements': list(missing_typo_elements),
                    'error': f'Missing typography elements: {missing_typo_elements}'
                })
            
            # Validar referencias de fuentes
            for element_name, element in typography.items():
                if 'family' in element and 'font' in element['family']:
                    font_ref = element['family']['font']
                    if font_ref not in config['font_families']:
                        broken_font_references.append({
                            'layout': layout_name,
                            'element': element_name,
                            'font_reference': font_ref,
                            'error': f"Font '{font_ref}' not found in font_families"
                        })
        
        # Verificar integración brand -> corporate
        if 'corporate' in config['layout_styles']:
            corp_layout = config['layout_styles']['corporate']
            if 'typography' in corp_layout:
                corp_typo = corp_layout['typography']
                # Verificar que h1, h2, h3 usen brand
                for header in ['h1', 'h2', 'h3']:
                    if (header in corp_typo and 
                        'family' in corp_typo[header] and 
                        'font' in corp_typo[header]['family']):
                        if corp_typo[header]['family']['font'] != 'brand':
                            report['warnings'].append({
                                'layout': 'corporate',
                                'element': header,
                                'issue': f"Corporate layout should use 'brand' font for {header}",
                                'current': corp_typo[header]['family']['font']
                            })
        
        if broken_font_references or missing_elements:
            report['valid'] = False
            report['violations'].extend(broken_font_references)
            report['violations'].extend(missing_elements)
        
        report['statistics']['broken_font_references'] = len(broken_font_references)
        report['statistics']['missing_elements'] = len(missing_elements)
        
    except Exception as e:
        report['valid'] = False
        report['violations'].append({
            'type': 'system_failure',
            'error': str(e)
        })
    
    return report

def format_header_h1(text: str, layout_name: str, sync_files: bool = False) -> str:
    """🎨 FORMAT H1 HEADER - Reino TEXT
    
    Formatea un header H1 usando el layout_style especificado.
    Sin fallbacks, solo configuración pura del Reino TEXT.
    
    Args:
        text: Texto del header
        layout_name: Nombre del layout_style
        sync_files: Si usar archivos sincronizados
        
    Returns:
        Header formateado según el Reino TEXT
    """
    typography = resolve_layout_style_typography(layout_name, 'h1', sync_files)
    return f"# {text}"

def format_header_h2(text: str, layout_name: str, sync_files: bool = False) -> str:
    """🎨 FORMAT H2 HEADER - Reino TEXT
    
    Formatea un header H2 usando el layout_style especificado.
    Sin fallbacks, solo configuración pura del Reino TEXT.
    
    Args:
        text: Texto del header
        layout_name: Nombre del layout_style
        sync_files: Si usar archivos sincronizados
        
    Returns:
        Header formateado según el Reino TEXT
    """
    typography = resolve_layout_style_typography(layout_name, 'h2', sync_files)
    return f"## {text}"

def format_header_h3(text: str, layout_name: str, sync_files: bool = False) -> str:
    """🎨 FORMAT H3 HEADER - Reino TEXT
    
    Formatea un header H3 usando el layout_style especificado.
    Sin fallbacks, solo configuración pura del Reino TEXT.
    
    Args:
        text: Texto del header
        layout_name: Nombre del layout_style
        sync_files: Si usar archivos sincronizados
        
    Returns:
        Header formateado según el Reino TEXT
    """
    typography = resolve_layout_style_typography(layout_name, 'h3', sync_files)
    return f"### {text}"
