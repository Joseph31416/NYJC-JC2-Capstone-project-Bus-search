from flask import Flask, request, render_template
from database import SqlOperations


app = Flask(__name__)
sql = SqlOperations()


@app.route("/")
def root():
    return render_template("index.html")


@app.route("/routes", methods=["POST", "GET"])
def routes():
    err = None
    if request.method == "GET":
        return render_template("input.html", err=err)
    else:
        b1 = request.form.get("BusStop1", None)
        b2 = request.form.get("BusStop2", None)
        if request.form.get("mode", None) in ["distance", "fare"]:
            mode = request.form.get("mode")
        else:
            err = "Invalid option."
            return render_template("input.html", err=err)
        if request.form.get("group", None) in ["adult", "student", "senior", "workfare", "disabilities"]:
            group = request.form.get("group")
        else:
            err = "Invalid option."
            return render_template("input.html", err=err)
        if request.form.get("payment_mode", None) in ["cash", "card"]:
            payment_mode = request.form.get("payment_mode")
        else:
            err = "Invalid option."
            return render_template("input.html", err=err)
        b1, b2 = sql.match(b1), sql.match(b2)
        entry = {"start": b1, "end": b2, "mode": mode, "group": group, "payment_mode": payment_mode}
        b1_code, b2_code = sql.get_bus_stop_code(b1), sql.get_bus_stop_code(b2)
        bus_routes = sql.find_routes((b1_code, b2_code))
        if len(bus_routes) == 0:
            err = "No direct bus between these two stops."
            return render_template("input.html", err=err)
        temp = sql.optimal(mode, b1_code, b2_code, bus_routes, group, payment_mode)
        results = [tuple(x.values()) for x in temp]
        keys = list(temp[0].keys())
        return render_template("routes.html", results=results, keys=keys, entry=entry)


app.run()
