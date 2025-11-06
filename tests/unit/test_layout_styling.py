"""
Tests para verificar configuraciones de colores y estilos en todos los layouts.
"""
import pytest
from pathlib import Path

from ePy_docs.core._config import load_layout


class TestLayoutColorConfiguration:
    """Tests para verificar configuraciones de colores en layouts."""
    
    @pytest.mark.parametrize("layout_name", [
        "professional", "creative", "minimal", "handwritten", 
        "classic", "scientific", "technical", "academic", "corporate"
    ])
    def test_layout_loads_successfully(self, layout_name):
        """Test que todos los layouts se cargan sin errores."""
        config = load_layout(layout_name)
        
        assert isinstance(config, dict)
        assert "layout_name" in config
        assert config["layout_name"] == layout_name
    
    def test_minimal_layout_uses_minimal_palette_only(self):
        """Test que minimal layout solo usa paleta minimal (pure B&W)."""
        config = load_layout("minimal")
        
        # Verificar configuración de tablas
        layout_config = config["colors"]["layout_config"]
        tables_config = layout_config["tables"]
        
        # Todas las paletas deben ser minimal (pure B&W, no grays)
        assert layout_config["default_palette"] == "minimal"
        assert tables_config["alt_row"]["palette"] == "minimal"
        assert tables_config["border"]["palette"] == "minimal"
        
        # Headers deben ser minimal
        for header_type in ["default", "engineering", "environmental", "financial"]:
            assert tables_config["header"][header_type]["palette"] == "minimal"
        
        # Status deben ser minimal
        for status_type in ["fail", "pass", "pending", "warning"]:
            assert tables_config["status"][status_type]["palette"] == "minimal"
    
    def test_handwritten_layout_uses_neutrals_graphite(self):
        """Test que handwritten layout usa neutrals para efecto grafito."""
        config = load_layout("handwritten")
        
        tables_config = config["colors"]["layout_config"]["tables"]
        
        # Debe usar neutrals como paleta principal
        assert tables_config["header"]["default"]["palette"] == "neutrals"
        assert tables_config["alt_row"]["palette"] == "neutrals"
        
        # Typography debe usar neutrals
        typography = config["colors"]["layout_config"]["typography"]
        assert typography["h1"]["palette"] == "neutrals"
        assert typography["h2"]["palette"] == "neutrals"
        assert typography["h3"]["palette"] == "neutrals"
    
    def test_classic_layout_uses_elegant_greys(self):
        """Test que classic layout usa grises elegantes."""
        config = load_layout("classic")
        
        tables_config = config["colors"]["layout_config"]["tables"]
        
        # Debe usar neutrals para grises clásicos
        assert tables_config["header"]["default"]["palette"] == "neutrals"
        
        # Verificar que callouts usan neutrals
        callouts = config["callouts"]
        for callout_type in ["caution", "important", "note", "tip", "warning"]:
            # Check palette in the colors configuration
            assert callouts[callout_type]["colors"]["text"]["palette"] == "neutrals"
    
    def test_creative_layout_maintains_colorful_palette(self):
        """Test que creative layout mantiene paletas coloridas."""
        config = load_layout("creative")
        
        # Debe mantener paleta creative como principal
        tables_config = config["colors"]["layout_config"]["tables"]
        assert tables_config["header"]["default"]["palette"] == "creative"
        
        # Callouts deben mantener colores vibrantes
        callouts = config["callouts"]
        # Check palettes in the colors configuration
        assert callouts["caution"]["colors"]["text"]["palette"] == "purples"
        assert callouts["important"]["colors"]["text"]["palette"] == "reds"
        assert callouts["tip"]["colors"]["text"]["palette"] == "greens"
        assert callouts["warning"]["colors"]["text"]["palette"] == "oranges"
    
    def test_corporate_layout_maintains_brand_colors(self):
        """Test que corporate layout mantiene colores de marca."""
        config = load_layout("corporate")
        
        tables_config = config["colors"]["layout_config"]["tables"]
        
        # Debe mantener paleta corporate
        assert tables_config["header"]["default"]["palette"] == "corporate"
        
        # Typography debe usar corporate
        typography = config["colors"]["layout_config"]["typography"]
        assert typography["h1"]["palette"] == "corporate"
        assert typography["caption"]["palette"] == "corporate"
    
    def test_professional_layout_uses_blues(self):
        """Test que professional layout usa paleta blues."""
        config = load_layout("professional")
        
        tables_config = config["colors"]["layout_config"]["tables"]
        
        # Debe usar blues como paleta principal
        assert tables_config["header"]["default"]["palette"] == "blues"
    
    def test_scientific_layout_maintains_scientific_palette(self):
        """Test que scientific layout mantiene paleta scientific."""
        config = load_layout("scientific")
        
        tables_config = config["colors"]["layout_config"]["tables"]
        
        # Debe mantener scientific palette
        assert tables_config["header"]["default"]["palette"] == "scientific"
        
        # Callouts deben usar scientific
        callouts = config["callouts"]
        assert callouts["note"]["colors"]["text"]["palette"] == "scientific"
    
    def test_technical_layout_maintains_technical_palette(self):
        """Test que technical layout mantiene paleta technical."""
        config = load_layout("technical")
        
        tables_config = config["colors"]["layout_config"]["tables"]
        
        # Debe usar technical palette
        assert tables_config["header"]["default"]["palette"] == "technical"
        
        # Category palettes deben ser technical
        category_palettes = config["tables"]["layout_config"]["category_palettes"]
        for category in category_palettes.values():
            assert category == "technical"
    
    def test_academic_layout_uses_academic_palette(self):
        """Test que academic layout usa paleta academic."""
        config = load_layout("academic")
        
        tables_config = config["colors"]["layout_config"]["tables"]
        
        # Debe usar academic como paleta principal
        assert tables_config["header"]["default"]["palette"] == "academic"


class TestLayoutStylingConfiguration:
    """Tests para verificar configuraciones de styling en layouts."""
    
    def test_minimal_layout_has_thin_lines(self):
        """Test que minimal layout tiene líneas muy finas."""
        config = load_layout("minimal")
        
        styling = config["tables"]["layout_config"]["styling"]
        
        # Grid width debe ser muy fino
        assert styling["grid_width"] == 0.1
        assert styling["border"]["width"] == 0.05
    
    def test_handwritten_layout_has_organic_lines(self):
        """Test que handwritten layout tiene líneas orgánicas."""
        config = load_layout("handwritten")
        
        styling = config["tables"]["layout_config"]["styling"]
        
        # Debe tener grid_width moderado para efecto orgánico
        assert styling["grid_width"] == 0.8
        assert styling["border"]["width"] == 0.3
    
    def test_classic_layout_has_elegant_lines(self):
        """Test que classic layout tiene líneas elegantes."""
        config = load_layout("classic")
        
        styling = config["tables"]["layout_config"]["styling"]
        
        # Debe tener líneas refinadas
        assert styling["grid_width"] == 0.5
        assert styling["border"]["width"] == 0.2
    
    def test_scientific_layout_has_fine_lines(self):
        """Test que scientific layout tiene líneas finas."""
        config = load_layout("scientific")
        
        styling = config["tables"]["layout_config"]["styling"]
        
        # Debe tener líneas finas para aspecto científico
        assert styling["grid_width"] == 0.3
        assert styling["border"]["width"] == 0.15
    
    def test_technical_layout_has_sober_lines(self):
        """Test que technical layout tiene líneas sobrias."""
        config = load_layout("technical")
        
        styling = config["tables"]["layout_config"]["styling"]
        
        # Debe tener líneas moderadas y sobrias
        assert styling["grid_width"] == 0.4
        assert styling["border"]["width"] == 0.2
    
    def test_professional_layout_has_elegant_lines(self):
        """Test que professional layout tiene líneas elegantes."""
        config = load_layout("professional")
        
        styling = config["tables"]["layout_config"]["styling"]
        
        # Debe tener grid_width elegante
        assert styling["grid_width"] == 0.3
    
    def test_academic_layout_has_elegant_grid(self):
        """Test que academic layout tiene grid elegante."""
        config = load_layout("academic")
        
        styling = config["tables"]["layout_config"]["styling"]
        
        # Debe tener grid_width elegante
        assert styling["grid_width"] == 0.25
    
    @pytest.mark.parametrize("layout_name", [
        "professional", "creative", "minimal", "handwritten", 
        "classic", "scientific", "technical", "academic", "corporate"
    ])
    def test_all_layouts_have_grid_width(self, layout_name):
        """Test que todos los layouts tienen grid_width configurado."""
        config = load_layout(layout_name)
        
        styling = config["tables"]["layout_config"]["styling"]
        
        assert "grid_width" in styling
        assert isinstance(styling["grid_width"], (int, float))
        assert styling["grid_width"] > 0
    
    @pytest.mark.parametrize("layout_name", [
        "professional", "creative", "minimal", "handwritten", 
        "classic", "scientific", "technical", "academic", "corporate"
    ])
    def test_all_layouts_have_border_width(self, layout_name):
        """Test que todos los layouts tienen border width configurado."""
        config = load_layout(layout_name)
        
        styling = config["tables"]["layout_config"]["styling"]
        
        assert "border" in styling
        assert "width" in styling["border"]
        assert isinstance(styling["border"]["width"], (int, float))
        assert styling["border"]["width"] > 0


class TestLayoutContrastAndReadability:
    """Tests para verificar contraste y legibilidad en layouts."""
    
    def test_handwritten_layout_has_good_contrast(self):
        """Test que handwritten layout tiene buen contraste header/texto."""
        config = load_layout("handwritten")
        
        tables_config = config["colors"]["layout_config"]["tables"]
        
        # Header debe usar tone claro con alpha bajo para buen contraste
        assert tables_config["header_bg_alpha"] == 0.3  # Alpha bajo
        
        # Header tone debe ser claro (secondary)
        assert tables_config["header"]["default"]["tone"] == "secondary"
        
        # Header color debe ser oscuro (senary) para contraste
        typography = config["colors"]["layout_config"]["typography"]
        assert typography["header_color"]["tone"] == "senary"
    
    def test_minimal_layout_maintains_white_background(self):
        """Test que minimal layout mantiene fondo blanco."""
        config = load_layout("minimal")
        
        typography = config["colors"]["layout_config"]["typography"]
        
        # Background debe ser blanco (primary)
        assert typography["background_color"]["palette"] == "neutrals"
        assert typography["background_color"]["tone"] == "primary"
    
    def test_all_layouts_have_readable_alpha_values(self):
        """Test que todos los layouts tienen valores alpha legibles."""
        layouts = ["professional", "creative", "minimal", "handwritten", 
                  "classic", "scientific", "technical", "academic", "corporate"]
        
        for layout_name in layouts:
            config = load_layout(layout_name)
            tables_config = config["colors"]["layout_config"]["tables"]
            
            # Alpha values deben estar en rango razonable
            if "header_bg_alpha" in tables_config:
                alpha = tables_config["header_bg_alpha"]
                assert 0.0 <= alpha <= 1.0, f"Layout {layout_name} alpha out of range: {alpha}"
            
            if "alt_row_alpha" in tables_config:
                alpha = tables_config["alt_row_alpha"]
                assert 0.0 <= alpha <= 1.0, f"Layout {layout_name} alt_row_alpha out of range: {alpha}"


class TestLayoutMetadata:
    """Tests para verificar metadata de layouts."""
    
    @pytest.mark.parametrize("layout_name", [
        "professional", "creative", "minimal", "handwritten", 
        "classic", "scientific", "technical", "academic", "corporate"
    ])
    def test_layouts_have_required_metadata(self, layout_name):
        """Test que todos los layouts tienen metadata requerido."""
        config = load_layout(layout_name)
        
        # Metadata básico
        assert "layout_name" in config
        assert "version" in config
        assert "description" in config
        assert "last_updated" in config
        
        # Configuraciones principales
        assert "colors" in config
        assert "tables" in config
        assert "callouts" in config
    
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