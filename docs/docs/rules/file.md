---
layout: docs
title: File Rules
---

# File Rules
{:.no_toc}

* TOC
{:toc}

## Copy

```python
file.copy(input, output)
```

| Parameter | Description |
|---|---|
|`input`|File to copy|
|`output`|Where to copy it|


## Template

```python
file.template(
    source, mapping, destination=None, left='###', right='###'
)
```

| Parameter | Description |
|---|---|
|`input`|Path to template|
|`mapping`|Dictionary mapping keys to values|
|`destination`|Output name|
|`left`|String to add to the left side of the key|
|`right`|String to add to the right side of the key|


## Group

```python
file.group(inputs, name)
```

| Parameter | Description |
|---|---|
|`inputs`|Paths to group|
|`name`|Name of the group|


## Download

```python
file.download(url, destination, sha256):
```

| Parameter | Description |
|---|---|
|`url`|Link to the file to download|
|`destination`|Output name|
|`sha256`|Checksum of the downloaded content|
