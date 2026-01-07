"""
CMS Hospital Enrollments API Service.

This service uses the official CMS Hospital Enrollments dataset to search for
healthcare organization addresses. This is a free, official government
data source with no API key required.

API Documentation: https://data.cms.gov/provider-characteristics/hospitals-and-other-facilities/hospital-enrollments
Dataset API: https://data.cms.gov/data-api/v1/dataset/f6f6505c-e8b0-4d57-b258-e2b94133aaf2/data
"""
import logging
import httpx
from typing import Optional, Dict, List, Any

# Configure logging
logger = logging.getLogger(__name__)


class CMSProviderService:
    """Service for searching CMS Hospital Enrollments data."""
    
    # CMS API URL for Hospital Enrollments dataset
    API_URL = "https://data.cms.gov/data-api/v1/dataset/f6f6505c-e8b0-4d57-b258-e2b94133aaf2/data"
    
    # Request timeout (in seconds)
    TIMEOUT = 15
    
    # Maximum number of results to retrieve
    MAX_RESULTS = 10
    
    @classmethod
    async def search_hospital_address(
        cls,
        hospital_name: str,
        state: Optional[str] = None
    ) -> Optional[Dict[str, str]]:
        """
        Search for a hospital's address using the CMS Hospital Enrollments API.
        
        This method queries the CMS Hospital Enrollments dataset to find
        hospital information including address, city, state, and ZIP code.
        
        Args:
            hospital_name: Name of the hospital to search for
            state: Optional 2-character state code to narrow search
            
        Returns:
            Dictionary with keys: address, city, state, zip_code
            Returns None if no match is found or if an error occurs
            
        Example:
            >>> result = await CMSProviderService.search_hospital_address(
            ...     "Tyrone Hospital",
            ...     "PA"
            ... )
            >>> print(result)
            {
                'address': '187 Hospital Drive',
                'city': 'Tyrone',
                'state': 'PA',
                'zip_code': '16686'
            }
        """
        try:
            # Build search query parameters
            query_params = cls._build_query_params(hospital_name, state)
            
            logger.info(f"Searching CMS Hospital Enrollments API for: {hospital_name}")
            
            # Perform API request
            results = await cls._perform_search(query_params)
            
            if not results:
                logger.warning(f"No CMS results found for: {hospital_name}")
                return None
            
            # Parse the best matching result
            address_data = cls._parse_best_match(results, hospital_name, state)
            
            if address_data:
                logger.info(f"Successfully found CMS address for {hospital_name}: {address_data}")
                return address_data
            else:
                logger.warning(f"Could not parse address from CMS results for: {hospital_name}")
                return None
                
        except Exception as e:
            logger.error(f"Error searching CMS Hospital Enrollments API for '{hospital_name}': {str(e)}", exc_info=True)
            return None
    
    @classmethod
    def _build_query_params(
        cls,
        hospital_name: str,
        state: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Build query parameters for the CMS API request.
        
        The Hospital Enrollments API uses a different query format than the
        Provider of Services API. It uses GET parameters with filter syntax.
        
        Args:
            hospital_name: Name of the hospital
            state: Optional state code
            
        Returns:
            Dictionary of query parameters
        """
        # Clean the hospital name for search
        clean_name = hospital_name.strip()
        
        # Build query parameters using the data-api filter format
        params = {
            "filter[ORGANIZATION NAME][condition][path]": "ORGANIZATION NAME",
            "filter[ORGANIZATION NAME][condition][operator]": "CONTAINS",
            "filter[ORGANIZATION NAME][condition][value]": clean_name,
            "limit": cls.MAX_RESULTS,
            "offset": 0
        }
        
        # Add state filter if provided
        if state:
            params["filter[ENROLLMENT STATE][condition][path]"] = "ENROLLMENT STATE"
            params["filter[ENROLLMENT STATE][condition][operator]"] = "="
            params["filter[ENROLLMENT STATE][condition][value]"] = state.upper()
        
        return params
    
    @classmethod
    async def _perform_search(cls, query_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Perform the actual API request to CMS.
        
        Args:
            query_params: Query parameters dictionary
            
        Returns:
            List of hospital enrollment records
            
        Raises:
            Exception: If the API request fails
        """
        try:
            async with httpx.AsyncClient(timeout=cls.TIMEOUT) as client:
                response = await client.get(
                    cls.API_URL,
                    params=query_params
                )
                
                response.raise_for_status()
                results = response.json()
                
                # The data-api returns results directly as a list
                if isinstance(results, list):
                    logger.debug(f"Retrieved {len(results)} results from CMS API")
                    return results
                else:
                    logger.warning(f"Unexpected response format from CMS API")
                    return []
                
        except httpx.HTTPStatusError as e:
            logger.error(f"CMS API HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.TimeoutException:
            logger.error(f"CMS API request timed out after {cls.TIMEOUT} seconds")
            raise
        except Exception as e:
            logger.error(f"CMS API request failed: {str(e)}")
            raise
    
    @classmethod
    def _parse_best_match(
        cls,
        results: List[Dict[str, Any]],
        search_name: str,
        expected_state: Optional[str] = None
    ) -> Optional[Dict[str, str]]:
        """
        Parse the best matching result from CMS API results.
        
        This method scores results based on name similarity and state match,
        then extracts address information from the best match.
        
        Args:
            results: List of hospital enrollment records from CMS API
            search_name: Original search name for comparison
            expected_state: Optional expected state code
            
        Returns:
            Dictionary with address components or None
        """
        if not results:
            return None
        
        # Score and sort results
        scored_results = []
        search_name_lower = search_name.lower()
        
        for result in results:
            org_name = result.get("ORGANIZATION NAME", "").lower()
            state_code = result.get("ENROLLMENT STATE", "")
            
            # Calculate similarity score (simple substring matching)
            score = 0
            
            # Exact match gets highest score
            if org_name == search_name_lower:
                score = 100
            # Partial match
            elif search_name_lower in org_name or org_name in search_name_lower:
                score = 50
            # Word overlap
            else:
                search_words = set(search_name_lower.split())
                org_words = set(org_name.split())
                overlap = len(search_words & org_words)
                score = overlap * 10
            
            # Bonus for state match
            if expected_state and state_code.upper() == expected_state.upper():
                score += 25
            
            scored_results.append((score, result))
        
        # Sort by score (descending)
        scored_results.sort(key=lambda x: x[0], reverse=True)
        
        # Get the best match
        if scored_results and scored_results[0][0] > 0:
            best_match = scored_results[0][1]
            
            # Extract address information using the correct field names
            address_data = {
                'address': best_match.get("ADDRESS LINE 1"),
                'city': best_match.get("CITY"),
                'state': best_match.get("ENROLLMENT STATE"),
                'zip_code': best_match.get("ZIP CODE")
            }
            
            # Only return if we have at least city and state
            if address_data.get('city') and address_data.get('state'):
                return address_data
        
        return None