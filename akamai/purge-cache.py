from pprint import pprint

import requests
from akamai.edgegrid import EdgeGridAuth, EdgeRc

# EDGERC_PATH: str = "~/.edgerc"
EDGERC_PATH: str = "./.edgerc"
CACHE_OBJECT_URL: list[str] = [
    "https://foo.bar.com/some/path",
]

# https://techdocs.akamai.com/developer/docs/set-up-authentication-credentials
# https://techdocs.akamai.com/developer/docs/authenticate-with-edgegrid
# https://techdocs.akamai.com/developer/docs/python
edgerc = EdgeRc(EDGERC_PATH)
section = "ccu"
baseurl = "https://%s" % edgerc.get(section, "host")

s = requests.Session()
s.auth = EdgeGridAuth.from_edgerc(edgerc, section)

cache_objects: dict = {"objects": CACHE_OBJECT_URL}

# https://techdocs.akamai.com/purge-cache/reference/invalidate-url
# https://www.postman.com/akamai/workspace/akamai-apis/request/13085889-40173a25-c198-4826-83cf-7cb5aeb411fb
print(baseurl)
network: str = "production"
response: dict = s.post(
    url=f"{baseurl}/ccu/v3/invalidate/url/{network}",
    json=cache_objects,
).json()

# https://techdocs.akamai.com/purge-cache/reference/api-errors
pprint(response)
