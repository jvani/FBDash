import os
import folium
import argparse
import numpy as np
import pandas as pd
import datetime as dt
from bs4 import BeautifulSoup


def parse_args():
    """Parse arguments.
    Returns:
        args - argparse object.
    """

    parser = argparse.ArgumentParser(description="Facebook data.")
    parser.add_argument("--path", dest="path", help="Path to data folder.")
    parser.add_argument("--output", dest="output", help="Path to save outputs.")
    args = parser.parse_args()

    return args


class fbdata(object):
    def __init__(self, path, output):
        """Container for Facebook data.
        Args:
            path (str) - Path to data folder.
            output (str) - Path to save outputs.
        """

        self.path = path
        self.coords = self.estimated_locations()
        self.output = self.output_folder(output)


    def estimated_locations(self):
        """Find estimated locations in security.htm. Return coordinate tuples
        and date created for plotting.

        Returns:
            coords (list) - list of lat/lon coordinate pairs and dates.
        """

        # -- Read security.html
        with open(os.path.join(self.path, "html", "security.htm"), "r") as ff:
            security_soup = BeautifulSoup("".join(ff.readlines()))

        # -- Pull all list items.
        list_items = [li.text for li in security_soup.find_all("li")]

        # -- Filter for Estimated location items.
        coords = filter(lambda x: x.startswith("Estimated"), list_items)

        # -- Strip and split strings.
        lstrip_str = "Estimated location inferred from IP: "
        coords = [tt.lstrip(lstrip_str) for tt in coords]
        coords = [tt.split("Created") for tt in coords]

        # -- Pull coordinate pairs from strings.
        cc = [[float(coord) for coord in ii[0].split(", ")] for ii in coords]

        # -- Pull dates created from strings.
        dd = [dt.datetime.strptime(ii[1].split(" at ")[0][2:], "%A, %B %d, %Y")
              for ii in coords]

        # -- Zip coordinates with dates (e.g., [[lat, lon], timestamp]).
        self.coords = zip(cc, dd)

        return self.coords


    def output_folder(self, output):
        """Check if given output folder exists, if not create the folder.
        Args:
            output (str) - Folder to save outputs.
        """

        if not os.path.exists(output):
            os.makedirs(output)

        return output


    def plot_estimated_locations(self, output):
        """Creates a folium map of estimated locations.
        Args:
            output (str) - Folder to save outputs.
        """

        df =  pd.DataFrame([[ii[0][0], ii[0][1], ii[1]]for ii in self.coords],
                             columns=["lat", "lon", "dd"]).set_index("dd")
        df.to_csv(os.path.join(output, "coords.csv"))

        m = folium.Map(
            location=[(df.lat.min() + df.lat.max()) / 2,
                      (df.lon.min() + df.lon.max()) / 2],
            zoom_start=4,
            tiles="cartodbpositron"
        )

        for coord in self.coords:
            folium.Marker(coord[0], popup=coord[1].strftime("%D")).add_to(m)

        m.save(os.path.join(output, "estimated_locations.html"))


if __name__ == "__main__":

    args = parse_args()
    fb = fbdata(args.path, args.output)
    fb.plot_estimated_locations(args.output)
