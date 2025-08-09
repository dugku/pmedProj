from scipy.stats import gaussian_kde
import numpy as np
from dataclasses import dataclass

def KDE_data(player_kill):
    """Calculate the KDE for the player kill data."""
    if player_kill.size == 0:
        return np.array([])

    kde = gaussian_kde(player_kill.T, bw_method=0.25)
    xmin, xmax = player_kill[:, 0].min(), player_kill[:, 0].max()
    ymin, ymax = player_kill[:, 1].min(), player_kill[:, 1].max()

    x_grid = np.linspace(xmin, xmax, 50)
    y_grid = np.linspace(ymin, ymax, 50)
    X, Y = np.mgrid[0:1024:300j, 0:1024:300j]
    positions = np.vstack([X.ravel(), Y.ravel()])
    
    Z = np.reshape(kde(positions).T, X.shape)

    return X, Y, Z