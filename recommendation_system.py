"""Content-based recommendations from a CSV catalog."""

from __future__ import annotations

import argparse
import csv
import math
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Item:
	item_id: str
	title: str
	tags: str
	description: str = ""


def _tokens(item: Item) -> Counter[str]:
	text = f"{item.tags.replace('|', ' ')} {item.description}"
	return Counter(re.findall(r"\w+", text.casefold()))


def shared_terms(left: Item, right: Item) -> list[str]:
	"""Return the unique normalized terms shared by two items."""
	return sorted(_tokens(left).keys() & _tokens(right).keys())


def load_items(csv_path: str | Path) -> list[Item]:
	"""Load items from a CSV with id, title, and tags columns."""
	with Path(csv_path).open(encoding="utf-8-sig", newline="") as csv_file:
		reader = csv.DictReader(csv_file)
		required = {"id", "title", "tags"}
		headers = set(reader.fieldnames or [])
		missing = required - headers
		if missing:
			raise ValueError(f"Missing required CSV columns: {', '.join(sorted(missing))}")

		items: list[Item] = []
		seen_ids: set[str] = set()
		for row_number, row in enumerate(reader, start=2):
			item_id = (row.get("id") or "").strip()
			title = (row.get("title") or "").strip()
			tags = (row.get("tags") or "").strip()
			if not item_id or not title:
				raise ValueError(f"CSV row {row_number} must have an id and title")
			if item_id in seen_ids:
				raise ValueError(f"Duplicate item id on CSV row {row_number}: {item_id}")
			seen_ids.add(item_id)
			items.append(Item(item_id, title, tags, (row.get("description") or "").strip()))

	if not items:
		raise ValueError("The CSV catalog contains no items")
	return items


def _cosine_similarity(left: Counter[str], right: Counter[str]) -> float:
	shared = left.keys() & right.keys()
	dot_product = sum(left[token] * right[token] for token in shared)
	left_norm = math.sqrt(sum(count * count for count in left.values()))
	right_norm = math.sqrt(sum(count * count for count in right.values()))
	if not left_norm or not right_norm:
		return 0.0
	return dot_product / (left_norm * right_norm)


def recommend(items: list[Item], item_id: str, limit: int = 5) -> list[tuple[Item, float]]:
	"""Return the most similar items and their cosine similarity scores."""
	if limit < 1:
		raise ValueError("limit must be at least 1")
	selected = next((item for item in items if item.item_id == item_id), None)
	if selected is None:
		raise ValueError(f"Item id not found: {item_id}")

	selected_tokens = _tokens(selected)
	scored = [
		(item, _cosine_similarity(selected_tokens, _tokens(item)))
		for item in items
		if item.item_id != item_id
	]
	scored = [result for result in scored if result[1] > 0]
	return sorted(scored, key=lambda result: (-result[1], result[0].title.casefold()))[:limit]


def main() -> int:
	parser = argparse.ArgumentParser(description="Recommend similar items from a CSV catalog.")
	parser.add_argument("--file", default="sample_items.csv", help="Path to the item CSV")
	parser.add_argument("--item", required=True, help="ID of the item to use as a starting point")
	parser.add_argument("--limit", type=int, default=5, help="Maximum recommendations to show")
	args = parser.parse_args()

	try:
		items = load_items(args.file)
		results = recommend(items, args.item, args.limit)
	except (OSError, ValueError) as error:
		parser.error(str(error))

	if not results:
		print("No similar items found.")
		return 0

	selected = next(item for item in items if item.item_id == args.item)
	print(f"Recommendations for {args.item}:")
	for item, score in results:
		matches = ", ".join(shared_terms(selected, item))
		print(f"{item.item_id}\t{item.title}\t{score:.0%}\tMatches: {matches}")
	return 0


if __name__ == "__main__":
	sys.exit(main())
