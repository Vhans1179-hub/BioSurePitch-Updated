"""
Sync PDFs to Gemini on Startup

This script syncs all local PDFs to Gemini File API when the backend starts.
It should be called during the application startup process.
"""
import asyncio
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.pdf_manager import get_pdf_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def sync_pdfs():
    """Sync all local PDFs to Gemini."""
    try:
        logger.info("Starting PDF sync to Gemini...")
        
        pdf_manager = get_pdf_manager()
        results = await pdf_manager.sync_pdfs_to_gemini(category=None, force=False)
        
        logger.info(
            f"PDF sync complete: {results['uploaded']} uploaded, "
            f"{results['skipped']} skipped, {results['failed']} failed"
        )
        
        if results['errors']:
            logger.warning(f"Errors during sync: {results['errors']}")
        
        return results
        
    except Exception as e:
        logger.error(f"Error syncing PDFs: {str(e)}", exc_info=True)
        return None


if __name__ == "__main__":
    asyncio.run(sync_pdfs())
