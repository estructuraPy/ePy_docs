"""Tests for PDF font configuration."""

import pytest
from ePy_docs.core._config import get_font_latex_config
from ePy_docs.core._pdf import get_pdf_config


class TestPDFFontConfiguration:
    """Test PDF font configuration for different layouts."""
    
    def test_classic_layout_no_custom_font(self):
        """Test that classic layout doesn't generate custom font config."""
        latex_config = get_font_latex_config('classic')
        
        # Classic uses system fonts, shouldn't have fontspec
        assert latex_config == "" or 'fontspec' not in latex_config
    
    def test_handwritten_layout_has_font_config(self):
        """Test that handwritten layout generates font configuration."""
        latex_config = get_font_latex_config('handwritten')
        
        # Handwritten should configure custom font
        assert 'fontspec' in latex_config
        assert 'setmainfont' in latex_config
        assert 'anm_ingenieria_2025' in latex_config
    
    def test_handwritten_layout_has_fallback(self):
        """Test that handwritten layout includes fallback font."""
        latex_config = get_font_latex_config('handwritten')
        
        # Should have fallback configured
        assert 'setsansfont' in latex_config or 'fallbackfont' in latex_config
    
    def test_pdf_config_includes_header(self):
        """Test that PDF config includes font configuration in header."""
        pdf_config = get_pdf_config('handwritten')
        
        assert 'include-in-header' in pdf_config
        assert 'text' in pdf_config['include-in-header']
        
        header_text = pdf_config['include-in-header']['text']
        assert 'fontspec' in header_text
    
    def test_pdf_config_uses_xelatex(self):
        """Test that PDF uses xelatex for custom fonts."""
        pdf_config = get_pdf_config('handwritten')
        
        # xelatex supports fontspec
        assert pdf_config['pdf-engine'] == 'xelatex'
    
    def test_pdf_config_geometry(self):
        """Test PDF geometry configuration."""
        pdf_config = get_pdf_config('handwritten')
        
        assert 'geometry' in pdf_config
        assert isinstance(pdf_config['geometry'], list)
        assert len(pdf_config['geometry']) == 4  # top, bottom, left, right
    
    def test_font_copy_to_output(self):
        """Test that fonts are copied to output directory."""
        from pathlib import Path
        import tempfile
        from ePy_docs.core._quarto import _copy_layout_fonts_to_output
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            fonts_dir = _copy_layout_fonts_to_output('handwritten', output_dir)
            
            assert fonts_dir.exists()
            assert fonts_dir.is_dir()
            
            # Check that font file was copied
            font_files = list(fonts_dir.glob('*.otf'))
            assert len(font_files) > 0
            
            # Verify return value is absolute path
            assert fonts_dir.is_absolute()
    
    def test_fonts_dir_passed_to_latex_config(self):
        """Test that absolute fonts_dir path is used in LaTeX configuration."""
        from pathlib import Path
        import tempfile
        from ePy_docs.core._config import get_font_latex_config
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a fake fonts directory
            fonts_dir = Path(tmpdir) / 'fonts'
            fonts_dir.mkdir()
            
            # Get LaTeX config with absolute path
            config = get_font_latex_config('handwritten', fonts_dir=fonts_dir)
            
            # Convert path to forward slashes for comparison (LaTeX format)
            expected_path = fonts_dir.as_posix() + "/"
            
            # Check that absolute path is in the config
            assert expected_path in config
            assert 'Path = ' + expected_path in config
            
            # Ensure relative path is NOT used
            assert 'Path = ./fonts/' not in config
