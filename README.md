# FileSifter
This is a forensic utility-based script, written and intended for Python 2.7 environments.   
The script, fileSifter.py is a single self-contained tool that operates exclusively 
using Python Standard Library modules.  This tool is meant to offer a means of efficiently
triaging the contents of a running computer, it's hard drive, or any other storage device 
and it's associated file-system.  Ideal scenarios where this might be employed is in 
situations where the computer or device might be encrypted and can't be shutdown for a 
typical dead-box examination of the storage device.  

In these situations, an examiner would historically be limited to conducting a live 
acquisition of every file on the computer or storage device.  While this might be effective, 
it can significantly increase the time it takes to review the contents of a device, as the 
examiner has no real-time feedback as to the contents of the device.  Additionally, 
critical time might be wasted as data is being collected that may not be relevant.  These 
are the some of the situations that File Sifter is designed for.  File Sifter operates by:

-Requests the user to create a new sifting job.

-Requests the user to specify a target folder path to scan.

-The user is then prompted to enabled or disable keyword filtering.  Enabling keyword 
filtering is recommended as this is where the tool is most effective.

-If keyword filtering is enabled, the user is prompted to provide a text file containing 
keywords relevant to the exam, investigation, etc.  

-The text file is then imported to the programs keyword list.

-The user then has the option to enable File Collection.  This will collect files found in 
the target folder, based off keyword settings.  The files will then be added to a TAR or 
ZIP container.

-If File Collection is enabled...The user is then provided the option to select the format 
for the file container.  As the collection is designed to be targeted based off of keyword, 
the logical extraction of files supports either a TAR or ZIP format.

-After these easy-to-use fields are completed, the program is ready to run.

-The program will begin recursively sifting through every folder and file inside the 
specified target folder.  The full path and filename will be read in, then compared against 
the keyword list for any matching words.

-If a keyword is found in the path or filename of a file, the file will be collected and 
added to the collection container/archive file.  The file will also be processed for 
relevant metadata, and its MD5 hash-value computed.  This information is immediately logged 
to a CSV file, and the user is provided an immediate notification of the search-hit in the 
console.  

-At the conclusion of the programs execution, the user has a TAR or ZIP container, a 
detailed CSV file of all files collected and their metadata, and a detailed log file.

-The logfile, will also provide a log of every file that was not collected or processed for 
metadata due to keyword exclusion, or other exception.

-Additionally, the user has complete control over the operating modes for the program:

Full Collection Mode: By choosing to disable keyword filtering.  In this scenario, all 
files in the designated folder will be collected, and processed for metadata and hash-value.
 
Scan Only Mode: By choosing to disable file collection.  Files will only be processed for 
hash and metadata, but will not be collected.


In addition, extensive exception handling for each of the described processes has been 
employed, to catch any open, read, and write errors.  The handling of these exceptions, as 
well as detailed logging of the processing completed by the script is handled by the 
standard logging module.  

Usage:

	Requirements:
		-Python 3.7 to 3.10
		-Appropriate permissions to access target files. Running as root, sudo, or admin
		is strongly recommended to avoid permission errors if file collection is enabled.
		-Plain text keyword file, with 1 word per line recommended.
	
	1. Program started by executing the fileSifter.py script.  (No special command line
        arguments necessary)
        
	2. Enter the name for your new sifting job.
	
	3. Enter Target Scan Folder
	
	4. Enter 'YES' or 'NO' to set keyword filtering on/off.
	
	5. Provide Keyword file.
	
	6. Enable/Disable file collection.
	
	7. If file collection enabled, Choose 'TAR' or 'ZIP'.
	
	8. Hit Enter to go...
