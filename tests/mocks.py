import json
import os
from httmock import urlmatch


def load_file(file):
    with open(os.path.join('.', 'tests', 'data', file), encoding="utf-8") as fp:
        return fp.read()


@urlmatch(path='/v1/pages', query='(url=.+)')
def page_mock(url, request):
    return load_file('page.json')


@urlmatch(path='/v1/pages', query=r'.*((embed=keywords.*)?(embed=segments.*)?(url=.+))+')
def page_embed_segments_keywords_mock(url, request):
    return load_file('page_embed_segments_keywords.json')


@urlmatch(path='/v1/pages', query=r'.*embed=keywords.*')
def page_embed_keywords_mock(url, request):
    text = load_file('page_embed_segments_keywords.json')
    data = json.loads(text)
    del data['_embedded']['grapeshot:segments']
    return json.dumps(data)


@urlmatch(path='/v1/pages', query=r'.*embed=segments.*')
def page_embed_segments_mock(url, request):
    text = load_file('page_embed_segments_keywords.json')
    data = json.loads(text)
    del data['_embedded']['grapeshot:keywords']
    return json.dumps(data)


@urlmatch(path='/v1/keywords', query=r'(url=.+)')
def keywords_mock(url, request):
    return load_file('keywords.json')


@urlmatch(path='/v1/segments', query=r'(url=.+)')
def segments_mock(url, request):
    return load_file('segments.json')


@urlmatch(path='/v1/pages')
def page_missing_url_mock(url, request):
    return {
        'status_code': 400,
        'content': load_file('400_error.json')
    }


@urlmatch(path='/v1/pages', query='(url=.+)')
def page_queued_mock(url, request):
    return load_file('page_queued.json')


@urlmatch(path='/v1/pages', query='(url=.+)')
def page_analyze_error_mock(url, request):
    return load_file('page_analyze_error.json')


@urlmatch(path='/v1/pages', query=r'.*((embed=keywords.*)?(embed=segments.*)?(url=.+))+')
def page_embed_segments_over_quota_mock(url, request):
    return load_file('page_embed_segments_over_quota.json')


@urlmatch(path='/v1/segments', query=r'(url=.+)')
def segments_over_quota_mock(url, request):
    return load_file('segments_over_quota.json')


@urlmatch(path='/v1/pages')
def unexpected_error_mock(url, request):
    return {
        'status_code': 500,
        'content': 'Something interfered with this request'
    }
