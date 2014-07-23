import os
from selenium import webdriver
import tempfile
import time
import unittest

files_dir = os.path.dirname(os.path.abspath(__file__)) + '/files/'

browser = webdriver.Firefox()


class TestUpload(unittest.TestCase):

    def setUp(self):
        browser.get('http://localhost')

    def tearDown(self):
        pass #browser.close()

    def create_temp_file(self, size):
        f = tempfile.NamedTemporaryFile()
        f.seek(size-1)
        f.write('\0x00')
        f.flush()
        return f

    def do_upload_file(self, fname):
        fileElement = browser.find_element_by_id('files')
        fileElement.send_keys(fname)

    def upload_file(self, size):
        f = self.create_temp_file(size)
        self.do_upload_file(f.name)

        progressBar = browser.find_element_by_id('uploadprogressbar')

        for i in range(60):
            if progressBar.text == "100%":
                response = browser.find_element_by_id('response')
                response.text.startswith("Succes")
                self.assertTrue(response.is_displayed)
                return
            else:
                time.sleep(1)
        self.fail("Upload not completed")

    def test_upload_atomic(self):
        self.upload_file(5120)

    def test_upload_chunked(self):
        self.upload_file(5120000)

if __name__ == '__main__':
    unittest.main()
