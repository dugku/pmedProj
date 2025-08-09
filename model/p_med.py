import numpy as np
from model.playering_field import is_valid_point
from shapely.geometry import Point
import pyomo.environ as pyo
from pyomo.opt import SolverFactory

def generate_canidate_points(polygon, step_size=15):

    valid_points = np.empty((0, 2), dtype=float)

    """Generate candidate points on a grid."""
    x_coords = np.arange(0, 1024, step_size)
    y_coords = np.arange(0, 1024, step_size)
    candidate_points = np.array(np.meshgrid(x_coords, y_coords)).T.reshape(-1, 2)

    for point in candidate_points:
        if is_valid_point(Point(point), polygon):
            valid_points = np.append(valid_points, [point], axis=0)
    
    return valid_points

def demand_points(polygon, kills):
    d = [tuple(p) for p in kills]

    valid = []
    #This is redundent wtf am I doing
    for i in d:
        if not is_valid_point(Point(i), polygon):
            continue
        
        valid.append(i)

    return valid


def weighted_demand_points(polygon, demand, kde_lay, step_size=15):
    """We need to use the KDE for kill data to weight the demand points."""
    d = {}
    weights = {k: 1.0 for k in kde_lay}

    for point in demand:
        if not is_valid_point(Point(point), polygon):
            print("Here")
            continue

        total_weight = 0.0
        for layer_name, (X, Y, Z) in kde_lay.items():
            # Find nearest KDE cell
            x_idx = np.argmin(np.abs(X[:, 0] - point[0]))
            y_idx = np.argmin(np.abs(Y[0] - point[1]))
            w = Z[x_idx, y_idx] * weights[layer_name]
            total_weight += w

        d[(point[0], point[1])] = total_weight

    return d

def compute_distance(demand, canidate, polygon):
    """
    demand is a {(x,y):val} numpy thingy
    """
    distances = {}
    for coord_i in demand:
        x1, y1 = coord_i
        for coord_j in canidate:
            x2, y2 = coord_j
            dist = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            distances[tuple(coord_i), tuple(coord_j)] = dist
    return distances
  

def compute_phis(kde_lays, can_p):
    flat_layers = {}
    for lay_nam, (X, Y, Z) in kde_lays.items():
        for point in can_p:
            key = tuple(point)
            x_idx = np.argmin(np.abs(X[:, 0] - key[0]))
            y_idx = np.argmin(np.abs(Y[0] - key[1]))

            flat_layers[(lay_nam, key)] = Z[x_idx, y_idx]

    return flat_layers
            
def model_thing(weight_demand, demand,canidate, distances, phis, lam_dat, polygon):
    d = [tuple(p) for p in demand]
    can = [tuple(p) for p in canidate]
    k = ["Kills", "PlHit", "Smoke", "HE", "Inferno", "PlFired"]

    model = pyo.ConcreteModel()

    model.I = pyo.Set(initialize=d, dimen=2)
    model.J = pyo.Set(initialize=can, dimen=2)
    model.K = pyo.Set(initialize=k)

    model.w = pyo.Param(model.I, initialize=weight_demand)
    model.d = pyo.Param(model.I, model.J, initialize=distances)

    model.X = pyo.Var(model.I, model.J, domain=pyo.Binary)
    model.Y = pyo.Var(model.J, domain=pyo.Binary)

    model.phi = pyo.Param(model.K, model.J, initialize=phis)
    model.lambdas = pyo.Param(model.K, initialize=lam_dat)

    model.p = pyo.Param(initialize=5)
    model.d_max = pyo.Param(initialize=250)

    def obj(model):
        first_expr = sum(model.w[i] * model.d[i, j] * model.X[i,j] for i in model.I for j in model.J)
        second_expr = sum(model.lambdas[k] * model.phi[k, j] * model.Y[j] for k in model.K for j in model.J)
        return first_expr + second_expr
    
    model.OBJ = pyo.Objective(rule=obj, sense=pyo.minimize)

    def link_rule(model, ix, iy, jx, jy):
     return model.X[(ix, iy), (jx, jy)] <= model.Y[(jx, jy)]
    model.linkCon = pyo.Constraint(model.I, model.J, rule=link_rule)

    def assignment(model, xi, yi):
        i = (xi, yi)
        return sum(model.X[i,j] for j in model.J) == 1
    model.assignmentCon = pyo.Constraint(model.I, rule=assignment)

    def placement_rule(model):
        return sum(model.Y[j] for j in model.J) == model.p
    model.placementCon = pyo.Constraint(rule=placement_rule)

    def distance_cap(model, xi, yi, xj, yj):
        i = (xi, yi)
        j = (xj , yj)
        return model.d[i,j] * model.X[i,j]  <= model.d_max
    model.distanceCapCon = pyo.Constraint(model.I, model.J, rule=distance_cap)

    opt = SolverFactory("cbc")

    results = opt.solve(model)

    return model, results