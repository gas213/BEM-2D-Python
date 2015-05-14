import numpy as np
       
    # x,z components of each panel's tangential and normal vectors
def panel_vectors(x,z):
    lpanel = np.sqrt((x[1:]-x[:-1])**2 + (z[1:]-z[:-1])**2)
    tx = (x[1:]-x[:-1])/lpanel
    tz = (z[1:]-z[:-1])/lpanel
    nx = -tz
    nz = tx
    return (tx,tz,nx,nz,lpanel)
    
    # x,z components of each midpoint's/collocation point's tangential and normal vectors
def point_vectors(xdp,xdm,zdp,zdm):
    tx = (xdp-xdm)/np.sqrt((xdp-xdm)**2 + (zdp-zdm)**2)
    tz = (zdp-zdm)/np.sqrt((xdp-xdm)**2 + (zdp-zdm)**2)
    nx = -tz
    nz = tx
    return(tx,tz,nx,nz)
    
def archive(array, axis=0):
    """
    Shifts array values along an axis (row-wise by default).
    
    Used for arrays that keep past values for differencing with respect to time.
    
    Args:
        array: The array that will be manipulated.
        axis: The axis to shift values along (0==row-wise, 1==column-wise).
    """
    if axis == 0:
        array[1:,:] = array[:-1,:]
    elif axis == 1:
        array[:,1:] = array[:,:-1]
        
# Velocity and velocity potential equations are defined in panel coordinates so a transformation should be done
# Each row of xp1/xp2/zp is an influence, and each column is a target
# NI is N influences, NT is N targets
# xi/zi is x/z of influences, xt/zt is x/z of target points
def transformation(xt,zt,xi,zi):
# Returns xp1, xp2, zp
# Others: NT, NI, tx, tz, nx, nz, dummy, x_tile, z_tile, tx_tile, tz_tile
    
    NT = np.size(xt)
    NI = np.size(xi)-1
    
    (tx,tz,nx,nz) = panel_vectors(xi,zi)[:-1]
    
    # Intermediary variables to reduce number of tile/repeat operations
    # From normalvectors: tx==nz, tz==-nx
    x_tile = np.repeat(xt[:,np.newaxis].T,NI,0) - np.repeat(xi[:-1,np.newaxis],NT,1)
    z_tile = np.repeat(zt[:,np.newaxis].T,NI,0) - np.repeat(zi[:-1,np.newaxis],NT,1)
    tx_tile = np.repeat(tx[:,np.newaxis],NT,1)
    tz_tile = np.repeat(tz[:,np.newaxis],NT,1)
    
    # Transforming left side collocation points from global to local coordinates
    xp1 = x_tile*tx_tile + z_tile*tz_tile
    zp = x_tile*(-tz_tile) + z_tile*tx_tile
    
    # Transforming right side panel points into local coordinate system
    dummy = (xi[1:]-xi[:-1])*tx + (zi[1:]-zi[:-1])*tz
    xp2 = xp1 - np.repeat(dummy[:,np.newaxis],NT,1)
    
    return(xp1,xp2,zp)
    
def absoluteToBody(Body, Solid, t, TSTEP):
    """Transforms absolute reference frame to body reference frame"""
    theta = Body.MP.THETA_MAX * np.sin(2 * np.pi * Body.MP.F * (t + TSTEP) + Body.MP.PHI)
    
    Body.BF.x = (Body.AF.x - Body.AF.x_le) * np.cos(-1*theta) - (Body.AF.z - Body.AF.z_le) * np.sin(-1*theta)
    Body.BF.z = (Body.AF.z - Body.AF.z_le) * np.cos(-1*theta) + (Body.AF.x - Body.AF.x_le) * np.sin(-1*theta)
    
    Solid.nodesNew[:,0] = (Solid.nodes[:,0] - Body.AF.x_le) * np.cos(-1*theta) - (Solid.nodes[:,1] - Body.AF.z_le) * np.sin(-1*theta)
    Solid.nodesNew[:,1] = (Solid.nodes[:,1] - Body.AF.z_le) * np.cos(-1*theta) + (Solid.nodes[:,0] - Body.AF.x_le) * np.sin(-1*theta)