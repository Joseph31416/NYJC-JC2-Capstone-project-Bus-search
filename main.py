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
    descs = sql.get_all_bus_stops()
    if request.method == "GET":
        return render_template("input.html", descs=descs, err=err, err_msgs=err_msgs)
    else:
        entry = {key: request.form.get(key, None) for key in ["start", "end", "mode", "group", "payment_mode"]}
        val.set_params(entry)
        err_msgs, passed = val.check_all_input()
        if not passed:
            return render_template("input.html", descs=descs, err=err, err_msgs=err_msgs)
        b1_desc, b1_rn = tuple(entry["start"].strip().split(','))
        b2_desc, b2_rn = tuple(entry["end"].strip().split(','))
        b1_rn, b2_rn = b1_rn.strip(), b2_rn.strip()
        b1_code, b2_code = sql.get_bus_stop_code(b1_desc, b1_rn), sql.get_bus_stop_code(b2_desc, b2_rn)
        bus_routes = sql.find_routes((b1_code, b2_code))
        err, passed = val.check_routes(bus_routes, entry["start"], entry["end"])
        if not passed:
            return render_template("input.html", descs=descs, err=err, err_msgs=err_msgs)
        temp = sql.optimal(entry["mode"], b1_code, b2_code, bus_routes, entry["group"], entry["payment_mode"])
        results = [tuple(x.values()) for x in temp]
        headers = ["Bus No.", "Distance (in km)", "Fare (in cents)"]
        if entry["group"] in ["student", "senior", "workfare"]:
            entry["group"] += " concession pass"
        return render_template("routes.html", results=results, headers=headers, entry=entry)


app.run()
