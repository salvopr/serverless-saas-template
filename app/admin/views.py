from datetime import datetime
from dateutil.relativedelta import relativedelta
from flask import render_template
from flask_login import login_required
from . import admin_blueprint
from app.admin.admin_required import admin_required
from app.events import MonthlyKPIs


@admin_blueprint.route("/", methods=["GET", "POST"])
@login_required
@admin_required
def index():
    """ Serve a page with the metrics """
    date_now = datetime.utcnow()
    kpi_this = MonthlyKPIs(date_now)
    kpi_prev = MonthlyKPIs(date_now - relativedelta(months=1))
    kpi_prev.analyze()
    kpi_this.analyze()
    return render_template('admin/analytics.html', kpi_this=kpi_this, kpi_prev=kpi_prev)
