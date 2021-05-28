from app.events import MonthlyKPIs, EventTypes
from datetime import datetime


def test_kpis(user_table, events_table):
    users = {
        "early_adopter@test.com": {datetime(2021, 3, 3): EventTypes.NEW_USER,
                                   datetime(2021, 3, 10): EventTypes.PAYMENT,
                                   datetime(2021, 4, 10): EventTypes.PAYMENT,
                                   datetime(2021, 5, 10): EventTypes.PAYMENT},
        "churn_trial@test.com": {datetime(2021, 3, 3): EventTypes.NEW_USER,
                                 datetime(2021, 3, 4): EventTypes.CHURN},
        "churn@test.com": {datetime(2021, 3, 3): EventTypes.NEW_USER,
                           datetime(2021, 3, 10): EventTypes.PAYMENT,
                           datetime(2021, 4, 4): EventTypes.CHURN},
        "churn2@test.com": {datetime(2021, 3, 3): EventTypes.NEW_USER,
                            datetime(2021, 3, 10): EventTypes.PAYMENT,
                            datetime(2021, 4, 10): EventTypes.PAYMENT,
                            datetime(2021, 5, 4): EventTypes.CHURN},
        "april@test.com": {datetime(2021, 4, 3): EventTypes.NEW_USER,
                           datetime(2021, 4, 10): EventTypes.PAYMENT,
                           datetime(2021, 5, 10): EventTypes.PAYMENT},
        "may@test.com": {datetime(2021, 5, 3): EventTypes.NEW_USER,
                         datetime(2021, 5, 10): EventTypes.PAYMENT},
        "trial@test.com": {datetime(2021, 5, 11): EventTypes.NEW_USER}
    }

    for u, evts in users.items():
        user_table.put_item(
            Item={"email": u,
                  "is_paying": False if evts[max(evts.keys())] == EventTypes.CHURN else True}
        )
        for date, e in evts.items():
            item = {"event_type": e,
                    "datetime": str(date),
                    "user": u}
            if e == EventTypes.PAYMENT:
                item["amount_paid"] = 1000
            events_table.put_item(Item=item)
    # KPIs in May
    kpi = MonthlyKPIs(datetime(2021, 5, 12))
    assert kpi.new_users() == 2
    assert kpi.churned_users() == 1
    assert kpi.churn() == 1.0
    assert kpi.mrr() == (10.0, 1)
    assert kpi.ltv() == 10

    # KPIs in April
    kpi = MonthlyKPIs(datetime(2021, 4, 12))
    assert kpi.new_users() == 1
    assert kpi.churned_users() == 1
    assert kpi.churn() == 0
    assert kpi.mrr() == (10.0, 1)
    assert kpi.ltv() == 0


def test_mau(events_table):
    for u in range(1, 10):
        item = {"event_type": EventTypes.ACTIVITY,
                "datetime": str(datetime(2021, 5, u)),
                "user": f"activity{u}@test.com"}

        events_table.put_item(Item=item)
    kpi = MonthlyKPIs(datetime(2021, 5, 21))
    assert kpi.mau() == 9
