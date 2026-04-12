import re
from typing import List, Dict, Tuple, Any
from app.repositories.data_repository import DataRepository

class GeographyService:
    CATEGORY_ALIASES = {
        "provinces": ["province", "provinces", "administrative"],
        "crops": ["crop", "crops", "agriculture", "farming"],
        "livestock": ["livestock", "animals"],
        "fruits": ["fruit", "fruits"],
        "forests": ["forest", "forests", "vegetation"],
        "energy_resources": ["energy", "power", "electricity"],
        "minerals": ["mineral", "minerals", "mining"],
        "rivers": ["river", "rivers"],
        "barrages": ["barrage", "barrages"],
        "ports": ["port", "seaport", "harbor"],
        "dryports": ["dryport", "dry port"],
        "airports": ["airport", "airports"],
        "dams": ["dam", "dams"],
        "industries": ["industry", "industries", "industrial"],
        "pipelines": ["pipeline", "pipelines"],
        "population": ["population", "density"],
        "landforms": ["landform", "relief", "plains"],
        "rain_systems": ["rain", "monsoon", "climate"],
        "mountain_ranges": ["mountain", "range"],
        "deserts": ["desert"],
        "plateaus": ["plateau"],
        "mountain_passes": ["pass"],
        "glaciers": ["glacier"],
        "canals": ["canal"],
        "fish_farms": ["fish", "fishing"],
        "drought_areas": ["drought", "arid"],
        "industrial_zones": ["sez", "industrial zone"]
    }

    def __init__(self, data_repository: DataRepository):
        self.data_repository = data_repository
        self._compiled_regexes = {}
        self._build_regexes()
        
        self._exact_name_index = {}
        self._word_index = {}
        self._all_items = []
        self._build_indexes()

    def _build_regexes(self):
        for category, keywords in self.CATEGORY_ALIASES.items():
            pattern = "|".join([rf"\b{kw}(s|es)?\b" for kw in keywords])
            self._compiled_regexes[category] = re.compile(pattern, re.IGNORECASE)

    def _build_indexes(self):
        data = self.data_repository.get_geography_data()
        for category, items in data.items():
            if isinstance(items, dict):
                items = [i for sub in items.values() for i in sub]
            
            for item in items:
                name = item.get("name", "").lower()
                item_id = item.get("id", "").lower()
                item_type = item.get("type", "").lower()
                
                item_search_str = f"{name} {item_id} {item_type}"
                self._all_items.append((category, item, name, item_search_str))
                
                if name:
                    if name not in self._exact_name_index:
                        self._exact_name_index[name] = []
                    self._exact_name_index[name].append((category, item, item_search_str))

        # Re-build _word_index to store integer indexes pointing to _all_items for better memory
        self._word_index.clear()
        for idx, (category, item, name, item_search_str) in enumerate(self._all_items):
            for word in item_search_str.split():
                if word:
                    if word not in self._word_index:
                        self._word_index[word] = set()
                    self._word_index[word].add(idx)

    def detect_category(self, query: str) -> str:
        query_lower = query.lower()
        for category, regex in self._compiled_regexes.items():
            if regex.search(query_lower):
                return category
        return None

    def match_entities(self, query: str) -> List[Tuple[int, str, Any]]:
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        modifiers = ["sea", "dry", "international", "intl", "domestic", "sez", "epz", "industrial"]
        active_modifiers = [mod for mod in modifiers if mod in query_lower]
        
        scores = {}  # Map item index to highest score

        # 1. Exact Name Matches
        if query_lower in self._exact_name_index:
            for category, item, search_str in self._exact_name_index[query_lower]:
                # find idx wrapper
                for idx, (c, i, n, s) in enumerate(self._all_items):
                    if c == category and n == query_lower and s == search_str:
                        scores[idx] = max(scores.get(idx, 0), 100)

        # 2. Substring & Word Matches
        for idx, (category, item, name, search_str) in enumerate(self._all_items):
            if name and name in query_lower:
                scores[idx] = max(scores.get(idx, 0), 80)
                
            if idx not in scores:
                if any(word in search_str for word in query_words):
                    scores[idx] = max(scores.get(idx, 0), 50)

        # Apply modifiers
        results = []
        for idx, score in scores.items():
            category, item, name, search_str = self._all_items[idx]
            final_score = score
            if active_modifiers:
                if any(mod in search_str for mod in active_modifiers):
                    final_score += 50
                else:
                    final_score -= 100
            
            if final_score > 0:
                results.append((final_score, category, item))

        return sorted(results, key=lambda x: x[0], reverse=True)

    def convert_to_feature(self, category: str, item: Dict[str, Any]) -> List[Dict[str, Any]]:
        features = []

        if "path" in item:
            features.append({
                "type": "path",
                "label": item.get("name", ""),
                "data": item["path"],
                "color": item.get("color", "#3b82f6")
            })

        elif "locations" in item:
            for loc in item["locations"]:
                features.append({
                    "type": "point",
                    "label": loc.get("name", item.get("name", "")),
                    "data": [loc["coordinate"]],
                    "color": item.get("color", "#f43f5e"),
                    "facts": loc.get("description", item.get("facts")),
                    "icon": item.get("icon", "map-pin")
                })

        elif "coordinate" in item:
            features.append({
                "type": "point",
                "label": item.get("name", ""),
                "data": [item["coordinate"]],
                "color": item.get("color", "#f43f5e"),
                "facts": item.get("facts"),
                "icon": item.get("icon", "anchor" if "port" in category else "map-pin")
            })

        elif "regions" in item or "coordinates" in item:
            region_data = item.get("regions") or [{"name": item.get("name", ""), "coordinates": item["coordinates"], "description": item.get("facts")}]
            features.append({
                "type": "region",
                "label": item.get("name", ""),
                "data": region_data,
                "color": item.get("color", "#10b981" if "regions" in item else "#fbbf24")
            })

        return features
