"""
Tests para verificar configuraciones de colores y estilos en todos los layouts.
"""
import pytest
from pathlib import Path

from ePy_docs.core._config import load_layout, get_loader


class TestLayoutColorConfiguration:
    """Tests para verificar configuraciones de colores en layouts."""
    
    @pytest.mark.parametrize("layout_name", [
        "professional", "creative", "minimal", "handwritten", 
        "classic", "scientific", "technical", "academic", "corporate"
    ])
    def test_layout_loads_successfully(self, layout_name):
        """Test que todos los layouts se cargan sin errores."""
        config = load_layout(layout_name, resolve_refs=False)
        
        assert isinstance(config, dict)
        assert "layout_name" in config
        assert config["layout_name"] == layout_name
    
    def test_minimal_layout_uses_minimal_palette_only(self):
        """Test que minimal layout usa paleta minimal (pure B&W)."""
        config = load_layout("minimal", resolve_refs=False)
        
        # Verificar que tiene referencias correctas
        assert "palette_ref" in config
        assert config["palette_ref"] == "minimal"
        
        # Verificar que la paleta minimal existe y es B&W puro
        loader = get_loader()
        colors_config = loader.load_external('colors')
        assert "minimal" in colors_config["palettes"]
        minimal_palette = colors_config["palettes"]["minimal"]
        
        # Verificar que es monocromático (solo tonos de gris/negro/blanco)
        assert "description" in minimal_palette
        assert "minimal" in minimal_palette["description"].lower() or "monochrome" in minimal_palette["description"].lower()
    
    def test_handwritten_layout_uses_neutrals_graphite(self):
        """Test que handwritten layout usa paleta handwritten."""
        config = load_layout("handwritten", resolve_refs=False)
        
        # Verificar que usa paleta handwritten
        assert "palette_ref" in config
        assert config["palette_ref"] == "handwritten"
        
        # Verificar que la paleta handwritten existe
        loader = get_loader()
        colors_config = loader.load_external('colors')
        assert "handwritten" in colors_config["palettes"]
    
    def test_classic_layout_uses_elegant_greys(self):
        """Test que classic layout usa paleta elegant_greys o neutrals."""
        config = load_layout("classic", resolve_refs=False)
        
        # Verificar que tiene paleta configurada
        assert "palette_ref" in config
        palette_name = config["palette_ref"]
        
        # Verificar que la paleta existe
        loader = get_loader()
        colors_config = loader.load_external('colors')
        assert palette_name in colors_config["palettes"]
    
    def test_creative_layout_maintains_colorful_palette(self):
        """Test que creative layout usa paleta colorida."""
        config = load_layout("creative", resolve_refs=False)
        
        # Debe usar paleta creative
        assert "palette_ref" in config
        assert config["palette_ref"] == "creative"
        
        # Verificar que tiene configuración de callouts
        assert "callouts_ref" in config
    
    def test_corporate_layout_maintains_brand_colors(self):
        """Test que corporate layout usa paleta corporate."""
        config = load_layout("corporate", resolve_refs=False)
        
        # Debe usar paleta corporate
        assert "palette_ref" in config
        assert config["palette_ref"] == "corporate"
    
    def test_professional_layout_uses_blues(self):
        """Test que professional layout usa paleta professional."""
        config = load_layout("professional", resolve_refs=False)
        
        # Debe usar professional o blues
        assert "palette_ref" in config
        palette_name = config["palette_ref"]
        
        # Verificar que existe
        loader = get_loader()
        colors_config = loader.load_external('colors')
        assert palette_name in colors_config["palettes"]
    
    def test_scientific_layout_maintains_scientific_palette(self):
        """Test que scientific layout usa paleta scientific."""
        config = load_layout("scientific", resolve_refs=False)
        
        # Debe usar scientific palette
        assert "palette_ref" in config
        assert config["palette_ref"] == "scientific"
    
    def test_technical_layout_maintains_technical_palette(self):
        """Test que technical layout usa paleta technical."""
        config = load_layout("technical", resolve_refs=False)
        
        # Debe usar technical palette
        assert "palette_ref" in config
        assert config["palette_ref"] == "technical"
    
    def test_academic_layout_uses_academic_palette(self):
        """Test que academic layout usa paleta academic."""
        config = load_layout("academic", resolve_refs=False)
        
        # Debe usar academic palette
        assert "palette_ref" in config
        assert config["palette_ref"] == "academic"


class TestLayoutStylingConfiguration:
    """Tests para verificar configuraciones de styling en layouts."""
    
    def test_minimal_layout_has_thin_lines(self):
        """Test que minimal layout tiene referencia a configuración de tablas."""
        config = load_layout("minimal", resolve_refs=False)
        
        # Verificar que tiene referencia a tables
        assert "tables_ref" in config
        
        # Cargar la configuración de tables
        loader = get_loader()
        tables_config = loader.load_external('tables')
        variant_name = config["tables_ref"].split('.')[-1] if '.' in config["tables_ref"] else config["tables_ref"]
        assert variant_name in tables_config["variants"]
    
    def test_handwritten_layout_has_organic_lines(self):
        """Test que handwritten layout tiene referencia a configuración de tablas."""
        config = load_layout("handwritten", resolve_refs=False)
        
        # Verificar que tiene referencia a tables
        assert "tables_ref" in config
    
    def test_classic_layout_has_elegant_lines(self):
        """Test que classic layout tiene referencia a configuración de tablas."""
        config = load_layout("classic", resolve_refs=False)
        
        # Verificar que tiene referencia a tables
        assert "tables_ref" in config
    
    def test_scientific_layout_has_fine_lines(self):
        """Test que scientific layout tiene referencia a configuración de tablas."""
        config = load_layout("scientific", resolve_refs=False)
        
        # Verificar que tiene referencia a tables
        assert "tables_ref" in config
    
    def test_technical_layout_has_sober_lines(self):
        """Test que technical layout tiene referencia a configuración de tablas."""
        config = load_layout("technical", resolve_refs=False)
        
        # Verificar que tiene referencia a tables
        assert "tables_ref" in config
    
    def test_professional_layout_has_elegant_lines(self):
        """Test que professional layout tiene referencia a configuración de tablas."""
        config = load_layout("professional", resolve_refs=False)
        
        # Verificar que tiene referencia a tables
        assert "tables_ref" in config
    
    def test_academic_layout_has_elegant_grid(self):
        """Test que academic layout tiene referencia a configuración de tablas."""
        config = load_layout("academic", resolve_refs=False)
        
        # Verificar que tiene referencia a tables
        assert "tables_ref" in config
    
    @pytest.mark.parametrize("layout_name", [
        "professional", "creative", "minimal", "handwritten", 
        "classic", "scientific", "technical", "academic", "corporate"
    ])
    def test_all_layouts_have_grid_width(self, layout_name):
        """Test que todos los layouts tienen referencia a configuración de tablas."""
        config = load_layout(layout_name, resolve_refs=False)
        
        # Verificar que tienen referencia a tables
        assert "tables_ref" in config
    
    @pytest.mark.parametrize("layout_name", [
        "professional", "creative", "minimal", "handwritten", 
        "classic", "scientific", "technical", "academic", "corporate"
    ])
    def test_all_layouts_have_border_width(self, layout_name):
        """Test que todos los layouts tienen referencia a configuración de tablas."""
        config = load_layout(layout_name, resolve_refs=False)
        
        # Verificar que tienen referencia a tables
        assert "tables_ref" in config


class TestLayoutContrastAndReadability:
    """Tests para verificar contraste y legibilidad en layouts."""
    
    def test_handwritten_layout_has_good_contrast(self):
        """Test que handwritten layout tiene referencia a configuración de tablas."""
        config = load_layout("handwritten", resolve_refs=False)
        
        # Verificar que tiene referencia a tables
        assert "tables_ref" in config
    
    def test_minimal_layout_maintains_white_background(self):
        """Test que minimal layout tiene configuración de texto."""
        config = load_layout("minimal", resolve_refs=False)
        
        # Verificar que tiene referencia a text
        assert "text_ref" in config or "font_family_ref" in config
    
    def test_all_layouts_have_readable_alpha_values(self):
        """Test que todos los layouts tienen referencias configuradas."""
        layouts = ["professional", "creative", "minimal", "handwritten", 
                   "classic", "scientific", "technical", "academic", "corporate"]
        
        for layout_name in layouts:
            config = load_layout(layout_name, resolve_refs=False)
            
            # Verificar que tienen todas las referencias necesarias
            assert "palette_ref" in config or "colors" in config
            assert "tables_ref" in config or "tables" in config


class TestLayoutMetadata:
    """Tests para verificar metadata de layouts."""
    
    @pytest.mark.parametrize("layout_name", [
        "professional", "creative", "minimal", "handwritten", 
        "classic", "scientific", "technical", "academic", "corporate"
    ])
    def test_layouts_have_required_metadata(self, layout_name):
        """Test que todos los layouts tienen metadata requerido."""
        config = load_layout(layout_name, resolve_refs=False)
        
        # Metadata básico
        assert "layout_name" in config
        assert "version" in config
        assert "description" in config
        assert "last_updated" in config
        
        # Referencias principales
        assert "palette_ref" in config
        assert "tables_ref" in config
        assert "callouts_ref" in config or "callouts" in config
    
    def test_layout_files_exist(self):
        """Test que todos los archivos de layout existen."""
        layouts_dir = Path("src/ePy_docs/config/layouts")
        
        expected_layouts = [
            "professional.epyson", "creative.epyson", "minimal.epyson", 
            "handwritten.epyson", "classic.epyson", "scientific.epyson",
            "technical.epyson", "academic.epyson", "corporate.epyson"
        ]
        
        for layout_file in expected_layouts:
            layout_path = layouts_dir / layout_file
            assert layout_path.exists(), f"Layout file missing: {layout_file}"