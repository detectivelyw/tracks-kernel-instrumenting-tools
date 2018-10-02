import sys, os, string, getopt

root_path = "SF:/home/detectivelyw/Documents/projects/tracks/linux-stable/"

def process_gcov(infile, outfile, src_file): 
   is_data_requested = 0
   for line in infile:
     if "SF:" in line:
       src_file_relative_path = line[len(root_path):]
       if src_file_relative_path.startswith(src_file):
         is_data_requested = 1
         # print src_file_relative_path
         outfile.write("SF:" + src_file_relative_path)
       else:
         is_data_requested = 0
     else: 
       if is_data_requested == 1:
         outfile.write(line)
       

def main(argv):
   inputfile = ''
   outputfile = './gcov_data.txt'
   src_file = ''
   try:
      opts, args = getopt.getopt(argv,"hi:d:",["ifile=","dir="])
   except getopt.GetoptError:
      print 'process-gcov-data.py -i <gcov-results-file> -d <dir_in_gcov_results>'
      sys.exit(2)

   for opt, arg in opts:
      if opt == '-h':
         print 'process-gcov-data.py -i <gcov-results-file> -d <dir_in_gcov_results>'
         sys.exit()
      elif opt in ("-i", "--ifile"):
         inputfile = arg
      elif opt in ("-d", "--dir"):
         src_file = arg   

   if os.path.isfile(inputfile):
     infile = open(inputfile, 'r')
     outfile = open(outputfile, 'w')
     process_gcov(infile, outfile, src_file)
     infile.close()
     outfile.close()
   else:
     print "File: ", inputfile, " does not exist!"
     sys.exit(2)

if __name__ == "__main__":
   main(sys.argv[1:])
