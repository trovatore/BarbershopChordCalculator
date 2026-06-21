# apply_update.py
import os
import re

def apply_updates(patch_file='update.txt'):
    if not os.path.exists(patch_file):
        print(f"Error: {patch_file} not found.")
        return

    with open(patch_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to find the SEARCH/REPLACE blocks
    pattern = re.compile(
        r'# FILE: (?P<filename>.*?)\n<<<<<< SEARCH\n(?P<search>.*?)\n======\n(?P<replace>.*?)\n>>>>>>',
        re.DOTALL
    )

    matches = list(pattern.finditer(content))
    if not matches:
        print("No valid SEARCH/REPLACE blocks found.")
        return

    for match in matches:
        filename = match.group('filename').strip()
        search_text = match.group('search')
        replace_text = match.group('replace')

        if not os.path.exists(filename):
            print(f"❌ File not found: {filename}")
            continue

        with open(filename, 'r', encoding='utf-8') as f:
            file_source = f.read()

        if search_text in file_source:
            new_source = file_source.replace(search_text, replace_text)
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(new_source)
            print(f"✅ Updated {filename}")
        else:
            print(f"❌ Could not find exact match in {filename}. Check for whitespace/indentation differences.")

if __name__ == "__main__":
    apply_updates()