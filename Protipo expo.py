#~/usr/bin/env python
import sys,os
import pefile
import hashlib
import xlsxwriter
import vt
import time

if __name__ == "__main__":
    #Define our virustotal API
    client = vt.Client("24b0d1fa768a3ed1fd9a5ed34df6e1c4c1b59fee982f1721dba362464a623a30")
    
    #Identify specified folder with suspect files
    dir_path = sys.argv[1]
 
    #Create a list of files with full path
    file_list = []
    for folder, subfolder, files in os.walk(dir_path):
        for f in files:
            full_path = os.path.join(folder, f)
            file_list.append(full_path)
 
    #Open XLSX file for writing
    file_name = "results.xlsx"
    workbook = xlsxwriter.Workbook(file_name)
    bold = workbook.add_format({'bold':True})
    worksheet = workbook.add_worksheet()
 
    #Write column headings
    row = 0
    worksheet.write('A1', 'SHA256', bold)
    worksheet.write('B1', 'Imphash', bold)
    worksheet.write('C1', 'Route', bold)
    worksheet.write('D1', 'Malware indicators', bold)
    worksheet.write('E1', 'URL', bold)
    row += 1
    
    
    # Counter to wait for virustotal api response
    counter = 0
    
    #Iterate through file_list to calculate imphash and sha256 file hash
    for item in file_list:
        analysis_results = ""
        url = ""
        
        if counter == 4: #Waiting to limit requests at virustotal
            time.sleep(60)
            counter = 0
            
        #Get route of the file
        route = str(item)

        #Get sha256
        fh = open(item, "rb")
        data = fh.read()
        fh.close()
        sha256 = hashlib.sha256(data).hexdigest()
 
        #Get import table hash
        pe = pefile.PE(item)
        ihash = pe.get_imphash()             
        
        #Get virustotal analysis
        try:
            file = client.get_object("/files/"+str(sha256))
            analysis_results = file.last_analysis_stats
            url = "https://www.virustotal.com/gui/file/" + str(sha256)
        except:
            pass
        
        #Write the info to the document
        worksheet.write(row, 0, sha256)
        worksheet.write(row, 1, ihash)
        worksheet.write(row, 2, route)
        worksheet.write(row, 3, str(analysis_results))
        worksheet.write(row, 4, str(url))
        
        row += 1
        counter+=1
    client.close()
    workbook.close()
