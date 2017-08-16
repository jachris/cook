---
layout: docs
title: LibreOffice Rules
---

# LibreOffice Rules
{:.no_toc}

* TOC
{:toc}

## Convert

```python
libreoffice.convert(
    source, destination=None, format=None
)
```

| Parameter | Description |
|---|---|
|`source`|Path to the file (not limited to `.odg`, `.odf`, ...)|
|`destination`|Output name including the suffix|
|`format`|Overwrite format inferred from the destination suffix|
