import requests
import unittest
import json
import logging

logger = logging.getLogger('test_server')

ENDPOINT = "http://localhost:8801/api"

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
		self.resp = requests.post(ENDPOINT + "/upload", data={"cryptofile":b"\x00"*(self.__class__.serverinfo["max_filesize_bytes"]+1),"metadata":"","chunknumber":0,"finishupload":True,"deletepassword":"loldonkey"})
	def test_chunk_zero_but_not_finishing(self):
		self.resp = requests.post(ENDPOINT + "/upload", data={"cryptofile":"a","metadata":"","chunknumber":0,"finishupload":False,"deletepassword":"loldonkey"})
	def tearDown(self):
		self.check_parsable_but_not_ok()
		self.assertFalse(self.unfinished, self.resp.text)
	def setUp(self):
		self.unfinished = False
	@classmethod
	def setUpClass(cls):
		cls.serverinfo = requests.get(ENDPOINT + "/serverinfo").json()
		logger.info(cls.serverinfo)

if __name__ == "__main__":
	logging.basicConfig(level="INFO")
	unittest.main()
