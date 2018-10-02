import sys, os, string, getopt


def generate_blacklist(infile, outfile): 
   blacklist = dict()
   prefix_string = " We reached unpopular paths in "
   for line in infile:
     if "We reached unpopular paths" in line:
       line_info = line.split("]")
       line = line_info[1][len(prefix_string):]
       if line not in blacklist:
         print line
         outfile.write(line) 
         blacklist[line] = 1
   

def main(argv):
   inputfile = ''
   outputfile = ''
   try:
      opts, args = getopt.getopt(argv,"hi:",["ifile="])
   except getopt.GetoptError:
      print 'generate-panic-blacklist.py -i <printk-log>'
      sys.exit(2)

   for opt, arg in opts:
      if opt == '-h':
         print 'generate-panic-blacklist.py -i <printk-log>'
         sys.exit()
      elif opt in ("-i", "--ifile"):
         inputfile = arg

   outputfile = inputfile + ".blacklist"
   if os.path.isfile(inputfile):
     infile = open(inputfile, 'r')
     outfile = open(outputfile, 'w')
     generate_blacklist(infile, outfile)
     infile.close()
     outfile.close()
   else:
     print "File: ", inputfile, " does not exist!"
     sys.exit(2)

if __name__ == "__main__":
   main(sys.argv[1:])
