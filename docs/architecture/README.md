# Solution design

![Solution design](solution-design.svg)

| File | Use |
|---|---|
| [`solution-design.svg`](solution-design.svg) | The diagram, sharp at any size (rendered on GitHub). |
| [`solution-design.png`](solution-design.png) | The same at 2× resolution, for slides. |
| [`solution_design.py`](solution_design.py) | Generates the SVG. Update it in the same change as the architecture. |

Solid boxes and arrows are live in Azure; dashed ones are planned (step 5 and later, or
phase 2). Red tags mark the resource groups the kill switch deletes at 100 % of the budget.

## Regenerate

The icons are the official
[Microsoft Azure Architecture Icons](https://learn.microsoft.com/azure/architecture/icons/)
(V24), embedded unmodified. Microsoft permits their use in architecture diagrams and
documentation; they are not committed here as separate files.

```bash
curl -sSLo /tmp/icons.zip https://arch-center.azureedge.net/icons/Azure_Public_Service_Icons_V24.zip
unzip -q /tmp/icons.zip -d /tmp/azure-icons
python3 docs/architecture/solution_design.py /tmp/azure-icons docs/architecture/solution-design.svg
```
