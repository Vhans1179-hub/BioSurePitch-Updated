import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from backend.config import settings

async def check():
    client = AsyncIOMotorClient(settings.mongodb_uri)
    db = client[settings.database_name]
    
    ext_count = await db.surgeon_papers.count_documents({})
    int_count = await db.internal_surgeon_papers.count_documents({})
    
    print(f'External papers collection: {ext_count} documents')
    print(f'Internal papers collection: {int_count} documents')
    
    # Get a sample from each
    if ext_count > 0:
        sample_ext = await db.surgeon_papers.find_one()
        print(f'\nSample external paper: {sample_ext.get("author_name", "N/A")} - {sample_ext.get("title", "N/A")[:50]}...')
    
    if int_count > 0:
        sample_int = await db.internal_surgeon_papers.find_one()
        print(f'Sample internal paper: {sample_int.get("author_name", "N/A")} - {sample_int.get("title", "N/A")[:50]}...')
    
    client.close()

asyncio.run(check())