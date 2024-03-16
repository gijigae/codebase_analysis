import json
import os
from pathlib import Path
import click
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
model = "claude-3-haiku-20240307"

def multi_highlight(file_contents):
    def _call_highlight(prompt):
        response = client.messages.create(
            messages = [
                {"role": "user", "content": f"You are a helpful assistant specialized in highlighting key features of code.\n\n{prompt}\n\nThere are 5 key features I can highlight."},
            ],
            max_tokens=512,
            model=model,
        )
        # Extract the 'text' value from the first dictionary in the list
        if response.content and hasattr(response.content[0], 'text'):  # Check if the list is not empty and if 'text' attribute exists
            return response.content[0].text  # Directly access the 'text' attribute
        else:
            return "" 

    args = [
        f"\n\nHighlight the key features of this code:\n\n{file_content}. What would you say is the key thing to look for for this code?"
        for file_content in file_contents
    ]
    rets = [_call_highlight(prompt) for prompt in args]
    return [ret.split("There are 5 key features I can highlight.")[-1] for ret in rets]

def multi_overall_summarize(file_contents):
    def _call_overall_summarize(prompt):
        response = client.messages.create(
            messages = [
                {"role": "user", "content": f"You are a helpful assistant specialized in providing overall summaries of codebases.\n\n{prompt}\n\nSure. There are multiple methods and classes."},
            ],
            max_tokens=1024,
            model=model,
        )
        # Assuming response.content is a list of ContentBlock objects
        if response.content and isinstance(response.content, list):
            texts = [item.text for item in response.content if hasattr(item, 'text')]
            return texts
        else:
            return []

    args = [
        f"Provide an overall summary of this codebase:\n\n{file_content}"
        for file_content in file_contents
    ]
    rets = [_call_overall_summarize(prompt) for prompt in args]
    # Process each text assuming rets is now a list of lists of strings
    return [''.join(ret).split("Sure. There are multiple methods and classes.")[-1] for ret in rets]

def multi_high_level_pseudocode(file_contents):
    def _call_high_level_pseudocode(prompt):
        response = client.messages.create(
            messages = [
                {"role": "user", "content": f"You are a helpful assistant specialized in generating high-level pythonic pseudocode.\n\n{prompt}\n\nRewrite above high-level logic in pythonic pseudocode with comments. Be very abstract and informative."},
            ],
            max_tokens=2048,
            model=model,
        )
        # Adjusted to correctly handle the ContentBlock structure
        if response.content and isinstance(response.content, list):
            # Extract 'text' from each ContentBlock in the response
            texts = [item.text for item in response.content if hasattr(item, 'text')]
            return '\n'.join(texts)  # Join all texts into a single string
        else:
            return ""

    args = [
        f"Generate high-level pseudocode for this code:\n\n{file_content}"
        for file_content in file_contents
    ]
    rets = [_call_high_level_pseudocode(prompt) for prompt in args]
    # No need to split by specific markers unless they are part of the response
    return rets

def single_analyze_import_relationships(file_content):
    import_lines = [
        line
        for line in file_content.split("\n")
        if line.startswith("import") or line.startswith("from")
    ]
    if import_lines:
        return "Imports found:\n" + "\n".join(import_lines)
    else:
        return "No imports found."

def multi_analyze_import_relationships(file_contents):
    return [
        single_analyze_import_relationships(file_content)
        for file_content in file_contents
    ]

def analyze_files_and_generate_json_batch(
    file_paths, output_directory, global_codebase_path
):
    contents = []
    relative_paths = []
    # Prepare content and relative paths for batch processing
    for file_path in file_paths:
        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                content = file_path.read_text(encoding="ISO-8859-1")
            except UnicodeDecodeError as e:
                print(f"Skipping file {file_path} due to encoding issue: {e}")
                continue
        relative_path = str(file_path.relative_to(global_codebase_path))
        content_with_header = f"# python file {relative_path}\n\n{content}"
        contents.append(content_with_header)
        relative_paths.append(relative_path)

    # Batch process analyses
    highlights = multi_highlight(contents)
    overall_summaries = multi_overall_summarize(contents)
    pseudocodes = multi_high_level_pseudocode(contents)
    import_relationships = multi_analyze_import_relationships(contents)

    # Process each file's analysis and save to output
    for i, file_path in enumerate(file_paths):
        output_file_path = output_directory / Path(relative_paths[i]).with_suffix(
            ".json"
        )
        output_md_path = output_directory / Path(relative_paths[i]).with_suffix(".md")
        output_file_path.parent.mkdir(parents=True, exist_ok=True)
        analyses = {
            "highlights": highlights[i],
            "overall_summary": overall_summaries[i],
            "pseudocode": pseudocodes[i],
            "import_relationships": import_relationships[i],
        }
        with output_file_path.open("w", encoding="utf-8") as f:
            json.dump(analyses, f, indent=4)
        with output_md_path.open("w", encoding="utf-8") as f:
            f.write("\n\n### Summary\n\n")
            f.write(analyses["overall_summary"].strip())
            f.write("\n\n### Highlights\n\n")
            f.write(analyses["highlights"].strip())
            f.write(f"```python\n{analyses['pseudocode'].strip()}\n```")
            f.write("\n\n\n### import Relationships\n\n")
            f.write(analyses["import_relationships"].strip())

def is_allowed_filetype(filename):
    allowed_extensions = ['.ts', '.tsx','.js', '.jsx','.py', '.sh', '.pyx', '.html', '.yaml', '.h', '.c', '.sql']
    return any(filename.endswith(ext) for ext in allowed_extensions)

def analyze_directory_and_generate_overall_json_batch(
    this_directory_path, output_directory, global_codebase_path
):
    file_paths = []
    for root, _, files in os.walk(this_directory_path):
        for file in files:
            if is_allowed_filetype(file):
                file_path = Path(root, file)
                file_paths.append(file_path)
    if file_paths:
        analyze_files_and_generate_json_batch(
            file_paths, output_directory, global_codebase_path
        )

@click.command()
@click.argument("codebase_dir", type=click.Path(exists=True, file_okay=False))
@click.argument("output_directory", type=click.Path(file_okay=False))
def main(codebase_dir, output_directory):
    codebase_dir = Path(codebase_dir)
    output_directory = Path(output_directory)
    analyze_directory_and_generate_overall_json_batch(
        codebase_dir, output_directory, codebase_dir
    )
    click.echo(f"Analysis complete. Output is saved in {output_directory}")

if __name__ == "__main__":
    main()