import sys
import os

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from app.services.llm_service import LLMService, LLMProviderFactory
    from app.services.geography_service import GeographyService
    from app.services.geography_image_service import GeographyImageAnalysisService
    from app.repositories.data_repository import DataRepository

    print("Imports successful.")

    # Test LLMService
    llm = LLMService()
    print("LLMService initialized. Text providers:", len(llm.text_providers), "Vision providers:", len(llm.vision_providers))

    # Test GeographyService
    repo = DataRepository()
    # Mock data so we don't need real JSONs right now for index building
    repo._loaded = True 
    repo._geography_data = {
        "cities": [
            {"id": "c1", "name": "Karachi", "type": "megacity"},
            {"id": "c2", "name": "Lahore", "type": "megacity"}
        ]
    }
    
    geo = GeographyService(repo)
    print("GeographyService initialized and indexes built.")
    matches = geo.match_entities("Karachi")
    print("Geography matches for 'Karachi':", matches)

    # Test GeographyImageAnalysisService
    geo_image = GeographyImageAnalysisService(llm)
    print("GeographyImageAnalysisService initialized.")
    
    print("All tests passed.")
except Exception as e:
    import traceback
    traceback.print_exc()
    sys.exit(1)
