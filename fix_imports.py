import os
import re

def fix_imports(directory):
    """Fix imports from nocturna to nocturna_calculations in Python files."""
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Replace imports
                new_content = re.sub(
                    r'from nocturna\.',
                    'from nocturna_calculations.',
                    content
                )
                new_content = re.sub(
                    r'import nocturna\.',
                    'import nocturna_calculations.',
                    new_content
                )
                
                if new_content != content:
                    print(f"Updating imports in {file_path}")
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)

if __name__ == '__main__':
    # Fix imports in tests directory
    fix_imports('tests') 