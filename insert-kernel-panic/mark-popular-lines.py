"""""""""""""""""
Author: Yiwen Li
"""""""""""""""""

import sys, os, string, getopt

POP_FILE_MAX = 3000

def main(argv):
   inputfile = ''
   outputfile = ''
   try:
      opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
   except getopt.GetoptError:
      print 'insert-kernel-panic.py -i <gcov-results-file> -o <outputfile>'
      sys.exit(2)

   for opt, arg in opts:
      if opt == '-h':
         print 'insert-kernel-panic.py -i <gcov-results-file> -o <outputfile>'
         sys.exit()
      elif opt in ("-i", "--ifile"):
         inputfile = arg
      elif opt in ("-o", "--ofile"):
         outputfile = arg   

   if os.path.isfile(inputfile):
     infile = open(inputfile, 'r')
     outfile = open(outputfile, 'w')
     insert_kernel_panic(infile, outfile)
     infile.close()
     outfile.close()
   else:
     print "File: ", inputfile, " does not exist!"
     sys.exit(2)

def insert_kernel_panic(infile, outfile):
    src_path = ""
    popular_lines_index = 0
    popular_lines_total = 0
    popular_lines_list = POP_FILE_MAX * [0]

    for lines in infile:
      if ("SF:" in lines):
        src_path = lines.rstrip(os.linesep)
        src_path = src_path[3:]
        print src_path
      else:
        if lines != "\n":
          line_num = int(lines)
          popular_lines_list[popular_lines_index] = line_num
          popular_lines_index += 1
          print "[popular_line " + str(popular_lines_index) + "] " + str(line_num)
          popular_lines_total = popular_lines_index
     
    # for i in range(0, popular_lines_total):
    #   print "[popular_line " + str(i+1) + "] " + str(popular_lines_list[i])
    #   outfile.write("[popular_line " + str(i+1) + "] " + str(popular_lines_list[i]) + "\n")

    srcfile = open(src_path, 'r')
    src_line_num = 1
    popular_lines_index = 0
    for src_line in srcfile: 
      if src_line_num == popular_lines_list[popular_lines_index]:
        popular_lines_index += 1
        print "[src_line " + str(src_line_num) + " *** popular line ***] " + src_line
        outfile.write("[src_line " + str(src_line_num) + " *** popular line ***] " + src_line)   
      else:
        print "[src_line " + str(src_line_num) + " *** unpopular line ***] " + src_line
        outfile.write("[src_line " + str(src_line_num) + " *** unpopular line ***] " + src_line) 
      src_line_num += 1


if __name__ == "__main__":
   main(sys.argv[1:])
