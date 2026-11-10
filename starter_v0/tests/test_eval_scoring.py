from __future__ import annotations

from run_eval import compare_subset


def test_compare_subset_handles_lists_of_item_objects() -> None:
    expected = {"items": [{"title": "A", "url": "https://example.org/a"}, {"title": "B", "url": "https://example.org/b"}]}
    same_items_reordered = {"items": [{"title": "B", "url": "https://example.org/b"}, {"title": "A", "url": "https://example.org/a"}]}
    missing_item = {"items": [{"title": "A", "url": "https://example.org/a"}]}

    assert compare_subset(expected, same_items_reordered)[0] is True
    assert compare_subset(expected, missing_item)[0] is False
