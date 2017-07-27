---
layout: docs
title: LaTeX Rules
---

# LaTeX Rules

## Render PDF

```python
latex.document(
    source, name=None, contains=None, texinputs=None, scan=True
)
```

| Parameter | Description |
|---|---|
|`source`|Path to the `.tex` file|
|`name`|Output name including the `.pdf` suffix|
|`contains`|List of additional dependencies|
|`texinputs`|Directories to search for when including anything|
|`scan`|Track implicit dependencies (`\include{...}`)|
