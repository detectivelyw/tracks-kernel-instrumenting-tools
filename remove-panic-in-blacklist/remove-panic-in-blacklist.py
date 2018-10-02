import sys, os, string, getopt

src_root_path = "/home/detectivelyw/Documents/projects/tracks/linux-stable/"

def remove_panic_in_blacklist(blacklist_file):
    blacklist_dict = dict()
    for line in blacklist_file:
      line_info = line.split(":")
      src_path = src_root_path + line_info[0]
      if line_info[1][-2] == ' ':
        blacklist_line_num = line_info[1][6:-2]
      else:
        blacklist_line_num = line_info[1][6:-1]
      if blacklist_line_num.endswith('\r'):
        tmp_num = blacklist_line_num[:-1]
        blacklist_line_num = tmp_num
      if blacklist_line_num.endswith(' '):
        tmp_num = blacklist_line_num[:-1]
        blacklist_line_num = tmp_num
      if src_path in blacklist_dict: 
        blacklist_dict[src_path].append(blacklist_line_num)
      else:
        blacklist_dict[src_path] = [blacklist_line_num]
    
    print blacklist_dict

    total_panic_removed = 0
    for src in blacklist_dict:    
      output_path = src + ".new"
      srcfile = open(src, 'r')
      output_file = open(output_path, 'w')
      src_line_num = 1

      for src_line in srcfile:
        if str(src_line_num) in blacklist_dict[src]:
          output_file.write("// [blacklist] " + src_line)
          total_panic_removed += 1
        else: 
          output_file.write(src_line)
        src_line_num += 1

      srcfile.close()
      output_file.close()
    print "total panic() calls removed: " + str(total_panic_removed)

def main(argv):
   blacklist = ''
   try:
      opts, args = getopt.getopt(argv,"hb:",["blacklist="])
   except getopt.GetoptError:
      print 'remove-panic-in-blacklist.py -b <blacklist>'
      sys.exit(2)

   for opt, arg in opts:
      if opt == '-h':
         print 'remove-panic-in-blacklist.py -b <blacklist>'
         sys.exit()
      elif opt in ("-b", "--blacklist"):
         blacklist = arg   

   if os.path.isfile(blacklist):
     blacklist_file = open(blacklist, 'r')
     remove_panic_in_blacklist(blacklist_file)
     blacklist_file.close()
   else:
     print "File: ", inputfile, " does not exist!"
     sys.exit(2)


if __name__ == "__main__":
   main(sys.argv[1:])
