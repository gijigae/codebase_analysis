# Automate Massive Codebase Analysis with Language Model

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

Run it via

```bash
pip install -r requirements.txt
ca_with_haiku.py CODEBASE_DIR OUTPUT_DIR
```

```


# Example Output:

The [following](https://github.com/cloneofsimo/reverse_eng_deepspeed_study/tree/main/decomposed) is example output from analysis of DeepSpeed codebase.

