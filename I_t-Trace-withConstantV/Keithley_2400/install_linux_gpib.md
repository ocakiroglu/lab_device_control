> **Note:** This guide is an adaptation of the original tutorial: [How to use GPIB with Raspberry Pi/Linux](https://community.element14.com/members-area/personalblogs/b/blog/posts/step-by-step-guide-how-to-use-gpib-with-raspberry-pi-linux) by Element14. It has been modified and updated to focus specifically on the **Keithley 2400** and the **NI GPIB-USB-HS** interface with a file **linux-gpib-4.3.6.tar.gz**.

# Keithley 2400 by NI GPIB-USB-HS Interface in Linux

Keithley 2400 is controlled by a special interface from National Instruments (NI) and called ‘GPIB-USB-HS’. However, NI doesn’t support Linux or later MacOS 10 for the communication with GPIB-USB-HS and a person from NI suggested using an open-source linux-gpib driver instead of the official one in the NI-Support forum.  Therefore, users in Linux must install linux-gpib by following the installation guide. 



<p align="center">
  <img src="keithley2400.png" alt="Keithley 2400" height="220">
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="GPIB-USB-HS_image.jpg" alt="GPIB-USB-HS interface" height="220">
  <br>
  <em>Figure 1: Keithley 2400 (Left) and National Instruments GPIB-USB-HS Interface (Right) </em>
</p>

## **1. Build and Install Linux-GPIB Module**

Initially, dependencies must be installed on the terminal.

```bash
sudo apt install build-essential texinfo texi2html libcwidget-dev libncurses5-dev libx11-dev binutils-dev bison flex libusb-1.0-0 libusb-dev libmpfr-dev libexpat1-dev tofrodos subversion autoconf automake libtool byacc gedit
```

We are ready to install the driver of NI GPIB-USB-HS equipment. Setup file ‘linux-gpib-4.3.6’ will be used for this purpose. The compressed tar file (assumed in the Download folder) must be extracted to home direction in order to install the driver.

```bash
cd ~/Downloads 
tar -xvf  linux-gpib-4.3.6.tar.gz -C ~
``` 

We can start the installation. The linux-gpib files is source files instead of setup files thus we make the installation at a low-level by following these steps:

```bash
cd ~/linux-gpib-4.3.6/linux-gpib-user-4.3.6 
./bootstrap
./configure --sysconfdir=/etc 
make 
sudo make install 
``` 

In this way, we succeeded to build and install linux-gpib-user files which helps us to control Keithley2400 by Python or another language (guile, perl, php, tcl… ). Next step is to build and install the driver with these commands

```bash
cd ~/linux-gpib-4.3.6/linux-gpib-kernel-4.3.6
make
sudo make install
``` 

If we receive any error in all steps, it means that we complete the installation of the driver. We can test the drivers by checking their file in the system.

```console
foo@bar:~$ ls /lib/modules/`uname -r`/gpib  
agilent_82350b  cec       hp_82335  lpvo_usb_gpib  sys  
agilent_82357a  fmh_gpib  hp_82341  nec7210        tms9914  
cb7210          gpio      ines      ni_usb         tnt4882
``` 

If you get such a return, it means that drivers are installed. You cannot use only Keithley2400 but other equipment since linux-gpib consists of many drivers of different equipment via GPIB communication. We can check whether Keithley 2400 is connected or not

```console
foo@bar:~$ lsusb | grep GPIB**  
Bus 001 Device 004: ID 3923:709b National Instruments Corp. GPIB-USB-HS	  
```

If we see this line in the return, it means that Keithley 2400 is detected by Linux. We should make driver module active in Linux

```bash
sudo modprobe ni_usb_gpib
```

There should be no error messages here or nothing returns. We can check if module was correctly used as well

```console
foo@bar:~$ lsmod | grep ni_usb  
gpib_common            31031  1 ni_usb_gpib	
```

If such a line returns, the module is ON in Linux. We need to configure a last file to set successful communication with Keithley 2400. We must edit /etc/gpib.conf file

```bash
sudo gedit /etc/gpib.conf
```

and these lines must be edited in the pop-up window with the followings

```text
interface {  
	minor = 0  
	board_type = "ni_usb_b"  
	name = "gpib0"  
	pad = 0  
	timeout = T3s  
	eos = 0x0a  
	set-reos = yes  
	set-bin = no  
	master = yes  
}

device { 
	minor = 0 
	name = "keithley2400"  
	pad = 24
	sad = 0  
	eos = 0x0a  
	set-reos = yes  
	set-bin = no  
	set-xeos = yes  
	set-eot = no  
	timeout = T3s  
}
```

We can save and close the window but settings can be restarted by this command  

```bash	  
sudo gpib_config
```

## **2. Test the Connection with Keithley 2400**

We can test the connection of Keithley 2400, whose GPIB address is 24\. However, there is higher security in Linux than in Windows or MacOS for USB connection. We must grant permission to linux-gpib in order to use the USB port without any restriction. 

```bash
sudo chmod 666 /dev/gpib0
```

Then, we can run the test. 

```bash
sudo ibtest
```

In the next screen, we type **‘d’** and click Enter, then type **‘w’** and click Enter, then type ‘*IDN?’ and click Enter, then type **‘r’** and Enter, then type **‘1024’** and Enter. We receive a message 'KEITHLEY INSTRUMENTS INC.,MODEL 2400,0824071,C34 Sep 21 2016 15:30:00/A02  /H/H\n' from Keithley 2400 if everything works. It means that we can send/receive data. 

## **3. Communication with Python**

Linux-Gpib module supplies a library to communicate via Python but we need to install it first. The library doesn’t exist in the pip or conda platform and we can’t install it within the virtual environment or conda environment (at least now). Therefore, we install it into global python of Linux.

```bash
cd \~/linux-gpib-4.3.6/linux-gpib-user-4.3.6/language/python
python ./setup.py install
```

Simple Python test can help to check access
```bash
python
>>> import gpib  
>>> keithley = gpib.dev(0, 24)  
>>> gpib.write(keithley, "*IDN?\n")  
>>> gpib.read(keithley, 1024)  
b'KEITHLEY INSTRUMENTS INC.,MODEL 2400,0824071,C34 Sep 21 2016 15:30:00/A02  /H/H\n'  
>>> exit()
```

If you receive such return from Keithley 2400, it means that Linux is ready to communicate with Keithley 2400. We can code/run but don’t forget only on Linux global Python. You should install numpy and matplotlib to run any pre written python codes.  
	
```bash
pip install numpy matplotlib
```

That’s all. Enjoy your experiment. 

## **4.References**

1) [https://forums.ni.com/t5/Instrument-Control-GPIB-Serial/What-setup-to-use-for-GPIB-USB-HS-and-Visa-under-Linux/m-p/2110182\#M55089](https://forums.ni.com/t5/Instrument-Control-GPIB-Serial/What-setup-to-use-for-GPIB-USB-HS-and-Visa-under-Linux/m-p/2110182#M55089)   
2) [https://community.element14.com/members-area/personalblogs/b/blog/posts/step-by-step-guide-how-to-use-gpib-with-raspberry-pi-linux](https://community.element14.com/members-area/personalblogs/b/blog/posts/step-by-step-guide-how-to-use-gpib-with-raspberry-pi-linux)  
3) [https://sourceforge.net/p/linux-gpib/git/ci/master/tree/](https://sourceforge.net/p/linux-gpib/git/ci/master/tree/) 