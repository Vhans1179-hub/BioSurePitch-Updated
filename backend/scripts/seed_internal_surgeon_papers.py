"""
Script to create and seed internal_surgeon_papers collection with Internal Surgeon_Papers_2024.csv data.
This creates a new collection separate from the external surgeon_papers collection.
"""
import asyncio
import csv
from datetime import datetime
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from backend.config import settings
from backend.models.surgeon_paper import SurgeonPaperCreate


async def seed_internal_surgeon_papers():
    """Seed the internal_surgeon_papers collection with internal papers data."""
    print("🌱 Starting internal surgeon papers data seeding...")
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(settings.mongodb_uri)
    db = client[settings.database_name]
    papers_collection = db["internal_surgeon_papers"]
    
    try:
        # Check if data already exists
        existing_count = await papers_collection.count_documents({})
        if existing_count > 0:
            print(f"⚠️  Database already contains {existing_count} internal surgeon papers.")
            response = input("Do you want to clear and reseed? (yes/no): ")
            if response.lower() != "yes":
                print("❌ Seeding cancelled.")
                return
            
            # Clear existing data
            print("🗑️  Clearing existing internal surgeon papers data...")
            await papers_collection.delete_many({})
            print("✅ Existing data cleared.")
        
        # Read Internal CSV file from project root
        csv_path = Path(__file__).parent.parent.parent / "Internal Surgeon_Papers_2024.csv"
        
        if not csv_path.exists():
            print(f"❌ CSV file not found at: {csv_path}")
            return
        
        print(f"📖 Reading Internal CSV file from: {csv_path}")
        
        papers = []
        skipped_rows = 0
        
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is line 1)
                # Skip empty rows
                if not row.get("Title") or not row["Title"].strip():
                    skipped_rows += 1
                    continue
                
                # Map CSV columns to model fields
                paper_data = {
                    "title": row["Title"].strip(),
                    "journal": row["Journal"].strip() if row.get("Journal") else "",
                    "author_name": row["Author Name"].strip() if row.get("Author Name") else "",
                    "affiliation": row["Hospital Affliation"].strip() if row.get("Hospital Affliation") else "",
                    "website": row["Website"].strip() if row.get("Website") and row["Website"].strip() else None,
                    "address": row["Address"].strip() if row.get("Address") and row["Address"].strip() else None,
                    "email": row["Email"].strip() if row.get("Email") and row["Email"].strip() else None
                }
                
                # Validate with Pydantic model
                try:
                    paper = SurgeonPaperCreate(**paper_data)
                except Exception as e:
                    print(f"⚠️  Validation error on row {row_num}: {e}")
                    skipped_rows += 1
                    continue
                
                # Convert to dict for MongoDB insertion
                paper_dict = paper.model_dump()
                paper_dict["created_at"] = datetime.utcnow()
                paper_dict["updated_at"] = datetime.utcnow()
                
                papers.append(paper_dict)
                print(f"  ✓ Processed row {row_num}: {paper_data['title'][:60]}...")
        
        if not papers:
            print("❌ No valid papers found in CSV file.")
            return
        
        # Insert all papers
        print(f"\n💾 Inserting {len(papers)} papers into internal_surgeon_papers collection...")
        result = await papers_collection.insert_many(papers)
        print(f"✅ Successfully inserted {len(result.inserted_ids)} internal surgeon papers!")
        
        if skipped_rows > 0:
            print(f"⚠️  Skipped {skipped_rows} empty or invalid rows.")
        
        # Create indexes
        print("🔍 Creating indexes...")
        await papers_collection.create_index("title")
        await papers_collection.create_index("author_name")
        await papers_collection.create_index("journal")
        await papers_collection.create_index("email")
        print("✅ Indexes created successfully!")
        
        # Display statistics
        print("\n📊 Seeding Statistics:")
        print(f"  Total papers: {len(papers)}")
        
        # Count by journal
        journal_counts = {}
        for p in papers:
            journal = p["journal"]
            journal_counts[journal] = journal_counts.get(journal, 0) + 1
        
        print(f"  Unique journals: {len(journal_counts)}")
        print(f"  Top journals:")
        for journal, count in sorted(journal_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"    - {journal}: {count}")
        
        # Count papers with websites
        papers_with_websites = sum(1 for p in papers if p.get("website"))
        print(f"  Papers with websites: {papers_with_websites}/{len(papers)}")
        
        # Count papers with emails
        papers_with_emails = sum(1 for p in papers if p.get("email"))
        print(f"  Papers with emails: {papers_with_emails}/{len(papers)}")
        
        # Count papers with addresses
        papers_with_addresses = sum(1 for p in papers if p.get("address"))
        print(f"  Papers with addresses: {papers_with_addresses}/{len(papers)}")
        
        print("\n🎉 Internal surgeon papers data seeding completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        raise
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(seed_internal_surgeon_papers())