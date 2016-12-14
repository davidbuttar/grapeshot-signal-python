#!/usr/bin/env python3
import argparse
import datetime
import json
import sys
import pyelasticsearch as pye

URL_MAPPINGS = {
    "urldata": {
        "properties": {
            "request_time": {
                "type": "date",
            },
            "response_time": {
                "type": "date",
            }
        }
    }
}



def run(infile, elastic):
    es = pye.ElasticSearch(elastic)
    doc_type = 'urldata'
    index_name = 'urls_{}_{}'.format('urls', datetime.datetime.utcnow().isoformat()).lower()
    es.create_index(index_name)
    es.put_mapping(index_name, doc_type, URL_MAPPINGS)
    with infile as f:

        data = (es.index_op(json.loads(line)) for line in f)
        chunks = pye.bulk_chunks(
            data, docs_per_chunk=500, bytes_per_chunk=10000)

        for chunk in chunks:
            es.bulk(chunk, doc_type=doc_type, index=index_name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("--infile", nargs="?",
                        help="file containing one url per line, defaults to stdin",
                        type=argparse.FileType('r'), default=sys.stdin)

    parser.add_argument("--elastic", nargs="?",
                        help="url for elastic, defaults to http://localhost:9200",
                        default='http://localhost:9200')

    args = parser.parse_args()
    run(args.infile, args.elastic)
