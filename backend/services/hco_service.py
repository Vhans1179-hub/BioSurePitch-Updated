"""
HCO Service Layer for BioSure Analytics.

This service encapsulates HCO data access logic, making it reusable
for both API routers and the chat system.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId


class HCOService:
    """Service for HCO data operations."""
    
    @staticmethod
    async def get_top_hcos_by_ghost_patients(
        db: AsyncIOMotorDatabase,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get top HCOs sorted by ghost patients count.
        
        Args:
            db: MongoDB database instance
            limit: Number of top HCOs to return (default: 5)
            
        Returns:
            List of HCO documents with calculated leakage_rate
        """
        hcos_collection = db["hcos"]
        
        # Query for top HCOs by ghost patients
        cursor = hcos_collection.find({}).sort("ghost_patients", -1).limit(limit)
        hcos_data = await cursor.to_list(length=limit)
        
        # Calculate leakage_rate for each HCO
        for hco in hcos_data:
            hco["_id"] = str(hco["_id"])
            total_patients = hco["ghost_patients"] + hco["treated_patients"]
            hco["leakage_rate"] = (
                (hco["ghost_patients"] / total_patients * 100) 
                if total_patients > 0 
                else 0.0
            )
        
        return hcos_data
    
    @staticmethod
    async def get_hcos(
        db: AsyncIOMotorDatabase,
        region: Optional[str] = None,
        state: Optional[str] = None,
        min_ghost_patients: Optional[int] = None,
        sort_by: str = "ghost_patients",
        limit: int = 100,
        skip: int = 0,
    ) -> tuple[List[Dict[str, Any]], int]:
        """
        Get paginated list of HCOs with optional filtering and sorting.
        
        Args:
            db: MongoDB database instance
            region: Filter by geographic region
            state: Filter by 2-character state code
            min_ghost_patients: Minimum number of ghost patients
            sort_by: Sort field (ghost_patients, leakage_rate, name)
            limit: Number of records to return
            skip: Number of records to skip for pagination
            
        Returns:
            Tuple of (list of HCO documents, total count)
        """
        hcos_collection = db["hcos"]
        
        # Build filter query
        filter_query = {}
        
        if region:
            filter_query["region"] = region
        
        if state:
            filter_query["state"] = state.upper()
        
        if min_ghost_patients is not None:
            filter_query["ghost_patients"] = {"$gte": min_ghost_patients}
        
        # Get total count
        total = await hcos_collection.count_documents(filter_query)
        
        # Determine sort order
        sort_field = "ghost_patients"
        sort_order = -1  # Descending by default
        
        if sort_by == "leakage_rate":
            # For leakage_rate, use aggregation pipeline
            pipeline = [
                {"$match": filter_query},
                {
                    "$addFields": {
                        "leakage_rate": {
                            "$multiply": [
                                {
                                    "$divide": [
                                        "$ghost_patients",
                                        {"$add": ["$ghost_patients", "$treated_patients"]}
                                    ]
                                },
                                100
                            ]
                        }
                    }
                },
                {"$sort": {"leakage_rate": -1}},
                {"$skip": skip},
                {"$limit": limit}
            ]
            
            hcos_data = await hcos_collection.aggregate(pipeline).to_list(length=limit)
        elif sort_by == "name":
            sort_field = "name"
            sort_order = 1  # Ascending for name
            cursor = hcos_collection.find(filter_query).sort(sort_field, sort_order).skip(skip).limit(limit)
            hcos_data = await cursor.to_list(length=limit)
        else:
            # Default: sort by ghost_patients descending
            cursor = hcos_collection.find(filter_query).sort("ghost_patients", -1).skip(skip).limit(limit)
            hcos_data = await cursor.to_list(length=limit)
        
        # Calculate leakage_rate if not already present
        for hco in hcos_data:
            hco["_id"] = str(hco["_id"])
            
            if "leakage_rate" not in hco:
                total_patients = hco["ghost_patients"] + hco["treated_patients"]
                hco["leakage_rate"] = (
                    (hco["ghost_patients"] / total_patients * 100)
                    if total_patients > 0
                    else 0.0
                )
        
        return hcos_data, total
    
    @staticmethod
    async def get_hco_by_name(
        db: AsyncIOMotorDatabase,
        name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Find an HCO by name (case-insensitive, fuzzy match).
        
        Args:
            db: MongoDB database instance
            name: HCO name to search for
            
        Returns:
            HCO document if found, None otherwise
        """
        hcos_collection = db["hcos"]
        
        # Try exact match first (case-insensitive)
        hco = await hcos_collection.find_one(
            {"name": {"$regex": f"^{name}$", "$options": "i"}}
        )
        
        if hco:
            hco["_id"] = str(hco["_id"])
            return hco
        
        # Try partial match if exact match fails
        hco = await hcos_collection.find_one(
            {"name": {"$regex": name, "$options": "i"}}
        )
        
        if hco:
            hco["_id"] = str(hco["_id"])
            return hco
        
        return None
    
    @staticmethod
    async def update_hco_address(
        db: AsyncIOMotorDatabase,
        hco_id: str,
        address_data: Dict[str, Any]
    ) -> bool:
        """
        Update an HCO's address information.
        
        Args:
            db: MongoDB database instance
            hco_id: HCO document ID (MongoDB ObjectId as string)
            address_data: Dictionary with address, city, state, zip_code
            
        Returns:
            True if update successful, False otherwise
        """
        hcos_collection = db["hcos"]
        
        # Prepare update document
        update_doc = {
            "updated_at": datetime.utcnow(),
            "address_last_updated": datetime.utcnow()
        }
        
        # Add address fields if provided
        if address_data.get("address"):
            update_doc["address"] = address_data["address"]
        if address_data.get("city"):
            update_doc["city"] = address_data["city"]
        if address_data.get("state"):
            update_doc["state"] = address_data["state"]
        if address_data.get("zip_code"):
            update_doc["zip_code"] = address_data["zip_code"]
        
        # Update the document
        result = await hcos_collection.update_one(
            {"_id": ObjectId(hco_id)},
            {"$set": update_doc}
        )
        
        return result.modified_count > 0