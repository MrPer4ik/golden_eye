from flask import render_template, make_response

from models import XRate

from api import update_rate


def get_all_rates():
    try:
        update_rate(840, 643)
        update_rate(840, 980)
        update_rate(1000, 840)
        xrates = XRate.select()
        return render_template("xrates.html", xrates=xrates)
    except Exception as ex:
        return make_response(str(ex), 500)
