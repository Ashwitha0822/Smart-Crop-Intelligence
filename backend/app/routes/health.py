import os
import math
from datetime import datetime, timedelta, timezone
from typing import List

import requests
from pyproj import Transformer

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..auth import current_user
from ..database import get_db
from ..models import CropHealth, User
from ..schemas import HealthIn


router = APIRouter(
    prefix="/api/health",
    tags=["Crop Health"]
)


# ============================================================
# HEALTH STATUS
# ============================================================

def status(ndvi: float):
    if ndvi >= 0.60:
        return "Healthy"

    if ndvi >= 0.30:
        return "Moderate"

    return "Poor"


# ============================================================
# MANUAL CROP HEALTH
# ============================================================

@router.post("")
def analyze(
    data: HealthIn,
    db: Session = Depends(get_db),
    user: User = Depends(current_user)
):
    health_status = status(data.ndvi)

    row = CropHealth(
        user_id=user.id,
        ndvi=data.ndvi,
        health_status=health_status,
        note=data.note
    )

    db.add(row)
    db.commit()
    db.refresh(row)

    return {
        "ndvi": data.ndvi,
        "health_status": health_status,
        "id": row.id,
        "note": data.note
    }


# ============================================================
# LATEST CROP HEALTH
# ============================================================

@router.get("/latest")
def latest_health(
    db: Session = Depends(get_db),
    user: User = Depends(current_user)
):
    row = (
        db.query(CropHealth)
        .filter(CropHealth.user_id == user.id)
        .order_by(CropHealth.id.desc())
        .first()
    )

    if not row:
        return {
            "available": False,
            "message": "No crop health analysis found."
        }

    return {
        "available": True,
        "id": row.id,
        "ndvi": row.ndvi,
        "health_status": row.health_status,
        "note": row.note,
        "created_at": row.created_at
    }


# ============================================================
# REQUEST MODELS
# ============================================================

class NDVIInput(BaseModel):
    b04: List[float]
    b08: List[float]


class SatelliteNDVIInput(BaseModel):
    latitude: float
    longitude: float


# ============================================================
# MANUAL B04 + B08 NDVI
# ============================================================

@router.post("/ndvi")
def calculate_ndvi(
    data: NDVIInput,
    db: Session = Depends(get_db),
    user: User = Depends(current_user)
):
    if len(data.b04) != len(data.b08):
        return {
            "success": False,
            "message": "B04 and B08 must contain the same number of pixels."
        }

    if len(data.b04) == 0:
        return {
            "success": False,
            "message": "No satellite pixel data provided."
        }

    ndvi_values = []

    for red, nir in zip(data.b04, data.b08):

        denominator = nir + red

        if denominator == 0:
            ndvi = 0.0
        else:
            ndvi = (nir - red) / denominator

        ndvi_values.append(ndvi)

    average_ndvi = sum(ndvi_values) / len(ndvi_values)

    health_status = status(average_ndvi)

    row = CropHealth(
        user_id=user.id,
        ndvi=average_ndvi,
        health_status=health_status,
        note="Calculated using Sentinel-2 B04 (Red) and B08 (NIR) bands"
    )

    db.add(row)
    db.commit()
    db.refresh(row)

    return {
        "success": True,
        "id": row.id,
        "ndvi": round(average_ndvi, 4),
        "health_status": health_status,
        "pixels_analyzed": len(ndvi_values),
        "message": "NDVI calculated successfully from B04 and B08."
    }


# ============================================================
# REAL SENTINEL-2 NDVI
# ============================================================

@router.post("/satellite")
def satellite_ndvi(
    data: SatelliteNDVIInput,
    db: Session = Depends(get_db),
    user: User = Depends(current_user)
):

    # ========================================================
    # 1. COPERNICUS CREDENTIALS
    # ========================================================

    client_id = os.getenv("CDSE_CLIENT_ID")
    client_secret = os.getenv("CDSE_CLIENT_SECRET")

    if not client_id or not client_secret:
        return {
            "success": False,
            "step": "credentials",
            "message": "Copernicus credentials are not configured."
        }

    # ========================================================
    # 2. VALIDATE COORDINATES
    # ========================================================

    if not (-90 <= data.latitude <= 90):
        return {
            "success": False,
            "step": "coordinates",
            "message": "Invalid latitude."
        }

    if not (-180 <= data.longitude <= 180):
        return {
            "success": False,
            "step": "coordinates",
            "message": "Invalid longitude."
        }

    lat = data.latitude
    lon = data.longitude

    # ========================================================
    # 3. COPERNICUS AUTHENTICATION
    # ========================================================

    token_url = (
        "https://identity.dataspace.copernicus.eu/"
        "auth/realms/CDSE/protocol/openid-connect/token"
    )

    try:
        token_response = requests.post(
            token_url,
            data={
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret
            },
            timeout=30
        )

    except requests.RequestException as e:
        return {
            "success": False,
            "step": "authentication",
            "message": "Could not connect to Copernicus.",
            "error": str(e)
        }

    if token_response.status_code != 200:
        return {
            "success": False,
            "step": "authentication",
            "message": "Copernicus authentication failed.",
            "status_code": token_response.status_code,
            "details": token_response.text[:1000]
        }

    try:
        token_json = token_response.json()
        access_token = token_json.get("access_token")

    except ValueError:
        return {
            "success": False,
            "step": "authentication",
            "message": "Invalid response from Copernicus authentication."
        }

    if not access_token:
        return {
            "success": False,
            "step": "authentication",
            "message": "Copernicus did not return an access token."
        }

    # ========================================================
    # 4. CONVERT LAT/LON TO UTM ZONE 44N
    # ========================================================

    # Hyderabad is in UTM Zone 44N.
    #
    # EPSG:4326  = latitude/longitude
    # EPSG:32644 = UTM Zone 44N in metres

    try:
        transformer = Transformer.from_crs(
            "EPSG:4326",
            "EPSG:32644",
            always_xy=True
        )

        x, y = transformer.transform(lon, lat)

    except Exception as e:
        return {
            "success": False,
            "step": "coordinate_conversion",
            "message": "Could not convert coordinates to UTM.",
            "error": str(e)
        }

    # ========================================================
    # 5. CREATE 1 KM × 1 KM AREA
    # ========================================================

    # 500 metres in each direction
    # gives approximately 1 km × 1 km area

    area_size = 500

    bbox = [
        x - area_size,
        y - area_size,
        x + area_size,
        y + area_size
    ]

    # ========================================================
    # 6. DATE RANGE
    # ========================================================

    today = datetime.now(timezone.utc).date()

    start_date = today - timedelta(days=90)

    start_time = f"{start_date}T00:00:00Z"
    end_time = f"{today}T23:59:59Z"

    # ========================================================
    # 7. SENTINEL-2 EVALSCRIPT
    # ========================================================

    evalscript = """
//VERSION=3

function setup() {

    return {
        input: [{
            bands: [
                "B04",
                "B08",
                "SCL",
                "dataMask"
            ]
        }],

        output: [
            {
                id: "ndvi",
                bands: 1,
                sampleType: "FLOAT32"
            },

            {
                id: "vegetation",
                bands: 1,
                sampleType: "FLOAT32"
            },

            {
                id: "dataMask",
                bands: 1
            }
        ]
    };
}


function evaluatePixel(sample) {

    // --------------------------------------------------------
    // No source data
    // --------------------------------------------------------

    if (sample.dataMask === 0) {

        return {
            ndvi: [0],
            vegetation: [0],
            dataMask: [0]
        };
    }


    // --------------------------------------------------------
    // Exclude water
    // SCL = 6 means water
    // --------------------------------------------------------

    if (sample.SCL === 6) {

        return {
            ndvi: [0],
            vegetation: [0],
            dataMask: [0]
        };
    }


    // --------------------------------------------------------
    // NDVI calculation
    // B04 = Red
    // B08 = Near Infrared
    // --------------------------------------------------------

    let denominator = sample.B08 + sample.B04;


    if (denominator === 0) {

        return {
            ndvi: [0],
            vegetation: [0],
            dataMask: [0]
        };
    }


    let ndvi =
        (sample.B08 - sample.B04)
        / denominator;


    // --------------------------------------------------------
    // Simple vegetation indicator
    //
    // NDVI > 0.20 is treated as vegetation
    // --------------------------------------------------------

    let vegetation = 0;

    if (ndvi > 0.20) {
        vegetation = 1;
    }


    return {

        ndvi: [ndvi],

        vegetation: [vegetation],

        dataMask: [1]
    };
}
"""

    # ========================================================
    # 8. COPERNICUS STATISTICS REQUEST
    # ========================================================

    statistics_request = {

        "input": {

            "bounds": {

                "bbox": bbox,

                "properties": {

                    "crs":
                        "http://www.opengis.net/def/crs/EPSG/0/32644"
                }
            },

            "data": [

                {

                    "type": "sentinel-2-l2a",

                    "dataFilter": {

                        "mosaickingOrder": "leastCC",

                        "maxCloudCoverage": 80
                    }
                }
            ]
        },


        "aggregation": {

            "timeRange": {

                "from": start_time,

                "to": end_time
            },


            "aggregationInterval": {

                "of": "P30D"
            },


            "evalscript": evalscript,


            # 10 metre Sentinel-2 resolution
            "resx": 10,

            "resy": 10
        }
    }

    # ========================================================
    # 9. CALL COPERNICUS STATISTICS API
    # ========================================================

    statistics_url = (
        "https://sh.dataspace.copernicus.eu/"
        "statistics/v1"
    )

    try:

        response = requests.post(

            statistics_url,

            headers={

                "Authorization":
                    f"Bearer {access_token}",

                "Content-Type":
                    "application/json",

                "Accept":
                    "application/json"
            },

            json=statistics_request,

            timeout=120
        )

    except requests.RequestException as e:

        return {

            "success": False,

            "step": "statistics_request",

            "message":
                "Could not connect to Copernicus Statistical API.",

            "error": str(e)
        }


    # ========================================================
    # 10. CHECK COPERNICUS RESPONSE
    # ========================================================

    if response.status_code != 200:

        return {

            "success": False,

            "step": "statistics_request",

            "message":
                "Copernicus satellite request failed.",

            "status_code":
                response.status_code,

            "details":
                response.text[:2000]
        }


    # ========================================================
    # 11. PARSE JSON
    # ========================================================

    try:

        result = response.json()

    except ValueError:

        return {

            "success": False,

            "step": "statistics_response",

            "message":
                "Copernicus returned invalid JSON.",

            "details":
                response.text[:2000]
        }


    # ========================================================
    # 12. EXTRACT NDVI STATISTICS
    # ========================================================

    try:

        ndvi_stats = (
            result["data"][0]
            ["outputs"]["ndvi"]
            ["bands"]["B0"]
            ["stats"]
        )


        raw_mean = ndvi_stats.get("mean")

        
        raw_sample_count = ndvi_stats.get("sampleCount")
        raw_no_data_count = ndvi_stats.get("noDataCount")


        average_ndvi = float(raw_mean)

        sample_count = int(
            raw_sample_count or 0
        )

        no_data_count = int(
            raw_no_data_count or 0
        )


    except (
        KeyError,
        IndexError,
        TypeError,
        ValueError
    ) as e:

        return {

            "success": False,

            "step": "ndvi_extraction",

            "message":
                "Could not extract valid NDVI statistics.",

            "error": str(e)
        }


    # ========================================================
    # 13. CHECK NDVI FOR NaN / INFINITY
    # ========================================================

    if not math.isfinite(average_ndvi):

        return {

            "success": False,

            "step": "ndvi_validation",

            "message":
                "Satellite API returned NaN or Infinity instead of a valid NDVI.",

            "raw_mean":
                str(raw_mean),

            "pixels_analyzed":
                sample_count,

            "no_data_pixels":
                no_data_count
        }


    # ========================================================
    # 14. CHECK NDVI RANGE
    # ========================================================

    if average_ndvi < -1 or average_ndvi > 1:

        return {

            "success": False,

            "step": "ndvi_validation",

            "message":
                "NDVI is outside the valid range of -1 to 1.",

            "ndvi":
                average_ndvi
        }


    # ========================================================
    # 15. CHECK VALID PIXELS
    # ========================================================

    if sample_count == 0:

        return {

            "success": False,

            "step": "pixel_analysis",

            "message":
                "No valid satellite pixels were available.",

            "pixels_analyzed":
                0,

            "no_data_pixels":
                no_data_count
        }


    # ========================================================
    # 16. EXTRACT VEGETATION STATISTICS
    # ========================================================

    vegetation_percentage = None

    try:

        vegetation_stats = (
            result["data"][0]
            ["outputs"]["vegetation"]
            ["bands"]["B0"]
            ["stats"]
        )


        vegetation_mean = float(
            vegetation_stats.get("mean", 0)
        )


        vegetation_percentage = vegetation_mean * 100


        # Keep percentage between 0 and 100

        vegetation_percentage = max(
            0,
            min(
                100,
                vegetation_percentage
            )
        )


    except (
        KeyError,
        IndexError,
        TypeError,
        ValueError
    ):

        vegetation_percentage = None


    # ========================================================
    # 17. HEALTH CLASSIFICATION
    # ========================================================

    health_status = status(
        average_ndvi
    )


    # ========================================================
    # 18. SAVE TO MYSQL
    # ========================================================

    try:

        if vegetation_percentage is not None:

            note = (
                "Sentinel-2 B04/B08 satellite NDVI "
                f"for latitude {lat:.6f}, "
                f"longitude {lon:.6f}; "
                f"vegetation coverage: "
                f"{vegetation_percentage:.2f}%"
            )

        else:

            note = (
                "Sentinel-2 B04/B08 satellite NDVI "
                f"for latitude {lat:.6f}, "
                f"longitude {lon:.6f}"
            )


        row = CropHealth(

            user_id=user.id,

            ndvi=float(
                average_ndvi
            ),

            health_status=
                health_status,

            note=note
        )


        db.add(row)

        db.commit()

        db.refresh(row)


    except Exception as e:

        db.rollback()

        return {

            "success": False,

            "step": "database",

            "message":
                "NDVI was calculated but could not be saved to the database.",

            "error":
                str(e)
        }


    # ========================================================
    # 19. FINAL RESPONSE
    # ========================================================

    return {

        "success": True,

        "id":
            row.id,

        "latitude":
            lat,

        "longitude":
            lon,

        "ndvi":
            round(
                average_ndvi,
                4
            ),

        "health_status":
            health_status,

        "vegetation_percentage":
            (
                round(
                    vegetation_percentage,
                    2
                )
                if vegetation_percentage is not None
                else None
            ),

        "pixels_analyzed":
            sample_count,

        "no_data_pixels":
            no_data_count,

        "analysis_period": {

            "from":
                start_time,

            "to":
                end_time
        },

        "message":
            "Real Sentinel-2 NDVI calculated successfully."
    }
# ============================================================
# CROP HEALTH HISTORY
# ============================================================

@router.get("/history")
def health_history(
    db: Session = Depends(get_db),
    user: User = Depends(current_user)
):
    rows = (
        db.query(CropHealth)
        .filter(CropHealth.user_id == user.id)
        .order_by(CropHealth.created_at.asc())
        .all()
    )

    return {
        "success": True,
        "count": len(rows),
        "history": [
            {
                "id": row.id,
                "ndvi": float(row.ndvi),
                "health_status": row.health_status,
                "note": row.note,
                "created_at": (
                    row.created_at.isoformat()
                    if row.created_at
                    else None
                )
            }
            for row in rows
        ]
    }