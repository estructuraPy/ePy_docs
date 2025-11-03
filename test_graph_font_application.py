"""
Test script demonstrating proper font application to graphs.
This shows how to apply fonts the same way tables do - directly to each element.
"""

import matplotlib.pyplot as plt
import numpy as np
from src.ePy_docs.core._images import setup_matplotlib_fonts, apply_fonts_to_plot

# Test with handwritten layout
print("Testing font application with handwritten layout...")
font_list = setup_matplotlib_fonts('handwritten')
print(f"Font list: {font_list}")

# Create a simple plot
fig, ax = plt.subplots(figsize=(10, 6))

# Generate sample data
x = np.linspace(0, 10, 100)
y1 = np.sin(x)
y2 = np.cos(x)

# Plot the data
ax.plot(x, y1, label='Sine Wave')
ax.plot(x, y2, label='Cosine Wave')

# Add labels and title
ax.set_xlabel('X Axis Label')
ax.set_ylabel('Y Axis Label')
ax.set_title('Graph Title - Testing Handwritten Font Application')
ax.legend()
ax.grid(True, alpha=0.3)

# NOW apply fonts directly to all text elements (like tables do)
apply_fonts_to_plot(ax, font_list)

# Save the result
output_path = 'results/report/test_graph_font_application.png'
plt.savefig(output_path, dpi=150, bbox_inches='tight')
print(f"Saved to: {output_path}")

# Show which elements were configured
print("\nText elements that received font_list:")
print(f"  - Title: {ax.get_title()}")
print(f"  - X Label: {ax.get_xlabel()}")
print(f"  - Y Label: {ax.get_ylabel()}")
print(f"  - X Tick labels: {len(ax.get_xticklabels())} labels")
print(f"  - Y Tick labels: {len(ax.get_yticklabels())} labels")
legend = ax.get_legend()
if legend:
    print(f"  - Legend texts: {len(legend.get_texts())} texts")

print("\n✅ Font application complete!")
print("This now works the same way as tables - fonts applied directly to each element.")
