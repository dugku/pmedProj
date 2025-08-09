from model import load_data
from model.plot import Plotter
from model.kde import KDE_data
from model.playering_field import make_polygon
from model.p_med import generate_canidate_points, demand_points, weighted_demand_points, compute_distance, compute_phis, model_thing
import numpy as np
import pprint
import polars as pl
import pyomo.environ as pyo
def controller(sess):
    dir_paht = "metadata"
    map_data = load_data.load_map_data(dir_paht)

    kill_data, ev_plHit, ev_smoke, ev_he, ev_inferno, ev_plFired  = load_data.query_data(sess, map_data)
    X, Y, Z = KDE_data(kill_data)
    X_plH, Y_plH, Z_plH = KDE_data(ev_plHit)
    X_smoke, Y_smoke, Z_smoke = KDE_data(ev_smoke)
    X_he, Y_he, Z_he = KDE_data(ev_he)
    X_inferno, Y_inferno, Z_inferno = KDE_data(ev_inferno)
    X_plFired, Y_plFired, Z_plFired = KDE_data(ev_plFired)

    kde_lay = {
        "Kills": (X, Y, Z),
        "PlHit": (X_plH, Y_plH, Z_plH),
        "Smoke": (X_smoke, Y_smoke, Z_smoke),
        "HE": (X_he, Y_he, Z_he),
        "Inferno": (X_inferno,Y_inferno,Z_inferno),
        "PlFired": (X_plFired, Y_plFired, Z_plFired)
    }

    polgon = make_polygon("img_files/de_mirage_radar_psd.png")

    can_p = generate_canidate_points(polgon)
    demand_p = demand_points(polgon, kill_data)

    phis = compute_phis(kde_lay, can_p)

    lams = {
        "Kills": 1.50,
        "PlHit": 0.6234,
        "Smoke": 0.10,
        "HE": 0.35,
        "Inferno": 0.75,
        "PlFired": 0.125
    }

    weighted_demand = weighted_demand_points(polgon, demand_p, kde_lay)
    dist = compute_distance(demand_p, can_p, polgon)
    model, results = model_thing(weighted_demand, demand_p, can_p, dist, phis, lams, polgon)

    p = Plotter(data_player=kill_data, X=X, Y=Y, Z=Z)

    p.plot_playable(polgon)

    if results.solver.termination_condition == pyo.TerminationCondition.optimal:
    # Load the solution into the model
        model.solutions.load_from(results)

        # --- whatever you need to see ---
        print("Objective:", pyo.value(model.OBJ))

        open_J = [j for j in model.J if pyo.value(model.Y[j]) > 0.5]
        p.plot_facilities(open_J)
        print("Open facilities:", open_J)

        for i in model.I:
            for j in model.J:
                if pyo.value(model.X[i, j]) > 0.5:
                    print(f"demand {i} → facility {j}")

    else:
        print("Solver status:", results.solver.termination_condition)