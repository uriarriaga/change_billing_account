import unittest
import os
import stat
import subprocess
import tempfile
import shutil

class TestChangeBillingAccount(unittest.TestCase):
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

if [[ "$1" == "beta" && "$2" == "billing" && "$3" == "projects" && "$4" == "list" ]]; then
    # Return some mock projects
    echo "project-a"
    echo "project-b"
    echo "project-c"
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

    def test_change_billing_account(self):
        # Path to the script under test
        script_path = os.path.abspath("change_billing_account.sh")

        # Run the script
        old_billing = "old-billing-id"
        new_billing = "new-billing-id"
        exceptions = ["project-b"]

        cmd = ["bash", script_path, old_billing, new_billing] + exceptions
        subprocess.check_call(cmd, stdout=subprocess.DEVNULL)

        # Verify gcloud calls
        with open(self.log_path, 'r') as f:
            lines = f.readlines()

        # We expect:
        # 1. beta billing projects list --billing-account=old-billing-id --format=value(projectId)
        # 2. beta billing projects link project-a --billing-account=new-billing-id
        # 3. beta billing projects link project-c --billing-account=new-billing-id
        # project-b should be skipped

        call_list = [l.strip() for l in lines]

        self.assertTrue(any(f"beta billing projects list --billing-account={old_billing}" in c for c in call_list), "Listing projects not called correctly")
        self.assertTrue(any(f"beta billing projects link project-a --billing-account={new_billing}" in c for c in call_list), "project-a not linked")
        self.assertTrue(any(f"beta billing projects link project-c --billing-account={new_billing}" in c for c in call_list), "project-c not linked")

        # Verify project-b was NOT linked
        self.assertFalse(any(f"beta billing projects link project-b" in c for c in call_list), "project-b was linked but should have been skipped")

if __name__ == '__main__':
    unittest.main()
