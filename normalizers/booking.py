# normalizers/booking.py
from typing import Dict, Any, List, Optional
from models.models_hotels import HotelItemOut, HotelSearchResultOut

def normalize_booking_response(raw: Dict[str, Any]) -> HotelSearchResultOut:
    """
    Converte o payload da RapidAPI Booking num formato estável (HotelItemOut),
    sem calcular distâncias (isso é feito no tool).
    """
    results = (((raw or {}).get("data") or {}).get("results")) or []
    items: List[HotelItemOut] = []

    for r in results:
        bp = (r.get("basicPropertyData") or {})
        loc = (bp.get("location") or {})
        reviews = (bp.get("reviews") or {})
        stars = (bp.get("starRating") or {})

        # preço total da estadia: preferir priceDisplayInfo.amountPerStay; fallback blocks[0].finalPrice
        price_info = (((r.get("priceDisplayInfo") or {}).get("displayPrice") or {}).get("amountPerStay")) or {}
        amount = price_info.get("amountUnformatted")
        currency = price_info.get("currency")
        if amount is None:
            blocks = r.get("blocks") or []
            if blocks:
                fp = (blocks[0] or {}).get("finalPrice") or {}
                amount = fp.get("amount")
                currency = fp.get("currency")

        item = HotelItemOut(
            name=bp.get("name") or (r.get("displayName") or {}).get("text") or "Unnamed",
            latitude=loc.get("latitude"),
            longitude=loc.get("longitude"),
            address=loc.get("address"),
            stars=stars.get("value"),
            review_score=reviews.get("totalScore"),
            review_count=reviews.get("reviewsCount"),
            total_price_amount=amount,
            total_price_currency=(currency or "EUR").upper() if currency else None,
            provider_hotel_id=str(bp.get("id")) if bp.get("id") is not None else None,
            deep_link=None,
        )

        if item.latitude is not None and item.longitude is not None:
            items.append(item)

    return HotelSearchResultOut(items=items, total_results=len(results))
