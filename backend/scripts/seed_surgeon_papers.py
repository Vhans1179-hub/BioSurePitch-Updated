"""
Database seeding script for surgeon papers data.
Loads data from Surgeon_Papers_2024.csv and inserts into MongoDB.
"""
import asyncio
import csv
from datetime import datetime
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from backend.config import settings
from backend.models.surgeon_paper import SurgeonPaperCreate


async def seed_surgeon_papers():
    """Seed the database with surgeon papers from CSV file."""
    print("🌱 Starting surgeon papers data seeding...")
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(settings.mongodb_uri)
    db = client[settings.database_name]
    papers_collection = db["surgeon_papers"]
    
    try:
        # Check if data already exists
        existing_count = await papers_collection.count_documents({})
        if existing_count > 0:
            print(f"⚠️  Database already contains {existing_count} surgeon papers.")
            response = input("Do you want to clear and reseed? (yes/no): ")
            if response.lower() != "yes":
                print("❌ Seeding cancelled.")
                return
            
            # Clear existing data
            print("🗑️  Clearing existing surgeon papers data...")
            await papers_collection.delete_many({})
        
        # Read CSV file from project root
        csv_path = Path(__file__).parent.parent.parent / "Surgeon_Papers_2024.csv"
        
        if not csv_path.exists():
            print(f"❌ CSV file not found at: {csv_path}")
            return
        
        print(f"📖 Reading CSV file from: {csv_path}")
        
        papers = []
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is line 1)
                # Map CSV columns to model fields
                paper_data = {
                    "title": row["Title"].strip(),
                    "journal": row["Journal"].strip(),
                    "author_name": row["Author Name"].strip(),
                    "affiliation": row["Affiliation"].strip(),
                    "website": row["Website"].strip() if row["Website"].strip() else None
                }
                
                # Validate with Pydantic model
                try:
                    paper = SurgeonPaperCreate(**paper_data)
                except Exception as e:
                    print(f"⚠️  Validation error on row {row_num}: {e}")
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
        print(f"\n💾 Inserting {len(papers)} papers into database...")
        result = await papers_collection.insert_many(papers)
        print(f"✅ Successfully inserted {len(result.inserted_ids)} surgeon papers!")
        
        # Create indexes
        print("🔍 Creating indexes...")
        await papers_collection.create_index("title")
        await papers_collection.create_index("author_name")
        await papers_collection.create_index("journal")
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
        
        print("\n🎉 Surgeon papers data seeding completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        raise
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(seed_surgeon_papers())