import unittest 
from unittest import mock
import sys
import os
import requests

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
from main import parse_video_id, fetch_youtube_id


class TestClass(unittest.TestCase):
  def test_runs(self):
    assert True
  def test_parse_video_id(self):
    assert parse_video_id("yt8m") is None
    assert parse_video_id('i("nXSc","0sf943sWZls");')=="0sf943sWZls"
  # This method will be used by the mock to replace requests.get
  def mocked_requests_get(*args, **kwargs):
      class MockYTRequest:
          def __init__(self, text, status_code):
              self.text = text
              self.status_code = status_code
          
          def raise_for_status(self):
             if self.status_code != 200:
                raise requests.RequestException()

      if args[0] == 'http://data.yt8m.org/2/j/i/IN/INVALIDPATH.js':
          return MockYTRequest(None, 404)
      elif args[0] == 'http://data.yt8m.org/2/j/i/nX/nXSc.js':
          return MockYTRequest('i("nXSc","0sf943sWZls");', 200)
      else:
          return MockYTRequest(None, 500)

  @mock.patch('main.requests.get', side_effect=mocked_requests_get)
  def test_fetch_youtube_id(self, mock_request_get):
     assert fetch_youtube_id("nXSc") == "0sf943sWZls"
     assert fetch_youtube_id("INVALIDPATH") is None
