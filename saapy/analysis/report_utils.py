# coding=utf-8

def rm_md_code(file_path):
    skip = False
    dst_file_path = '{}-clean.md'.format(file_path.rsplit('.', 1)[0])
    with open(file_path) as src:
        with open(dst_file_path, 'w') as dst:
            for line in src:
                if skip:
                    skip = not line.startswith('```')
                elif line.startswith('```python'):
                    skip = True
                else:
                    dst.write(line)
