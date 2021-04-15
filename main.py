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
        # render input page
        return render_template("input.html", descs=descs, err=err, err_msgs=err_msgs)
    else:
        # retrieve form submission
        entry = {key: request.form.get(key, None) for key in ["start", "end", "mode", "group", "payment_mode"]}
        val.set_params(entry)
        # retrieve validation results
        err_msgs, passed = val.check_all_input()
        if not passed:
            # render input page if input validation fails
            return render_template("input.html", descs=descs, err=err, err_msgs=err_msgs)
        bus_routes, b1_code, b2_code = sql.find_routes(entry["start"], entry["end"])
        err, passed = val.check_routes(bus_routes, entry["start"], entry["end"])
        if not passed:
            # render input page if routes verification fails
            return render_template("input.html", descs=descs, err=err, err_msgs=err_msgs)
        temp = sql.optimal(entry["mode"], b1_code, b2_code, bus_routes, entry["group"], entry["payment_mode"])
        results = [tuple(x.values()) for x in temp]
        headers = ["Bus No.", "Distance (in km)", "Fare (in cents)"]
        if entry["group"] in ["student", "senior", "workfare"]:
            entry["group"] += " concession pass"
        return render_template("routes.html", results=results, headers=headers, entry=entry)


app.run()
