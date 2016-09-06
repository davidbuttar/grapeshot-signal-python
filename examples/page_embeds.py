import sys
import os
import requests.exceptions
from grapeshot_signal import SignalClient, APIError, OverQuotaError, rels


#
# An example showing request of page analysis with segments and keywords
# in a single request using embedding.
#
# Run with a single argument, the url of the you want to analyze.
#
# Set your API key in environment variable GRAPESHOT_API_KEY
#

api_key = os.environ.get("GRAPESHOT_API_KEY")


def print_model(model_name, model, field):
    print(model_name)

    if model.is_ok():
        print(field, '=', model[field])

    elif model.is_queued():
        print('URL is queued. Try again in a minute or two.')

    elif model.is_error():
        print('Unable to analyze page. {0} {1}'.format(model['error_code'], model['error_message']))


def main(url):

    client = SignalClient(api_key)

    try:
        page = client.get_page(url, [rels.keywords, rels.segments])
        print_model("Page", page, "language")

        if not page.is_error() and not page.is_queued():
            segments = page.get_embedded(rels.segments)
            print_model("Segments", segments, "segments")

            keywords = page.get_embedded(rels.keywords)
            print_model("Keywords", keywords, "keywords")

    except APIError as err:
        # Non-200 level response
        print('API error: {0}'.format(err))

    except OverQuotaError as err:
        # Over your Grapeshot plan quota
        print('Over quota error: {0}'.format(err.href()))

    except requests.exceptions.ConnectionError as err:
        print('Connection error {0}'.format(err))


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage: {0} <webpage_url>".format(sys.argv[0]))
        sys.exit(1)

    main(sys.argv[1])
