import os
import tempfile
import unittest
from htmlrepo import collect_code_files

class TestHTMLRepo(unittest.TestCase):
    
    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.TemporaryDirectory()
        self.test_file_paths = []
        
        # Create some test files
        self.test_file_paths.append(self._create_file("test1.py", "print('Hello World')"))
        self.test_file_paths.append(self._create_file("test2.js", "console.log('Hello World')"))
        self.test_file_paths.append(self._create_file("test3.html", "<h1>Hello World</h1>"))
        
        # Create a temporary config file
        self.temp_config_file = tempfile.NamedTemporaryFile(delete=False)
    
    def tearDown(self):
        # Cleanup the temporary directory and config file
        self.test_dir.cleanup()
        os.unlink(self.temp_config_file.name)
    
    def _create_file(self, filename, content):
        file_path = os.path.join(self.test_dir.name, filename)
        with open(file_path, 'w') as f:
            f.write(content)
        return file_path

    def test_yaml_output(self):
        output_file = os.path.join(self.test_dir.name, "output.yaml")
        collect_code_files(self.test_dir.name, output_file, [], [], [], 'yaml')
        
        with open(output_file, 'r') as f:
            output = f.read()
        
        self.assertIn("files:", output)
        self.assertIn("path: " + self.test_file_paths[0], output)
        self.assertIn("print('Hello World')", output)

    def test_json_output(self):
        output_file = os.path.join(self.test_dir.name, "output.json")
        collect_code_files(self.test_dir.name, output_file, [], [], [], 'json')
        
        with open(output_file, 'r') as f:
            output = f.read()
        
        self.assertIn('"files": [', output)
        self.assertIn('"path": "' + self.test_file_paths[0], output)
        self.assertIn('"print(\'Hello World\')"', output)

    def test_xml_output(self):
        output_file = os.path.join(self.test_dir.name, "output.xml")
        collect_code_files(self.test_dir.name, output_file, [], [], [], 'xml')
        
        with open(output_file, 'r') as f:
            output = f.read()
        
        self.assertIn("<files>", output)
        self.assertIn("<path>" + self.test_file_paths[0] + "</path>", output)
        self.assertIn("<![CDATA[\nprint('Hello World')\n", output)

    def test_html_output(self):
        output_file = os.path.join(self.test_dir.name, "output.html")
        collect_code_files(self.test_dir.name, output_file, [], [], [], 'html')
        
        with open(output_file, 'r') as f:
            output = f.read()
        
        self.assertIn("<html><body><pre>", output)
        self.assertIn(f"<code>\nprint('Hello World')</code>", output)

    def test_exclude_extensions(self):
        output_file = os.path.join(self.test_dir.name, "output.yaml")
        collect_code_files(self.test_dir.name, output_file, [], ['.py'], [], 'yaml')
        
        with open(output_file, 'r') as f:
            output = f.read()
        
        self.assertNotIn("print('Hello World')", output)
        self.assertIn("console.log('Hello World')", output)

    def test_ignore_folders(self):
        # Create a subdirectory and a file inside it
        sub_dir = os.path.join(self.test_dir.name, "subdir")
        os.makedirs(sub_dir)
        sub_file_path = self._create_file("subdir/test4.py", "print('This should be ignored')")
        
        output_file = os.path.join(self.test_dir.name, "output.yaml")
        collect_code_files(self.test_dir.name, output_file, [], [], [sub_dir], 'yaml')
        
        with open(output_file, 'r') as f:
            output = f.read()
        
        self.assertNotIn("print('This should be ignored')", output)

    def test_default_config(self):
        # Write to the temporary config file
        with open(self.temp_config_file.name, 'w') as f:
            f.write("!*.js\n")
        
        output_file = os.path.join(self.test_dir.name, "output.yaml")
        
        # Call collect_code_files with the temporary config file
        collect_code_files(
            root_dir=self.test_dir.name, 
            output_file=output_file, 
            extensions=[], 
            exclude_extensions=[], 
            ignore_dirs=[], 
            output_format='yaml', 
            config=self.temp_config_file.name  # Modify your function to accept this or apply it inside the test
        )
        
        with open(output_file, 'r') as f:
            output = f.read()
        
        self.assertNotIn("console.log('Hello World')", output)


if __name__ == '__main__':
    unittest.main()
