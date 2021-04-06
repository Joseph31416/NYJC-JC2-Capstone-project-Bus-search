from flask import Flask, request, render_template
from database import SqlOperations
from validation import Validation
from config import Config

app = Flask(__name__)
config = Config()
sql = SqlOperations(config)
val = Validation(config)


@app.route("/")
def root():
    return render_template("index.html")


@app.route("/routes", methods=["POST", "GET"])
def routes():
    err, err_msgs = None, None
    if request.method == "GET":
        return render_template("input.html", err=err, err_msgs=err_msgs)
    else:
        b1 = request.form.get("BusStop1", None)
        b2 = request.form.get("BusStop2", None)
        mode = request.form.get("mode", None)
        group = request.form.get("group", None)
        payment_mode = request.form.get("payment_mode", None)
        val.set_params(b1, b2, mode, group, payment_mode)
        err_msgs, passed = val.check_all_input()
        if not passed:
            return render_template("input.html", err=err, err_msgs=err_msgs)
        b1, b2 = sql.match(b1), sql.match(b2)
        entry = {"start": b1, "end": b2, "mode": mode, "group": group, "payment_mode": payment_mode}
        b1_code, b2_code = sql.get_bus_stop_code(b1), sql.get_bus_stop_code(b2)
        bus_routes = sql.find_routes((b1_code, b2_code))
        err, passed = val.check_routes(bus_routes, b1, b2)
        if not passed:
            return render_template("input.html", err=err, err_msgs=err_msgs)
        temp = sql.optimal(mode, b1_code, b2_code, bus_routes, group, payment_mode)
        results = [tuple(x.values()) for x in temp]
        headers = ["Bus No.", "Distance (in km)", "Fare (in cents)"]
        return render_template("routes.html", results=results, headers=headers, entry=entry)


app.run()
