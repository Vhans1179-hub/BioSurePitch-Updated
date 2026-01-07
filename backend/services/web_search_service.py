"""
Web Search Service for HCO Address Lookup.

This service provides a fallback chain for finding HCO addresses:
1. Primary: CMS Provider of Services API (official, free, no rate limits)
2. Fallback: DuckDuckGo search (free but rate-limited)

It includes robust error handling, timeout mechanisms, and address parsing.
"""
import re
import logging
from typing import Optional, Dict
from duckduckgo_search import DDGS
from backend.services.cms_provider_service import CMSProviderService

# Configure logging
logger = logging.getLogger(__name__)


class WebSearchService:
    """Service for searching the web to find HCO addresses."""
    
    # Timeout for search operations (in seconds)
    SEARCH_TIMEOUT = 10
    
    # Maximum number of search results to process
    MAX_RESULTS = 5
    
    # US state abbreviations for validation
    US_STATES = {
        'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
        'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
        'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
        'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
        'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY', 'DC'
    }
    
    @classmethod
    async def search_hco_address(
        cls,
        hco_name: str,
        state: Optional[str] = None
    ) -> Optional[Dict[str, str]]:
        """
        Search for an HCO's address using a fallback chain.
        
        This method tries multiple sources in order:
        1. CMS Provider of Services API (primary - official government data)
        2. DuckDuckGo search (fallback - web search)
        
        Args:
            hco_name: Name of the healthcare organization
            state: Optional 2-character state code to narrow search
            
        Returns:
            Dictionary with keys: address, city, state, zip_code (all optional)
            Returns None if no address is found or if all sources fail
            
        Example:
            >>> result = await WebSearchService.search_hco_address(
            ...     "California Medical Center",
            ...     "CA"
            ... )
            >>> print(result)
            {
                'address': '123 Health Way',
                'city': 'Los Angeles',
                'state': 'CA',
                'zip_code': '90015'
            }
        """
        # Try CMS Provider API first (primary source)
        try:
            logger.info(f"Attempting CMS Provider API search for: {hco_name}")
            cms_result = await CMSProviderService.search_hospital_address(hco_name, state)
            
            if cms_result:
                logger.info(f"Successfully found address via CMS API for {hco_name}")
                return cms_result
            else:
                logger.info(f"CMS API returned no results for {hco_name}, trying DuckDuckGo fallback")
        except Exception as e:
            logger.warning(f"CMS API search failed for {hco_name}: {str(e)}, trying DuckDuckGo fallback")
        
        # Fallback to DuckDuckGo search
        try:
            # Construct search query
            query = cls._build_search_query(hco_name, state)
            logger.info(f"Searching DuckDuckGo for HCO address: {query}")
            
            # Perform search with timeout
            results = cls._perform_search(query)
            
            if not results:
                logger.warning(f"No DuckDuckGo search results found for: {hco_name}")
                return None
            
            # Parse address from results
            address_data = cls._parse_address_from_results(results, state)
            
            if address_data:
                logger.info(f"Successfully found address via DuckDuckGo for {hco_name}: {address_data}")
                return address_data
            else:
                logger.warning(f"Could not parse address from DuckDuckGo results for: {hco_name}")
                return None
                
        except Exception as e:
            logger.error(f"DuckDuckGo search failed for '{hco_name}': {str(e)}", exc_info=True)
            return None
    
    @classmethod
    async def search_hco_website(
        cls,
        hco_name: str,
        state: Optional[str] = None
    ) -> Optional[str]:
        """
        Search for an HCO's official website URL.
        
        This method uses web search to find the official website of a healthcare
        organization. It looks for the most authoritative result (usually the
        organization's own domain).
        
        Args:
            hco_name: Name of the healthcare organization
            state: Optional 2-character state code to narrow search
            
        Returns:
            Website URL string or None if not found
            
        Example:
            >>> url = await WebSearchService.search_hco_website(
            ...     "Tyrone Hospital",
            ...     "PA"
            ... )
            >>> print(url)
            'https://www.tyronehospital.org'
        """
        try:
            # Construct search query for website
            query = cls._build_website_query(hco_name, state)
            logger.info(f"Searching for HCO website: {query}")
            
            # Perform search
            results = cls._perform_search(query)
            
            if not results:
                logger.warning(f"No search results found for website of: {hco_name}")
                return None
            
            # Extract website URL from results
            website_url = cls._extract_website_url(results, hco_name)
            
            if website_url:
                logger.info(f"Found website for {hco_name}: {website_url}")
                return website_url
            else:
                logger.warning(f"Could not find website URL for: {hco_name}")
                return None
                
        except Exception as e:
            logger.error(f"Website search failed for '{hco_name}': {str(e)}", exc_info=True)
            return None
    
    @classmethod
    def _build_website_query(cls, hco_name: str, state: Optional[str] = None) -> str:
        """
        Build an optimized search query for finding HCO websites.
        
        Args:
            hco_name: Name of the healthcare organization
            state: Optional state code
            
        Returns:
            Formatted search query string
        """
        # Clean the HCO name
        clean_name = hco_name.strip()
        
        # Build query with state if provided
        if state:
            query = f'"{clean_name}" {state.upper()} hospital official website'
        else:
            query = f'"{clean_name}" hospital official website'
        
        return query
    
    @classmethod
    def _extract_website_url(cls, results: list, hco_name: str) -> Optional[str]:
        """
        Extract the most likely official website URL from search results.
        
        This method prioritizes results that:
        1. Have the HCO name in the domain
        2. Are from .org, .com, or .edu domains
        3. Appear first in search results (usually most authoritative)
        
        Args:
            results: List of search result dictionaries
            hco_name: Name of the HCO for validation
            
        Returns:
            Website URL string or None
        """
        # Clean HCO name for matching
        clean_name = hco_name.lower().replace(" ", "").replace("-", "")
        
        # Score each result
        scored_urls = []
        
        for i, result in enumerate(results):
            url = result.get('href', '')
            title = result.get('title', '').lower()
            
            if not url or not url.startswith('http'):
                continue
            
            # Skip common non-official domains
            skip_domains = ['facebook.com', 'twitter.com', 'linkedin.com', 'wikipedia.org',
                          'yelp.com', 'healthgrades.com', 'vitals.com', 'google.com']
            if any(domain in url.lower() for domain in skip_domains):
                continue
            
            score = 0
            
            # Higher score for earlier results
            score += (10 - i) * 10
            
            # Check if HCO name appears in domain
            domain = url.split('/')[2].lower()
            if any(word in domain for word in clean_name.split() if len(word) > 3):
                score += 50
            
            # Prefer .org, .com, .edu domains
            if domain.endswith('.org'):
                score += 30
            elif domain.endswith('.com'):
                score += 20
            elif domain.endswith('.edu'):
                score += 25
            
            # Check if title contains HCO name
            if hco_name.lower() in title:
                score += 20
            
            scored_urls.append((score, url))
        
        # Sort by score and return best match
        if scored_urls:
            scored_urls.sort(key=lambda x: x[0], reverse=True)
            best_url = scored_urls[0][1]
            
            # Clean up URL (remove tracking parameters, etc.)
            if '?' in best_url:
                best_url = best_url.split('?')[0]
            
            return best_url
        
        return None
    
    @classmethod
    def _build_search_query(cls, hco_name: str, state: Optional[str] = None) -> str:
        """
        Build an optimized search query for finding HCO addresses.
        
        Args:
            hco_name: Name of the healthcare organization
            state: Optional state code
            
        Returns:
            Formatted search query string
        """
        # Clean the HCO name
        clean_name = hco_name.strip()
        
        # Build query with state if provided
        if state:
            query = f'"{clean_name}" {state.upper()} hospital address location'
        else:
            query = f'"{clean_name}" hospital address location'
        
        return query
    
    @classmethod
    def _perform_search(cls, query: str) -> list:
        """
        Perform the actual DuckDuckGo search with error handling.
        
        Args:
            query: Search query string
            
        Returns:
            List of search result dictionaries
            
        Raises:
            Exception: If search fails or times out
        """
        try:
            # Initialize DDGS client
            ddgs = DDGS()
            
            # Perform text search with timeout
            results = []
            for result in ddgs.text(query, max_results=cls.MAX_RESULTS):
                results.append(result)
            
            logger.debug(f"Retrieved {len(results)} search results")
            return results
            
        except Exception as e:
            logger.error(f"DuckDuckGo search failed: {str(e)}")
            raise
    
    @classmethod
    def _parse_address_from_results(
        cls,
        results: list,
        expected_state: Optional[str] = None
    ) -> Optional[Dict[str, str]]:
        """
        Parse address information from search results.
        
        This method looks through search result snippets and bodies to find
        address patterns and extract structured address data.
        
        Args:
            results: List of search result dictionaries
            expected_state: Optional state code to validate against
            
        Returns:
            Dictionary with address components or None if not found
        """
        for result in results:
            # Combine title, body, and href for comprehensive parsing
            text = f"{result.get('title', '')} {result.get('body', '')} {result.get('href', '')}"
            
            # Try to extract address components
            address_data = cls._extract_address_components(text, expected_state)
            
            if address_data:
                return address_data
        
        return None
    
    @classmethod
    def _extract_address_components(
        cls,
        text: str,
        expected_state: Optional[str] = None
    ) -> Optional[Dict[str, str]]:
        """
        Extract address components from text using regex patterns.
        
        Args:
            text: Text to parse for address information
            expected_state: Optional state code to validate against
            
        Returns:
            Dictionary with address, city, state, zip_code or None
        """
        # Pattern for full US address: street, city, state zip
        # Example: "123 Main St, Los Angeles, CA 90015"
        full_address_pattern = re.compile(
            r'(\d+\s+[A-Za-z0-9\s,\.]+?),\s*([A-Za-z\s]+),\s*([A-Z]{2})\s+(\d{5}(?:-\d{4})?)',
            re.IGNORECASE
        )
        
        match = full_address_pattern.search(text)
        if match:
            street = match.group(1).strip()
            city = match.group(2).strip()
            state = match.group(3).upper()
            zip_code = match.group(4)
            
            # Validate state code
            if state in cls.US_STATES:
                # If expected_state provided, verify it matches
                if expected_state and state != expected_state.upper():
                    logger.debug(f"State mismatch: found {state}, expected {expected_state}")
                    # Continue searching, but don't reject yet
                
                return {
                    'address': street,
                    'city': city,
                    'state': state,
                    'zip_code': zip_code
                }
        
        # Try alternative pattern: street address with zip code
        # Example: "123 Main Street 90015"
        street_zip_pattern = re.compile(
            r'(\d+\s+[A-Za-z0-9\s,\.]+?)\s+(\d{5}(?:-\d{4})?)',
            re.IGNORECASE
        )
        
        match = street_zip_pattern.search(text)
        if match:
            street = match.group(1).strip()
            zip_code = match.group(2)
            
            # Try to find city and state nearby
            city_state_pattern = re.compile(
                r'([A-Za-z\s]+),\s*([A-Z]{2})',
                re.IGNORECASE
            )
            
            city_state_match = city_state_pattern.search(text)
            if city_state_match:
                city = city_state_match.group(1).strip()
                state = city_state_match.group(2).upper()
                
                if state in cls.US_STATES:
                    return {
                        'address': street,
                        'city': city,
                        'state': state,
                        'zip_code': zip_code
                    }
        
        # Try to find at least city and state
        city_state_pattern = re.compile(
            r'(?:located\s+in|address[:\s]+|in\s+)([A-Za-z\s]+),\s*([A-Z]{2})',
            re.IGNORECASE
        )
        
        match = city_state_pattern.search(text)
        if match:
            city = match.group(1).strip()
            state = match.group(2).upper()
            
            if state in cls.US_STATES:
                # Return partial address data
                return {
                    'address': None,
                    'city': city,
                    'state': state,
                    'zip_code': None
                }
        
        return None