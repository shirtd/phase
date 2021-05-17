import numpy as np
import numpy.linalg as la

def tet_circumcenter(T):
    alpha = np.array([[a[0], a[1], a[2], 1] for a in T])
    Dx = np.array([[a[0]*a[0] + a[1]*a[1] + a[2]*a[2], a[1], a[2], 1] for a in T])
    Dy = np.array([[a[0]*a[0] + a[1]*a[1] + a[2]*a[2], a[0], a[2], 1] for a in T])
    Dz = np.array([[a[0]*a[0] + a[1]*a[1] + a[2]*a[2], a[0], a[1], 1] for a in T])
    return np.array([la.det(Dx), -1*la.det(Dy), la.det(Dz)]) / (2 * la.det(alpha))

# def circumcenter(t):
#     t = t.T
#     f = np.array([( t[0,1] - t[0,0] ) ** 2 + ( t[1,1] - t[1,0] ) ** 2,
#             ( t[0,2] - t[0,0] ) ** 2 + ( t[1,2] - t[1,0] ) ** 2])
#     top = np.array([( t[1,2] - t[1,0] ) * f[0] - ( t[1,1] - t[1,0] ) * f[1],
#                 - ( t[0,2] - t[0,0] ) * f[0] + ( t[0,1] - t[0,0] ) * f[1]])
#     det  = (t[1,2]-t[1,0] ) * (t[0,1]-t[0,0]) - (t[1,1]-t[1,0]) * (t[0,2]-t[0,0])
#     if det == 0: return None
#     return np.array([t[0,0] + 0.5 * top[0] / det, t[1,0] + 0.5 * top[1] / det])


def torus(r1=0.5, r2=1, n=64):
    r1, r2 = 0.5, 1
    phi, theta = np.linspace(-np.pi, np.pi, n), np.linspace(-np.pi, np.pi, n)
    x = (r1 * np.cos(phi) + r2) * np.cos(theta)
    y = (r1 * np.cos(phi) + r2) * np.sin(theta)
    z = r1 * np.sin(phi)
    return np.vstack((x,y,z)).T

def ripple(x, y, f=1, l=1, w=1):
    t = la.norm(np.stack((x, y), axis=2), axis=2) + 1/12
    t[t > 1] = 1.
    return (1 - t) - np.exp(-t / l) * np.cos(2*np.pi*f*(1-t) * np.sin(2*np.pi*w*t))
