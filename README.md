# Automate Massive Codebase Analysis (CA) with Language Model

<p align="center">
  <img src="chimp.webp" alt="Chimp" width="400">
</p>

Ever had to go over all the codebase and analyze everything one-by-one? Ever wanted to "read over all of it really fast" and get "high level picture" per folder? This short tiny codebase does exactly that, hope to make your codebase-analysis time shorter.

This will recursively generate...

* High-level summary of the codebase
* Highlights of the codebase
* Pythonic Pseudocode
* Import Relationships

# Installation & Use



Rename the `.env.example`to `.env` and add your own API key from Anthropic.

Update the list of allowed_extensions to limit the types of file extensions.

```bash
allowed_extensions = ['.ts', '.tsx','.js', '.jsx','.py']
```

Run it via

```bash
pip install -r requirements.txt
ca_with_haiku.py CODEBASE_DIR OUTPUT_DIR
```

# Example Output:

## Python Codebase

The [following](https://github.com/gijigae/codebase_analysis/tree/main/dify_ca_sample/api/tasks) is example output from analysis of dify/api/tasks codebase.

## Typescript Codebase

The [following](https://github.com/gijigae/codebase_analysis/tree/main/dify_ca_sample/web/service) is example output from analysis of dify/web/service codebase.


