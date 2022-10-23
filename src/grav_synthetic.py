'''
grav_synthetic.py
This script will perform the ABC workflow on a synthetic 1D gravity anomaly.
We will look at a dense, dipping, dyke like body.

The SimPEG workflow presented here is based largely on the example gravity
forward model code in the docs, found here:
https://docs.simpeg.xyz/content/tutorials/03-gravity/plot_1a_gravity_anomaly.html

@author Harrison Button / ignorant-fool
'''

# Imports
import numpy as np
from scipy.interpolate import LinearNDInterpolator
import matplotlib as mpl
import matplotlib.pyplot as plt

from discretize import TensorMesh
from discretize.utils import mkvc

from SimPEG.utils import model_builder, surface2ind_topo
from SimPEG import maps
from SimPEG.potential_fields import gravity

# define the topography
[x_topo, y_topo] = np.meshgrid(
    np.linspace(-200, 200, 41),
    np.linspace(-200, 200, 41))
z_topo = -15 * np.exp(-(x_topo ** 2 + y_topo ** 2) / 80 ** 2)
x_topo, y_topo, z_topo = mkvc(x_topo), mkvc(y_topo), mkvc(z_topo)
topo_xyz = np.c_[x_topo, y_topo, z_topo]

# Define the survey
# Define the observation locations as an (N, 3) numpy array or load them.
# Note that we are only running a single 1D line for the survey.
x = np.linspace(-80.0, 80.0, 17)
y = np.linspace(0, 0, 1)
x, y = np.meshgrid(x, y)
x, y = mkvc(x.T), mkvc(y.T)
fun_interp = LinearNDInterpolator(np.c_[x_topo, y_topo], z_topo)
z = fun_interp(np.c_[x, y]) + 5.0
receiver_locations = np.c_[x, y, z]
# Define the component(s) of the field we want to simulate as strings within
# a list. Here we simulate only the vertical component of gravity anomaly.
components = ["gz"]
# Use the observation locations and components to define the receivers. To
# simulate data, the receivers must be defined as a list.
receiver_list = gravity.receivers.Point(
    receiver_locations,
    components=components)
receiver_list = [receiver_list]
# Defining the source field.
source_field = gravity.sources.SourceField(receiver_list=receiver_list)
# Defining the survey
survey = gravity.survey.Survey(source_field)

# define the tensor mesh
dh = 5.0
hx = [(dh, 5, -1.3), (dh, 40), (dh, 5, 1.3)]
hy = [(dh, 5, -1.3), (dh, 40), (dh, 5, 1.3)]
hz = [(dh, 5, -1.3), (dh, 15)]
mesh = TensorMesh([hx, hy, hz], "CCN")

# Define density contrast values for each unit in g/cc
background_density = 0.0
block_density = -0.2
sphere_density = 0.2

# Find the indices for the active mesh cells (e.g. cells below surface)
ind_active = surface2ind_topo(mesh, topo_xyz)

# Define mapping from model to active cells. The model consists of a value for
# each cell below the Earth's surface.
nC = int(ind_active.sum())
model_map = maps.IdentityMap(nP=nC)

# Define model. Models in SimPEG are vector arrays.
model = background_density * np.ones(nC)

# You could find the indices of specific cells within the model and
# change their value to add structures.
ind_block = (
    (mesh.gridCC[ind_active, 0] > -50.0)
    & (mesh.gridCC[ind_active, 0] < -20.0)
    & (mesh.gridCC[ind_active, 1] > -15.0)
    & (mesh.gridCC[ind_active, 1] < 15.0)
    & (mesh.gridCC[ind_active, 2] > -50.0)
    & (mesh.gridCC[ind_active, 2] < -30.0)
)
model[ind_block] = block_density

# You can also use SimPEG utilities to add structures to
# the model more concisely
ind_sphere = model_builder.getIndicesSphere(
    np.r_[35.0, 0.0, -40.0], 15.0, mesh.gridCC)
ind_sphere = ind_sphere[ind_active]
model[ind_sphere] = sphere_density

# Plot Density Contrast Model
fig = plt.figure(figsize=(9, 4))
plotting_map = maps.InjectActiveCells(mesh, ind_active, np.nan)

ax1 = fig.add_axes([0.1, 0.12, 0.73, 0.78])
mesh.plotSlice(
    plotting_map * model,
    normal="Y",
    ax=ax1,
    ind=int(mesh.nCy / 2),
    grid=True,
    clim=(np.min(model), np.max(model)),
    pcolorOpts={"cmap": "viridis"},
)
ax1.set_title("Model slice at y = 0 m")
ax1.set_xlabel("x (m)")
ax1.set_ylabel("z (m)")

ax2 = fig.add_axes([0.85, 0.12, 0.05, 0.78])
norm = mpl.colors.Normalize(vmin=np.min(model), vmax=np.max(model))
cbar = mpl.colorbar.ColorbarBase(
    ax2, norm=norm, orientation="vertical", cmap=mpl.cm.viridis
)
cbar.set_label("$g/cm^3$", rotation=270, labelpad=15, size=12)

plt.show()

# Define the forward simulation. By setting the 'store_sensitivities' keyword
# argument to "forward_only", we simulate the data without storing the
# sensitivities
simulation = gravity.simulation.Simulation3DIntegral(
    survey=survey,
    mesh=mesh,
    rhoMap=model_map,
    actInd=ind_active,
    store_sensitivities="forward_only",
)

# Compute predicted data for some model
# SimPEG uses right handed coordinate where Z is positive upward.
# This causes gravity signals look "inconsistent" with density
# values in visualization.
dpred = simulation.dpred(model)

# need to add a 1D plot of the profile data here

save_output = False
if save_output:
    # have to re-jig this stuff
    out_path = "../data/"

    fname = out_path + "gravity_topo.txt"
    np.savetxt(fname, np.c_[topo_xyz], fmt="%.4e")

    np.random.seed(737)
    maximum_anomaly = np.max(np.abs(dpred))
    noise = 0.01 * maximum_anomaly * np.random.rand(len(dpred))
    fname = out_path + "gravity_data.obs"
    np.savetxt(fname, np.c_[receiver_locations, dpred + noise], fmt="%.4e")
