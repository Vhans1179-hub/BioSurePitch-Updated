# Surgeon Papers Search Feature - Internal/External Workflow

## Overview

The surgeon papers search feature now implements a sophisticated workflow that prioritizes internal data while providing seamless access to external data when needed. This ensures data consistency and gives users control over their internal database.

## Workflow

### 1. Initial Search (Internal First)
When a user searches for publications by a surgeon (e.g., "Show me publications by Nakamura H"), the system:
- **Searches the `internal_surgeon_papers` collection first**
- If papers are found, displays them with all available information
- Provides an option to check for updates from external sources

### 2. Fetch External Data
If the user wants to check external sources or if no internal data exists:
- User types: `Fetch external data for [Author Name]`
- System searches the `surgeon_papers` (external) collection
- Compares internal and external data if both exist
- Shows differences and missing information

### 3. Update Internal Database
When differences or missing data are identified:
- User types: `Update internal for [Author Name]`
- System synchronizes internal database with external data
- Updates existing papers with new information
- Adds missing papers to internal collection
- Confirms successful update

## User Commands

### Search for Papers
```
Show me publications by Nakamura H
Find papers by Sharma R
What papers did Kahraman E publish?
```

### Fetch External Data
```
Fetch external data for Nakamura H
```

### Update Internal Database
```
Update internal for Nakamura H
```

## Data Comparison

The system compares the following fields:
- **Title** - Paper title
- **Journal** - Journal name
- **Author Name** - Author's name
- **Affiliation** - Hospital/institution affiliation
- **Website** - Paper or institution website
- **Address** - Hospital/institution address
- **Email** - Contact email

### Comparison Statuses

1. **Up to date** ✅
   - All fields match between internal and external

2. **Missing fields** ⚠️
   - External has data that internal doesn't have
   - Example: External has email, internal doesn't

3. **Different values** ⚠️
   - Both have the field but values differ
   - Example: Different affiliation addresses

4. **Missing paper** ⚠️
   - Paper exists in external but not in internal

## Response Examples

### Example 1: Papers Found in Internal Database

```markdown
**Surgeon Papers by Nakamura H** (1 found in internal database):

1. **[System Changes to Carry Out Working-style Reforms at Department of Cardiovascular Surgery of the Local University Hospital].**
   - **Author:** Nakamura H
   - **Journal:** Kyobu geka. The Japanese journal of thoracic surgery
   - **Affiliation:** Department of Cardiovascular Surgery, Kochi University, Nankoku, Japan.
   - **Website:** https://www.kochi-u.ac.jp/kms/en/courses/31/
   - **Address:** Kohasu,Oko-cho,Nankoku-shi,Kochi 783-8505, JAPAN
   - **Email:** kms-info@kochi-u.ac.jp

💡 **Want to check for updates?**
Type: `Fetch external data for Nakamura H` to compare with external database.
```

### Example 2: No Internal Data Found

```markdown
No papers found for author **Sharma R** in the internal database.

💡 **Would you like to search external data?**
Type: `Fetch external data for Sharma R`
```

### Example 3: Comparison Results

```markdown
**Comparison: Internal vs External Data for Nakamura H**

📄 **[System Changes to Carry Out Working-style Reforms...]**
   ⚠️ **Status:** Differences found

   - **Email:** Missing in internal
     External value: kms-info@kochi-u.ac.jp
   - **Address:** Values differ
     Internal: Kohasu, Nankoku, Japan
     External: Kohasu,Oko-cho,Nankoku-shi,Kochi 783-8505, JAPAN

💡 **Update internal database?**
Type: `Update internal for Nakamura H` to sync with external data.
```

### Example 4: Update Confirmation

```markdown
✅ **Update Complete**

Successfully updated 1 paper(s) for **Nakamura H** in the internal collection.
```

## Database Collections

### internal_surgeon_papers
- Contains curated, verified surgeon papers
- Maintained by the organization
- Primary source for searches
- Can be updated from external sources

### surgeon_papers (External)
- Contains comprehensive external data
- Updated from external CSV files
- Used as reference for updates
- Read-only for comparison purposes

## Data Model

Both collections use the same schema:

```javascript
{
  title: String (required),
  journal: String (required),
  author_name: String (required),
  affiliation: String (required),
  website: String (optional),
  address: String (optional),
  email: String (optional),
  created_at: DateTime,
  updated_at: DateTime
}
```

## Backend Services

### SurgeonPaperService

Key methods:
- `search_internal_by_author()` - Search internal collection
- `search_by_author()` - Search external collection
- `search_both_collections()` - Search both simultaneously
- `compare_papers()` - Compare internal vs external papers
- `update_internal_paper()` - Update existing internal paper
- `add_to_internal_collection()` - Add new paper to internal

### SurgeonPaperSearchHandler

Handles three types of actions:
- `search` - Initial search in internal collection
- `fetch_external` - Fetch and compare external data
- `update_internal` - Update internal with external data

## Data Management Scripts

### Update External Collection
```bash
python -m backend.scripts.update_external_surgeon_papers
```
- Updates `surgeon_papers` collection
- Reads from `External Surgeon_Papers_2024.csv`
- Clears and reloads all external data

### Seed Internal Collection
```bash
python -m backend.scripts.seed_internal_surgeon_papers
```
- Seeds `internal_surgeon_papers` collection
- Reads from `Internal Surgeon_Papers_2024.csv`
- Creates new collection if doesn't exist

## Testing

Run the workflow test:
```bash
python test_surgeon_paper_workflow.py
```

This tests:
- Collection counts
- Internal search
- External search
- Paper comparison
- Simultaneous search of both collections

## Benefits

1. **Data Control** - Organization maintains curated internal database
2. **Transparency** - Users see exactly what data differs
3. **Flexibility** - Easy to sync with external sources when needed
4. **Audit Trail** - All updates are timestamped
5. **User Choice** - Users decide when to fetch/update external data

## Future Enhancements

Potential improvements:
- Automatic scheduled sync with external sources
- Conflict resolution UI for ambiguous differences
- Bulk update operations
- Export internal database to CSV
- Version history for paper updates
- Email notifications for new external papers