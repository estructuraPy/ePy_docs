#!/usr/bin/env python3

from ePy_docs.writers import DocumentWriter

# Create a simple test
writer = DocumentWriter()

# Add the test QMD file
writer.add_quarto_file("test_table_processing.qmd", convert_tables=True)

# Generate the content
writer.generate(html=True, pdf=False, markdown=True)

print("Test completed. Check the output for table duplication issues.")