---
layout: docs
title: GIMP Rules
---

# GIMP Rules
{:.no_toc}

* TOC
{:toc}

## Export XCF

```python
gimp.export(source, destination=None, format='png')
```

| Parameter | Description |
|---|---|
|`source`|Path to the XCF file|
|`destination`|Where to put the result relative to the build directory. If it is `None`, then the result will be placed under the new extension given by `format` inside the build directory.|
|`format`|Specifies the result format|
