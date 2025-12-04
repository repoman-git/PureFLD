# Rendered Diagrams

This directory contains PNG and SVG exports of Mermaid diagrams.

## How to Generate

Use Mermaid CLI:
```bash
npm install -g @mermaid-js/mermaid-cli

# Export all diagrams
for file in ../*.mmd; do
  filename=$(basename "$file" .mmd)
  mmdc -i "$file" -o "${filename}.png"
  mmdc -i "$file" -o "${filename}.svg"
done
```

Or use Mermaid Live Editor: https://mermaid.live/

