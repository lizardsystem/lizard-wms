from django.test import TestCase

from lizard_wms import url_utils


class TestCombineUrlAndParams(TestCase):
    def test_empty_params_dict(self):
        self.assertEquals(
            url_utils.combine_url_and_params(
                'http://example.com/',
                {}),
            'http://example.com/')

    def test_one_param(self):
        self.assertEquals(
            url_utils.combine_url_and_params(
                'http://example.com/',
                {'question': 'answer'}),
            'http://example.com/?question=answer')

    def test_existing_param(self):
        self.assertEquals(
            url_utils.combine_url_and_params(
                'http://example.com/?one=two',
                {'question': 'answer'}),
            'http://example.com/?one=two&question=answer')

    def test_domain_without_slash(self):
        self.assertEquals(
            url_utils.combine_url_and_params(
                'http://example.com',
                {'question': 'answer'}),
            'http://example.com/?question=answer')

    def test_escaping_space(self):
        self.assertEquals(
            url_utils.combine_url_and_params(
                'http://example.com/',
                {'question': 'answer with spaces'}),
            'http://example.com/?question=answer+with+spaces')

    def test_escaping(self):
        self.assertEquals(
            url_utils.combine_url_and_params(
                'http://example.com/',
                {'question': 'answer&ampersand'}),
            'http://example.com/?question=answer%26ampersand')

