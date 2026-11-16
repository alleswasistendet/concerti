from app.cConcertFilterProxyModel import ConcertFilterProxyModel
from app.cConcertTableModel import ConcertTableModel
from database.models import Concert


def test_filter_model():
    concerts = [
        (
            1,
            Concert(
                date="2025-06-09",
                institution="Teatro alla Scala",
                title="Siegfried",
                price=10.0,
                typology="Opera",
            ),
        ),
        (
            2,
            Concert(
                date="2026-04-13",
                institution="Filarmonica della Scala",
                title="Mariotti",
                price=20.0,
                typology="Concerto",
                subtypology="Sinfonico",
            ),
        ),
        (
            3,
            Concert(
                date="2026-06-30",
                institution="Bayerische Staatsoper",
                title="Turandot",
                price=68.0,
                typology="Opera",
            ),
        ),
    ]

    source_model = ConcertTableModel(concerts)

    proxy = ConcertFilterProxyModel()
    proxy.setSourceModel(source_model)

    # No filter applied
    assert proxy.rowCount() == 3

    # Filter by year
    proxy.set_month_year(year=2026)
    assert proxy.rowCount() == 2

    # Filter by month and year
    proxy.set_month_year(month=4, year=2026)
    assert proxy.rowCount() == 1

    # Clear date filter
    proxy.set_month_year()
    assert proxy.rowCount() == 3

    # Substring search
    proxy.set_column_filter(2, "siegfried")
    assert proxy.rowCount() == 1

    # Exact match
    proxy.set_column_filter(4, "Opera", mode="exact")
    assert proxy.rowCount() == 1

    # No match with combined filter
    proxy.set_column_filter(2, "additional")
    assert proxy.rowCount() == 0

    # Clear one filter
    proxy.set_column_filter(2, "")
    assert proxy.rowCount() == 2

    # Clear remaining filters
    proxy.set_column_filter(3, "")
    proxy.set_column_filter(4, "")
    assert proxy.rowCount() == 3

    # Price interval
    proxy.set_price_range(5.0, 20.0)
    assert proxy.rowCount() == 2

    proxy.set_price_range(price_min=20.0)
    assert proxy.rowCount() == 2

    proxy.set_price_range(price_max=10.0)
    assert proxy.rowCount() == 1

    proxy.set_price_range()
    assert proxy.rowCount() == 3
