import csv
import tempfile
import unittest
from pathlib import Path

from recommendation_system import Item, load_items, recommend


class RecommendationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.items = [
            Item("a", "Space Story", "space|science fiction", "mission among the stars"),
            Item("b", "Mars Mission", "space|science fiction", "astronaut on a mission"),
            Item("c", "Garden Guide", "plants|gardening", "grow flowers at home"),
        ]

    def test_recommendations_rank_matching_items_and_exclude_source(self) -> None:
        results = recommend(self.items, "a")

        self.assertEqual([item.item_id for item, _ in results], ["b"])
        self.assertGreater(results[0][1], 0)

    def test_unknown_id_and_invalid_limit_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "Item id not found"):
            recommend(self.items, "missing")
        with self.assertRaisesRegex(ValueError, "at least 1"):
            recommend(self.items, "a", 0)

    def test_load_items_reads_optional_description(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            csv_path = Path(directory) / "items.csv"
            with csv_path.open("w", encoding="utf-8", newline="") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(["id", "title", "tags", "description"])
                writer.writerow(["a", "Space Story", "space|science fiction", "stars"])

            items = load_items(csv_path)

        self.assertEqual(items, [Item("a", "Space Story", "space|science fiction", "stars")])


if __name__ == "__main__":
    unittest.main()