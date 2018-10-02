"""""""""""""""""""""""

<Author> Yiwen Li

<Program description> 
This script works in the following way: 
1. It reads in the Gcov data(processed) first.
2. For each source file in the Gcov data:
  2.1 Go through the popular lines for that source file and store the popular-lines info in the popular_lines_list[]
  2.2 Go through the ast data for that source file and store the ast-nodes info in the ast_info dict. 
  2.3 Read the actual source file now and go through each line in it. For each line, use the popular-lines info 
      and the ast-nodes info we have acquired to determine if we are going to insert a panic call at this line. 
  2.4 Write the line with (or without) our panic call to our output source file. 
3. Go through all the source files, and then we are done.  

"""""""""""""""""""""""


import sys, os, string, getopt

POP_FILE_MAX = 10000
SRC_FILE_MAX = 20000
src_root_path = "/home/detectivelyw/Documents/projects/tracks/linux-stable/"

def insert_kernel_panic(gcov_data_file, ast_data_file):
    src_path = ""
    output_path = ""
    popular_lines_index = 0
    popular_lines_total = 0
    popular_lines_list = POP_FILE_MAX * [0]
    source_lines_list = SRC_FILE_MAX * [0]
    total_panic_inserted = 0

    # go through the Gcov data file, find and process each source file
    # first, read the Gcov kernel trace popular paths data into our popular_lines_list[POP_FILE_MAX] array
    for lines in gcov_data_file:
      if ("SF:" in lines):
        src_path = lines.rstrip(os.linesep)
        src_path = src_path[3:]
        popular_lines_list = POP_FILE_MAX * [0]
        popular_lines_index = 0
        popular_lines_total = 0
      else:
        if lines != "\n":
          line_num = int(lines)
          popular_lines_list[popular_lines_index] = line_num
          popular_lines_index += 1
          popular_lines_total = popular_lines_index
        else:
          # when we reached the end of one source file data in the Gcov results, start processing the corresponding
          # ast node data of that source file
          # read the ast node info of the given source file, and load it into our ast_info dictionary
          ast_info = dict()
          ast_data = open(ast_data_file, 'r')
          for ast_line in ast_data:
            if (ast_line.startswith(src_path)):
              line_info = ast_line.split(",")
              if line_info[1] in ast_info:
                ast_info[line_info[1]].append(line_info[2][:-1])
              else:
                ast_info[line_info[1]] = [line_info[2][:-1]]
          ast_data.close()

          # now create the output file(instrumented source file)
          src_path = src_root_path + src_path
          output_path = src_path + ".new"
          srcfile = open(src_path, 'r')
          output_file = open(output_path, 'w')

          src_line_num = 1
          popular_lines_index = 0
          source_lines_list = SRC_FILE_MAX * [0]
          for src_line in srcfile: 
            if src_line_num == popular_lines_list[popular_lines_index]:
              popular_lines_index += 1
              source_lines_list[src_line_num] = 1
            else:
              source_lines_list[src_line_num] = 0
            src_line_num += 1
          srcfile.close()
          
          srcfile = open(src_path, 'r')
          print "working on: " + src_path
          src_line_num = 1
          instrumented_src_line_num = 1
          popular_lines_index = 0
          is_unpopular_function = 0
          
          panic_header = "#include <linux/kernel.h> \n"
          output_file.write(panic_header)
          instrumented_src_line_num += 1

          for src_line in srcfile: 
            if (is_unpopular_function == 1) and (src_line == "{\n"):
              output_file.write(src_line)
              instrumented_src_line_num += 1
              output_file.write("	if (kernel_init_done) panic(" + "\"We reached unpopular paths in " + src_path[len(src_root_path):] + ": line " + str(instrumented_src_line_num) + " \\n\"); \n")
              total_panic_inserted += 1
              print str(total_panic_inserted) + " panic() calls inserted"
              src_line_num += 1
              instrumented_src_line_num += 1
              is_unpopular_function = 0
              continue     

            if source_lines_list[src_line_num] == 1:
              if str(src_line_num) not in ast_info:
                # output_file.write("[src_line " + str(src_line_num) + " *** popular line ***] " + src_line)
                output_file.write(src_line)
              else:
                if "FunctionDefinition" in ast_info[str(src_line_num)]:
                  # output_file.write("[src_line " + str(src_line_num) + " *** popular line *** <FunctionDefinition> ] " + src_line)   
                  output_file.write(src_line)
                else:
                  if "ParameterDeclaration" in ast_info[str(src_line_num)]:
                    is_unpopular_function = 0
                    # output_file.write("[src_line " + str(src_line_num) + " *** popular line *** <ParameterDeclaration> ] " + src_line)
                    output_file.write(src_line)
                  else:
                    # output_file.write("[src_line " + str(src_line_num) + " *** popular line ***] " + src_line)
                    output_file.write(src_line)
            else:
              if str(src_line_num) not in ast_info:
                # output_file.write("[src_line " + str(src_line_num) + " *** unpopular line ***] " + src_line) 
                output_file.write(src_line)
              else:
                if "FunctionDefinition" in ast_info[str(src_line_num)]:
                  is_unpopular_function = 1
                  # output_file.write("[src_line " + str(src_line_num) + " *** unpopular line *** <FunctionDefinition>] " + src_line)
                  output_file.write(src_line)
                else: 
                  if "ParameterDeclaration" in ast_info[str(src_line_num)]:
                    # output_file.write("[src_line " + str(src_line_num) + " *** unpopular line *** <ParameterDeclaration>] " + src_line)
                    output_file.write(src_line)
                  else:
                    # output_file.write("[src_line " + str(src_line_num) + " *** unpopular line ***] " + src_line) 
                    output_file.write(src_line)
            src_line_num += 1
            instrumented_src_line_num += 1
          srcfile.close()
          print src_path + " done!"
          output_file.close()
    print "Program has finished!"
    print "Totally " + str(total_panic_inserted) + " panic() calls have been inserted!"

def main(argv):
   gcov_data = ''
   ast_data = ''
   try:
      opts, args = getopt.getopt(argv,"hg:a:",["gcov=","ast="])
   except getopt.GetoptError:
      print 'insert-kernel-panic.py -g <gcov-data-file> -a <ast-data-file>'
      sys.exit(2)

   for opt, arg in opts:
      if opt == '-h':
         print 'insert-kernel-panic.py -g <gcov-data-file> -a <ast-data-file>'
         sys.exit()
      elif opt in ("-g", "--gcov"):
         gcov_data = arg
      elif opt in ("-a", "--ast"):
         ast_data = arg   

   if os.path.isfile(gcov_data):
     gcov_data_file = open(gcov_data, 'r')
     insert_kernel_panic(gcov_data_file, ast_data)
     gcov_data_file.close()
   else:
     print "File: ", inputfile, " does not exist!"
     sys.exit(2)


if __name__ == "__main__":
   main(sys.argv[1:])
