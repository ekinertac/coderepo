#!/usr/bin/env python3

import os
import sys
import json
import fnmatch
import argparse
from .utils import create_default_ignore_file


class ConfigParser:
    def __init__(self, config_file):
        self.config_file = config_file

    def parse(self):
        extensions = []
        exclude_patterns = []
        ignore_folders = []
        ignore_files = ["report.yaml", "report.html", "report.json", "report.xml"]

        with open(self.config_file, 'r') as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                if line.startswith('!'):
                    if '/' in line:
                        ignore_folders.append(line[1:])
                    elif '*' in line or '.' in line:
                        exclude_patterns.append(line[1:])
                    else:
                        ignore_files.append(line[1:])
                elif line.startswith('/'):
                    ignore_folders.append(line)
                elif '.' in line:
                    extensions.append(line)

        return extensions, exclude_patterns, ignore_folders, ignore_files


import os
import mimetypes


class FileCollector:
    def __init__(self, root_dir, ignore_dirs, ignore_files, exclude_patterns):
        self.root_dir = root_dir
        self.ignore_dirs = ignore_dirs
        self.ignore_files = ignore_files
        self.exclude_patterns = exclude_patterns

    def should_ignore(self, path):
        abs_path = os.path.abspath(path)
        for ignore_dir in self.ignore_dirs:
            if ignore_dir in abs_path:
                return True
        filename = os.path.basename(abs_path)
        for pattern in self.ignore_files + self.exclude_patterns:
            if fnmatch.fnmatch(filename, pattern):
                return True
        return False

    def is_binary_file(self, file_path):
        # Open the file in binary mode and check for non-text characters
        with open(file_path, 'rb') as file:
            chunk = file.read(1024)
            if b'\0' in chunk:  # A binary file often contains null bytes
                return True
        return False

    def collect(self):
        files_data = []
        for dirpath, dirnames, filenames in os.walk(self.root_dir):
            dirnames[:] = [d for d in dirnames if not self.should_ignore(os.path.join(dirpath, d))]
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                if self.should_ignore(file_path):
                    continue
                if not self.is_binary_file(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as code_file:
                            content = code_file.read()
                        files_data.append({'path': file_path, 'content': content})
                    except UnicodeDecodeError as e:
                        print(f"Error reading file {file_path}: {e}", file=sys.stderr)
                    except Exception as e:
                        print(f"Skipping unreadable file {file_path}: {e}", file=sys.stderr)
        return files_data


class Formatter:
    def format_yaml_like(self, files_data):
        output = "files:\n"
        for file_data in files_data:
            output += f"  - path: {file_data['path']}\n"
            output += "    content: |\n"
            content_lines = file_data['content'].splitlines()
            for line in content_lines:
                output += f"      {line}\n"
        return output

    def format_json(self, files_data):
        return json.dumps({'files': files_data}, indent=2)

    def format_html(self, files_data):
        output = "<html><body><pre>\n"
        for file_data in files_data:
            output += f"<h2>{file_data['path']}</h2>\n"
            output += "<code>\n"
            output += file_data['content']
            output += "</code>\n<br/>\n"
        output += "</pre></body></html>"
        return output

    def format_xml(self, files_data):
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

    def format(self, files_data, output_format):
        if output_format == 'yaml':
            return self.format_yaml_like(files_data)
        elif output_format == 'json':
            return self.format_json(files_data)
        elif output_format == 'xml':
            return self.format_xml(files_data)
        else:  # Default to HTML
            return self.format_html(files_data)


class FileWriter:
    def __init__(self, output_file):
        self.output_file = output_file

    def write(self, content):
        if self.output_file == '-':
            print(content)
        else:
            with open(self.output_file, 'w') as file:
                file.write(content)


class CodeFileCollectorApp:
    def __init__(self, args):
        self.args = args
        self.exclude_patterns = args.exclude_extensions if args.exclude_extensions else []
        self.ignore_folders = [os.path.abspath(os.path.join(args.start_directory, d)) for d in args.ignore_folders] if args.ignore_folders else []
        self.ignore_files = args.ignore_files if args.ignore_files else []

    def run(self):
        # Check if the default config file exists, create it if it doesn't
        create_default_ignore_file()

        if os.path.exists(self.args.config):
            config_parser = ConfigParser(self.args.config)
            _, config_exclude_patterns, config_ignore_folders, config_ignore_files = config_parser.parse()
            self.exclude_patterns = config_exclude_patterns or self.exclude_patterns
            self.ignore_folders.extend([os.path.abspath(os.path.join(self.args.start_directory, d)) for d in config_ignore_folders])
            self.ignore_files.extend(config_ignore_files)

        file_collector = FileCollector(
            root_dir=self.args.start_directory,
            ignore_dirs=self.ignore_folders,
            ignore_files=self.ignore_files,
            exclude_patterns=self.exclude_patterns
        )

        files_data = file_collector.collect()

        formatter = Formatter()
        formatted_output = formatter.format(files_data, self.args.format)

        file_writer = FileWriter(self.args.output)
        file_writer.write(formatted_output)


def main():
    parser = argparse.ArgumentParser(description="Collect code files into a structured format.")
    parser.add_argument('start_directory', help="The directory to start searching from.")
    parser.add_argument('-o', '--output', default='report.yaml', help="The output file name. Use '-' for stdout.")
    parser.add_argument('-f', '--format', choices=['yaml', 'json', 'xml', 'html'], default='yaml', help="The output format: yaml, json, xml, or html.")
    parser.add_argument('-e', '--extensions', nargs='*', help="List of file extensions to include.")
    parser.add_argument('-x', '--exclude-extensions', nargs='*', help="List of file extensions to exclude.")
    parser.add_argument('-i', '--ignore-folders', nargs='*', help="List of directories to ignore.")
    parser.add_argument('--ignore-files', nargs='*', help="List of files to ignore (supports wildcards).")
    parser.add_argument('-c', '--config', default=os.path.expanduser('~/.htmlrepoignore'), help="Path to a config file for default settings.")

    args = parser.parse_args()

    app = CodeFileCollectorApp(args)
    app.run()
