from __future__ import annotations

import asyncio
import os
from urllib.parse import urlparse

from fastapi import APIRouter

router = APIRouter(
    prefix="/api/guidance",
    tags=["Treatment & IPM Guidance"],
)

# These are explanatory disease-management notes, not a substitute for a diagnosis
# confirmed by an agricultural specialist or an approved product label.
GUIDANCE = {
    "Apple___Apple_scab": {
        "disease_type": "Fungal disease",
        "summary": "Apple scab is a fungal disease that mainly affects leaves and fruit.",
        "management": [
            "Remove and destroy fallen infected leaves and fruit.",
            "Prune dense branches to improve air circulation.",
            "Avoid prolonged leaf wetness and unnecessary overhead irrigation.",
            "Monitor new leaves and fruit regularly during disease-favorable weather.",
        ],
        "treatment": [
            "Use sanitation and canopy management first.",
            "Where fungicide treatment is required, confirm a product registered and labelled for apple scab in your location.",
            "Follow the product label for dose, timing, protective equipment and pre-harvest interval.",
        ],
    },
    "Apple___Black_rot": {
        "disease_type": "Fungal disease",
        "summary": "Black rot is a fungal disease that can affect apple leaves, branches and fruit.",
        "management": [
            "Remove infected fruit, dead wood and visible cankers.",
            "Prune affected branches and remove plant debris from the orchard.",
            "Improve canopy ventilation by avoiding excessive crowding.",
            "Monitor fruit and branches regularly for new symptoms.",
        ],
        "treatment": [
            "Use sanitation and pruning as the first management steps.",
            "Where chemical control is necessary, confirm a locally registered product labelled for apple black rot.",
            "Follow the product label strictly and observe the specified pre-harvest interval.",
        ],
    },
    "Apple___Cedar_apple_rust": {
        "disease_type": "Fungal disease",
        "summary": "Cedar apple rust is a fungal disease that produces characteristic spots on apple leaves and fruit.",
        "management": [
            "Monitor leaves and fruit regularly.",
            "Improve air circulation in the canopy.",
            "Remove heavily affected plant material where practical.",
            "Where possible, manage nearby alternate hosts according to local agricultural guidance.",
        ],
        "treatment": [
            "Use preventive disease-management practices.",
            "Where fungicide use is required, confirm a locally registered product labelled for cedar apple rust.",
            "Follow label instructions for application timing and safety.",
        ],
    },
    "Apple___healthy": {
        "disease_type": "Healthy",
        "summary": "No disease symptom was identified by the model.",
        "management": [
            "Continue regular field monitoring.",
            "Maintain balanced irrigation and nutrition.",
            "Remove damaged or diseased plant material promptly.",
            "Keep the growing area clean and well ventilated.",
        ],
        "treatment": [
            "No disease treatment is indicated from this prediction.",
            "Do not apply pesticides unnecessarily.",
        ],
    },
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": {
        "disease_type": "Fungal disease",
        "summary": "Gray leaf spot is a fungal leaf disease of maize.",
        "management": [
            "Use resistant or tolerant hybrids where available.",
            "Maintain good field sanitation and residue management.",
            "Use crop rotation where appropriate.",
            "Monitor lower leaves first because symptoms can develop there.",
        ],
        "treatment": [
            "Use cultural management as the foundation.",
            "Where fungicide treatment is justified, confirm a product registered and labelled for maize gray leaf spot in your location.",
            "Follow label directions and safety requirements.",
        ],
    },
    "Corn_(maize)___Common_rust_": {
        "disease_type": "Fungal disease",
        "summary": "Common rust is a fungal disease that produces rust-colored pustules on maize leaves.",
        "management": [
            "Use resistant hybrids where available.",
            "Monitor the crop frequently during favorable weather.",
            "Maintain good crop nutrition and overall plant health.",
            "Manage heavily affected plant residue according to local recommendations.",
        ],
        "treatment": [
            "Assess disease severity before chemical treatment.",
            "If fungicide use is needed, confirm a locally registered product labelled for maize common rust.",
            "Follow the product label carefully.",
        ],
    },
    "Corn_(maize)___Northern_Leaf_Blight": {
        "disease_type": "Fungal disease",
        "summary": "Northern leaf blight is a fungal disease that causes elongated lesions on maize leaves.",
        "management": [
            "Use resistant hybrids where available.",
            "Practice crop rotation where suitable.",
            "Manage crop residue appropriately.",
            "Monitor the crop early so disease spread can be identified quickly.",
        ],
        "treatment": [
            "Use resistant varieties and cultural management first.",
            "Where fungicide treatment is justified, confirm a registered product labelled for northern leaf blight of maize.",
            "Follow label instructions, protective equipment requirements and harvest restrictions.",
        ],
    },
    "Corn_(maize)___healthy": {
        "disease_type": "Healthy",
        "summary": "No disease symptom was identified by the model.",
        "management": [
            "Continue regular crop monitoring.",
            "Maintain proper irrigation and balanced nutrition.",
            "Keep the field clean and manage crop residue appropriately.",
        ],
        "treatment": [
            "No disease treatment is indicated from this prediction.",
            "Avoid unnecessary pesticide applications.",
        ],
    },
    "Grape___Black_rot": {
        "disease_type": "Fungal disease",
        "summary": "Grape black rot is a fungal disease that can affect leaves and fruit.",
        "management": [
            "Remove infected berries and plant debris.",
            "Improve canopy airflow and sunlight penetration.",
            "Remove diseased plant material during pruning.",
            "Monitor developing fruit closely during favorable weather.",
        ],
        "treatment": [
            "Begin with sanitation and canopy management.",
            "Where fungicide treatment is required, confirm a product registered and labelled for grape black rot in your area.",
            "Follow label directions and observe the required pre-harvest interval.",
        ],
    },
    "Grape___Esca_(Black_Measles)": {
        "disease_type": "Fungal disease complex",
        "summary": "Esca is associated with fungal infections and can cause leaf and fruit symptoms in grapevines.",
        "management": [
            "Remove and destroy severely affected plant material where practical.",
            "Use careful pruning practices to reduce infection opportunities.",
            "Disinfect pruning tools between affected plants where appropriate.",
            "Monitor vines for recurring symptoms.",
        ],
        "treatment": [
            "Management focuses heavily on sanitation and vine health.",
            "There is no single universal pesticide treatment that guarantees control.",
            "Consult local agricultural experts before applying any chemical treatment.",
        ],
    },
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": {
        "disease_type": "Fungal disease",
        "summary": "Leaf blight can cause leaf spotting and reduce healthy leaf area.",
        "management": [
            "Remove severely affected leaves where practical.",
            "Improve canopy ventilation.",
            "Avoid creating prolonged periods of leaf wetness.",
            "Maintain good sanitation around vines.",
        ],
        "treatment": [
            "Use sanitation and canopy management first.",
            "For chemical control, confirm products are registered and labelled for the diagnosed disease on grapes.",
            "Follow label instructions exactly.",
        ],
    },
    "Grape___healthy": {
        "disease_type": "Healthy",
        "summary": "No disease symptom was identified by the model.",
        "management": [
            "Continue regular vineyard monitoring.",
            "Maintain balanced nutrition and irrigation.",
            "Keep the canopy properly managed and ventilated.",
        ],
        "treatment": [
            "No disease treatment is indicated from this prediction.",
            "Avoid unnecessary pesticide applications.",
        ],
    },
    "Orange___Haunglongbing_(Citrus_greening)": {
        "disease_type": "Bacterial-associated citrus disease",
        "summary": "Citrus greening is a serious citrus disease associated with Candidatus Liberibacter bacteria and insect-vector transmission.",
        "management": [
            "Confirm suspected cases using appropriate plant-health diagnostic support where possible.",
            "Monitor trees regularly for characteristic symptoms.",
            "Remove and manage infected trees according to local citrus disease-control recommendations.",
            "Manage the insect vector using an integrated pest-management approach.",
        ],
        "treatment": [
            "There is no simple curative pesticide treatment for an infected tree.",
            "Management focuses on early detection, infected-tree management and vector management.",
            "Follow local plant-protection authority guidance.",
        ],
    },
}

# Previously added local candidate options. These are NOT verified against current
# Telangana registration or an individual product label; web sources are shown separately.
PESTICIDE_RECOMMENDATIONS = {
    "Apple___Apple_scab": [
        "Captan 50% WP",
        "Captan 75% WP",
        "Difenoconazole 25% EC",
        "Dodine 65% WP",
        "Mancozeb 75% WG",
    ],
    "Corn_(maize)___Common_rust_": [
        "Kresoxim-methyl 44.3% SC",
        "Tebuconazole",
        "Chlorothalonil",
        "Mancozeb",
    ],
    "Corn_(maize)___Northern_Leaf_Blight": [
        "Mancozeb",
        "Zineb",
        "Propiconazole 25% EC",
    ],
}

OFFICIAL_DOMAINS = [
    "agritech.tnau.ac.in",
    "tnau.ac.in",
    "icar.gov.in",
    "ncipm.org.in",
    "ppqs.gov.in",
    "agriwelfare.gov.in",
]


def _display_name(value: str) -> str:
    return value.replace("_", " ").replace("___", " / ").replace("%", "%").strip()


def _is_official_domain(url: str) -> bool:
    host = (urlparse(url).hostname or "").lower()
    return any(host == domain or host.endswith("." + domain) for domain in OFFICIAL_DOMAINS)


def _search_official_sources(crop: str, diagnosis: str) -> dict:
    """Search public agricultural sources; keyless mode is rate-limited."""
    try:
        from tavily import TavilyClient
    except ImportError:
        return {
            "sources": [],
            "status": "not_installed",
            "message": "Install tavily-python to enable web search.",
        }

    api_key = os.getenv("TAVILY_API_KEY")
    try:
        client = TavilyClient(api_key=api_key) if api_key else TavilyClient()
        crop_text = _display_name(crop)
        disease_text = _display_name(diagnosis)
        query = (
            f"India {crop_text} {disease_text} crop disease management treatment "
            "fungicide pesticide official agricultural university ICAR label recommendation"
        )

        try:
            response = client.search(
                query=query,
                search_depth="advanced",
                max_results=8,
                include_domains=OFFICIAL_DOMAINS,
            )
        except TypeError:
            # Compatibility with SDK releases that expose fewer search parameters.
            response = client.search(query)

        results = response.get("results", []) if isinstance(response, dict) else []
        sources = []
        seen_urls = set()
        for item in results:
            url = (item.get("url") or "").strip()
            if not url or url in seen_urls or not _is_official_domain(url):
                continue
            seen_urls.add(url)
            sources.append({
                "title": (item.get("title") or url).strip(),
                "url": url,
                "domain": urlparse(url).hostname or "official source",
                "snippet": (item.get("content") or "").strip()[:900],
            })
            if len(sources) >= 6:
                break

        return {
            "sources": sources,
            "status": "ok" if sources else "no_results",
            "message": "",
        }
    except Exception as exc:
        # Keep disease detection working even if search is unavailable or rate-limited.
        return {
            "sources": [],
            "status": "search_error",
            "message": str(exc)[:300],
        }


@router.get("/{crop}/{diagnosis}")
async def get_guidance(crop: str, diagnosis: str):
    key = f"{crop}___{diagnosis}"
    stored_guidance = GUIDANCE.get(key)

    if stored_guidance is None:
        # Unknown disease labels still get official web-search results instead of a 404.
        stored_guidance = {
            "disease_type": "Disease type requires confirmation",
            "summary": (
                "No local guidance entry exists for this model label. "
                "Review the official agricultural sources below and confirm the diagnosis."
            ),
            "management": [
                "Check the diagnosis against the crop image and field symptoms.",
                "Consult a local agricultural extension officer before treatment.",
            ],
            "treatment": [
                "Do not select a pesticide from the model label alone.",
                "Use a product only when an official source and current product label support its use for this crop and disease.",
            ],
        }

    healthy = diagnosis.lower() == "healthy"
    if healthy:
        search_result = {"sources": [], "status": "healthy", "message": ""}
    else:
        search_result = await asyncio.to_thread(_search_official_sources, crop, diagnosis)

    candidates = [] if healthy else PESTICIDE_RECOMMENDATIONS.get(key, [])

    return {
        "success": True,
        "crop": crop,
        "diagnosis": diagnosis,
        "guidance": stored_guidance,
        "pesticide_policy": (
            "Use only legally registered products labelled for the crop and diagnosed disease in your location. "
            "Follow the product label, protective equipment requirements, application instructions and pre-harvest interval."
        ),
        "pesticide_recommendations": candidates,
        "web_sources": search_result["sources"],
        "web_search_status": search_result["status"],
    }
