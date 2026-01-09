# Surgeon Papers Data Management Scripts

This directory contains scripts for managing surgeon papers data in the MongoDB database.

## Collections

- **surgeon_papers**: External surgeon papers data (from `External Surgeon_Papers_2024.csv`)
- **internal_surgeon_papers**: Internal surgeon papers data (from `Internal Surgeon_Papers_2024.csv`)

## Data Model

Both collections use the same schema with the following fields:

- `title`: Paper title (required)
- `journal`: Journal name (required)
- `author_name`: Author name (required)
- `affiliation`: Hospital affiliation (required)
- `website`: Paper or author website URL (optional)
- `address`: Hospital or institution address (optional)
- `email`: Contact email (optional)
- `created_at`: Creation timestamp (auto-generated)
- `updated_at`: Last update timestamp (auto-generated)

## Scripts

### 1. update_external_surgeon_papers.py

Updates the `surgeon_papers` collection with data from `External Surgeon_Papers_2024.csv`.

**Usage:**
```bash
python -m backend.scripts.update_external_surgeon_papers
```

**What it does:**
- Prompts for confirmation before clearing existing data
- Reads data from `External Surgeon_Papers_2024.csv` in the project root
- Validates each row using Pydantic models
- Clears the existing `surgeon_papers` collection
- Inserts all valid papers
- Creates indexes on title, author_name, journal, and email fields
- Displays statistics about the imported data

**Interactive prompts:**
- "Do you want to clear and reload with external papers data? (yes/no):"

### 2. seed_internal_surgeon_papers.py

Creates and seeds the `internal_surgeon_papers` collection with data from `Internal Surgeon_Papers_2024.csv`.

**Usage:**
```bash
python -m backend.scripts.seed_internal_surgeon_papers
```

**What it does:**
- Checks if the `internal_surgeon_papers` collection already has data
- Prompts for confirmation before clearing existing data (if any)
- Reads data from `Internal Surgeon_Papers_2024.csv` in the project root
- Validates each row using Pydantic models
- Inserts all valid papers into the new collection
- Creates indexes on title, author_name, journal, and email fields
- Displays statistics about the imported data

**Interactive prompts:**
- "Do you want to clear and reseed? (yes/no):" (only if data already exists)

### 3. seed_surgeon_papers.py (Legacy)

Original seeding script that reads from `Surgeon_Papers_2024.csv`. This script is kept for backward compatibility but may not include the new address and email fields.

## CSV File Format

Both CSV files should have the following columns:

```
Title,Journal,Author Name,Hospital Affliation,Website,Address,Email
```

**Notes:**
- Empty rows are automatically skipped
- Rows with missing required fields (Title, Journal, Author Name, Affiliation) will be skipped with a warning
- Optional fields (Website, Address, Email) can be empty
- The CSV files should be placed in the project root directory

## Running the Scripts

### Prerequisites

1. Ensure MongoDB is running and accessible
2. Set up the `.env` file with correct MongoDB connection string
3. Place the CSV files in the project root:
   - `External Surgeon_Papers_2024.csv`
   - `Internal Surgeon_Papers_2024.csv`

### Step-by-Step Process

1. **Update External Papers (surgeon_papers collection):**
   ```bash
   python -m backend.scripts.update_external_surgeon_papers
   ```
   - Type `yes` when prompted to confirm the update

2. **Seed Internal Papers (internal_surgeon_papers collection):**
   ```bash
   python -m backend.scripts.seed_internal_surgeon_papers
   ```
   - Type `yes` when prompted to confirm (if data exists)

### Expected Output

Both scripts will display:
- Progress messages for each processed row
- Number of papers inserted
- Number of rows skipped (if any)
- Statistics including:
  - Total papers
  - Unique journals
  - Top journals by count
  - Papers with websites
  - Papers with emails
  - Papers with addresses

## Indexes

The following indexes are created automatically:

- `title`: For searching by paper title
- `author_name`: For searching by author
- `journal`: For filtering by journal
- `email`: For email lookups

## Error Handling

- **CSV file not found**: Script will exit with an error message
- **Validation errors**: Invalid rows are skipped with a warning message
- **Database connection errors**: Script will raise an exception with details
- **Empty CSV**: Script will exit if no valid papers are found

## Troubleshooting

### ModuleNotFoundError
If you get `ModuleNotFoundError: No module named 'backend'`, make sure to run the script as a module:
```bash
python -m backend.scripts.update_external_surgeon_papers
```
Not:
```bash
python backend/scripts/update_external_surgeon_papers.py
```

### CSV Encoding Issues
If you encounter encoding errors, ensure the CSV files are saved with UTF-8 encoding.

### Database Connection Issues
Verify your MongoDB connection string in the `.env` file and ensure MongoDB is running.

## Data Verification

After running the scripts, you can verify the data using MongoDB Compass or the mongo shell:

```javascript
// Check external papers count
db.surgeon_papers.countDocuments()

// Check internal papers count
db.internal_surgeon_papers.countDocuments()

// Sample external paper
db.surgeon_papers.findOne()

// Sample internal paper
db.internal_surgeon_papers.findOne()