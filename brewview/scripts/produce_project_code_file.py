import os

import fire


def fetch_and_store_code_files(directory='.', output_dir='output', max_tokens=4000):
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    output_file_counter = 1
    current_token_count = 0

    # Open the first output file
    output_file = open(f"{output_dir}/output_{output_file_counter}.txt", 'w')

    # Traverse directory recursively
    for subdir, dirs, files in os.walk(directory):
        for file in files:
            filepath = subdir + os.sep + file

            if filepath.endswith((".py", ".html", ".css")):
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                tokens = content.split() # split content into tokens
                
                # If adding the new tokens would exceed the max token count
                if current_token_count + len(tokens) > max_tokens:
                    # Close the current output file
                    output_file.close()
                    # Increment the file counter
                    output_file_counter += 1
                    # Open a new output file
                    output_file = open(f"{output_dir}/output_{output_file_counter}.txt", 'w')
                    # Reset the token count
                    current_token_count = 0

                # Determine file type
                if filepath.endswith(".py"):
                    file_type = "python"
                elif filepath.endswith(".html"):
                    file_type = "html"
                elif filepath.endswith(".css"):
                    file_type = "css"
                
                # Write to output file
                output_file.write(f"==={file_type}===\n")
                output_file.write(f"File: {filepath}\n")
                output_file.write(f"Content:\n{content}\n\n")
                
                # Update the token count
                current_token_count += len(tokens)

    # Close the last output file
    output_file.close()

if __name__ == "__main__":
    fire.Fire(fetch_and_store_code_files)
