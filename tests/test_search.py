from semantic_search_service import ContentItem, search_content


class FakeClient:
    def embeddings(self, text):
        return [1.0, 0.0]

    def query(self, collection, embedding, top_k, filter_):
        assert filter_ == {"subscriber_tier": "supporter"}
        return {"matches": [{"id": "a", "metadata": {"text": "launch checklist"}}]}

    def rerank(self, query, candidates, top_k):
        return {"results": [{"id": "a", "text": "launch checklist", "score": 1.0}]}


def test_search_returns_ranked_content_for_subscriber():
    result = search_content(FakeClient(), "creator-content", "launch checklist", "supporter")
    assert result == [{"id": "a", "text": "launch checklist", "score": 1.0}]

