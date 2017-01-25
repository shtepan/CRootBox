import math
import numpy as np
from scipy import sparse

from numpy.linalg.linalg import norm

#
# Creates the linear system describing the pressure inside a xylem network
#
# in:
# seg     numpy array (Ns,2) of segment indices [1]
# nodes   numpy array (N,3) of the node coordinates [L]
# radius  segment radii [L]
# kr      radial conductivity for each segment [L2 T M−1]
# kz      axial conductivity for each segment [L5 T]
# rho     density of soil water [M L-3]
# g       gravitational acceleration [L T−2]
# soil_p  lambda funciton returning the soil matric potential at a given location, p=soil_p(x,y,z) [M L−1 T−2]
#
# out: 
# Q,b     The equations are represented by the linear system Qx=b
# 
def xylem_flux_ls(seg, nodes, radius, kr, kz, rho, g, soil_p):
        
    Ns = seg.shape[0]
    N = nodes.shape[0]
    
    I = np.zeros(4*Ns)
    J = np.zeros(4*Ns)    
    V = np.zeros(4*Ns)
    b = np.zeros(N)
    
    k = 0     

    for c in range(0,Ns):
        
        i = seg[c,0]
        j = seg[c,1]
        
        n1 = nodes[i,:]
        n2 = nodes[j,:]
        mid = 0.5*(n1+n2)
        
        p_s = soil_p(mid[0],mid[1],mid[2]) # evaluate soil matric potential

        v = n2-n1
        l = norm(v)        
        v = v / l # normed direction        
        a = radius[c]
        
        cii = a*math.pi*l*kr[c] + kz[c]/l # Eqn 10
        cij = a*math.pi*l*kr[c] - kz[c]/l # Eqn 11
        bi = 2.*a*math.pi*l*kr[c]*p_s # firstterm of Eqn 12 & 13            
        
        # edge ij
        b[i] +=  (bi + kz[c]*rho*g*v[2])  # Eqn 12        
        
        I[k] = i
        J[k] = i     
        V[k] += cii
        k += 1                
        
        I[k] = i
        J[k] = j        
        V[k] += cij
        k += 1 
        
        # edge ji
        i,j = j, i
        
        b[i] += (bi - kz[c]*rho*g*v[2]) # Eqn 13

        I[k] = i
        J[k] = i  
        V[k] += cii    
        k += 1                
        
        I[k] = i
        J[k] = j        
        V[k] += cij
        
        k += 1 
        
    Q = sparse.coo_matrix((V,(I,J)))
    Q = sparse.csr_matrix(Q) # Sparse row matrix seems the most reasonable to solve Qx = b iteratively
    
    return (Q, b)

#
# Modifies the linear system to describe Diriclet BC at the node indices n0
#
# in: 
#
#
# out:
# Q, b    the updated linear system
#
def xylem_flux_bc_dirichlet(Q, b, n0, d):
    c = 0
    for c in range(0, len(n0)):
        i = n0[c]      
        # print("Dirichlet BC at node "+str(i)) 
        e0 = np.zeros((1,Q.shape[1])) # build zero vector
        Q[i,:] = sparse.csr_matrix(e0) # replace row i with ei
        Q[i,i] = 1
        b[i] = d[c]    
        c += 1

    return Q, b 



