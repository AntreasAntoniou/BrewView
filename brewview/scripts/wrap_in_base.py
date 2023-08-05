import os

import fire


def wrap_html_with_base(directory_path):
    base_extends_line = "{% extends 'base.html' %}\n"
    block_content_start_line = "{% block content %}\n"
    block_content_end_line = "{% endblock %}\n"

    # Walking through the directory, including subdirectories
    for foldername, subfolders, filenames in os.walk(directory_path):
        for filename in filenames:
            if filename.endswith(".html"):
                file_path = os.path.join(foldername, filename)
                with open(file_path, 'r+') as file:
                    content = file.read()

                    # Check if the file is already wrapped
                    if base_extends_line.strip() not in content:
                        # Rewind the file and write the new content
                        file.seek(0)
                        file.write(base_extends_line + block_content_start_line + content + block_content_end_line)
                        file.truncate()
                print(f"Processed {file_path}")

if __name__ == "__main__":
    fire.Fire(wrap_html_with_base)
