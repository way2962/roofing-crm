import os


def company(request):
    """Inject company name into all templates."""
    return {
        'company_name': os.getenv('COMPANY_NAME', 'RoofPro CRM'),
        'company_slug': os.getenv('COMPANY_SLUG', 'roofpro'),
    }
