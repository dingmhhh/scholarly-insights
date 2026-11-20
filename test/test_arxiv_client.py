
from arxiv_client import parse_arxiv_response


def test_parse_arxiv_xml():
    xml = b"""
    <feed xmlns="http://www.w3.org/2005/Atom"
          xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/">
      <opensearch:totalResults>1</opensearch:totalResults>
      <entry>
        <id>http://arxiv.org/abs/2401.12345v1</id>
        <title>Example AI Paper</title>
        <summary>Example abstract</summary>
        <published>2024-01-20T00:00:00Z</published>
        <author><name>Alice Smith</name></author>
        <category term="cs.AI"/>
        <link title="pdf"
              href="https://arxiv.org/pdf/2401.12345"/>
      </entry>
    </feed>
    """

    result = parse_arxiv_response(xml)

    assert result["total_results"] == 1
    assert len(result["articles"]) == 1

    article = result["articles"][0]

    assert article["id"] == "2401.12345"
    assert article["title"] == "Example AI Paper"
    assert article["authors"] == ["Alice Smith"]
    assert article["categories"] == ["cs.AI"]
    assert article["published"] == "2024-01-20"
