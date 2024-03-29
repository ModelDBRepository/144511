from sim import Simulation
import network
import neuron
import progress
from math import ceil


def run(netdef,tosave,modify,procs,thisProc,stims,param,repeats,sim_time,SaveSpikes,SaveVoltage,SaveConductance,SaveCurrent):
    net = netdef()

    if SaveVoltage:
        net.recordVoltage()

    repeats = int(repeats)
    # Randomseed was 200 for most figures
    # Changed to 200 for rat
    # Changed to 200 for anurans
    s = Simulation(net, randomseed=200,delay=25)
    s.verbose = False
    s.sim_time = sim_time
    s.dt = 0.050
    total = len(stims)*len(param)*repeats
    spp = ceil(float(total)/procs)
    start = thisProc*spp
    end = (thisProc+1)*spp
    count = 0
    for a in param: 
        s.set_amplitude(net.sim_amp)
        for d in stims*repeats:
            if count >= start and count < end:
                net = modify(net,a,d)
                progress.update(count-start,spp,thisProc)
                s.stim_dur = d 
                s.run()
                key = [a,d] 
                net.savecells(tosave, key, spikes=SaveSpikes,voltage=SaveVoltage,conductance=SaveConductance,current=SaveCurrent)
            count += 1
    progress.update(spp,spp,thisProc)

    r = [thisProc,net.savedparams,net.savedcells]
    return r

def C_JUST_DNLL(net,a,stim,getparams=False):

    # I used this simulation to figure out the actual input rate of the inhibitory spikes
    # It turns out to be 250 Hz
    if getparams:
        stims = [1000]
        param = [1]
        return [1000,1500,stims,param]

    mult = 1.0

    # modifyAMPA/NMDA scale by total number of receptors so we multiply by 2 since we have 2 inputs
    net.cells["IC"]["cells"][0].sec["soma"].modifyAMPA(gmax=0.004*2*mult)
    net.cells["IC"]["cells"][0].sec["soma"].modifyNMDA(gmax=0.020*2*mult,mg=1.0)
    net.cells["IC"]["cells"][0].sec["soma"].modifyGABAa(gmax=0.0025)

    net.cells["IC"]["cells"][0].sec["soma"](0.5).pas.g = 1.0/4000

    net.cells["MSO_ON"]["delay"] = 10
    net.cells["MSO_OFF"]["delay"] = 6
    net.cells["DNLL"]["delay"] = 0

    net.cells["MSO_ON"]["stim"] = "IClamp"
    net.cells["MSO_ON"]["stimamp"] = 0.1
    net.cells["MSO_OFF"]["stim"] = "IClamp"
    net.cells["MSO_OFF"]["stimamp"] = 0.1

    return net

def C_PAIREDTONE(net,a,stim,getparams=False):
    if getparams:
        stims = [1]
        delay = [i for i in range(0,105,5)]
        param = []
        for i in delay:
            param.append([i])
        return [20,250,stims,param]

    # modifyAMPA/NMDA scale by total number of receptors so we multiply by 2 since we have 2 inputs
    net.cells["IC"]["cells"][0].sec["soma"].modifyAMPA(gmax=0.004*4)
    net.cells["IC"]["cells"][0].sec["soma"].modifyNMDA(gmax=0.020*4,mg=1.0)
    net.cells["IC"]["cells"][0].sec["soma"].modifyGABAa(gmax=0.0025*2)

    net.cells["IC"]["cells"][0].sec["soma"](0.5).pas.g = 1.0/4000

    net.cells["MSO_ON"]["delay"] = 10+a[0]
    net.cells["MSO_OFF"]["delay"] = 6+a[0]
    net.cells["DNLL"]["delay"] = 9+a[0]

    net.cells["MSO_ON2"]["delay"] = 10
    net.cells["MSO_OFF2"]["delay"] = 6
    net.cells["DNLL2"]["delay"] = 9

    net.cells["MSO_ON"]["stim"] = "IClamp"
    net.cells["MSO_ON"]["stimamp"] = 0.1
    net.cells["MSO_OFF"]["stim"] = "IClamp"
    net.cells["MSO_OFF"]["stimamp"] = 0.1

    net.cells["MSO_ON2"]["stim"] = "IClampFixed15"
    net.cells["MSO_ON2"]["stimamp"] = 0.1
    net.cells["MSO_OFF2"]["stim"] = "IClampFixed15"
    net.cells["MSO_OFF2"]["stimamp"] = 0.1

    return net

def C_DEFAULT(net,a,stim,getparams=False):
    if getparams:
        stims = [i for i in range(1,26,1)]
        param = [1]
        return [1,100,stims,param]

    mult = 1.0

    # modifyAMPA/NMDA scale by total number of receptors so we multiply by 2 since we have 2 inputs
    net.cells["IC"]["cells"][0].sec["soma"].modifyAMPA(gmax=0.004*2*mult)
    net.cells["IC"]["cells"][0].sec["soma"].modifyNMDA(gmax=0.020*2*mult,mg=1.0)
    net.cells["IC"]["cells"][0].sec["soma"].modifyGABAa(gmax=0.0025)

    net.cells["IC"]["cells"][0].sec["soma"](0.5).pas.g = 1.0/4000

    net.cells["MSO_ON"]["delay"] = 10
    net.cells["MSO_OFF"]["delay"] = 6
    net.cells["DNLL"]["delay"] = 9

    net.cells["MSO_ON"]["stim"] = "IClamp"
    net.cells["MSO_ON"]["stimamp"] = 0.1
    net.cells["MSO_OFF"]["stim"] = "IClamp"
    net.cells["MSO_OFF"]["stimamp"] = 0.1

    return net

def C_NMDA_BETA(net,a,stim,getparams=False):
    if getparams:
        stims = [i for i in range(1,201,2)]#+[i for i in range(50,100,2)]+[i for i in range(100,251,5)];

        NMDAbeta = [0.00165,0.0033,0.0066,0.0132]
        param = []
        for b in NMDAbeta:
                param.append([a,b])
        return [5,500,stims,param]

    if stim <= 25:
        mult = 0.375*(stim)
        mult = 0.04*stim
        mult = 1
    else:
        mult = 1.0

    # modifyAMPA/NMDA scale by total number of receptors so we multiply by 2 since we have 2 inputs
    net.cells["IC"]["cells"][0].sec["soma"].modifyAMPA(gmax=0.004*2*mult)
    net.cells["IC"]["cells"][0].sec["soma"].modifyNMDA(gmax=(0.020+0.010)*2*mult,Beta=a[0],mg=1.0)
    net.cells["IC"]["cells"][0].sec["soma"].modifyGABAa(gmax=0.0025) # Normally 0.0035

    net.cells["MSO_ON"]["delay"] = 10
    net.cells["MSO_OFF"]["delay"] = 6
    net.cells["DNLL"]["delay"] = 9

    net.cells["MSO_ON"]["stim"] = "IClamp"
    net.cells["MSO_ON"]["stimamp"] = 0.1
    net.cells["MSO_OFF"]["stim"] = "IClamp"
    net.cells["MSO_OFF"]["stimamp"] = 0.1

    return net

def C_TAU(net,a,stim,getparams=False):
    if getparams:
        stims = [i for i in range(1,201,5)]
        tau = [7000,8000,9000,10000]
        #tau = [2000,3000,4000,5000,6000]
        param = []
        for t in tau:
            param.append([t])
        return [20,300,stims,param]

    mult = 1

    # modifyAMPA/NMDA scale by total number of receptors so we multiply by 2 since we have 2 inputs
    net.cells["IC"]["cells"][0].sec["soma"].modifyAMPA(gmax=0.004*2*mult)
    net.cells["IC"]["cells"][0].sec["soma"].modifyNMDA(gmax=0.020*2*mult,Beta=0.0066,mg=1.0)
    net.cells["IC"]["cells"][0].sec["soma"](0.5).pas.g = 1.0/a[0]
    net.cells["IC"]["cells"][0].sec["soma"].modifyGABAa(gmax=0.0025) # Normally 0.0035

    net.cells["MSO_ON"]["delay"] = 10
    net.cells["MSO_OFF"]["delay"] = 6
    net.cells["DNLL"]["delay"] = 9

    net.cells["MSO_ON"]["stim"] = "IClamp"
    net.cells["MSO_ON"]["stimamp"] = 0.1
    net.cells["MSO_OFF"]["stim"] = "IClamp"
    net.cells["MSO_OFF"]["stimamp"] = 0.1

    return net

def C_GABA(net,a,stim,getparams=False):

    if getparams:
        stims = [i for i in range(1,201,5)]#+[i for i in range(50,100,2)]+[i for i in range(100,251,5)];
        stims = [i for i in range(1,26,1)]
        #stims = [i for i in range(1,51,2)]#+[i for i in range(50,100,2)]+[i for i in range(100,251,5)];
        inhg = [0.0,0.001, 0.0015, 0.0025, 0.0035, 0.0045]
        inhg = [0.0]
        param = []
        for i in inhg:
            param.append([i])
        return [20,200,stims,param]

    mult = 1 

    # modifyAMPA/NMDA scale by total number of receptors so we multiply by 2 since we have 2 inputs
    net.cells["IC"]["cells"][0].sec["soma"].modifyAMPA(gmax=0.004*2*mult)
    net.cells["IC"]["cells"][0].sec["soma"].modifyNMDA(gmax=0.020*2*mult,Beta=0.0066,mg=1.0)
    net.cells["IC"]["cells"][0].sec["soma"].modifyGABAa(gmax=a[0]) # Normally 0.0025
    net.cells["IC"]["cells"][0].sec["soma"](0.5).pas.g = 1.0/4000

    net.cells["MSO_ON"]["delay"] = 10 
    net.cells["MSO_OFF"]["delay"] = 6 
    net.cells["DNLL"]["delay"] = 9

    net.cells["MSO_ON"]["stim"] = "IClamp"
    net.cells["MSO_ON"]["stimamp"] = 0.1
    net.cells["MSO_OFF"]["stim"] = "IClamp"
    net.cells["MSO_OFF"]["stimamp"] = 0.1

    return net

def C_NMDA(net,a,stim,getparams=False):

    if getparams:
        stims = [i for i in range(10,201,10)]#+[i for i in range(50,100,2)]+[i for i in range(100,251,5)];
        stims = [i for i in range(1,51,2)]#+[i for i in range(50,100,2)]+[i for i in range(100,251,5)];
        inhg = [0.0,0.005,0.01,0.015,0.02,0.025,0.03,0.035]
        inhg = [0.035, 0.045, 0.55, 0.65, 0.75, 0.85, 0.95, 0.105]
        param = []
        for i in inhg:
            param.append([i])
        return [20,200,stims,param]

    mult = 1 

    # modifyAMPA/NMDA scale by total number of receptors so we multiply by 2 since we have 2 inputs
    net.cells["IC"]["cells"][0].sec["soma"].modifyAMPA(gmax=(0.004+0.002)*2*mult)
    #net.cells["IC"]["cells"][0].sec["soma"].modifyAMPA(gmax=(0.004+0.002)*2*mult) # For NMDA onset test
    net.cells["IC"]["cells"][0].sec["soma"].modifyNMDA(gmax=a[0]*2*mult,Beta=0.0066,mg=1.0)
    net.cells["IC"]["cells"][0].sec["soma"].modifyGABAa(gmax=0.0025) # Normally 0.0035
    net.cells["IC"]["cells"][0].sec["soma"](0.5).pas.g = 1.0/4000

    net.cells["MSO_ON"]["delay"] = 10 
    net.cells["MSO_OFF"]["delay"] = 6 
    net.cells["DNLL"]["delay"] = 9

    net.cells["MSO_ON"]["stim"] = "IClamp"
    net.cells["MSO_ON"]["stimamp"] = 0.1
    net.cells["MSO_OFF"]["stim"] = "IClamp"
    net.cells["MSO_OFF"]["stimamp"] = 0.1

    return net

def C_AMPA(net,a,stim,getparams=False):

    if getparams:
        stims = [i for i in range(1,51,2)]#+[i for i in range(50,100,2)]+[i for i in range(100,251,5)];
        inhg = [0.0,0.002,0.004,0.006,0.008]
        param = []
        for i in inhg:
            param.append([i])
        return [20,200,stims,param]

    mult = 1 

    # modifyAMPA/NMDA scale by total number of receptors so we multiply by 2 since we have 2 inputs
    net.cells["IC"]["cells"][0].sec["soma"].modifyAMPA(gmax=a[0]*2*mult)
    net.cells["IC"]["cells"][0].sec["soma"].modifyNMDA(gmax=0.020*2*mult,Beta=0.0066,mg=1.0)
    net.cells["IC"]["cells"][0].sec["soma"].modifyGABAa(gmax=0.0025) # Normally 0.0035
    net.cells["IC"]["cells"][0].sec["soma"](0.5).pas.g = 1.0/4000

    net.cells["MSO_ON"]["delay"] = 10 
    net.cells["MSO_OFF"]["delay"] = 6 
    net.cells["DNLL"]["delay"] = 9

    net.cells["MSO_ON"]["stim"] = "IClamp"
    net.cells["MSO_ON"]["stimamp"] = 0.1
    net.cells["MSO_OFF"]["stim"] = "IClamp"
    net.cells["MSO_OFF"]["stimamp"] = 0.1

    return net

def C_ONSET(net,a,stim,getparams=False):
    if getparams:
        stims = [i for i in range(1,61,2)]#+[i for i in range(50,100,2)]+[i for i in range(100,251,5)];
        Onset = [10,20,30,40]
        param = []
        for a in Onset:
            param.append([a])
        return [20,500,stims,param]

    mult = 1

    # modifyAMPA/NMDA scale by total number of receptors so we multiply by 2 since we have 2 inputs
    net.cells["IC"]["cells"][0].sec["soma"].modifyAMPA(gmax=0.004*2*mult)
    net.cells["IC"]["cells"][0].sec["soma"].modifyNMDA(gmax=0.020*2*mult,Beta=0.0066,mg=1.0)
    net.cells["IC"]["cells"][0].sec["soma"].modifyGABAa(gmax=0.0025) # Normally 0.0035

    net.cells["IC"]["cells"][0].sec["soma"](0.5).pas.g = 1.0/4000

    net.cells["MSO_ON"]["delay"] = a[0]
    net.cells["MSO_OFF"]["delay"] = 6 
    net.cells["DNLL"]["delay"] = 9

    net.cells["MSO_ON"]["stim"] = "IClamp"
    net.cells["MSO_ON"]["stimamp"] = 0.1
    net.cells["MSO_OFF"]["stim"] = "IClamp"
    net.cells["MSO_OFF"]["stimamp"] = 0.1

    return net

def C_RAT(net,a,stim,getparams=False):
    if getparams:
        stims = [i for i in range(5,206,10)]
        stims = [5, 15, 26, 36, 46, 56, 67, 77, 87, 97, 108, 118, 128, 138, 149, 159, 169, 180, 190, 200]
        param = [i for i in range(100)]
        #param = [1]
        return [20,500,stims,param]

    mult = 1.0

    # modifyAMPA/NMDA scale by total number of receptors so we multiply by 2 since we have 2 inputs
    net.cells["IC"]["cells"][0].sec["soma"].modifyAMPA(gmax=0.0030*2*mult)
    net.cells["IC"]["cells"][0].sec["soma"].modifyNMDA(gmax=0.012*2*mult,Beta=0.0066,mg=1.0)
    net.cells["IC"]["cells"][0].sec["soma"].modifyGABAaRange(list(range(10)), gmax=0.00080/10)
    net.cells["IC"]["cells"][0].sec["soma"].modifyGABAaRange(list(range(10,20)), gmax=0.0030/10) #0.00677

    net.cells["IC"]["cells"][0].sec["soma"](0.5).pas.g = 1.0/10000

    net.cells["MSO_ON"]["delay"] = 15
    net.cells["MSO_OFF"]["delay"] = 32
    net.cells["DNLL"]["delay"] = 50
    net.cells["DNLLEarly"]["delay"] = 15
    net.cells["DNLLEarly"]["mindur"] = 35

    net.cells["MSO_ON"]["stim"] = "IClamp"
    net.cells["MSO_ON"]["stimamp"] = 0.1
    net.cells["MSO_OFF"]["stim"] = "IClamp"
    net.cells["MSO_OFF"]["stimamp"] = 0.1

    return net

def C_BAT(net,a,stim,getparams=False):
    if getparams:
        stims = [i for i in range(1,26,1)]
        param = [1]
        return [20,150,stims,param]

    if stim <= 1:
        mult = 0.0
    else:
        mult = 1.0

    # modifyAMPA/NMDA scale by total number of receptors so we multiply by 2 since we have 2 inputs
    net.cells["IC"]["cells"][0].sec["soma"].modifyAMPA(gmax=0.0090*2*mult)
    net.cells["IC"]["cells"][0].sec["soma"].modifyNMDA(gmax=0.0*2*mult,Beta=0.0066,mg=1.0)
    net.cells["IC"]["cells"][0].sec["soma"].modifyGABAa(gmax=0.0052)

    net.cells["IC"]["cells"][0].sec["soma"](0.5).pas.g = 1.0/1500

    net.cells["MSO_ON"]["delay"] = 13
    net.cells["MSO_OFF"]["delay"] = 14
    net.cells["DNLL"]["delay"] = 13

    net.cells["MSO_ON"]["stim"] = "IClamp"
    net.cells["MSO_ON"]["stimamp"] = 0.1
    net.cells["MSO_OFF"]["stim"] = "IClamp"
    net.cells["MSO_OFF"]["stimamp"] = 0.1

    return net

def C_BAT_JUN2(net,a,stim,getparams=False):
    if getparams:
        stims = [i for i in range(1,26,1)]
        param = [1]
        return [20,150,stims,param]

    if stim <= 1:
        mult = 0.0
    else:
        mult = 1.0

    # modifyAMPA/NMDA scale by total number of receptors so we multiply by 2 since we have 2 inputs
    net.cells["IC"]["cells"][0].sec["soma"].modifyAMPA(gmax=0.012*2*mult)
    net.cells["IC"]["cells"][0].sec["soma"].modifyNMDA(gmax=0.008*2*mult,Beta=0.0066,mg=1.0)
    net.cells["IC"]["cells"][0].sec["soma"].modifyGABAa(gmax=0.0080)

    net.cells["IC"]["cells"][0].sec["soma"](0.5).pas.g = 1.0/1200

    net.cells["MSO_ON"]["delay"] = 12
    net.cells["MSO_OFF"]["delay"] = 14
    net.cells["DNLL"]["delay"] = 12

    net.cells["MSO_ON"]["stim"] = "IClamp"
    net.cells["MSO_ON"]["stimamp"] = 0.1
    net.cells["MSO_OFF"]["stim"] = "IClamp"
    net.cells["MSO_OFF"]["stimamp"] = 0.1

    return net

def C_ANURANS_T(net,a,stim,getparams=False):
    if getparams:
        stims = [2,5,10,15,20,25,30,40,50,100]
        #stims = [5,100]
        param = [1]
        return [20,200,stims,param]

    mult = 1.0

    # modifyAMPA/NMDA scale by total number of receptors so we multiply by 3 since we have 2 inputs
    net.cells["IC"]["cells"][0].sec["soma"].modifyAMPA(gmax=0.00119*2*mult)
    net.cells["IC"]["cells"][0].sec["soma"].modifyNMDA(gmax=0.036*2*mult,Beta=0.0066,mg=1.0)
    net.cells["IC"]["cells"][0].sec["soma"].modifyGABAa(gmax=0.00032)

    net.cells["IC"]["cells"][0].sec["soma"](0.5).pas.g = 1.0/9000

    net.cells["MSO_ON"]["delay"] = 34+4
    net.cells["MSO_OFF"]["delay"] = 0 
    net.cells["DNLL"]["delay"] = 25+4 

    net.cells["MSO_ON"]["stim"] = "IClamp"
    net.cells["MSO_ON"]["stimamp"] = 0.1
    net.cells["MSO_OFF"]["stim"] = "IClamp"
    net.cells["MSO_OFF"]["stimamp"] = 0

    return net

def C_ANURANS(net,a,stim,getparams=False):
    if getparams:
        stims = [2,5,10,15,20,25,30,40,50,100]
        param = [1]
        return [20,200,stims,param]

    mult = 1.0

    # modifyAMPA/NMDA scale by total number of receptors so we multiply by 2 since we have 2 inputs
    net.cells["IC"]["cells"][0].sec["soma"].modifyAMPA(gmax=0.005*2*mult)
    net.cells["IC"]["cells"][0].sec["soma"].modifyNMDA(gmax=0.020*2*mult,Beta=0.0066,mg=1.0)
    net.cells["IC"]["cells"][0].sec["soma"].modifyGABAa(gmax=0.0014)

    net.cells["IC"]["cells"][0].sec["soma"](0.5).pas.g = 1.0/5000

    net.cells["MSO_ON"]["delay"] = 50
    net.cells["MSO_OFF"]["delay"] = 0 
    net.cells["DNLL"]["delay"] = 25 

    net.cells["MSO_ON"]["stim"] = "IClamp"
    net.cells["MSO_ON"]["stimamp"] = 0.1
    net.cells["MSO_OFF"]["stim"] = "IClamp"
    net.cells["MSO_OFF"]["stimamp"] = 0

    return net

def C_MOUSE_SP(net,a,stim,getparams=False):
    if getparams:
        stims = [i for i in range(1,32,2)]+[50,75,100]
        stims = [1, 3.6, 6.3, 8.9, 11.5, 14.2, 17,20,22,25,28,30,50,75,100]
        param = [1]
        return [20,250,stims,param]

    if stim <= 1:
        mult = 1.0
    else:
        mult = 1.0

    # modifyAMPA/NMDA scale by total number of receptors so we multiply by 2 since we have 2 inputs
    net.cells["IC"]["cells"][0].sec["soma"].modifyAMPA(gmax=0.0019*2*mult)
    net.cells["IC"]["cells"][0].sec["soma"].modifyNMDA(gmax=0.019*2*mult,Beta=0.0066,mg=1.0)
    net.cells["IC"]["cells"][0].sec["soma"].modifyGABAa(gmax=0.0012)

    net.cells["IC"]["cells"][0].sec["soma"](0.5).pas.g = 1.0/5000

    net.cells["MSO_ON"]["delay"] = 14
    net.cells["MSO_OFF"]["delay"] = 6
    net.cells["DNLL"]["delay"] = 12

    net.cells["MSO_ON"]["stim"] = "IClamp"
    net.cells["MSO_ON"]["stimamp"] = 0.1
    net.cells["MSO_OFF"]["stim"] = "IClamp"
    net.cells["MSO_OFF"]["stimamp"] = 0.1

    return net





