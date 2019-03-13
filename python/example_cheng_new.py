#
# Example Exudation
#
# 1) Opens plant and root parameters from a file
# 2) Simulates root growth
# 3) Outputs a VTP (for vizualisation in ParaView)
#
#  Computes analytical solution of moving point/line sources based on Carslaw and Jaeger
#

import py_rootbox as rb
# from pyevtk.hl import gridToVTK
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import ticker
import matplotlib.colors as colors


def v2a(vd):  # rb.std_vector_double_ to numpy array
    l = np.zeros(len(vd))
    for i in range(0, len(vd)):
        l[i] = vd[i]
    return l


rootsystem = rb.RootSystem()
name = "Anagallis_straight_simple"

#
# Open plant and root parameter from a file
#
rootsystem.openFile(name)

for i in range(0, 10):
    p = rootsystem.getRootTypeParameter(i + 1)
    p.gf = 2  # linear growth function

#
# Initialize
#
rootsystem.initialize()

#
# Simulate
#
simtime = 10  # or 20, 40, 60 days
dt = 10  # try other values here
N = round(simtime / dt)  # steps
for i in range(0, int(N)):
    rootsystem.simulate(dt, False);

#
# Export final result (as vtp)
#
rootsystem.write(name + ".vtp")  # use ot_polylines for nicer visualization, ot_segments for animations

params = rb.ExudationParameters()
params.Dt = 2.43e-6*3600*24  # cm2/d
params.Dl = 2.43e-6*3600*24   # cm2/d
params.lambda_ = 2.60e-6*3600*24   # d-1
params.R = 16.7   # -
params.M = 4    # µg/d/tip

nx = 70
ny = 70
nz = 60
width = 7  # cm
depth = 30  # cm

C = rb.getExudateConcentration(rootsystem, params, nx, ny, nz, width, depth, 0)  # 0 = mvp line, 1 = mvp segments
C = v2a(C);  # make a numpy array
C = np.reshape(C, (nx, ny, nz))  # hope that works, it does not :-(, or does it?

X = np.linspace(-width / 2, width / 2, nx)
Y = np.linspace(-width / 2, width / 2, ny)
Z = np.linspace(0, -depth, nz)

X_, Y_, Z_ = np.meshgrid(X, Y, Z, indexing = "ij")  # stupid matlab default

# print(X_.shape)
# print(Y_.shape)
# print(Z_.shape)
num_th = (C > 0).sum()  # number of points for which concentration is larger than threshold
print("volume of concentration above threshold: " + str(num_th * 0.125))  # volume for which concentration is larger than threshold (cm3)
print("this is " + str(num_th * 0.125 / (15 * 15 * 30) * 100) + "% of the overall volume")
# gridToVTK("./Exudates", X, Y, Z, pointData = {"Exudates":C})

fig1 = plt.figure()
ax = plt.axes()
C_ = C[:, int(ny/2), :]
levels = np.logspace(np.log10(np.max(C_)) - 5, np.log10(np.max(C_)), 100)  # -8 -6.3
cs = ax.contourf(X_[:, int(ny/2), :], Z_[:, int(ny/2), :], C_, levels = levels, locator = ticker.LogLocator(), cmap = 'jet')
ax.set_xlabel('x')
ax.set_ylabel('z')
plt.axis('equal')
cbar = fig1.colorbar(cs)

fig2 = plt.figure()
nodes = rootsystem.getNodes()
node_tip = nodes[-10]
idy = (np.abs(Y - node_tip.y)).argmin()  # y-index of soil element closest to the point on the root axis
idz = (np.abs(Z - node_tip.z)).argmin()  # z-index of soil element closest to the point on the root axis
C_ = C[:, idy, idz]  # 1d array
plt.plot(X, C_, 'k-')
plt.xlabel('x')
plt.ylabel('z')

plt.show()