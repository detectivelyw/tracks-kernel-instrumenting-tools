import sys, os, string, getopt

def process_csv(infile, outfile, src_file): 
   for line in infile:
     if line.startswith(src_file):
       outfile.write(line)

def main(argv):
   inputfile = ''
   outputfile = './ast_data.txt'
   src_file = ''
   try:
      opts, args = getopt.getopt(argv,"hi:d:",["ifile=","dir="])
   except getopt.GetoptError:
      print 'process-kernel-node-csv.py -i <kernel-csv-file> -d <dir_in_csv>'
      sys.exit(2)

   for opt, arg in opts:
      if opt == '-h':
         print 'process-kernel-node-csv.py -i <kernel-csv-file> -d <dir_in_csv>'
         sys.exit()
      elif opt in ("-i", "--ifile"):
         inputfile = arg
      elif opt in ("-d", "--dir"):
         src_file = arg   

   if os.path.isfile(inputfile):
     infile = open(inputfile, 'r')
     outfile = open(outputfile, 'w')
     process_csv(infile, outfile, src_file)
     infile.close()
     outfile.close()
   else:
     print "File: ", inputfile, " does not exist!"
     sys.exit(2)

if __name__ == "__main__":
   main(sys.argv[1:])
