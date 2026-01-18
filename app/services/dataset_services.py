"""
app/services/dataset_services.py

Facade for ScraperService to match requested API:
services.dataset_services.expand_dataset
"""

from app.services.scraper import ScraperService

_scraper = ScraperService()

def expand_dataset(domain: str, label: str):
    """
    Expands the dataset for a given label in a domain.
    Facades ScraperService.scrape_brand.
    """
    return _scraper.scrape_brand(brand_name=label, domain=domain)
