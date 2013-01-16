import pylab, numpy as np, CoolProp.CoolProp as cp
from scipy.interpolate import interp1d
import pylab

#Turn off lookup for sure
cp.UseSaturationLUT(0) 


def InlineLabel(xv,yv,x = None, y= None, axis = None, fig = None):
    """
    This will give the coordinates and rotation required to align a label with
    a line on a plot
    """
    
    def ToPixelCoords(xv,yv,axis,fig):
        [Axmin,Axmax]=axis.get_xlim()
        [Aymin,Aymax]=axis.get_ylim()
        DELTAX_axis=Axmax-Axmin
        DELTAY_axis=Aymax-Aymin
        
        width=fig.get_figwidth()
        height=fig.get_figheight()
        pos=axis.get_position().get_points()
        [[Fxmin,Fymin],[Fxmax,Fymax]]=pos
        DELTAX_fig=width*(Fxmax-Fxmin)
        DELTAY_fig=height*(Fymax-Fymin)
        
        #Convert coords to pixels
        x=(xv-Axmin)/DELTAX_axis*DELTAX_fig+Fxmin
        y=(yv-Aymin)/DELTAY_axis*DELTAY_fig+Fymin
        
        return x,y
    
    def ToDataCoords(xv,yv,axis,fig):
        [Axmin,Axmax]=axis.get_xlim()
        [Aymin,Aymax]=axis.get_ylim()
        DELTAX_axis=Axmax-Axmin
        DELTAY_axis=Aymax-Aymin
        
        width=fig.get_figwidth()
        height=fig.get_figheight()
        pos=axis.get_position().get_points()
        [[Fxmin,Fymin],[Fxmax,Fymax]]=pos
        DELTAX_fig=(Fxmax-Fxmin)*width
        DELTAY_fig=(Fymax-Fymin)*height
        
        #Convert back to measurements
        x=(xv-Fxmin)/DELTAX_fig*DELTAX_axis+Axmin
        y=(yv-Fymin)/DELTAY_fig*DELTAY_axis+Aymin
        
        return x,y
    
    if axis is None:
        axis=pylab.gca()
    
    if fig is None:
        fig=pylab.gcf()
    
    
    
    if y is None and x is not None:
        trash=0
        (xv,yv)=ToPixelCoords(xv,yv,axis,fig)
        #x is provided but y isn't
        (x,trash)=ToPixelCoords(x,trash,axis,fig)
    
        #Get the rotation angle
        f = interp1d(xv, yv)
        y = f(x)
        h = 0.001*x
        dy_dx = (f(x+h)-f(x-h))/(2*h)
        rot = np.arctan(dy_dx)/np.pi*180.
        
    elif x is None and y is not None:
        #y is provided, but x isn't
        
        _xv = xv[::-1]
        _yv = yv[::-1]
        #Find x by interpolation
        x = interp1d(yv, xv)(y)
        trash=0
        (xv,yv)=ToPixelCoords(xv,yv,axis,fig)
        (x,trash)=ToPixelCoords(x,trash,axis,fig)
        
        f = interp1d(xv, yv)
        y = f(x)
        h = 0.001*x
        dy_dx = (f(x+h)-f(x-h))/(2*h)
        rot = np.arctan(dy_dx)/np.pi*180.
        
    (x,y)=ToDataCoords(x,y,axis,fig)
    return (x,y,rot)

def show():
    """
    A convenience function to call pylab.show()
    """
    pylab.show()
    
def Ts(Ref,Tmin = None, Tmax = None, show=False, axis=None, **kwargs):
    """
    Make a temperature- entropy plot for the given fluid
    
    Will plot in the current axis unless the optional parameter *axis* gives the name for the axis to use
    """

    ax = axis if axis is not None else pylab.gca()
    if Tmin is None:
        Tmin = cp.Props(Ref,'Tmin')
    if Tmax is None:
        Tmax = cp.Props(Ref,'Tcrit')-1e-10
        
    if Tmin > cp.Props(Ref,'Tcrit'):
        raise ValueError('Tmin cannot be greater than fluid critical temperature')
    if Tmax > cp.Props(Ref,'Tcrit'):
        raise ValueError('Tmax cannot be greater than fluid critical temperature')
    Tmin = max(Tmin, cp.Props(Ref,'Tmin')+0.01)
    Tmax = min(Tmax, cp.Props(Ref,'Tcrit')-1e-10)
    Tsat = np.linspace(Tmin,Tmax,1000)
    (ssatL,ssatV)=(0.0*Tsat,0.0*Tsat)
    for i in range(len(Tsat)):
        ssatL[i] = cp.Props('S','T',Tsat[i],'Q',0,Ref)
        ssatV[i] = cp.Props('S','T',Tsat[i],'Q',1,Ref)
        
    ax.plot(ssatL,Tsat,'k')
    ax.plot(ssatV,Tsat,'k')
    ax.plot(np.r_[ssatL[-1],ssatV[-1]],np.r_[Tsat[-1],Tsat[-1]],'k')

    ax.set_xlabel('Entropy [kJ/kg$\cdot$K]')
    ax.set_ylabel('Temperature [K]')
    ax.autoscale(enable=True)
    if show:
        pylab.show()

def Ph(Ref, Tmin=None, Tmax = None, show = False, axis=None, **kwargs):
    
    """
    Make a pressure-enthalpy plot for the given fluid
    
    Will plot in the current axis unless the optional parameter *axis* gives the name for the axis to use
    """
    
    ax = axis if axis is not None else pylab.gca()
    if Tmin is None:
        Tmin = cp.Props(Ref,'Tmin')
    if Tmax is None:
        Tmax = cp.Props(Ref,'Tcrit')-1e-10
        
    if Tmin > cp.Props(Ref,'Tcrit'):
        raise ValueError('Tmin cannot be greater than fluid critical temperature')
    if Tmax > cp.Props(Ref,'Tcrit'):
        raise ValueError('Tmax cannot be greater than fluid critical temperature')
    Tmin = max(Tmin, cp.Props(Ref,'Tmin')+0.01)
    Tmax = min(Tmax, cp.Props(Ref,'Tcrit')-1e-10)
    
    Tsat = np.linspace(Tmin,Tmax,1000)
    (hsatL,psatL,hsatV,psatV)=(0.0*Tsat,0.0*Tsat,0.0*Tsat,0.0*Tsat)
    for i in range(len(Tsat)):
        hsatL[i] = cp.Props('H','T',Tsat[i],'Q',0,Ref)
        hsatV[i] = cp.Props('H','T',Tsat[i],'Q',1,Ref)
        psatL[i] = cp.Props('P','T',Tsat[i],'Q',0,Ref)
        psatV[i] = cp.Props('P','T',Tsat[i],'Q',1,Ref)

    ax.plot(hsatL,psatL,'k')
    ax.plot(hsatV,psatV,'k')
    ax.plot(np.r_[hsatL[-1],hsatV[-1]],np.r_[psatL[-1],psatV[-1]],'k')
    
    ax.set_xlabel('Enthalpy [kJ/kg]')
    ax.set_ylabel('Pressure [kPa]')
    ax.autoscale(enable=True)
    if show:
        pylab.show()
    
def Ps(Ref, Tmin=None, Tmax = None, show = False, axis = None, **kwargs):
    
    """
    Make a pressure-entropy plot for the given fluid
    
    Will plot in the current axis unless the optional parameter *axis* gives the name for the axis to use
    """
    ax = axis if axis is not None else pylab.gca()
    if Tmin is None:
        Tmin = cp.Props(Ref,'Tmin')
    if Tmax is None:
        Tmax = cp.Props(Ref,'Tcrit')-1e-10
        
    if Tmin > cp.Props(Ref,'Tcrit'):
        raise ValueError('Tmin cannot be greater than fluid critical temperature')
    if Tmax > cp.Props(Ref,'Tcrit'):
        raise ValueError('Tmax cannot be greater than fluid critical temperature')
        
    Tmin = max(Tmin, cp.Props(Ref,'Tmin')+0.01)
    Tmax = min(Tmax, cp.Props(Ref,'Tcrit')-1e-10)
    
    Tsat = np.linspace(Tmin,Tmax,1000)
    (ssatL,psatL,ssatV,psatV)=(0.0*Tsat,0.0*Tsat,0.0*Tsat,0.0*Tsat)
    for i in range(len(Tsat)):
        ssatL[i] = cp.Props('S','T',Tsat[i],'Q',0,Ref)
        ssatV[i] = cp.Props('S','T',Tsat[i],'Q',1,Ref)
        psatL[i] = cp.Props('P','T',Tsat[i],'Q',0,Ref)
        psatV[i] = cp.Props('P','T',Tsat[i],'Q',1,Ref)

    ax.plot(ssatL,psatL,'k')
    ax.plot(ssatV,psatV,'k')
    ax.plot(np.r_[ssatL[-1],ssatV[-1]],np.r_[psatL[-1],psatV[-1]],'k')
    
    ax.set_xlabel('Entropy [kJ/kg/K]')
    ax.set_ylabel('Pressure [kPa]')
    ax.autoscale(enable=True)
    if show:
        pylab.show()
        
def Prho(Ref, Tmin=None, Tmax = None, show = False, axis = None, **kwargs):
    
    """
    Make a pressure-density plot for the given fluid
    
    Will plot in the current axis unless the optional parameter *axis* gives the name for the axis to use
    """
    ax = axis if axis is not None else pylab.gca()
    if Tmin is None:
        Tmin = cp.Props(Ref,'Tmin')
    if Tmax is None:
        Tmax = cp.Props(Ref,'Tcrit')-1e-5
        
    if Tmin > cp.Props(Ref,'Tcrit'):
        raise ValueError('Tmin cannot be greater than fluid critical temperature')
    if Tmax > cp.Props(Ref,'Tcrit'):
        raise ValueError('Tmax cannot be greater than fluid critical temperature')
    Tmin = max(Tmin, cp.Props(Ref,'Tmin')+0.01)
    Tmax = min(Tmax, cp.Props(Ref,'Tcrit')-1e-5)
    
    Tsat = np.linspace(Tmin,Tmax,1000)
    (rhosatL,psatL,rhosatV,psatV)=(0.0*Tsat,0.0*Tsat,0.0*Tsat,0.0*Tsat)
    for i in range(len(Tsat)):
        rhosatL[i] = cp.Props('D','T',Tsat[i],'Q',0,Ref)
        rhosatV[i] = cp.Props('D','T',Tsat[i],'Q',1,Ref)
        psatL[i] = cp.Props('P','T',Tsat[i],'Q',0,Ref)
        psatV[i] = cp.Props('P','T',Tsat[i],'Q',1,Ref)

    ax.plot(rhosatL,psatL,'k')
    ax.plot(rhosatV,psatV,'k')
    ax.plot(np.r_[rhosatL[-1],rhosatV[-1]],np.r_[psatL[-1],psatV[-1]],'k')
    
    ax.set_xlabel('Density [kg/m$^3$]')
    ax.set_ylabel('Pressure [kPa]')
    ax.autoscale(enable=True)
    if show:
        pylab.show()
        
def Trho(Ref, Tmin=None, Tmax = None, show = False, axis = None, **kwargs):
    
    """
    Make a Temperature-density plot for the given fluid
    
    Will plot in the current axis unless the optional parameter *axis* gives the name for the axis to use
    """
    ax = axis if axis is not None else pylab.gca()
    if Tmin is None:
        Tmin = cp.Props(Ref,'Tmin')
    if Tmax is None:
        Tmax = cp.Props(Ref,'Tcrit')-1e-5
        
    if Tmin > cp.Props(Ref,'Tcrit'):
        raise ValueError('Tmin cannot be greater than fluid critical temperature')
    if Tmax > cp.Props(Ref,'Tcrit'):
        raise ValueError('Tmax cannot be greater than fluid critical temperature')
    Tmin = max(Tmin, cp.Props(Ref,'Tmin')+0.01)
    Tmax = min(Tmax, cp.Props(Ref,'Tcrit')-1e-5)
    
    Tsat = np.linspace(Tmin,Tmax,1000)
    (rhosatL,rhosatV)=(0.0*Tsat,0.0*Tsat)
    for i in range(len(Tsat)):
        rhosatL[i] = cp.Props('D','T',Tsat[i],'Q',0,Ref)
        rhosatV[i] = cp.Props('D','T',Tsat[i],'Q',1,Ref)

    ax.plot(rhosatL,Tsat,'k')
    ax.plot(rhosatV,Tsat,'k')
    ax.plot(np.r_[rhosatL[-1],rhosatV[-1]],np.r_[Tsat[-1],Tsat[-1]],'k')
    
    ax.set_xlabel('Density [kg/m$^3$]')
    ax.set_ylabel('Temperature [K]')
    ax.autoscale(enable=True)
    if show:
        pylab.show()
        
if __name__=='__main__':
    Trho('R245fa', show = True)
    Prho('R245fa', show = True)
    Ps('R290', show = True)
    Ps('R290', show = True)
    Ph('R290', show = True)
    Ts('R290', show = True)
