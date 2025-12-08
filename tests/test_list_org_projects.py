import unittest
import os
import stat
import subprocess
import tempfile
import shutil

class TestListOrgProjects(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.bin_dir = os.path.join(self.test_dir, 'bin')
        os.makedirs(self.bin_dir)
        self.gcloud_path = os.path.join(self.bin_dir, 'gcloud')
        self.log_path = os.path.join(self.test_dir, 'gcloud.log')

        # Create a fake gcloud script
        with open(self.gcloud_path, 'w') as f:
            f.write(f"""#!/bin/bash
echo "$@" >> "{self.log_path}"

if [[ "$1" == "asset" && "$2" == "search-all-resources" ]]; then
    # Output mock csv
    echo "name,projectId,projectNumber,state,displayName"
    echo "//cloudresourcemanager.googleapis.com/projects/123,my-project,123,ACTIVE,My Project"
fi
""")
        st = os.stat(self.gcloud_path)
        os.chmod(self.gcloud_path, st.st_mode | stat.S_IEXEC)

        # Update PATH
        self.original_path = os.environ.get('PATH')
        os.environ['PATH'] = f"{self.bin_dir}:{self.original_path}"

    def tearDown(self):
        shutil.rmtree(self.test_dir)
        if self.original_path:
            os.environ['PATH'] = self.original_path

    def test_list_org_projects(self):
        script_path = os.path.abspath("list_org_projects.sh")
        org_id = "123456"
        output_file = os.path.join(self.test_dir, "output.csv")

        cmd = ["bash", script_path, org_id, output_file]
        subprocess.check_call(cmd, stdout=subprocess.DEVNULL)

        # Verify gcloud call
        with open(self.log_path, 'r') as f:
            lines = f.readlines()

        expected_arg_part = f"--scope=organizations/{org_id}"
        self.assertTrue(any(expected_arg_part in l for l in lines), "gcloud asset search-all-resources not called with correct scope")

        # Verify output file content
        self.assertTrue(os.path.exists(output_file), "Output file was not created")
        with open(output_file, 'r') as f:
            content = f.read()
            self.assertIn("my-project", content, "Output file does not contain expected project data")

if __name__ == '__main__':
    unittest.main()
