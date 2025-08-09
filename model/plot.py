import matplotlib.pyplot as plt
import numpy as np
from dataclasses import dataclass
from shapely.plotting import plot_points, plot_polygon
@dataclass
class Plotter:
    """Will take a numpy array with the first column as x and the second as y."""
    data_player: np.ndarray
    X: np.ndarray
    Y: np.ndarray
    Z: np.ndarray
    img: str = "img_files/de_mirage_radar_psd.png"

    def plot_playerDat(self):
      img = "img_files/de_mirage_radar_psd.png"
      """Need to flip the y-axis to match the coordinate system."""
      dis_imnage = plt.imread(img)
      w,h = dis_imnage.shape[1], dis_imnage.shape[0]
      fig, ax = plt.subplots(figsize=(10, 6))
      ax.imshow(dis_imnage, extent=[0, w, 0, h], aspect='auto')
      x_coords = self.data_player[:, 0]
      y_coords = h - self.data_player[:, 1]

      ax.scatter(x_coords, y_coords, alpha=0.5)
      plt.savefig("plot.png")
      plt.close(fig)

    def plot_kde(self):
        """Plot the KDE data."""
        dis_im = plt.imread(self.img)
        h, w = dis_im.shape[:2]

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.imshow(dis_im, extent=[0, w, 0, h])
        ax.contourf(self.X, h - self.Y, self.Z, levels=50, cmap='Reds', alpha=0.7)
        ax.scatter(self.data_player[:, 0], h - self.data_player[:, 1], color='red', s=10, alpha=0.25)
        plt.savefig("kde_plot.png")  
        plt.close(fig)  

    def plot_playable(self, polygon):
      print("Here")
      fig, ax = plt.subplots()

      plot_polygon(polygon, ax=ax, add_points=False, color='purple')

      # Set equal aspect ratio
      ax.set_aspect('equal')

      # Display the plot
      ax.invert_yaxis()
      plt.savefig("playable.png")  
      plt.close(fig)  

    def plot_canidate(self, candidate_points):
      """inpit is a numpy array with the first column as x and the second as y."""
      fig, ax = plt.subplots()

      ax.scatter(candidate_points[:, 0], candidate_points[:, 1], color='blue', s=3, alpha=0.5)

        # Set equal aspect ratio
      ax.set_aspect('equal')

        # Display the plot
      ax.invert_yaxis()
      plt.savefig("candidate_points.png")  
      plt.close(fig)

    def plot_demand(self, demand_points):
      """inpit is a numpy array with the first column as x and the second as y."""
      fig, ax = plt.subplots()

      ax.scatter(demand_points[:, 0], demand_points[:, 1], color='green', s=3, alpha=0.5)

        # Set equal aspect ratio
      ax.set_aspect('equal')

        # Display the plot
      ax.invert_yaxis()
      plt.savefig("demand_points.png")  
      plt.close(fig)

    def plot_facilities(self, open_fac):
      fig, ax = plt.subplots()
      tImg = plt.imread(self.img)
      h,w = tImg.shape[:2]

      ax.imshow(tImg, extent=[0, w, 0, h])

      x_coords = [x[0] for x in open_fac]
      y_coords = [h - y[1] for y in open_fac]
      ax.scatter(x_coords, y_coords, color="red", s=5)
    
      plt.savefig("open4.png")
      plt.close()
