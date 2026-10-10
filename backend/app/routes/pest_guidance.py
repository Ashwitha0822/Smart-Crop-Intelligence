from fastapi import APIRouter, HTTPException


router = APIRouter(
    prefix="/api/pest-guidance",
    tags=["Pest Guidance"]
)


PEST_GUIDANCE = {

    "rice leaf roller": {
        "crop": "Rice",
        "type": "Insect pest",
        "summary": "Larvae feed on rice leaves and can reduce the photosynthetic area.",
        "management": [
            "Monitor leaves regularly for folding and larval feeding.",
            "Avoid unnecessary excessive nitrogen application.",
            "Conserve natural enemies and avoid unnecessary broad-spectrum insecticide use.",
            "Use treatment only when pest pressure reaches the locally recommended threshold."
        ],
        "treatment": [
            "Remove heavily affected plant material where practical.",
            "Use biological or botanical options where locally recommended.",
            "If chemical control is necessary, use only a product registered and labelled for the crop and pest in your location."
        ]
    },

    "asiatic rice borer": {
        "crop": "Rice",
        "type": "Insect pest",
        "summary": "A stem-boring pest that can cause dead hearts and damaged panicles in rice.",
        "management": [
            "Monitor the crop regularly for dead hearts and white ear symptoms.",
            "Use pheromone traps for monitoring where locally recommended.",
            "Conserve parasitoids and other natural enemies.",
            "Avoid unnecessary insecticide applications."
        ],
        "treatment": [
            "Use biological control measures such as recommended parasitoids where available.",
            "Use need-based treatment when monitoring indicates damaging pest levels.",
            "Any pesticide must be registered and labelled for rice and the diagnosed pest."
        ]
    },

    "yellow rice borer": {
        "crop": "Rice",
        "type": "Insect pest",
        "summary": "A rice stem borer that can damage stems and developing panicles.",
        "management": [
            "Inspect rice plants for dead hearts and white ears.",
            "Use pheromone monitoring where recommended.",
            "Maintain field sanitation and remove crop residues appropriately.",
            "Conserve beneficial insects."
        ],
        "treatment": [
            "Use biological control where locally recommended.",
            "Apply chemical treatment only when monitoring indicates the need.",
            "Follow the registered product label and pre-harvest interval."
        ]
    },

    "rice gall midge": {
        "crop": "Rice",
        "type": "Insect pest",
        "summary": "The larvae damage growing rice shoots and can produce characteristic silver shoot or gall-like symptoms.",
        "management": [
            "Monitor tillers regularly for characteristic damage.",
            "Use resistant or tolerant varieties where locally recommended.",
            "Maintain field sanitation and balanced crop nutrition.",
            "Base treatment decisions on local economic thresholds."
        ],
        "treatment": [
            "Use recommended cultural and biological management first.",
            "Use chemical control only when economically justified.",
            "Use only products registered and labelled for rice gall midge in your location."
        ]
    },

    "brown plant hopper": {
        "crop": "Rice",
        "type": "Insect pest",
        "summary": "A sap-sucking rice pest that can cause hopper burn and can also transmit plant diseases.",
        "management": [
            "Regularly inspect the base of rice plants for nymphs and adults.",
            "Avoid excessive nitrogen fertilization.",
            "Avoid overly dense planting and maintain suitable field spacing.",
            "Use intermittent drainage where appropriate and conserve natural predators."
        ],
        "treatment": [
            "Use monitoring and economic thresholds before chemical intervention.",
            "Direct any approved treatment toward the lower portion of the rice canopy where the hoppers occur.",
            "Use only locally registered products labelled for rice brown plant hopper."
        ]
    },

    "white backed plant hopper": {
        "crop": "Rice",
        "type": "Insect pest",
        "summary": "A sap-sucking rice hopper that can cause plant drying and yield loss.",
        "management": [
            "Regularly monitor the base of rice plants.",
            "Avoid excessive nitrogen application.",
            "Use appropriate irrigation management.",
            "Conserve spiders, mirid bugs and other natural enemies."
        ],
        "treatment": [
            "Treat only when pest populations reach a locally recommended threshold.",
            "Prefer integrated and selective management approaches.",
            "Use only legally registered products labelled for the crop and pest."
        ]
    },

    "small brown plant hopper": {
        "crop": "Rice",
        "type": "Insect pest",
        "summary": "A small sap-sucking rice hopper that can contribute to plant weakening and crop damage.",
        "management": [
            "Monitor rice plants and the lower canopy regularly.",
            "Avoid excessive nitrogen fertilization.",
            "Maintain suitable plant spacing.",
            "Conserve natural enemies."
        ],
        "treatment": [
            "Use threshold-based management.",
            "Prefer selective and integrated methods where available.",
            "Use only products registered and labelled for rice and the identified pest."
        ]
    },

    "rice water weevil": {
        "crop": "Rice",
        "type": "Insect pest",
        "summary": "A rice weevil whose larvae can feed on roots and weaken plants.",
        "management": [
            "Monitor young rice fields for signs of root feeding and plant weakening.",
            "Maintain appropriate water management.",
            "Remove volunteer rice and weeds that may support pest populations.",
            "Use locally recommended cultural and biological measures."
        ],
        "treatment": [
            "Base intervention on field monitoring and local recommendations.",
            "Use non-chemical measures where practical.",
            "Use only registered products labelled for rice water weevil."
        ]
    },

    "corn borer": {
        "crop": "Maize",
        "type": "Insect pest",
        "summary": "A stem-boring pest that can weaken maize plants and damage growing tissues.",
        "management": [
            "Scout plants regularly for boring symptoms and larval damage.",
            "Remove severely damaged plant material where practical.",
            "Maintain field sanitation after harvest.",
            "Conserve natural enemies and use biological control where locally recommended."
        ],
        "treatment": [
            "Use threshold-based intervention.",
            "Prefer biological or integrated methods where available.",
            "Use only products registered and labelled for maize and the diagnosed pest."
        ]
    },

    "army worm": {
        "crop": "Maize",
        "type": "Insect pest",
        "summary": "A caterpillar pest that can rapidly defoliate maize and other crops.",
        "management": [
            "Scout young plants frequently for eggs and caterpillars.",
            "Remove weeds that can harbour the pest where appropriate.",
            "Encourage natural enemies.",
            "Take action early when damaging populations are detected."
        ],
        "treatment": [
            "Use biological or botanical control options where locally recommended.",
            "Apply pesticide treatment only when needed and according to the registered label.",
            "Rotate approved modes of action where chemical treatment is necessary and recommended."
        ]
    },

    "Viteus vitifoliae": {
        "crop": "Grape",
        "type": "Insect pest",
        "summary": "Grape phylloxera is a sap-feeding pest that can damage grape roots and foliage.",
        "management": [
            "Monitor grape roots and foliage for characteristic feeding symptoms.",
            "Use suitable resistant or tolerant rootstocks where recommended.",
            "Use clean planting material.",
            "Remove and manage severely affected material according to local guidance."
        ],
        "treatment": [
            "Use integrated management and clean planting material.",
            "Chemical treatment should be based on local recommendations and registration status.",
            "Use only products specifically labelled for grapes and the diagnosed pest."
        ]
    },

    "Ampelophaga": {
        "crop": "Grape",
        "type": "Insect pest",
        "summary": "An insect pest associated with grape foliage and plant feeding.",
        "management": [
            "Inspect grape foliage regularly for feeding damage.",
            "Remove heavily infested plant material where practical.",
            "Maintain orchard sanitation.",
            "Conserve beneficial insects."
        ],
        "treatment": [
            "Use monitoring to determine whether intervention is necessary.",
            "Prefer biological and cultural measures where available.",
            "Use only locally registered products labelled for grapes and the pest."
        ]
    },

    "Icerya purchasi Maskell": {
        "crop": "Orange",
        "type": "Insect pest",
        "summary": "A scale-like sap-feeding pest that can weaken citrus plants and produce honeydew.",
        "management": [
            "Inspect young shoots, leaves and branches regularly.",
            "Prune heavily infested portions where practical.",
            "Conserve natural enemies.",
            "Control ants where they interfere with natural biological control."
        ],
        "treatment": [
            "Use biological control where locally recommended.",
            "Use horticultural or botanical options only when appropriate and locally approved.",
            "Use only products registered and labelled for citrus and the pest."
        ]
    },

    "Unaspis yanonensis": {
        "crop": "Orange",
        "type": "Insect pest",
        "summary": "A citrus scale insect that can weaken branches, leaves and fruiting tissues.",
        "management": [
            "Inspect branches and foliage for scale infestations.",
            "Prune heavily infested material where practical.",
            "Maintain orchard sanitation.",
            "Conserve natural enemies."
        ],
        "treatment": [
            "Use monitoring-based treatment.",
            "Prefer integrated and selective management.",
            "Use only locally registered products labelled for citrus scale insects."
        ]
    },

    "Aleurocanthus spiniferus": {
        "crop": "Orange",
        "type": "Insect pest",
        "summary": "A citrus whitefly associated with sap feeding and honeydew production.",
        "management": [
            "Inspect the underside of leaves regularly.",
            "Remove heavily infested leaves where practical.",
            "Conserve parasitoids and predators.",
            "Avoid unnecessary broad-spectrum insecticide use."
        ],
        "treatment": [
            "Use biological control and monitoring where appropriate.",
            "Treat when local thresholds justify intervention.",
            "Use only registered products labelled for the crop and pest."
        ]
    },

    "Tetradacus c Bactrocera minax": {
        "crop": "Orange",
        "type": "Insect pest",
        "summary": "A fruit-fly pest that can damage citrus fruit.",
        "management": [
            "Collect and destroy fallen and infested fruit.",
            "Maintain orchard sanitation.",
            "Use traps and monitoring where locally recommended.",
            "Avoid leaving infested fruit in the orchard."
        ],
        "treatment": [
            "Use trapping and sanitation as key management measures.",
            "Use approved bait or other treatment only when locally recommended.",
            "Follow the registered product label and pre-harvest interval."
        ]
    },

    "Phyllocnistis citrella Stainton": {
        "crop": "Orange",
        "type": "Insect pest",
        "summary": "The citrus leafminer damages young citrus leaves by creating serpentine mines.",
        "management": [
            "Monitor young flushes for leaf mines.",
            "Avoid excessive nitrogen that produces highly susceptible flush.",
            "Conserve parasitoids and natural enemies.",
            "Prune and dispose of severely affected shoots where appropriate."
        ],
        "treatment": [
            "Use biological control where available.",
            "Use need-based treatment during vulnerable flush periods.",
            "Use only products registered and labelled for citrus leafminer."
        ]
    },

    "Aphis citricola Vander Goot": {
        "crop": "Orange",
        "type": "Insect pest",
        "summary": "An aphid that feeds on young citrus growth and can weaken shoots.",
        "management": [
            "Inspect tender shoots and young leaves frequently.",
            "Conserve ladybirds, lacewings and other natural enemies.",
            "Avoid unnecessary broad-spectrum insecticides.",
            "Manage excessive soft vegetative growth."
        ],
        "treatment": [
            "Use biological and cultural management first.",
            "Use need-based treatment when economically justified.",
            "Use only locally registered products labelled for citrus aphids."
        ]
    },

    "Rhytidodera bowrinii white": {
        "crop": "Mango",
        "type": "Insect pest",
        "summary": "A beetle pest associated with mango plant tissues.",
        "management": [
            "Inspect trunks, branches and growing tissues for signs of infestation.",
            "Remove and destroy severely infested material where practical.",
            "Maintain orchard sanitation.",
            "Monitor regularly during susceptible periods."
        ],
        "treatment": [
            "Prefer mechanical and cultural control where feasible.",
            "Use chemical intervention only when locally recommended.",
            "Use only products registered and labelled for mango and the pest."
        ]
    },

    "Sternochetus frigidus": {
        "crop": "Mango",
        "type": "Insect pest",
        "summary": "A mango-associated weevil pest that can damage developing plant or fruit tissues.",
        "management": [
            "Collect and destroy infested or fallen fruit where appropriate.",
            "Maintain orchard sanitation.",
            "Monitor fruit and plant tissues regularly.",
            "Remove breeding sources where practical."
        ],
        "treatment": [
            "Use sanitation and monitoring as primary measures.",
            "Use approved treatment only when local recommendations indicate a need.",
            "Follow product label, PPE and pre-harvest interval requirements."
        ]
    }
}


@router.get("/{pest_name}")
def get_pest_guidance(
    pest_name: str
):
    pest_name = pest_name.strip()

    if pest_name not in PEST_GUIDANCE:
        raise HTTPException(
            status_code=404,
            detail="Guidance is not available for this pest."
        )

    data = PEST_GUIDANCE[pest_name]

    return {
        "success": True,
        "pest": pest_name,
        **data,
        "pesticide_policy": (
            "Use pesticides only when necessary and only "
            "products legally registered and labelled for "
            "the crop and diagnosed pest in your location. "
            "Follow the label, protective equipment, "
            "application instructions and pre-harvest interval. "
            "Follow local agricultural recommendations."
        )
    }