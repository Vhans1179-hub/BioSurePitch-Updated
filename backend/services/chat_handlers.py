"""
Query Handlers for Chat-Based Data Insights.

This module implements handlers for different types of data queries
that can be processed through the chat interface.
"""
import re
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase

from backend.services.hco_service import HCOService
from backend.services.contract_service import ContractService
from backend.services.patient_service import PatientService
from backend.services.web_search_service import WebSearchService
from backend.services.surgeon_paper_service import SurgeonPaperService

# Configure logging
logger = logging.getLogger(__name__)


def make_hco_clickable(hco_name: str) -> str:
    """
    Wrap an HCO name in a markdown link that triggers address lookup.
    
    Args:
        hco_name: The name of the HCO to make clickable
        
    Returns:
        Markdown-formatted link string
    """
    return f"[{hco_name}](#lookup-address:{hco_name})"


class QueryHandler(ABC):
    """Abstract base class for query handlers."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        """
        Initialize the query handler.
        
        Args:
            db: MongoDB database instance
        """
        self.db = db
    
    @abstractmethod
    async def handle(self, params: Dict[str, Any]) -> str:
        """
        Handle the query and return a formatted response.
        
        Args:
            params: Dictionary of extracted parameters from the query
            
        Returns:
            Formatted response string
        """
        raise NotImplementedError


class TopHCOsHandler(QueryHandler):
    """Handler for 'top N HCOs by ghost patients' queries."""
    
    # Regex pattern to match queries like:
    # - "top 5 HCOs with highest ghost patients"
    # - "show me top 10 hcos ghost patients"
    # - "top hcos by ghost patients"
    PATTERN = re.compile(
        r"top\s+(\d+)?\s*hcos?.*(?:ghost|patients?)",
        re.IGNORECASE
    )
    
    @classmethod
    def matches(cls, message: str) -> Optional[Dict[str, Any]]:
        """
        Check if the message matches this handler's pattern.
        
        Args:
            message: User message to check
            
        Returns:
            Dictionary of extracted parameters if match found, None otherwise
        """
        match = cls.PATTERN.search(message)
        if match:
            # Extract limit from regex group, default to 5
            limit_str = match.group(1)
            limit = int(limit_str) if limit_str else 5
            
            # Cap limit at reasonable maximum
            limit = min(limit, 20)
            
            return {"limit": limit}
        return None
    
    async def handle(self, params: Dict[str, Any]) -> str:
        """
        Handle the top HCOs query.
        
        Args:
            params: Dictionary containing 'limit' parameter
            
        Returns:
            Formatted markdown response with top HCOs
        """
        limit = params.get("limit", 5)
        
        # Fetch data using HCO service
        hcos = await HCOService.get_top_hcos_by_ghost_patients(
            self.db,
            limit=limit
        )
        
        # Format response
        return self._format_response(hcos)
    
    def _format_response(self, hcos: List[Dict[str, Any]]) -> str:
        """
        Format HCO data into a natural language response.
        
        Args:
            hcos: List of HCO documents
            
        Returns:
            Markdown-formatted response string
        """
        if not hcos:
            return "No HCO data found."
        
        lines = [f"Here are the top {len(hcos)} HCOs with the highest ghost patients:\n"]
        
        for i, hco in enumerate(hcos, 1):
            name = hco.get("name", "Unknown")
            state = hco.get("state", "??")
            ghost_patients = hco.get("ghost_patients", 0)
            leakage_rate = hco.get("leakage_rate", 0.0)
            
            lines.append(
                f"{i}. **{name}** ({state}) - {ghost_patients} ghost patients "
                f"({leakage_rate:.1f}% leakage rate)"
            )
        
        return "\n".join(lines)


class ContractTemplatesHandler(QueryHandler):
    """Handler for 'show contract templates' queries."""
    
    # Regex pattern to match queries like:
    # - "show contract templates"
    # - "list all contracts"
    # - "what contract templates are available"
    PATTERN = re.compile(
        r"(?:show|list|what|get).*(?:contract|template)s?",
        re.IGNORECASE
    )
    
    @classmethod
    def matches(cls, message: str) -> Optional[Dict[str, Any]]:
        """
        Check if the message matches this handler's pattern.
        
        Args:
            message: User message to check
            
        Returns:
            Empty dictionary if match found, None otherwise
        """
        match = cls.PATTERN.search(message)
        if match:
            return {}
        return None
    
    async def handle(self, params: Dict[str, Any]) -> str:
        """
        Handle the contract templates query.
        
        Args:
            params: Dictionary (empty for this handler)
            
        Returns:
            Formatted markdown response with contract templates
        """
        # Fetch data using Contract service
        templates = await ContractService.get_all_templates()
        
        # Format response
        return self._format_response(templates)
    
    def _format_response(self, templates: List[Dict[str, Any]]) -> str:
        """
        Format contract template data into a natural language response.
        
        Args:
            templates: List of contract template documents
            
        Returns:
            Markdown-formatted response string
        """
        if not templates:
            return "No contract templates found."
        
        lines = [f"Here are the available contract templates ({len(templates)} total):\n"]
        
        for i, template in enumerate(templates, 1):
            name = template.get("name", "Unknown")
            outcome_type = template.get("outcome_type", "unknown")
            default_rebate = template.get("default_rebate_percent", 0)
            time_window = template.get("default_time_window", 0)
            
            lines.append(
                f"{i}. **{name}**\n"
                f"   - Outcome: {outcome_type}\n"
                f"   - Default rebate: {default_rebate}%\n"
                f"   - Time window: {time_window} months"
            )
        
        return "\n".join(lines)


class ContractSimulationHandler(QueryHandler):
    """Handler for 'simulate contract' or 'expected rebate' queries."""
    
    # Regex pattern to match queries like:
    # - "what's the expected rebate for 12-month survival"
    # - "simulate 12-month-survival contract"
    # - "rebate for toxicity contract"
    PATTERN = re.compile(
        r"(?:simulate|rebate|expected|calculate).*(?:12-month|survival|toxicity|retreatment)",
        re.IGNORECASE
    )
    
    @classmethod
    def matches(cls, message: str) -> Optional[Dict[str, Any]]:
        """
        Check if the message matches this handler's pattern.
        
        Args:
            message: User message to check
            
        Returns:
            Dictionary with template_id if match found, None otherwise
        """
        match = cls.PATTERN.search(message)
        if match:
            # Try to identify which template based on keywords
            message_lower = message.lower()
            
            if "12-month" in message_lower or "survival" in message_lower:
                return {"template_id": "survival-12m"}
            elif "toxicity" in message_lower:
                return {"template_id": "toxicity-30d"}
            elif "retreatment" in message_lower:
                return {"template_id": "retreatment-18m"}
            
            # Default to survival-12m if unclear
            return {"template_id": "survival-12m"}
        return None
    
    async def handle(self, params: Dict[str, Any]) -> str:
        """
        Handle the contract simulation query.
        
        Args:
            params: Dictionary containing 'template_id' parameter
            
        Returns:
            Formatted markdown response with simulation results
        """
        template_id = params.get("template_id", "survival-12m")
        
        # Get template details first
        template = await ContractService.get_template_by_id(template_id)
        
        if not template:
            return f"Contract template '{template_id}' not found."
        
        # Run simulation with default parameters
        default_rebate = template.get("default_rebate_percent", 50)
        default_time_window = template.get("default_time_window", 12)
        default_therapy_price = 150000  # Default therapy price
        
        simulation = await ContractService.simulate_contract(
            template_id=template_id,
            rebate_percent=default_rebate,
            therapy_price=default_therapy_price,
            time_window=default_time_window
        )
        
        if not simulation:
            return "Unable to simulate contract. Please check if patient data is available."
        
        # Format response
        return self._format_response(simulation)
    
    def _format_response(self, simulation: Dict[str, Any]) -> str:
        """
        Format simulation data into a natural language response.
        
        Args:
            simulation: Simulation results dictionary
            
        Returns:
            Markdown-formatted response string
        """
        template_name = simulation.get("template_name", "Unknown")
        outcome_type = simulation.get("outcome_type", "unknown")
        total_patients = simulation.get("total_patients", 0)
        failure_count = simulation.get("failure_count", 0)
        failure_rate = simulation.get("failure_rate", 0.0)
        total_rebate = simulation.get("total_rebate", 0.0)
        low_rebate = simulation.get("low_rebate", 0.0)
        high_rebate = simulation.get("high_rebate", 0.0)
        avg_rebate = simulation.get("avg_rebate_per_treated", 0.0)
        
        lines = [
            f"**Contract Simulation: {template_name}**\n",
            f"**Outcome Type:** {outcome_type}",
            f"**Patient Cohort:** {total_patients:,} patients\n",
            f"**Outcome Results:**",
            f"- Failures: {failure_count:,} patients ({failure_rate:.1f}%)",
            f"- Successes: {total_patients - failure_count:,} patients ({100 - failure_rate:.1f}%)\n",
            f"**Financial Exposure:**",
            f"- Expected rebate: ${total_rebate:,.2f}",
            f"- Low estimate (-20%): ${low_rebate:,.2f}",
            f"- High estimate (+20%): ${high_rebate:,.2f}",
            f"- Average per patient: ${avg_rebate:,.2f}"
        ]
        
        return "\n".join(lines)


class PatientStatsHandler(QueryHandler):
    """Handler for patient statistics and demographics queries."""
    
    # Regex pattern to match queries like:
    # - "patient statistics"
    # - "show patient demographics"
    # - "what's the average patient age"
    # - "payer distribution"
    PATTERN = re.compile(
        r"(?:patient|cohort|demographic).*(?:stat|age|payer|distribution|info)|(?:average|avg).*(?:age|patient)|payer.*distribution",
        re.IGNORECASE
    )
    
    @classmethod
    def matches(cls, message: str) -> Optional[Dict[str, Any]]:
        """
        Check if the message matches this handler's pattern.
        
        Args:
            message: User message to check
            
        Returns:
            Empty dictionary if match found, None otherwise
        """
        match = cls.PATTERN.search(message)
        if match:
            return {}
        return None
    
    async def handle(self, params: Dict[str, Any]) -> str:
        """
        Handle the patient statistics query.
        
        Args:
            params: Dictionary (empty for this handler)
            
        Returns:
            Formatted markdown response with patient statistics
        """
        # Fetch data using Patient service
        stats = await PatientService.get_patient_stats()
        
        if not stats:
            return "No patient data available."
        
        # Format response
        return self._format_response(stats)
    
    def _format_response(self, stats: Dict[str, Any]) -> str:
        """
        Format patient statistics into a natural language response.
        
        Args:
            stats: Patient statistics dictionary
            
        Returns:
            Markdown-formatted response string
        """
        total = stats.get("total_patients", 0)
        avg_age = stats.get("avg_age", 0)
        male_pct = stats.get("male_percent", 0)
        female_pct = stats.get("female_percent", 0)
        avg_prior = stats.get("avg_prior_lines", 0)
        
        lines = [
            f"**Patient Cohort Statistics** ({total:,} total patients)\n",
            "**Demographics:**",
            f"- Average age: {avg_age} years",
            f"- Gender: {male_pct}% Male, {female_pct}% Female",
            f"- Average prior treatment lines: {avg_prior}\n",
        ]
        
        # Add payer distribution
        payer_dist = stats.get("payer_dist", {})
        if payer_dist:
            lines.append("**Payer Distribution:**")
            for payer, count in sorted(payer_dist.items(), key=lambda x: x[1], reverse=True):
                pct = round((count / total * 100), 1) if total > 0 else 0
                lines.append(f"- {payer}: {count:,} patients ({pct}%)")
            lines.append("")
        
        # Add region distribution
        region_dist = stats.get("region_dist", {})
        if region_dist:
            lines.append("**Regional Distribution:**")
            for region, count in sorted(region_dist.items(), key=lambda x: x[1], reverse=True):
                pct = round((count / total * 100), 1) if total > 0 else 0
                lines.append(f"- {region}: {count:,} patients ({pct}%)")
            lines.append("")
        
        # Add age buckets
        age_buckets = stats.get("age_buckets", {})
        if age_buckets:
            lines.append("**Age Distribution:**")
            for age_range in ["50-59", "60-69", "70-79", "80+"]:
                count = age_buckets.get(age_range, 0)
                pct = round((count / total * 100), 1) if total > 0 else 0
                lines.append(f"- {age_range}: {count:,} patients ({pct}%)")
        
        return "\n".join(lines)


class PatientOutcomesHandler(QueryHandler):
    """Handler for patient outcome queries (toxicity, events, retreatment)."""
    
    # Regex pattern to match queries like:
    # - "how many patients had toxicity"
    # - "toxicity events"
    # - "retreatment rate"
    # - "12-month events"
    PATTERN = re.compile(
        r"(?:toxicity|retreatment|event|outcome).*(?:patient|rate|count)|(?:how many|what percent).*(?:toxicity|retreatment|event)",
        re.IGNORECASE
    )
    
    @classmethod
    def matches(cls, message: str) -> Optional[Dict[str, Any]]:
        """
        Check if the message matches this handler's pattern.
        
        Args:
            message: User message to check
            
        Returns:
            Empty dictionary if match found, None otherwise
        """
        match = cls.PATTERN.search(message)
        if match:
            return {}
        return None
    
    async def handle(self, params: Dict[str, Any]) -> str:
        """
        Handle the patient outcomes query.
        
        Args:
            params: Dictionary (empty for this handler)
            
        Returns:
            Formatted markdown response with outcome statistics
        """
        # Fetch data using Patient service
        stats = await PatientService.get_patient_stats()
        
        if not stats:
            return "No patient data available."
        
        # Format response
        return self._format_response(stats)
    
    def _format_response(self, stats: Dict[str, Any]) -> str:
        """
        Format patient outcome statistics into a natural language response.
        
        Args:
            stats: Patient statistics dictionary
            
        Returns:
            Markdown-formatted response string
        """
        total = stats.get("total_patients", 0)
        
        toxicity_count = stats.get("toxicity_count", 0)
        toxicity_pct = stats.get("toxicity_percent", 0)
        
        event_12m_count = stats.get("event_12m_count", 0)
        event_12m_pct = stats.get("event_12m_percent", 0)
        
        retreatment_18m_count = stats.get("retreatment_18m_count", 0)
        retreatment_18m_pct = stats.get("retreatment_18m_percent", 0)
        
        lines = [
            f"**Patient Outcome Statistics** ({total:,} total patients)\n",
            "**Clinical Outcomes:**",
            f"- **30-Day Toxicity Events:** {toxicity_count:,} patients ({toxicity_pct}%)",
            f"  - ICU/inpatient readmission with CRS/ICANS within 30 days",
            f"- **12-Month Events:** {event_12m_count:,} patients ({event_12m_pct}%)",
            f"  - Death or escalation to new MM treatment within 12 months",
            f"- **18-Month Retreatment:** {retreatment_18m_count:,} patients ({retreatment_18m_pct}%)",
            f"  - Received new high-cost MM treatment within 18 months",
        ]
        
        return "\n".join(lines)


class HCOAddressHandler(QueryHandler):
    """Handler for HCO address lookup queries with database fallback to web search."""
    
    # Regex pattern to match queries like:
    # - "What is the address of [HCO Name]?"
    # - "Where is [HCO Name] located?"
    # - "Address of [HCO Name]"
    # - "Find address for [HCO Name]"
    PATTERN = re.compile(
        r"(?:what\s+is\s+the\s+)?(?:address|location)(?:\s+of|\s+for)?\s+(.+?)(?:\?|$)|"
        r"(?:where\s+is)\s+(.+?)\s+(?:located|address)(?:\?|$)|"
        r"(?:find|get|show)\s+(?:the\s+)?address\s+(?:of|for)\s+(.+?)(?:\?|$)",
        re.IGNORECASE
    )
    
    # Address cache validity period (90 days)
    ADDRESS_CACHE_DAYS = 90
    
    @classmethod
    def matches(cls, message: str) -> Optional[Dict[str, Any]]:
        """
        Check if the message matches this handler's pattern.
        
        Args:
            message: User message to check
            
        Returns:
            Dictionary with 'hco_name' if match found, None otherwise
        """
        match = cls.PATTERN.search(message)
        if match:
            # Extract HCO name from any of the capture groups
            hco_name = match.group(1) or match.group(2) or match.group(3)
            if hco_name:
                # Clean up the HCO name
                hco_name = hco_name.strip().rstrip('?.,!')
                return {"hco_name": hco_name}
        return None
    
    async def handle(self, params: Dict[str, Any]) -> str:
        """
        Handle the HCO address lookup query.
        
        This method:
        1. Searches for the HCO in the database
        2. Returns cached address if available and recent
        3. Falls back to web search if address not found or outdated
        4. Searches for the HCO's official website URL
        5. Updates database with found address
        
        Args:
            params: Dictionary containing 'hco_name' parameter
            
        Returns:
            Formatted markdown response with address information and website link
        """
        hco_name = params.get("hco_name", "").strip()
        
        if not hco_name:
            return "Please specify an HCO name to look up the address."
        
        logger.info(f"Looking up address for HCO: {hco_name}")
        
        # Step 1: Search for HCO in database
        hco = await HCOService.get_hco_by_name(self.db, hco_name)
        
        if not hco:
            return (
                f"I couldn't find an HCO named **{hco_name}** in our database. "
                "Please check the name and try again, or ask me to show you the top HCOs."
            )
        
        # Step 2: Check if address exists and is recent
        has_address = bool(hco.get("address") or hco.get("city"))
        address_last_updated = hco.get("address_last_updated")
        
        # Determine if we need to refresh the address
        needs_refresh = True
        if has_address and address_last_updated:
            # Check if address is within cache validity period
            cache_cutoff = datetime.utcnow() - timedelta(days=self.ADDRESS_CACHE_DAYS)
            if address_last_updated > cache_cutoff:
                needs_refresh = False
                logger.info(f"Using cached address for {hco_name}")
        
        # Step 3: If address missing or outdated, search the web
        if not has_address or needs_refresh:
            logger.info(f"Searching web for address of {hco_name}")
            
            try:
                # Perform web search for address
                address_data = await WebSearchService.search_hco_address(
                    hco_name=hco.get("name", hco_name),
                    state=hco.get("state")
                )
                
                if address_data:
                    # Update database with found address
                    hco_id = hco.get("_id")
                    update_success = await HCOService.update_hco_address(
                        self.db,
                        hco_id,
                        address_data
                    )
                    
                    if update_success:
                        logger.info(f"Successfully updated address for {hco_name}")
                        # Update local hco dict with new data
                        hco.update(address_data)
                        has_address = True
                    else:
                        logger.warning(f"Failed to update address in database for {hco_name}")
                else:
                    logger.warning(f"Web search returned no results for {hco_name}")
                    
            except Exception as e:
                logger.error(f"Error during web search for {hco_name}: {str(e)}", exc_info=True)
                # Continue with cached data if available
        
        # Step 4: Search for website URL
        website_url = None
        try:
            logger.info(f"Searching for website of {hco_name}")
            website_url = await WebSearchService.search_hco_website(
                hco_name=hco.get("name", hco_name),
                state=hco.get("state")
            )
            if website_url:
                logger.info(f"Found website for {hco_name}: {website_url}")
        except Exception as e:
            logger.error(f"Error searching for website of {hco_name}: {str(e)}", exc_info=True)
            # Continue without website URL
        
        # Step 5: Format and return response
        return self._format_response(hco, has_address, needs_refresh and has_address, website_url)
    
    def _format_response(
        self,
        hco: Dict[str, Any],
        has_address: bool,
        from_web_search: bool,
        website_url: Optional[str] = None
    ) -> str:
        """
        Format HCO address information into a natural language response.
        
        Args:
            hco: HCO document with address information
            has_address: Whether address information is available
            from_web_search: Whether address was found via web search
            website_url: Optional website URL for the HCO
            
        Returns:
            Markdown-formatted response string
        """
        hco_name = hco.get("name", "Unknown")
        
        if not has_address:
            response = (
                f"I couldn't find address information for **{hco_name}**. "
                "The address may not be publicly available or the HCO name might need verification."
            )
            
            # Add website link if available
            if website_url:
                response += f"\n\n🌐 **Website:** {website_url}"
            
            return response
        
        # Build address components
        lines = [f"**Address for {hco_name}:**\n"]
        
        # Street address
        if hco.get("address"):
            lines.append(f"📍 {hco['address']}")
        
        # City, State, ZIP
        location_parts = []
        if hco.get("city"):
            location_parts.append(hco["city"])
        if hco.get("state"):
            location_parts.append(hco["state"])
        if hco.get("zip_code"):
            location_parts.append(hco["zip_code"])
        
        if location_parts:
            lines.append(f"   {', '.join(location_parts)}")
        
        # Add website link if available
        if website_url:
            lines.append(f"\n🌐 **Website:** {website_url}")
        
        # Add source indicator
        if from_web_search:
            lines.append("\n*Address found via CMS/web search and cached for future queries.*")
        else:
            lines.append("\n*Address retrieved from database.*")
        
        return "\n".join(lines)

class SurgeonPaperSearchHandler(QueryHandler):
    """Handler for surgeon paper search queries by author name."""
    
    # Regex pattern to match queries like:
    # - "Find papers by Kahraman E"
    # - "What papers did Sharma R publish?"
    # - "Show me publications by Nakamura H"
    # - "Search surgeon papers for author Smith"
    # - "Papers by Dr. Johnson"
    PATTERN = re.compile(
        r"(?:find|search|show|get|list|what).*(?:papers?|publications?).*(?:by|for|from|author)\s+(.+?)(?:\?|$)|"
        r"(?:papers?|publications?).*(?:by|from)\s+(.+?)(?:\?|$)|"
        r"(?:author|surgeon)\s+(.+?).*(?:papers?|publications?)",
        re.IGNORECASE
    )
    
    @classmethod
    def matches(cls, message: str) -> Optional[Dict[str, Any]]:
        """
        Check if the message matches this handler's pattern.
        
        Args:
            message: User message to check
            
        Returns:
            Dictionary with 'author_name' if match found, None otherwise
        """
        match = cls.PATTERN.search(message)
        if match:
            # Extract author name from any of the capture groups
            author_name = match.group(1) or match.group(2) or match.group(3)
            if author_name:
                # Clean up the author name
                author_name = author_name.strip().rstrip('?.,!')
                # Remove common words that might be captured
                author_name = re.sub(r'\b(publish|published|write|wrote|author)\b', '', author_name, flags=re.IGNORECASE).strip()
                return {"author_name": author_name}
        return None
    
    async def handle(self, params: Dict[str, Any]) -> str:
        """
        Handle the surgeon paper search query.
        
        This method:
        1. Extracts the author name from parameters
        2. Searches the surgeon_papers collection
        3. Returns formatted results with Title, Journal, and Affiliation
        4. Handles cases where no results are found
        
        Args:
            params: Dictionary containing 'author_name' parameter
            
        Returns:
            Formatted markdown response with search results
        """
        author_name = params.get("author_name", "").strip()
        
        if not author_name:
            return "Please specify an author name to search for surgeon papers."
        
        logger.info(f"Searching surgeon papers for author: {author_name}")
        
        # Search for papers by author name
        papers = await SurgeonPaperService.search_by_author(
            self.db,
            author_name,
            limit=20
        )
        
        # Format and return response
        return self._format_response(author_name, papers)
    
    def _format_response(self, author_name: str, papers: List[Dict[str, Any]]) -> str:
        """
        Format surgeon paper search results into a natural language response.
        
        Args:
            author_name: The author name that was searched
            papers: List of surgeon paper documents
            
        Returns:
            Markdown-formatted response string
        """
        if not papers:
            return (
                f"I couldn't find any surgeon papers for author **{author_name}** in our database. "
                "Please check the spelling or try a different author name."
            )
        
        # Build response
        lines = [f"**Surgeon Papers by {author_name}** ({len(papers)} found):\n"]
        
        for i, paper in enumerate(papers, 1):
            title = paper.get("title", "Unknown Title")
            journal = paper.get("journal", "Unknown Journal")
            affiliation = paper.get("affiliation", "Unknown Affiliation")
            author = paper.get("author_name", author_name)
            
            lines.append(f"{i}. **{title}**")
            lines.append(f"   - **Author:** {author}")
            lines.append(f"   - **Journal:** {journal}")
            lines.append(f"   - **Affiliation:** {affiliation}")
            
            # Add website link if available
            if paper.get("website"):
                website = paper['website']
                lines.append(f"   - **Link:** [Affiliation Website]({website})")
            
            lines.append("")  # Empty line between papers
        
        return "\n".join(lines)




class GeneralChatHandler(QueryHandler):
    """Handler for general chat queries (non-data queries)."""
    
    async def handle(self, params: Dict[str, Any]) -> str:
        """
        Handle general chat queries using keyword matching.
        
        Args:
            params: Dictionary containing 'message' parameter
            
        Returns:
            Contextual response string
        """
        message = params.get("message", "").lower()
        
        # Check for keywords and return appropriate responses
        if "help" in message:
            return (
                "I'm here to help! You can ask me about:\n\n"
                "**Data Insights:**\n"
                "- 'Show me top 5 HCOs with highest ghost patients'\n"
                "- 'Show contract templates'\n"
                "- 'What's the expected rebate for 12-month survival?'\n"
                "- 'Patient statistics' or 'Show patient demographics'\n"
                "- 'How many patients had toxicity events?'\n\n"
                "**Dashboard Features:**\n"
                "- Cohort analysis and metrics\n"
                "- Contract simulation\n"
                "- Ghost radar features"
            )
        
        if "dashboard" in message:
            return (
                "The dashboard provides comprehensive analytics including cohort analysis, "
                "contract simulation, and ghost radar features. You can navigate between "
                "different sections using the sidebar."
            )
        
        if "cohort" in message:
            return (
                "The Cohort Overview shows key metrics like retention rates, engagement scores, "
                "and user growth. You can filter by different time periods to analyze trends."
            )
        
        if "contract" in message and "simulate" not in message:
            return (
                "The Contract Simulator allows you to model different contract scenarios and "
                "see projected outcomes. You can ask me 'show contract templates' or "
                "'what's the expected rebate for 12-month survival?'"
            )
        
        if "ghost" in message or "radar" in message:
            return (
                "Ghost Radar helps identify inactive or at-risk users. It uses advanced analytics "
                "to detect patterns that might indicate user churn."
            )
        
        if "hello" in message or "hi" in message:
            return "Hello! How can I assist you today?"
        
        if "thank" in message:
            return "You're welcome! Feel free to ask if you need anything else."
        
        # Default response
        return (
            "I understand. Is there anything specific you'd like to know? You can ask me:\n"
            "- 'Show me top 5 HCOs with highest ghost patients'\n"
            "- 'Show contract templates'\n"
            "- 'What's the expected rebate for 12-month survival?'\n"
            "- 'Patient statistics' or 'How many patients had toxicity?'\n"
            "- Or ask about dashboard features"
        )