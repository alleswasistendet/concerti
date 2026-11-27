def compute_statistics(concerts):
    event_count = len(concerts)

    total_price = sum(concert.price or 0.0 for concert in concerts)

    average_price = total_price / event_count if event_count > 0 else None

    return {
        "event_count": event_count,
        "total_price": total_price,
        "average_price": average_price,
    }


def compute_institution_statistics(concerts):
    institution_counts = {}

    for concert in concerts:
        institution = concert.institution or "Non specificato"

        institution_counts[institution] = institution_counts.get(institution, 0) + 1

    return institution_counts


def compute_monthly_statistics(concerts):
    monthly_totals = {}

    for concert in concerts:
        year_month = concert.date[:7]

        monthly_totals[year_month] = monthly_totals.get(year_month, 0.0) + (
            concert.price or 0.0
        )

    return dict(sorted(monthly_totals.items()))
