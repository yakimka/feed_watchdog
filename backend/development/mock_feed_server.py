import argparse
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse
from uuid import uuid4

XML_BODY = """
<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"
    xmlns:media="http://search.yahoo.com/mrss/" xml:lang="en-US">
  <id>tag:github.com,2008:/yakimka/feed_watchdog/commits/master</id>
  <link type="text/html" rel="alternate"
    href="https://github.com/yakimka/feed_watchdog/commits/master"/>
  <link type="application/atom+xml" rel="self"
    href="https://github.com/yakimka/feed_watchdog/commits/master.atom"/>
  <title>Recent Commits to feed_watchdog:master</title>
  <updated>2023-04-08T21:52:49Z</updated>
    {entries}
</feed>
"""
XML_ENTRY = """
  <entry>
    <id>{id}</id>
    <link type="text/html" rel="alternate" href="{link}"/>
    <title>{title}</title>
    <updated>2023-04-08T21:52:49Z</updated>
    <media:thumbnail height="30" width="30"
        url="https://avatars.githubusercontent.com/u/28621349"/>
    <author>
      <name>yakimka</name>
      <uri>https://github.com/yakimka</uri>
    </author>
    <content type="text">{content}</content>
  </entry>
"""


def feed_request_handler() -> type[BaseHTTPRequestHandler]:
    class MyMockFeedHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            self.send_response(200)
            self.send_header("Content-type", "text/xml")
            self.end_headers()

            num_entries = int(self.QUERY.get("quantity", [10])[0])
            self.wfile.write(self._make_feed(num_entries=num_entries))

        def _make_feed(self, num_entries: int) -> bytes:
            entries = []
            for i in range(1, num_entries + 1):
                entry = XML_ENTRY.strip().format(
                    id=f"entry-{i}-{uuid4()}",
                    link=f"https://github.com/yakimka/feed_watchdog/?num={i}",
                    title=f"Title of entry #{i}",
                    content=f"Content of entry #{i}",
                )
                entries.append(entry)

            return XML_BODY.strip().format(entries="".join(entries)).encode("utf-8")

        @property
        def QUERY(self) -> dict:  # noqa: N802
            res = urlparse(self.path)
            return parse_qs(res.query)

    return MyMockFeedHandler


def run_server(port: int, server_class=ThreadingHTTPServer) -> None:
    server_address = ("", port)
    httpd = server_class(server_address, feed_request_handler())
    httpd.serve_forever()


def main(argv: list[str]) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8001)
    args = parser.parse_args(argv[1:])
    print("Starting server on port", args.port)
    run_server(port=args.port)


if __name__ == "__main__":
    main(sys.argv)
