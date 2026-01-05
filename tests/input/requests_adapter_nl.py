ID = "requests_adapter_nl"
TITLE = "Requests response"
TAGS = ["requests", "http"]
REQUIRES = ['requests']
DISPLAY_INPUT = "Response(status_code=200, url='https://example.com')"


def build():
    import requests as rq

    resp = rq.Response()
    resp.status_code = 200
    resp.url = "https://example.com"
    return resp


def expected(meta):
    return f"An HTTP response with status {meta['status_code']}."
