# apply_update.py
import os
import re

def apply_updates(patch_file='update.txt'):
    if not os.path.exists(patch_file):
        print(f"Error: {patch_file} not found.")
        return

    with open(patch_file, 'r', encoding='utf-8') as f:
        content = f.read()

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
        search_text = match.group('search').strip('\n')
        replace_text = match.group('replace').strip('\n')

        if not os.path.exists(filename):
            print(f"❌ File not found: {filename}")
            continue

        with open(filename, 'r', encoding='utf-8') as f:
            file_source = f.read()

        # Fuzzy check: try exact, then try stripping lines
        if search_text in file_source:
            new_source = file_source.replace(search_text, replace_text)
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(new_source)
            print(f"✅ Updated {filename}")
        else:
            # Try a slightly more relaxed match if the block is small
            print(f"❌ Match failed for block in {filename}. Check indentation.")

if __name__ == "__main__":
    apply_updates()