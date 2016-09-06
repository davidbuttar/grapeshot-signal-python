import unittest
from httmock import urlmatch, HTTMock
from grapeshot_signal import SignalClient, APIError, OverQuotaError, rels
import tests.mocks as mocks


class TestClient(unittest.TestCase):

    def setUp(self):
        api_key = 'my-api-key'
        self.client = SignalClient(api_key)

    def tearDown(self):
        self.client = None

    def test_get_page(self):
        with HTTMock(mocks.page_mock):
            page = self.client.get_page('http://bbc.com/')
            self.assertIsNotNone(page)
            self.assertTrue(page.is_ok())
            self.assertFalse(page.is_over_quota())
            self.assertFalse(page.is_queued())
            self.assertFalse(page.is_error())
            self.assertIsNotNone(page.url())
            self.assertEqual(page['language'], 'en')

    def test_get_page_embedded(self):
        with HTTMock(mocks.page_embed_segments_keywords_mock):
            page = self.client.get_page('http://bbc.com/', embed=[rels.segments, rels.keywords])
            self.assertIsNotNone(page)
            self.assertTrue(page.is_ok())
            self.assertEqual(page['language'], 'en')

            segments = page.get_embedded(rels.segments)
            self.assertIsNotNone(segments)
            self.assertTrue(segments.is_ok())
            self.assertEqual(page['language'], 'en')
            self.assertIsNotNone(segments['segments'])

            keywords = page.get_embedded(rels.keywords)
            self.assertIsNotNone(keywords)
            self.assertTrue(keywords.is_ok())
            self.assertEqual(keywords['language'], 'en')
            self.assertIsNotNone(keywords['keywords'])

    def test_get_page_links(self):
        with HTTMock(mocks.page_mock, mocks.keywords_mock, mocks.segments_mock):
            page = self.client.get_page('http://bbc.com/')
            self.assertIsNotNone(page)
            self.assertTrue(page.is_ok())
            self.assertEqual(page['language'], 'en')

            segments = self.client.get_link(page, rels.segments)
            self.assertIsNotNone(segments)
            self.assertTrue(segments.is_ok())
            self.assertEqual(page['language'], 'en')
            self.assertIsNotNone(segments['segments'])

            keywords = self.client.get_link(page, rels.keywords)
            self.assertIsNotNone(keywords)
            self.assertTrue(keywords.is_ok())
            self.assertEqual(keywords['language'], 'en')
            self.assertIsNotNone(keywords['keywords'])

    def test_get_page_queued(self):
        with HTTMock(mocks.page_queued_mock):
            page = self.client.get_page('http://bbc.com/')
            self.assertIsNotNone(page)
            self.assertTrue(page.is_queued())

    def test_get_page_400_error(self):
        with HTTMock(mocks.page_missing_url_mock):
            try:
                page = self.client.get_page('')
                self.assertIsNone(page)
                self.assertFalse('We expect an error to be raised')
            except APIError as err:
                self.assertEqual(err.status_code(), 400)
                self.assertGreater(len(err.error()), 0)
                self.assertGreater(len(err.message()), 0)
                errors = err.errors()
                self.assertEqual(len(errors), 1)
                self.assertEqual(errors[0]['field'], 'url')
                self.assertGreater(len(errors[0]['message']), 0)
                self.assertEqual(str(err), err.__unicode__())

    def test_get_page_analyze_error(self):
        with HTTMock(mocks.page_analyze_error_mock):
            page = self.client.get_page('http://bbc.com/')
            self.assertIsNotNone(page)
            self.assertTrue(page.is_error())
            self.assertEqual(page['error_code'], 'gx_error')
            self.assertIsNotNone(page['error_message'])

    def test_get_page_embed_segments_over_quota(self):
        with HTTMock(mocks.page_embed_segments_over_quota_mock):
            page = self.client.get_page('http://bbc.com/')
            self.assertIsNotNone(page)

            try:
                segments = page.get_embedded(rels.segments)
                self.assertIsNone(segments)
                self.assertFalse('We expect an error to be raised')
            except OverQuotaError as err:
                self.assertEqual(err.href(), page.get_link_href(rels.segments))

    def test_get_page_segments_over_quota_link(self):
        with HTTMock(mocks.page_mock, mocks.segments_over_quota_mock):
            page = self.client.get_page('http://bbc.com/')
            self.assertIsNotNone(page)

            try:
                segments = self.client.get_link(page, rels.segments)
                self.assertIsNone(segments)
                self.assertFalse('We expect an error to be raised')
            except OverQuotaError as err:
                self.assertEqual(err.href(), page.get_link_href(rels.segments))

    def test_unexpected_server_error(self):
        with HTTMock(mocks.unexpected_error_mock):
            try:
                page = self.client.get_page('http://bbc.com/')
                self.assertIsNone(page)
                self.assertFalse('We expect an error to be raised')
            except APIError as err:
                self.assertIsNotNone(err)
                self.assertEqual(err.status_code(), 500)
