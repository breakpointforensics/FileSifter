
#Import Modules

from builtins import input
from builtins import str
from builtins import object
import sys      #Imports the Standard Python sys module.
import socket   #Imports the Standard Python socket module.
import logging  #Imports the Standard Python logging module.
import time     #Imports the Standard Python time module.
import os       #Imports the Standard Python os module.
import stat     #Imports the Standard Python stat module.
import hashlib  #Imports the Standard Python hashlib module.
import csv      #Imports the Standard Python csv module.
import tarfile  #Imports the Standard Python tar module.
import zipfile  #Imports the Standard Python zip module.
from tkinter import Tk  					#Imports the standard Python Tkinter module as the alias Tk.
from tkinter.filedialog import askdirectory   	#Import just askdirectory from tkFileDialog
from tkinter.filedialog import asksaveasfilename  #Import just asksaveasfilename from tkFileDialog
from tkinter.filedialog import askopenfilename    #Import just askopenfilename from tkFileDialog



#fileSifter.py
#Version 0.3.4.1
#7/21/2022
#Author: David Haddad

#Description:
'''
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


'''

# Define pseudo constants
SCRIPT_NAME = 'fileSifter.py'
SCRIPT_VERSION = '0.3.4.1'

#Create counter variable to track function calls.
counter = 0


#
# Name: WalkPath() Function
#
# Desc: Uses os.walk function to recursivly scan all files and folders under the path specified by variable targetFolder.
#       use Python Standard Library module os and sys
#
#  
# Actions: 
#              Uses the standard library modules os and sys
#              to traverse the directory path passed from the rawinput variable targetFolder,
#              that was specified by the user.  For each file discovered, WalkPath
#              will call the Function FileSifter().
#              The function will proceed through this loop until each file identifed by WalkPath as been passed to FileSifter.
#

def WalkPath():
    #Initiate a variable for process and error counts starting at 0, to be incremented with each successful loop, or error.
    
    #Initiate _CSVWriter class, and assign name/path for CSV report.    
    oCVS = _CSVWriter(jobName + '_Report.csv', gl_hashType)
    
    # Create a loop that process all the files starting
    # at the rootPath, all sub-directories will also be
    # processed
    
    logging.info('Walking Target Folder: ' + targetFolder +"\n")
    
    # Create a loop that process all the files in designated targetFolder using os WalkPath function.    
    for root, dirs, files in os.walk(targetFolder):

        for file in files:
            #Join each file name with the target folder path and assign to fname.             
            fname = os.path.join(root, file)
            #Then pass full path of filename to the FileSifter function, and pass return results to CSVWriter.            
            result = FileSifter(fname, file, oCVS)

                  
                
    #At conclusion of loop, close CSV file.       
    oCVS.writerClose()
        
    return

#End WalkPath==================================================

#
# Name: BuildKeywordList Function
#
# Desc: Opens keyword text file specified by user.
#       Then imports each word into a set and converts set to lower case.


# Input:    keywordFileInput = the plain text file input by user
#           
#  
# Actions: 
#              Attempts to open the keywordFileInput file.
#              Reads, splits, converts to lowercase, adds to set.
#
def BuildKeywordList():
    #Try to open the keyword text file, split it, and build a set variable called searchKeywords
    print('Builiding Keyword List...')
    logging.info('Building Keyword List')
    
    searchKeywords = list()
    
    try:
        
        searchKeywords = set(open(keywordFileInput).read().split())
        
        
        
        #Loop through searchKeywords converting them to lowercase and add them to searchKeywordsLower.
        for searchKeyword in searchKeywords:
            searchKeywordsLower.append(searchKeyword.lower())
            
            #Print out each keyword as it's imported and add to log.
            print ('Keyword Added: ' + searchKeyword)
            logging.info ('Keyword Added: ' + searchKeyword)
            
        print('Keyword List Successfully Built')
        logging.info ('Keyword List Successfully Built')
    
    except IOError:
        #If open fails report the error.
        logging.warning('Open Failed: ' + keywordFileInput)
    
        
# End BuildKeywordList Function ===================================

#
# Name: FileSifter Function
#
# Desc: Reviews one file at a time passed from WalkPath function.  
#       Determines if keywordFiltering has been enabled. If enabled, 
#       the files name and path are checked against the keyword set provided by user.
#       Any matching files are passed to a TAR or ZIP process to collect that file. The matching
#       files metadata, and md5 hash value are also collected and appended to a CSV report.  
#       keywordFiltering can also be set to disabled, which will result in the function collecting and
#       processing all files walked in designated path. 

# Input:    theFile = the full path of the file
#           simpleName = just the filename itself
#  
# Actions: 
#              Attempts to hash the file and extract metadata
#              Call GenerateReport for successful hashed files
#
def FileSifter(theFile, simpleName, o_result):
    #Use the global counter variable.
    global counter
    global match
    
    #Check to see if keywordFiltering has been enabled.
    #If YES continue, if NO jump to next if statement.
    if keywordFilteringEnabled == 'YES':
        
        
        #Create lowercase variable for theFile, so searchkeywords and theFile are same case when matching.
        theFileLower = theFile.lower()
        
        #Loop through every word in searchKeywordsLower.
        for match in searchKeywordsLower:
            #If any words in searchKeywordsLower occur in the filename or path then...
            if match in theFileLower:
                #Print the Matching File
                print ("Found Keyword Match in: " + theFile)
                #Print the keyword that matched.
                print ('Keyword: ' + match)
                #Call the File Scraper function for only keyword matches.
                FileScraper(theFile, simpleName, o_result)
                #Increment counter by 1
                counter += 1
                       
        
        #If keyword match not found in filepath and name, log skipped file and skip to next file.
        else:
            logging.warning('[' + repr(theFile) + ', Skipped, NO Keyword Match' + ']')
            print ()
    
    if keywordFilteringEnabled == 'NO':
        #Call the File Scraper Function for all files in target.
        FileScraper(theFile, simpleName, o_result)
        #Increment counter by 1
        counter += 1
           
    return False

# End fileSifter Function ===================================


#
# Name: FileScraper Function
#
# Desc: Injests Files passed from FileSifter.
#       Scrapes the files metadata and computes md5 hash value.
#       Then file is appended to a TAR or ZIP if collection is enabled.
#       File metadata and hash are then written out to CSV file. 

# Input:    theFile = the full path of the file
#           simpleName = just the filename itself
#  
# Actions: 
#              Verifys files is real.
#              Get metadat using os.stat
#              MD5 Hash File
#              Pass results to CSV
#

def FileScraper (theFile, simpleName, o_result):
    global match
    # Verify that the path is valid
    if os.path.exists(theFile):

        #Verify that the path is not a symbolic link
        if not os.path.islink(theFile):

            #Verify that the file is real
            if os.path.isfile(theFile):

                #Path and file successfully validated, try to open the file. If try fails, exception occurs and is logged.
                try:
                    #Attempt to open the file
                    f = open(theFile, 'rb')
                except IOError:
                    #if open fails report the error
                    logging.warning('Open Failed: ' + theFile)
                    return


                else:
                    try:
                        # Attempt to read the file. If try fails, exception occurs and is logged.
                        rd = f.read()
                    except IOError:
                        # if read fails, then close the file and report error
                        f.close()
                        logging.warning('Read Failed: ' + theFile)
                        return
                    else:
                        #If file successfully opened and read, os module called to gather file metadata using stat. Then store gathered
                        #metadata in variable theFileStats.

                        theFileStats =  os.stat(theFile)
                        (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(theFile)

                        #Print the simple file name
                        print ("Processing File: " + theFile)

                        # Assign the string of size, to variable filesize.
                        fileSize = str(size)

                        #Convert the mtime,atime,and ctime to local time and assign variable names to each.
                        modifiedTime = time.ctime(mtime)
                        accessTime = time.ctime(atime)
                        createdTime = time.ctime(ctime) 

                        #Check if file collection enabled then grab the files.
                        if fileCollectionEnabled == 'YES':

                            #If keyword match found, collect the file and add to ZIP or TAR container depending on user choice.
                            if compressionChoice == "ZIP":
                                #Open and assign zip container to z, and set ZipFile to append mode. 
                                z = zipfile.ZipFile((containerName + ".zip"), "a",zipfile.ZIP_DEFLATED)
                                #Write theFile to the zip container.
                                z.write(theFile)
                                #Close the zip.
                                z.close()

                            if compressionChoice == "TAR":

                                #Open and assign tar container to tar, and set tarfile to append mode.
                                tar = tarfile.open((containerName + '.tar'), "a")
                                #Write theFile to tar container.
                                tar.add(theFile)
                                #Close theFile
                                tar.close()                                  



                        #process the file hashes


                        #Calcuation and Print the MD5
                        #Hash value is computed
                        hash = hashlib.md5()
                        hash.update(rd)
                        #Variable hexMD5 created, and defined as the hexadecimal value of the computed hash.
                        hexMD5 = hash.hexdigest()
                        #Convert hexMD5 to uppercase.
                        hashValue = hexMD5.upper()



                        #File processing completed
                        #Close the Active File
                        print("================================")
                        f.close()

                        # write one row to the output file containing file metadata values.

                        o_result.writeCSVRow(theFile, simpleName, fileSize, modifiedTime, accessTime, createdTime, hashValue, match)

                        # Add Path, Filename, hashvalue, hashtype, and hashvalue to log file.
                        logging.info("+-------------------------------------------------------------")
                        logging.info("+Keyword Match Found! File Processed:")
                        logging.info("+File Path:  "+theFile)
                        logging.info("+File Name:  "+simpleName)
                        logging.info("+Hash Type:  "+gl_hashType)
                        logging.info("+Hash Value: "+hashValue)
                        logging.info("+-------------------------------------------------------------\n")

                        return True

            #Else Statements that will catch all files that are skipped, not files, or have not existant paths, and logs error.
            else:
                logging.warning('[' + repr(theFile) + ', Skipped NOT a File' + ']')
                return False
        else:
            logging.warning('[' + repr(theFile) + ', Skipped Link NOT a File' + ']')
            return False
    else:
        logging.warning('[' + repr(theFile) + ', Path does NOT exist' + ']')
        
    return False

# End FileScraper Function ===================================

# 
# Class: _CSVWriter 
#
# Desc: Handles all methods related to comma separated value operations
#
# Methods        constructor:     Initializes the CSV File
#                writeCVSRow:     Writes a single row to the csv file
#                writerClose:     Closes the CSV File

class _CSVWriter(object):

    def __init__(self, fileName, hashType):
        try:
            # Open/Create a writer object as self.csvFile.
            self.csvFile = open(fileName, 'w')
            #Establish file as having a comma delimiter.
            self.writer = csv.writer(self.csvFile, delimiter=',', quoting=csv.QUOTE_ALL)
            #Write a header row to the CSV file.
            self.writer.writerow( ('Path', 'File', 'Size', 'Modified Time', 'Accessed Time', 'Created Time', gl_hashType, 'Keyword') )
        #If file CSV file can't be opened or written to write error to log file.    
        except:
            logging.error('CSV File Failure')

    #Write a single row of results to CSV file that was passed from HashFile.
    def writeCSVRow(self, filePath, fileName, fileSize, mTime, aTime, cTime, hashVal, match):
        self.writer.writerow( (filePath, fileName, fileSize, mTime, aTime, cTime, hashVal, match))

    #Closes the csv file after write.
    def writerClose(self):
        self.csvFile.close()

# End _CSVWriter Class ===================================





#Create some global variables
match = ''
#Assign variable for hashtype as MD5.
gl_hashType = 'MD5'
#Create a set of valid setting to validate user input against.
gl_values = set(["YES", "NO"]) 
#Create empty list, for lowercase searchKeywords.
searchKeywordsLower = []


#Empty list for later functionality.  Not used at this time
#fileScanHits = []



#Print Initial Welcome Message in Console Window with a Line Break and more underlining characters.
print ("Welcome to " + str(SCRIPT_NAME) + " " + str(SCRIPT_VERSION) + "\n==========================")

#Use raw_input function to present console request to create a new job name.
jobName = input("\nPlease create a name for the new sifting job:")
print ('New Job: '+jobName+' Created')

# Turn on Logging using standard python logging package, assign logname variable, and set formating for time and messages.
logging.basicConfig(filename=jobName+'.log',level=logging.DEBUG,format='%(asctime)s %(message)s')

#Use the standar time module to record start time to startTime variable.
startTime = time.time()


# Record the welcome message and write to log.
logging.info('')
logging.info("Welcome to " + SCRIPT_NAME + " " + SCRIPT_VERSION + " New Scan Started")
logging.info('')
logging.info ('New Job Created: '+jobName)
logging.info('')

#Use the sys module to log the OS Platform and version.
logging.info('Detected Operating System: ' + sys.platform)
logging.info('Detected Operating System Version: ' + sys.version)
#logging.info('Detected Operating System Host Name: ' + os.environ['COMPUTERNAME'])
logging.info('')




#Get the target folder from the user
#==================================================================

#Start a while loop to aid in validation of user input.
while True:
    #Request user to specify target scan folder. First using Tkinter GUI, with console fall back.
    try:
        logging.info("Calling TK directory selection window... ")
        #Keep the root GUI window from appearing.
        Tk().withdraw()
        print('Opening folder selction window...')
        print('Please select a target folder to scan:')
        #Call GUI based directory open window using Tkinter.
        targetFolder = askdirectory(title='Please select a target folder to scan:') 
    
    except:
        #Calling TK GUI askdirectory window failed. Request user to specify targetFolder to scan, using raw_input from console.
        print("Failed to open folder selction window...")
        logging.info('Failed to open folder selection window. TKinter may not be installed. Falling back to console raw input.')
        targetFolder = input("Please manually enter folder path to scan: ")        
        
    print(targetFolder + ' Selected as Target Folder')    
    
    #Use os module to validate if specified folder is valid.
    if os.path.exists(targetFolder):
        #If folder is valid, print notification, log validation, and break loop to continue script.
        print("Valid Target Folder Entered!")
        logging.info("Valid Target Folder Entered: " + targetFolder)
        break
    
    #If os module determines targetFolder is not valid, prompt user with notification of problem, log error, the return to beginning of loop
    #so user can reenter a valid folder path.
    else:
        print("Invalid folder path entered.  Please try again.")
        logging.warning(targetFolder + " is not a valid directory")


#Setup process for keywordFiltering.
#Request user enable or disable this option.
#If so, import a text file of keywords and add words to searchKeywords set.
#==========================================================================


#Create empty variable called keywordFilteringEnabled to store user choice in.
keywordFilteringEnabled = []

#Start a while loop to aid in validation of user input.
while True:
    #Print out the valid user input options.
    print ('\nKeyword Filtering Enabled:\nYES\nNO')
    
    #Use raw_input function to present console request to user to enter keywordfiltering choice, and pass input converted to uppercase, to variable keywordFilteringEnabled.
    keywordFilteringEnabled = input("\nEnable Keyword Filtering?, or 'q' to exit:").upper()

    #Set q as break command to end while loop and exit script using sys modules exit function.
    if keywordFilteringEnabled == "Q":
        print (SCRIPT_NAME + " Closed")
        sys.exit(0)

    #Validates the raw_input against the valid choices in the set "values".  If input exists in "values", the while loop breaks and continues script.
    if keywordFilteringEnabled in gl_values:
        print ('\nValid Keyword Filtering Choice Entered')
        logging.info('Keyword Filtering Selection Validated')
        break
    
    else:
        
        #If raw_input not in set "gl_values", prints error message and returns to raw_input prompt.
        print("\nNot a Valid choice!\nValid Keyword Filtering Choices:\nYES\nNO")

#If keyword filtering enabled, get the keyword list and process it.
if keywordFilteringEnabled == 'YES':
    
    #Create am empty set to hold searchKeyword.
    searchKeywords = set()    

    #Start a while loop to aid in validation of user input.
    while True:
        #Request user to specify keyword text file to import first using Tkinter GUI, with console fall back.
        try:
            
            logging.info("Calling TK file selection window... ")
            print('\nPlease enter text file with keywords to search filenames for.\n(A plain text file with 1 word per line is recommended): ')
            #Keep the root GUI window from appearing.
            Tk().withdraw() 
            print('Opening file selction window...')
            print('Please select plain text file containing keywords:')            
            #Call GUI based file open window using Tkinter.
            keywordFileInput = askopenfilename(title='Please select plain text file containing keywords:', filetypes=[("text files",".txt")]) # show an "Open" dialog box and return the path to the selected file
            
        except:
            #Calling TK GUI askopenfilename window failed. Request user to specify keyword file to import, using raw_input from console.
            print("Failed to open file selction window...")
            logging.warning('Failed to open file selection window. TKinter may not be installed. Falling back to console raw input.')
            keywordFileInput = input("\nPlease manually specify text file with keywords to search filenames for.\n(A plain text file with 1 word per line is recommended): ")
                      
        
        
        print(keywordFileInput + ' Selected')        
        
        #Use os module to validate if specified folder is valid.
        if os.path.exists(keywordFileInput):
            
            # Verify that the path is valid
            if os.path.exists(keywordFileInput):
        
                #Verify that the path is not a symbolic link
                if not os.path.islink(keywordFileInput):
        
                    #Verify that the file is real.
                    if os.path.isfile(keywordFileInput):
                        
                        #Add file validation to log.
                        logging.info("Keyword File is valid file")
                        print('Keyword File Found')                  
                        break
    
                #Else Statements that will catch if keywordFileInput is skipped, not a file, or does not existant path, and logs error.
                else:
                    logging.warning('[' + repr(keywordFileInput) + ', Skipped NOT a File' + ']')
                    
            else:
                logging.warning('[' + repr(keywordFileInput) + ', Skipped Link NOT a File' + ']')
        else:
            logging.warning('[' + repr(keywordFileInput) + ', Path does NOT exist' + ']')        
    
    
    #Call the the BuildKeywordList function to try and build the keyword list.
    BuildKeywordList()  
   
        
#If keyword filtering disabled, skip txt file import and continue script.
elif keywordFilteringEnabled == 'NO':
    logging.info('Keyword Filtering Enabled: ' + keywordFilteringEnabled)
    print('Keyword Filtering is Disabled')
    print('All Files In Target Folder Will Be Processed and Collected')
        
#==================================================================


#Request user to enabled file collection and set desired compression container type for collected files.
#==========================================================================


#Create empty variable called fileCollectionEnabled to store user choice in.
fileCollectionEnabled = []

#Start a while loop to aid in validation of user input.
while True:
    #Print out the valid user input options.
    print ('\nFile Collection Enabled:\nYES\nNO')
    
    #Use raw_input function to present console request to user to enter file collection choice, and pass input converted to uppercase, to variable fileCollectionEnabled.
    fileCollectionEnabled = input("\nEnable File Collection?, or 'q' to exit:").upper()

    #Set q as break command to end while loop and exit script using sys modules exit function.
    if fileCollectionEnabled == "Q":
        print (SCRIPT_NAME + " Closed")
        sys.exit(0)

    #Validates the raw_input against the valid choices in the set "gl_values".  If input exists in "gl_values", the while loop breaks and continues script.
    if fileCollectionEnabled in gl_values:
        print ('\nValid File Collection Choice Entered')
        logging.info('File Collection Selection Validated')
        break
    
    else:
        
        #If raw_input not in set "gl_values", prints error message and returns to raw_input prompt.
        print("\nNot a Valid choice!\nValid File Collection Choices:\nYES\nNO")


#File Collection Enabled.  Get some settings from the user to set it up.
if fileCollectionEnabled == 'YES':
    
    #Log that file collection is turned on.
    logging.info('File Collection Enabled')
    
    #Create a set of valid compression choices to validate user input against.
    containerFormats = set(["ZIP", "TAR"])
    
    #Create empty variable called compressionChoice
    compressionChoice = []
    
    #Use raw_input function to present console request to user name the zip or tar file that will be created.
    containerName = str(jobName)
    
    #Start a while loop to aid in user input validation.
    while True:
        print ('\nValid Compression Choices:\nTAR\nZIP')
        
        #Use raw_input function to present console request to user to enter compression choice, and pass input converted to uppercase, to variable compressionChoice.
        compressionChoice = input("Please enter compression choice, or 'q' to exit:").upper()    
    
        #Set q as break command to end while loop and exit script using sys modules exit function.
        if compressionChoice == "Q":
            print (SCRIPT_NAME + " Closed")
            sys.exit(0)
        
        #Create an empty zip container if ZIP selected
        if compressionChoice == "ZIP":   
            z = zipfile.ZipFile(containerName + ".zip", "w",zipfile.ZIP_DEFLATED)
            z.close()    
    
        #Validates the raw_input against the valid choices in the set "containerFormats".  If input exists in "containerFormats", the while loop breaks and continues script.
        if compressionChoice in containerFormats:
            print (compressionChoice + ' Selected')
            logging.info('Compression Container Choice Set To: ' + compressionChoice)  
            break
        
        else:
            
            #If raw_input not in set "containerFormats", prints error message and returns to raw_input prompt.
            print("Not a Valid choice!\nValid Compression Choices:\nTAR\nZIP")
    
    
    print ('Collected files will be added to: ' +containerName + '.' + compressionChoice) 


#File collection disabled.  Print confirmation and log setting.
else:
    print('File Collection Disabled. File Sifter will operate in Scan Only Mode Only\n')
    #Log that file collection is turned off.
    logging.info('File Collection Disabled')

#==================================================================    
    
#Provide final confirmation message before starting the sifting process...
input('Now ready to begin sifting files...Press Enter to Continue...')

# Calls the WalkPath function, and assign count of files to filesProcessed variable.
logging.info('Sifting Started...')
WalkPath()

    
#==================================================================

#Finish Things up...

# Record the end time and calculate the duration for all processing.
endTime = time.time()
duration = endTime - startTime

#Write out a count of files process, the duration in seconds, and notifiction of Normal Termination to log file.
logging.info('Files Processed: ' + str(counter) )
logging.info('Elapsed Time: ' + str(duration) + ' seconds')
logging.info('')
logging.info('Program Terminated Normally')
logging.info('')

#Print notification in console that program has completed.
print ('Files Processed: ' + str(counter) )
print ("File Sifter Completed")


