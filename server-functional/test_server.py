import requests
import unittest
import json
import logging
import zlib
import sys
from colorama import init, Fore, Back, Style

logger = logging.getLogger('test_server')

ENDPOINT = "you_forgot_to_provide_the_endpoint_as_the_first_command_line_argument"

class TestErrorHandling(unittest.TestCase):
	def check_parsable_but_not_ok(self):
		try:
			self.assertNotEqual(self.resp.json()["status"], "OK")
		except Exception as e:
			logger.warning(self.resp.text)
			raise e
	def test_missing_post_params(self):
		self.resp = requests.post(ENDPOINT + "/upload")
	def test_invalid_uploadpassword(self):
		self.resp = requests.post(ENDPOINT + "/upload", data={"cryptofile":"a","metadata":"","chunknumber":1,"finishupload":False,"deletepassword":"loldonkey"})
		self.unfinished = True
		self.resp = requests.post(ENDPOINT + "/upload", data={"cryptofile":"b","chunknumber":2,"finishupload":True,"fileid":self.resp.json()["fileid"], "uploadpassword": self.resp.json()["uploadpassword"] + "BOB"})
		self.unfinished = False
	def test_chunk_too_big(self):
		if 100*10**6 < self.__class__.serverinfo["max_filesize_bytes"]+1:
			print(Fore.RED + "skipping test, max_filesize_bytes very big: {}".format(self.__class__.serverinfo["max_filesize_bytes"]) + Fore.RESET)
			return
		self.resp = requests.post(ENDPOINT + "/upload", data=zlib.compress(json.dumps({"cryptofile":"\x00"*(self.__class__.serverinfo["max_filesize_bytes"]+1),"metadata":"","chunknumber":0,"finishupload":True,"deletepassword":"loldonkey"}).encode("utf-8")), headers={'Content-Encoding': 'gzip'})
	def test_chunk_zero_but_not_finishing(self):
		""" it should not be possible to download chunks before the whole hushfile is finished """
		self.reference = "a"
		self.resp = requests.post(ENDPOINT + "/upload", data={"cryptofile":self.reference,"metadata":"","chunknumber":0,"finishupload":False,"deletepassword":"loldonkey"})
		self.resp = requests.get(ENDPOINT + "/file", params={"chunknumber":0,"fileid":self.resp.json()["fileid"]})
	def tearDown(self):
		self.check_parsable_but_not_ok()
		self.assertFalse(self.unfinished, self.resp.text)
	def setUp(self):
		self.unfinished = False
	@classmethod
	def setUpClass(cls):
		cls.serverinfo = requests.get(ENDPOINT + "/serverinfo").json()
		logger.info(cls.serverinfo)

class TestFileEquality(unittest.TestCase):
	def test_basic_one_chunk_equality(self):
		self.reference = "a"
		self.resp = requests.post(ENDPOINT + "/upload", data={"cryptofile":self.reference,"metadata":"","chunknumber":0,"finishupload":True,"deletepassword":"loldonkey"})
		self.resp = requests.get(ENDPOINT + "/file", params={"chunknumber":0,"fileid":self.resp.json()["fileid"]})
	def test_compressed_one_chunk_equality(self):
		self.reference = "a"
		self.resp = requests.post(ENDPOINT + "/upload", data=zlib.compress(json.dumps({"cryptofile":self.reference,"metadata":"","chunknumber":0,"finishupload":True,"deletepassword":"loldonkey"}).encode("utf-8")), headers={'Content-Encoding': 'gzip'})
		self.assertEqual(self.resp.json()["status"], "OK")
		self.resp = requests.get(ENDPOINT + "/file", params={"chunknumber":0,"fileid":self.resp.json()["fileid"]})
	def tearDown(self):
		self.assertEqual(self.reference, self.resp.text)

if __name__ == "__main__":
	global ENDPOINT

	init()

	logging.basicConfig(level="DEBUG")
	if sys.hexversion < 0x03000000:
		sys.exit("Python 3 is required to run this program.")
	if len(sys.argv) > 1: ENDPOINT = sys.argv.pop()
	unittest.main()
