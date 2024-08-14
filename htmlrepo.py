#!/usr/bin/env python3

import os
import sys
import json
from pathlib import Path

def parse_config_file(config_file):
    extensions = []
    exclude_extensions = []
    ignore_folders = []

    with open(config_file, 'r') as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if line.startswith('!'):
                exclude_extensions.append(line[1:])
            elif line.startswith('/'):
                ignore_folders.append(line[1:])
            else:
                extensions.append(line)

    return extensions, exclude_extensions, ignore_folders

def format_yaml_like(files_data):
    output = "files:\n"
    for file_data in files_data:
        output += f"  - path: {file_data['path']}\n"
        output += "    content: |\n"
        content_lines = file_data['content'].splitlines()
        for line in content_lines:
            output += f"      {line}\n"
    return output

def format_json(files_data):
    return json.dumps({'files': files_data}, indent=2)

def format_html(files_data):
    output = "<html><body><pre>\n"
    for file_data in files_data:
        output += f"<h2>{file_data['path']}</h2>\n"
        output += "<code>\n"
        output += file_data['content']
        output += "</code>\n<br/>\n"
    output += "</pre></body></html>"
    return output

def format_xml(files_data):
    output = "<files>\n"
    for file_data in files_data:
        output += f"  <file>\n"
        output += f"    <path>{file_data['path']}</path>\n"
        output += "    <content><![CDATA[\n"
        output += file_data['content']
        output += "\n    ]]></content>\n"
        output += "  </file>\n"
    output += "</files>"
    return output

def collect_code_files(root_dir, output_file, extensions, exclude_extensions, ignore_dirs, output_format):
    files_data = []
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip ignored directories
        dirnames[:] = [d for d in dirnames if os.path.join(dirpath, d) not in ignore_dirs]
        
        for filename in filenames:
            file_ext = os.path.splitext(filename)[1]
            if file_ext in exclude_extensions or filename == output_file:
                continue
            if not extensions or file_ext in extensions:
                file_path = os.path.join(dirpath, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as code_file:
                        content = code_file.read()
                    files_data.append({
                        'path': file_path,
                        'content': content
                    })
                except UnicodeDecodeError as e:
                    print(f"Error reading file {file_path}: {e}", file=sys.stderr)
    
    if output_format == 'yaml':
        formatted_output = format_yaml_like(files_data)
    elif output_format == 'json':
        formatted_output = format_json(files_data)
    elif output_format == 'xml':
        formatted_output = format_xml(files_data)
    else:  # Default to HTML
        formatted_output = format_html(files_data)

    if output_file == '-':
        print(formatted_output)
    else:
        with open(output_file, 'w') as file:
            file.write(formatted_output)

if __name__ == "__main__":
    import argparse

    # Default extensions for most common programming languages
    default_extensions = [
        '.js', '.ts', '.py', '.jsx', '.tsx', '.html', '.css', '.cpp', '.java', 
        '.c', '.cs', '.rb', '.php', '.go', '.rs', '.swift', '.json',
        '.xml', '.yml', '.yaml', '.sh', '.bash', '.ps1', '.bat', '.cmd',
        '.sql', '.pl', '.perl', '.r', '.lua', '.m', '.mm', '.h', '.hpp',
        '.hxx', '.cxx', '.cshtml', '.aspx', '.jsp', '.asp', '.ejs', '.md',
        '.markdown', '.rst', '.txt', '.conf', '.cfg', '.ini', '.env', '.envrc',
        'Dockerfile', 'Makefile', 'Rakefile', 'Gemfile', 'Vagrantfile', 'Procfile',
    ]

    parser = argparse.ArgumentParser(description="Collect code files into a structured format.")
    parser.add_argument('start_directory', help="The directory to start searching from.")
    parser.add_argument('-o', '--output', default='report.yaml', help="The output file name. Use '-' for stdout.")
    parser.add_argument('-f', '--format', choices=['yaml', 'json', 'xml', 'html'], default='yaml', help="The output format: yaml, json, xml, or html.")
    parser.add_argument('-e', '--extensions', nargs='*', help="List of file extensions to include.")
    parser.add_argument('-x', '--exclude-extensions', nargs='*', help="List of file extensions to exclude.")
    parser.add_argument('-i', '--ignore-folders', nargs='*', help="List of directories to ignore.")
    parser.add_argument('-c', '--config', default=os.path.expanduser('~/.htmlrepoignore'), help="Path to a config file for default settings.")

    args = parser.parse_args()

    # Initialize with defaults
    extensions = args.extensions if args.extensions else default_extensions
    exclude_extensions = args.exclude_extensions if args.exclude_extensions else []
    ignore_folders = args.ignore_folders if args.ignore_folders else []

    # Load settings from config file if it exists
    if os.path.exists(args.config):
        config_extensions, config_exclude_extensions, config_ignore_folders = parse_config_file(args.config)
        extensions = config_extensions or extensions
        exclude_extensions = config_exclude_extensions or exclude_extensions
        ignore_folders = config_ignore_folders or ignore_folders

    # Resolve full paths for ignored directories
    ignore_dirs = [os.path.abspath(os.path.join(args.start_directory, d)) for d in ignore_folders]
    
    collect_code_files(args.start_directory, args.output, extensions, exclude_extensions, ignore_dirs, args.format)
