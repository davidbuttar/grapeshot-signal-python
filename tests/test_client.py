from __future__ import absolute_import
import unittest
from httmock import urlmatch, HTTMock
from grapeshot_signal import SignalClient, APIError, OverQuotaError, rels
import mocks


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
    
    def test_get_text(self):
        with HTTMock(mocks.text_mock):
            text = self.client.get_text('On the 9th. William Findley and David Redick--deputed by the Committee of Safety (as it is designated) which met on the 2d. of this month at Parkinson Ferry arrived in Camp with the Resolutions of the said Committee; and to give information of the State of things in the four Western Counties of Pennsylvania to wit--Washington Fayette Westd. & Alligany in order to see if it would prevent the March of the Army into them.  At 10 oclock I had a meeting with these persons in presence of Govr. Howell (of New Jersey) the Secretary of the Treasury, Colo. Hamilton, & Mr. Dandridge: Govr. Mifflin was invited to be present, but excused himself on acct. of business.  I told the Deputies that by one of the Resolutions it would appear that they were empowered to give information of the disposition & of the existing state of matters in the four Counties above men[tioned]; that I was ready to hear & would listen patiently, and with candour to what they had to say.  Mr. Findley began. He confined his information to such parts of the four Counties as he was best acquainted with; referring to Mr. Reddick for a recital of what fell within his knowledge, in the other parts of these Counties.  The substance of Mr. Findleys communications were as follows--viz.--That the People in the parts where he was best acquainted, had seen there folly; and he believed were disposed to submit to the Laws; that he thought, but could not undertake to be responsible, for the re-establishment of the public Offices for the Collection of the Taxes on distilled spirits, & Stills--intimating however, that it might be best for the present, & until the peoples minds were a little more tranquilized, to hold the Office of Inspection at Pitsburgh under the protection--or at least under the influence of the Garrison; That he thought the Distillers would either enter their stills or would put them down; That the Civil authority was beginning to recover its tone; & enumerated some instances of it; That the ignorance, & general want of information among the people far exceeded any thing he had any conception of; That it was not merely the excise law their opposition was aimed at, but to all law, & Government; and to the Officers of Government; and that the situation in which he had been, & the life he had led for sometime, was such, that rather than go through it again, he would prefer quitting this scene altogether.  Mr. Redicks information was similar to the above; except as to the three last recitals--on wch. I do not recollect that he expressed any sentiment further than that the situation of those who were not in the opposition to government whilst the frenzy was at its height, were obliged to sleep with their Arms by their bed Sides every night; not knowing but that before Morning they might have occasion to use them in defence of their persons, or their properties.  He added, that for a long time after the riots commenced, and until lately, the distrust of one another was such, that even friends were affraid to communicate their sentiments to each other; That by whispers this was brought about; and growing bolder as they became more communicative they found their strength, and that there was a general disposition not only to acquiesce under, but to support the Laws--and he gave some instances also of Magistrates enforcing them.  He said the People of those Counties believed that the opposition to the Excise law--or at least that their dereliction to it, in every other part of the U. States was similar to their own, and that no Troops could be got to March against them for the purpose of coercion; that every acct. until very lately, of Troops marching against them was disbelieved; & supposed to be the fabricated tales of governmental men; That now they had got alarmed; That many were disposing of their property at an under rate, in order to leave the Country, and added (I think) that they wd. go to Detroit. That no person of any consequence, except one, but what had availed themselves of the proffered amnesty; That those who were still in the opposition, and obnoxious to the laws, were Men of little or no property, & cared but little where they resided; That he did not believe there was the least intention in them to oppose the Army; & that there was not three rounds of ammunition for them in all the Western Country. He (& I think Mr. Findley also) was apprehensive that the resentments of the Army might be productive of treatment to some of these people that might be attended with disagreeable consequences; & on that account seemed to deprecate the March of it: declaring however, that it was their wish, if the people did not give proofs of unequivocal submission, that it might not stop short of its object.')
            self.assertIsNotNone(text)
            self.assertTrue(text.is_ok())
            self.assertFalse(text.is_over_quota())
            self.assertFalse(text.is_queued())
            self.assertFalse(text.is_error())
            self.assertIsNotNone(text.text())
            self.assertEqual(text['language'], 'en')

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

if __name__ == '__main__':
    unittest.main()
