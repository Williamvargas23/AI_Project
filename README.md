# AI_Project

Content-based item recommendation using Python's standard library. The first
version compares tags and descriptions with cosine similarity; it does not
require installing packages.

## Requirements

- Python 3.10 or newer

## Run it

From this folder, run:

```powershell
python recommendation_system.py --item movie-001
```

The command uses `sample_items.csv` by default. Choose how many results to show
or provide another catalog:

```powershell
python recommendation_system.py --file sample_items.csv --item movie-004 --limit 3
```

## CSV format

The required columns are `id`, `title`, and `tags`. Tags should be separated
with `|`. The optional `description` column adds more text to compare.
Identifiers must be unique and each row must have an ID and title.

```csv
id,title,tags,description
movie-001,Example film,science fiction|adventure,Space exploration
```

Recommendations exclude the selected item, show only items with at least one
matching term, and are ordered by cosine similarity. Each result also lists the
normalized terms it shares with the selected item.

## Tests

Run the test suite with:

```powershell
python -m unittest -v
```