# csv2sparam.py
# shabaz rev 1 September 2021
# ian revforMYLab March 2023
#
# This code can be used for converting dataset information from the FPC1500 VNA into Touchstone format, as a .s1p file
# Workflow:
# 1. Perform measurement using the FPC1500 in VNA mode
# 2. Press the "SAVE/RECALL" rubber button
# 3. Select "Save" soft-button, and then scroll down to \Public\Datasets
# 4. Press "Save" soft-button to commit the file into the file system; it will have a name like "Dataset001.set"
# 5. Use the InstrumentView PC software and connect to the FPC1500 and then go to Instrument->FileTransfer
# 6. Transfer across the .set file onto your PC
# 7. Click on the dataset file as shown on the right side of InstrumentView, and the click on the Eye icon to view the dataset graphically
# 8. Now you can click on "Save" on the left side of InstrumentView, choosing "Save as type" to be "CSV File"
# 9. Go to you PC's file explorer and copy the CSF file, renaming it "input.csv"
# 10. Run this Python code, by typing:
#                                       python ./csv2sparam.py
# 11. If all goes well, an output.s1p file will be generated
# 12. You can open the file using software such as Python scikit-rf library, or Iowa Hills Smith Chart, or SPARGraph

#%%
import csv
from datetime import datetime

freqwidth=14
paramwidth=26
tstamp = datetime.now();
fstart="0"
fstop="0"

f = open("/home/ori/Documents/Work/VNA/Convert/output.s1p", "w")
with open('/home/ori/Documents/Work/VNA/Convert/input.csv', newline='', encoding="utf8") as csvfile:
    reader = csv.reader(csvfile, delimiter = ',')
    found=0
    totlines=0
    for i in range(1,34):
        next(reader)
    for row in reader:
        if (found==0):
            if len(row)<3:
                continue
            if row[0]=='Frequency [Hz]':
                print("Start of dataset found")
                found=1
                f.write("! Enter description here\n")
                f.write("! "+ str(tstamp)+"\n")
                f.write("# MHZ S MA R 50\n")
                headerline=['!Freq', 'MagS11', 'AngS11']
                line="{: <15} {: <24} {: <24}\n".format(*headerline)
                f.write(line)
                continue
        else:
            freq=row[0]
            mag=row[1]
            pha=row[2]
            totlines=totlines+1
            dataline=[str(float(freq)/1e6), str(pow(10, float(mag)/20.0)), str(pha)]
            line="{: <15} {: <24} {: <24}\n".format(*dataline)
            f.write(line)
            if (totlines==1):
                fstart=freq
            else:
                fstop=freq
    f.write("")
    f.close()

print("Completed "+str(totlines)+" entries ("+fstart+" - "+fstop+" MHz)")
print("output.s1p generated.\nBye.")
# %%
