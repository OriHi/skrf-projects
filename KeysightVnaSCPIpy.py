import pyvisa as visa
import numpy as np
"""
Copyright (c) 2019 Keysight Technologies, Inc.

This software is provided "as is" and Keysight Technologies makes no warranty of any kind iwth regard to this software.

Original author: Mark E. Hanni
Description: Bare minimum implementation of SCPI calls using python
"""

MY_NAME = 'KeysightVnaSCPIpy'
MY_NAME_LONG = 'KeysightVnaSCPIpy for VNAs by Mark Hanni'

import sys # if this import fails all hope is lost.

# Import checks and handling. 
try:
    # check python version, this is okay'ish for single version tolerance.  Multiversion tolerance requires a bit more fancy footwork with the tuple
    if(sys.version_info.major != 3 or sys.version_info.minor < 7):
        raise OSError('{0} requires Python >= 3.7.x.'.format(MY_NAME_LONG))   
    # load pyvisa
    import visa
    pyVisaVersion = ['0','0','0']
    if hasattr(visa, '__version__'):
        pyVisaVersion = visa.__version__.split('.')
    else:
        import pkg_resources
        pyVisaVersion = pkg_resources.get_distribution("pyvisa").version.split('.')
    
    pyVisaVersion = [int(aNumber) for aNumber in pyVisaVersion] # Thank you stackoverflow for this gem!
    # check pyvisa.visa version & block on non-match
    if(pyVisaVersion[0] != 1 or pyVisaVersion[1] < 10):
        raise OSError('{0} requires pyvisa == 1.10.x '.format(MY_NAME_LONG))

    # load 'normal' modules.  Seriously, these should be pretty okay
    import time
    import numpy as np
except ModuleNotFoundError as ex:
    print(ex.msg)
    quit()
except OSError as ex:
    print(ex.args[0])
    quit()

    
class VnaSCPI():
    # Constructor
    # By python convention variables prefixed with underscore are treated as "private".  Python has no concept of member variables.
    # dunderscore things are typically special names and such, also get mangled by the interpreter to prevent overlapping names.  Considered 'superprivate' by convention.
    def __init__(self, VisaAddress):
        """ Initialize a new VNA object and connect to VNA at Address VisaAddress"""
        self.OpenConnection(VisaAddress)
        return

    #region General helper methods
    def DoSpoll(self):
        """ Do blocking Spoll operations on connected instrument """
        self._Instrument.write('*CLS')
        self._Instrument.write('*ESE %d' % (1))
        bits = 0
        while bits != 32:
            self._Instrument.write('*OPC')
            temp_values = self._Instrument.query_ascii_values('*STB?')
            bits = int(temp_values[0])
            time.sleep(0.1)
        return

    def DoOPCQueryUntilReady(self):
        """ Do a *OPC? query and block until instrument says it's ready again """
        opc = self.Query('*OPC?')
        ndx_i = 0
        maxIter = 120
        while int(opc) != 1 and ndx_i < maxIter:
            ndx_i = ndx_i + 1
            time.sleep(0.5)
            opc = self.Query('*OPC?')
            time.sleep(0.5)

    def Write(self, CommandString):
        self._Instrument.write(CommandString)
        return

    def Query(self, QueryString):
        ret = self._Instrument.query(QueryString)
        return ret
    
    def QueryBinary(self, QueryString):
        binData = self._Instrument.query_binary_values(QueryString, container=np.array, is_big_endian=True)
        return binData
    #region General SCPI Methods

    #region VNA Hardware Path Configuration
    def SetHwPathElement(self, ChannelNumber, PathElement, ElementState):
        """ Configure VNA hardware RF path element with name PathElement to state ElementState """
        self.Write(':SENS{0}:PATH:CONF:ELEM "{1}","{2}"'.format(ChannelNumber, PathElement, ElementState))
        return

    def GetHwPathElementState(self, ChannelNumber, PathElement):
        """ Get the configured state of the VNA's RF hardware path element with name PathElement """
        elementState = self.Query(':SENS{0}:PATH:CONF:ELEM? "{1}"'.format(ChannelNumber, PathElement))
        return elementState
    #endregion
    
    def OpenConnection(self, InstVisaAddr):
        """ Open connection to VNA at given VISA address string """
        self._rm = visa.ResourceManager()
        # pyvisa has a weird EOL termination sequence by default.  Setting write_termination this seems to make it behave better with some instruments (I'm looking at you Keysight E36103A...).
        self._Instrument = self._rm.open_resource(InstVisaAddr, write_termination='\n') 
        self.IDNString = self.Query('*IDN?')
        _idnArray = str.split(self.IDNString, ',')
        self.VNAModel = _idnArray[1]
        self.VNASerial = _idnArray[2]
        self.VNAFirmware = _idnArray[3]
        return

    def CloseConnection(self):
        """ Close the connection to the VNA and release all resources """
        #self._Instrument.before_close()
        self._Instrument.close()
        self._rm.close()
        return

    def GetIDN(self):
        """ Get the VNA's full *IDN? response string"""
        return self.IDNString

    def GetFirmwareVersion(self):
        """ Get the firwmare version of the connected VNA """
        return self.VNAFirmware

    def GetModelNumber(self):
        """ Get the model number of the connected VNA """
        return self.VNAModel
    
    def GetVNASerialNumber(self):
        """ Get the serial number of the connected VNA """
        return self.VNASerial

    def DoPreset(self):
        """ Preset the instrument """
        self.Write(":SYST:FPR")
        self.DoSpoll()
        return

    def DoAutoScaleAll(self, WindowNumber):
        """ Autoscale all traces in the window with window number WindowNumber """
        self.Write(':DISP:WIND{0}:Y:AUTO'.format(WindowNumber))
        self.DoSpoll()
        return
    def GetNextAvailableChannel(self):
        channels = str.split(self.Query(':SYST:CHAN:CAT?'), ',')
        return len(channels)

    def GetNextAvailableWindow(self):
        windows = str.split(self.Query(':DISP:CAT?'))
        return len(windows)

    def GetWindowState(self, WindowNumber):
        windowState = self.Query(':DISP:WIND{0}:STAT?'.format(WindowNumber))
        return int(windowState) > 0

    def GetNextAvailableTrace(self, WindowNumber):
        traceNum = 0
        if(self.GetWindowState(WindowNumber)):
           traces = str.split(self.Query(':DISP:WIND{0}:CAT?'.format(WindowNumber)), ',')
           traceNum = len(traces)   
        else:
            traceNum = traceNum + 1

        return max(traceNum, 1)

    def GetPortNumber(self, portName):
        portNum = self.Query(':SYST:CAP:HARD:PORT:PNUM? "{0}"'.format(portName))
        return int(portNum.rstrip())

    def CreateMeasurement(self, measurementClass, measurementParameter, measurementName, channelNumber, windowNumber, traceNumber):
        """ Create measurement for given paramete in specified measurement class, assigning the channelNumber and windowNumber values provided. """
        self.Write(':CALC1:CUST:DEF "{0}","{1}","{2}"'.format(measurementName, measurementClass, measurementParameter))
        self.Write(':DISP:WIND{0}:STAT 1'.format(windowNumber)) # Turn on window
        self.Write(':DISP:WIND{0}:TRAC{1}:FEED "{2}"'.format(windowNumber, traceNumber, measurementName))
        self.DoSpoll()
        return

    def SetDataFormat(self, dataFormat = 'ASCII,0'):
        """ Set the VNA data format, affects response to queries with formatted data.  Choose from  ASCii,0 | REAL,32 | REAL,64"""
        self.Write('FORM {0}'.format(dataFormat))
        
        # if(dataFormat.capitalize() != 'ASCII,0'):
        #     self.Write('FORM:BORD SWAP')
        # else:
        #     self.Write('FORM:BORD NORM')

        self.DoSpoll()
        return
    #TODO Option code query - do I even need that?  eh .. not for alpha prototype
    #endregion
    
    #region Sweeping and holding
    def DoSweepHold(self, channelNumber):
        """ Put channel with channelNumber into sweep hold mode """
        self.Write(':SENS{0}:SWE:MODE HOLD'.format(channelNumber))
        return

    def DoSweepSingle(self, channelNumber):
        """ Put channel with channelNumber into sweep single mode """
        self.Write(':SENS{0}:SWE:MODE SING'.format(channelNumber))
        self.DoSpoll()
        return

    def SetSweepType(self, channelNumber, sweepType='LIN'):
        """ Set the VNA sweep type.  Choose from LINear, LOGarithmic, POWer, CW, SEGMent, PHASe """
        self.Write(':SENS{0}:SWE:TYPE {1}'.format(channelNumber, sweepType))
        return
    #endregion
    
    #region SA measurements
    def SetSADftBwAutoMode(self, channelNumber,state=True):
        """ Sets the DFT bandwidth auto mode on (true) or off (false) for SA measurements """
        self.Write(':SENS{0}:SA:DFT:BAND:AUTO {1}'.format(channelNumber, int(state)))
        return

    def SetSAAdcFilterCutoff(self, channelNumber, adcFilterCutoff):
        """ Sets the SA channel's ADC Filter Cutoff frequency"""
        self.Write(':SENS{0}:SA:ADC:FILT {1}'.format(channelNumber, adcFilterCutoff))
        return

    def GetSAAdcFilterCutoff(self, channelNumber):
        """ Gets the SA channel's ADC Filter Cutoff frequency"""
        filterCutoffFreq = self.Query(':SENS{0}:SA:ADC:FILT?'.format(channelNumber))
        return float(filterCutoffFreq)

    def SetSARandomLOState(self, channelNumber, state=True):
        """ Sets the SA measurement's LO randomization state to On (true, default) or Off (false) """
        self.Write(':SENS{0}:SA:LO:RAND:STAT {1}'.format(channelNumber, int(state)))
        return
    def SetSARBWShape(self, channelNumber, shape='GAUS'):
        """ Set the shape of the RBW filter.  Select from GAUSsian, FLATtop, KAISer, BLACkman, NONE """
        self.Write(':SENS{0}:SA:BAND:SHAP {1}'.format(channelNumber, shape))
        return

    def SetSAImageRejectMode(self, channelNumber, mode='NORM'):
        """ Set the SA channel image reject mode.  Choose from NHIGh, NLOW, MIN, NORMal, BETTer, MAX """
        self.Write(':SENS{0}:SA:IMAG:REJ {1}'.format(channelNumber, mode))
        return

    def SetSAMultitoneMode(self, channelNumber, state=False):
        """ Turn On (true) or Off (false) SA multitone measurement mode """
        self.Write(':SENS{0}:SA:COH:MULT:STAT {1}'.format(channelNumber, int(state)))
        return
    
    def SetSAMultitonePhaseMode(self, channelNumber, state=False):
        """ Turn On (true) or Off (false) phase measurements for SA multitone mode """
        self.Write('SENS{0}:SA:COH:PHASE:STATE {1}'.format(channelNumber, int(state)))
        return 

    def SetSAMultitoneHarmonicRejectionNumber(self, channelNumber, harmonicNumberToRejectTo):
        """ Set the harmonic rejection level for SA measurements.  Harmonics at or below this level will be rejected """
        self.Write(':SENS{0}:SA:COH:MULT:HREJ {1}'.format(channelNumber, harmonicNumberToRejectTo))
        return
    
    def SetSAMultioneDataDisplayMode(self, channelNumber, mode='ALL'):
        """ Set the SA measurement's data display mode for multitone measurements.  Choose from ALL, ZNTones, or DNTones """
        self.Write('SENS{0}:SA:COH:MULT:DATA {1}'.format(channelNumber, mode))
        return
    
    def SetSANyquistRejectLevel(self, channelNumber, nyquistRejectionLevel = 2):
        """ Set the Nyquist rejection level for the SA measurement channel """
        self.Write(':SENS{0}:SA:COH:MULT:NYQR {1}'.format(channelNumber, nyquistRejectionLevel))
        return

    def SetSAMultitoneReferenceTone(self, channelNumber, frequency):
        """ Sets the reference tone for SA channel's multitone measurements """
        self.Write(':SENS{0}:SA:COH:MULT:REF {1}'.format(channelNumber, frequency))
        return

    def GetSAMultitoneReferenceTone(self, channelNumber):
        """ Gets the multitone referenc tone frequency """
        return float(self.Query('SENS{0}:SA:COH:MULT:REF?'.format(channelNumber)))

    def SetSAMultitoneToneSpacing(self, channelNumber, toneSpacing):
        """ Sets the tone spacing for the SA channel's multitone measurements """
        self.Write(':SENS{0}:SA:COH:MULT:SPAC {1}'.format(channelNumber, toneSpacing))
        return

    def GetSAMultitoneToneSpacing(self, channelNumber):
        """ Gets the multitone tone spacing from the SA channel """
        return float(self.Query("SENS{0}:SA:COH:MULT:SPACING?".format(channelNumber)))

    def SetSAADCStackAvergingState(self, channelNumber, mode = False):
        """ Turns on (True) or Off (false) the averaging using ADC stacks.  Takes precidence over VBW.  Useful for coherent multitone measurements """
        self.Write(':SENS{0}:SA:ADC:STAC:STAT {1}'.format(channelNumber, int(mode)))
        return
    
    def SetSAADCNumberOfStacksForAvgerage(self, channelNumber, additionalStacksForAverage = 0):
        """ Sets the number of additional ADC acquisitions that are stacked to present the average measurement.  Takes precedence over VBW.  Default = 0 turns off stacking """
        self.Write(':SENS{0}:SA:ADC:STACking:VALue {1}'.format(channelNumber, additionalStacksForAverage))
        return

    def GetSASweepStartFrequency(self, channelNumber):
        """ Get the sweep start frequency of the SA channel """
        return float(self.Query("SENSe{0}:SA:DATA:STARt?".format(channelNumber)))  

    def GetSAStartFrequencyRoundedOnMultiToneGrid(self, channelNumber):
        """ Get the start frequency for the SA sweep that is rounded to the multitone grid, this is a bit of measurement physics that probably should be in the VNA f/w """
        # Auguie says we need this one so that we are on the grid.  This value can differ slightly from the SA Sweep start frequency.
        # The frequency of the first RF bin is aligned with the current DFT grid.
        sweepStartFreq = self.GetSASweepStartFrequency(channelNumber)
        toneSpacing = self.GetSAMultitoneToneSpacing(channelNumber)
        refrencFrequency = self.GetSAMultitoneReferenceTone(channelNumber)
        startNew = np.round((sweepStartFreq-refrencFrequency)/toneSpacing)*toneSpacing + refrencFrequency
        return startNew

    def SetSARecieverForFIFO(self, channelNumber, receiver):
        """ Set the reciever to export the data from for the FIFO buffer """
        # Note, this actually takes a list but for simplicity only set 1 reciever to the FIFO right now
        # The order of the recievers in the list determines the order of the data in the FIFO buffer
        self.Write('SENS{0}:SA:DATA:REC:LIST "{1}"'.format(channelNumber, receiver))
        return

    def SetSAFIFOState(self, channelNumber, state = False):
        """ Set the SA measurement FIFO export buffer state On (TRUE) or Off (False, default)"""
        self.Write("SENS{0}:SA:DATA:FIFO {1}".format(channelNumber, int(state)))
        return

    def GetSANumberOfMeasurementLOs(self, channelNumber):
        """ Get the count of the LOs used in the measurement """
        return int(self.Query('SENSE{0}:SA:LO:LIST:COUNT?'.format(channelNumber)))

    def GetSAMeasurementLOatIndex(self, channelNumber, LOndx):
        """ Get the frequency value of the LO used for measurement at index in the list of LOs """
        return float(self.Query("SENSE{0}:SA:LO:LIST:VALUE? {1}".format(channelNumber, LOndx)))

    def GetSAMeasurementChunkCount(self, channelNumber):
        """ Get the number of measurement chunks for the SA measurement channel """
        return int(self.Query('SENSE{0}:SA:LO:CHUNk:COUNT?'.format(channelNumber)))

    def GetSAMeasurementChunkStart(self, channelNumber, chunkIndx):
        """ Get the start frequency for the specified measurement chunk at index chunkIndx """
        return float(self.Query("SENSE{0}:SA:LO:CHUNk:STARt? {1}".format(channelNumber, chunkIndx)))

    def GetSAMeasurementChunkStop(self, channelNumber, chunkIndx):
        """ Get the stop frequency for the specified measurement chunk at index chunkIndx """
        return float(self.Query("SENSE{0}:SA:LO:CHUNk:STOP? {1}".format(channelNumber, chunkIndx)))
    
    #endregion
    
    #region External Source control
    # For the sake of brevity these methods implement the most basic and crude mechanisms to handle external devices.
    # The device with name DeviceName must already exist and have IO Enabled.  Else, all crazy will break loose.
    def GetExtDeviceState(self, DeviceName):
        """ Get the Activation state (shown in UI) of the external device with DeviceName. """
        state = False
        stateAsInt = self.Query(':SYST:CONF:EDEV:STAT? \"{0}\"'.format(DeviceName))
        if stateAsInt > 0:
            state = True
        return state

    def SetExtDeviceState(self, DeviceName, State):
        """ Sets External Device, with DeviceName, activation (shown in UI) state to State """
        stateVal = 0
        if State:
            stateVal = 1
        self.Write('SYST:CONF:EDEV:STAT \"{0}\",{1}'.format(DeviceName, stateVal))
        return
    
    def SetExtDeviceModulationControlState(self, DeviceName, State):
        """ Sets the modulation control state of the external device, DeviceName, to state, State.  True = On, False = Off """
        self.Write('SYST:CONF:EDEV:SOUR:MOD:CONT:STAT \"{0}\",{1}'.format(DeviceName, int(State)))
        return

    def SetExtSrcModulationFile(self, ChannelNumber, DeviceName, ModulationFile):
        """ Set the modulation file to play using the external vector source with name DeviceName.  The file and path in ModulationFile must already be present on the VNA """
        self.Write(':SOUR{0}:MOD:LOAD "{1}","{2}"'.format(ChannelNumber, ModulationFile, DeviceName))
        #print(self.Query(":SOUR1:MOD:FILE? \"esg\""))
        self.DoSpoll()
        return

    def SetExtSrcModulationState(self, ChannelNumber, DeviceName, State):
        """ Set the modulation control state of the external vector source with DeviceName to State. """
        self.Write('SOUR{0}:MOD:STAT {1},\"{2}\"'.format(ChannelNumber, int(State), DeviceName))
        return
    #endregion 

    #region Source Frequency and power levels

    def SetSourcePowerMode(self, SourceState=True):
        """ Set the source power state to on if True, off if False """
        if(SourceState):
            self.Write(':OUTP:STAT 1')
        else:
            self.Write(':OUTP:STAT 0')
        return

    def SetSourceFrequencyFixed(self, channelNumber, sourceFrequency, sourceName):
        """ Sets fixed freqency of source with a given sourceName """
        self.Write(':SOUR{0}:FREQ:FIX {1},"{2}"'.format(channelNumber, sourceFrequency, sourceName))
        self.DoSpoll()
        return

    def SetSourcePower(self, channelNumber, sourceLevel, sourceName):
        """ Set the source with given sourceName to the level (in dBm) given by sourceLevel """
        self.Write(':SOUR{0}:POW:LEV:IMM:AMPL {1},"{2}"'.format(channelNumber, sourceLevel, sourceName))
        self.DoSpoll()
        return

    def SetSourceState(self, channelNumber, sourceName, state='OFF'):
        """ Set source control state.  Use: AUTO, ON, OFF, NOCTRL for state """
        self.Write(':SOUR{0}:POW:MODE {1},"{2}"'.format(channelNumber, state.capitalize(), sourceName))
        self.DoSpoll()
        return

    def SetSweepCenterFrequency(self, channelNumber, frequency):
        """ Set the measurement channel's center frequency """
        self.Write(':SENS{0}:FREQ:CENT {1}'.format(channelNumber, frequency))
        return

    def SetSweepSpan(self, channelNumber, spanHz):
        """ Set the measurement channel's span """
        self.Write(':SENS{0}:FREQ:SPAN {1}'.format(channelNumber, spanHz))
        return

    #endregion

    #region VNA FIFO operations
    def ClearFIFO(self):
        """ Clear the VNA FIFO buffer """
        self.Write("SYST:FIFO:DATA:CLEAR")
        self.DoSpoll
        return
    
    def GetDataFromFIFO(self):
        nofdata = int(self.Query("SYST:FIFO:DATA:COUNT?"))
        data = self.QueryBinary("SYST:FIFO:DATA? {0}".format(nofdata))
        self.DoSpoll()
        return data
    #endregion 
# __main__ guard
if __name__ == '__main__':
    print("This script is intended to be ran as a library and called from a python program.")
# EOF