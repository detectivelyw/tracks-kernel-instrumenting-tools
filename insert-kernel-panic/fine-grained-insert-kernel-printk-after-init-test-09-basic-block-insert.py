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

          global_int_var_header = "extern int kernel_init_done; \n"
          # output_file.write("[src_line " + str(instrumented_src_line_num) + " *** inserted line ***] " + global_int_var_header)
          output_file.write(global_int_var_header)
          instrumented_src_line_num += 1

          linkage_header = "#include <linux/linkage.h> \n"
          # output_file.write("[src_line " + str(instrumented_src_line_num) + " *** inserted line ***] " + linkage_header)
          output_file.write(linkage_header)
          instrumented_src_line_num += 1

          asm_line = "asmlinkage __printf(1, 2) __cold \n"
          # output_file.write("[src_line " + str(instrumented_src_line_num) + " *** inserted line ***] " + asm_line)
          output_file.write(asm_line)
          instrumented_src_line_num += 1

          printk_header = "int printk(const char *fmt, ...); \n"
          # output_file.write("[src_line " + str(instrumented_src_line_num) + " *** inserted line ***] " + printk_header)
          output_file.write(printk_header)
          instrumented_src_line_num += 1

          num_total_inserted_lines_srcfile = 0
          # indicate whether we are inside of a function: <0:not>; <1:in>; <2:ready,just saw functionName>
          is_inside_function = 0
          parenthesis_counter = 0
          is_if_single = 2
          is_consecutive_unpopular_expression = 2

          for src_line in srcfile: 
            if "{" in src_line:
              if is_inside_function == 2:
                is_inside_function = 1
                parenthesis_counter = 0
              if is_inside_function == 1:
                parenthesis_counter += 1

            if "}" in src_line:
              if is_inside_function == 1:
                parenthesis_counter -= 1
                # print "!!! parenthesis_counter = " + str(parenthesis_counter) + "\n"  
              if parenthesis_counter == 0:
                is_inside_function = 0
                # print "!!! End of function !!!"

            # try to identify if this line is split from a multiple-line function call or statement
            count_left_parenthesis = src_line.count('(')
            count_right_parenthesis = src_line.count(')')
            if count_right_parenthesis > count_left_parenthesis:
              is_consecutive_unpopular_expression = 1
              

            if (is_unpopular_function == 1) and (src_line == "{\n"):
              output_file.write(src_line)
              instrumented_src_line_num += 1
              # if is_inside_function == 1:
                # output_file.write("[src_line " + str(instrumented_src_line_num) + " *** inserted line *** <Printk> (InFunction)] " + "	if (kernel_init_done == 1) printk(" + "\"We reached unpopular paths in " + src_path[len(src_root_path):] + ": line " + str(instrumented_src_line_num) + " \\n\"); \n")
              # else:
                # output_file.write("[src_line " + str(instrumented_src_line_num) + " *** inserted line *** <Printk> ] " + "	if (kernel_init_done == 1) printk(" + "\"We reached unpopular paths in " + src_path[len(src_root_path):] + ": line " + str(instrumented_src_line_num) + " \\n\"); \n")
              output_file.write("	if (kernel_init_done == 1) printk(" + "\"We reached unpopular paths in " + src_path[len(src_root_path):] + ": line " + str(instrumented_src_line_num) + " \\n\"); \n")
              total_panic_inserted += 1
              num_total_inserted_lines_srcfile += 1
              print str(total_panic_inserted) + " printk() calls inserted"
              src_line_num += 1
              instrumented_src_line_num += 1
              is_unpopular_function = 0
              continue     

            if source_lines_list[src_line_num] == 1:
              if str(src_line_num) not in ast_info:
                # if is_inside_function == 1: 
                #   output_file.write("[src_line " + str(instrumented_src_line_num) + " *** popular line *** (InFunction)] " + src_line)
                # else:
                #   output_file.write("[src_line " + str(instrumented_src_line_num) + " *** popular line ***] " + src_line)
                output_file.write(src_line)
              else:
                if "FunctionDefinition" in ast_info[str(src_line_num)]:
                  is_inside_function = 2
                  # output_file.write("[src_line " + str(instrumented_src_line_num) + " *** popular line *** <FunctionDefinition> ] " + src_line)   
                  output_file.write(src_line)
                else:
                  if "ParameterDeclaration" in ast_info[str(src_line_num)]:
                    is_inside_function = 2
                    is_unpopular_function = 0
                    # output_file.write("[src_line " + str(instrumented_src_line_num) + " *** popular line *** <ParameterDeclaration> ] " + src_line)
                    output_file.write(src_line)
                  else:
                    is_expression = 0
                    for node_type in ast_info[str(src_line_num)]:
                      if "IfStatement" in node_type:
                        if "{" not in src_line:
                          is_if_single = 0
                        output_file.write(src_line)
                        is_expression = 1
                        break
                      if "Expression" in node_type:
                        # if is_inside_function == 1:
                        #   output_file.write("[src_line " + str(instrumented_src_line_num) + " *** popular line *** <Expression> (InFunction)] " + src_line)
                        # else:
                        #   output_file.write("[src_line " + str(instrumented_src_line_num) + " *** popular line *** <Expression> ] " + src_line)
                        output_file.write(src_line)
                        is_expression = 1
                        break
                    if is_expression == 0:
                      # if is_inside_function == 1:
                      #   output_file.write("[src_line " + str(instrumented_src_line_num) + " *** popular line *** (InFunction)] " + src_line)
                      # else:
                      #   output_file.write("[src_line " + str(instrumented_src_line_num) + " *** popular line *** ] " + src_line)
                      output_file.write(src_line)

            else:
              if str(src_line_num) not in ast_info:
                # if is_inside_function == 1:
                #   output_file.write("[src_line " + str(instrumented_src_line_num) + " *** unpopular line *** (InFunction)] " + src_line)
                # else:
                #   output_file.write("[src_line " + str(instrumented_src_line_num) + " *** unpopular line ***] " + src_line) 
                output_file.write(src_line)
              else:
                if "FunctionDefinition" in ast_info[str(src_line_num)]:
                  is_inside_function = 2
                  is_unpopular_function = 1
                  # output_file.write("[src_line " + str(instrumented_src_line_num) + " *** unpopular line *** <FunctionDefinition>] " + src_line)
                  output_file.write(src_line)
                else: 
                  if "ParameterDeclaration" in ast_info[str(src_line_num)]:
                    is_inside_function = 2
                    # output_file.write("[src_line " + str(instrumented_src_line_num) + " *** unpopular line *** <ParameterDeclaration>] " + src_line)
                    output_file.write(src_line)
                  else:
                    is_expression = 0
                    for node_type in ast_info[str(src_line_num)]:
                      if "IfStatement" in node_type:
                        if "{" not in src_line:
                          is_if_single = 0
                        if is_inside_function == 1:
                          if is_if_single == 1:
                            if is_consecutive_unpopular_expression == 1:
                              is_consecutive_unpopular_expression = 0
                              output_file.write(src_line)
                              is_expression = 1
                              break
                            else:
                              output_file.write("	{  if (kernel_init_done == 1) printk(" + "\"We reached unpopular paths in " + src_path[len(src_root_path):] + ": line " + str(instrumented_src_line_num) + " \\n\"); \n")
                              is_consecutive_unpopular_expression = 0
                          else:
                            if is_consecutive_unpopular_expression == 1:
                              is_consecutive_unpopular_expression = 0
                              output_file.write(src_line)
                              is_expression = 1
                              break
                            else:
                              # output_file.write("[src_line " + str(instrumented_src_line_num) + " *** unpopular line *** <Expression> (InFunction)] " + src_line)
                              output_file.write("	if (kernel_init_done == 1) printk(" + "\"We reached unpopular paths in " + src_path[len(src_root_path):] + ": line " + str(instrumented_src_line_num) + " \\n\"); \n")
                              is_consecutive_unpopular_expression = 0

                          total_panic_inserted += 1
                          num_total_inserted_lines_srcfile += 1
                          print str(total_panic_inserted) + " printk() calls inserted"
                          instrumented_src_line_num += 1
                        # else:
                          # output_file.write("[src_line " + str(instrumented_src_line_num) + " *** unpopular line *** <Expression> ] " + src_line)
                        if is_if_single == 1:
                          output_file.write(src_line + "  } \n")
                          instrumented_src_line_num += 1
                        else:
                          output_file.write(src_line)
                        is_expression = 1
                        break
                      if "Expression" in node_type:
                        if is_inside_function == 1:
                          if is_if_single == 1: 
                            if is_consecutive_unpopular_expression == 1:
                              is_consecutive_unpopular_expression = 0
                              output_file.write(src_line)
                              is_expression = 1
                              break
                            else: 
                              output_file.write("	{  if (kernel_init_done == 1) printk(" + "\"We reached unpopular paths in " + src_path[len(src_root_path):] + ": line " + str(instrumented_src_line_num) + " \\n\"); \n")
                              is_consecutive_unpopular_expression = 0
                          else:
                            if is_consecutive_unpopular_expression == 1:
                              is_consecutive_unpopular_expression = 0
                              output_file.write(src_line)
                              is_expression = 1
                              break
                            else:
                              # output_file.write("[src_line " + str(instrumented_src_line_num) + " *** unpopular line *** <Expression> (InFunction)] " + src_line)
                              output_file.write("	if (kernel_init_done == 1) printk(" + "\"We reached unpopular paths in " + src_path[len(src_root_path):] + ": line " + str(instrumented_src_line_num) + " \\n\"); \n")
                              is_consecutive_unpopular_expression = 0
                          
                          total_panic_inserted += 1
                          num_total_inserted_lines_srcfile += 1
                          print str(total_panic_inserted) + " printk() calls inserted"
                          instrumented_src_line_num += 1
                        # else:
                          # output_file.write("[src_line " + str(instrumented_src_line_num) + " *** unpopular line *** <Expression> ] " + src_line)
                        if is_if_single == 1:
                          output_file.write(src_line + "  } \n")
                          instrumented_src_line_num += 1
                        else:
                          output_file.write(src_line)
                        is_expression = 1
                        break
                    if is_expression == 0:
                      # if is_inside_function == 1:
                      #   output_file.write("[src_line " + str(instrumented_src_line_num) + " *** unpopular line *** (InFunction)] " + src_line)
                      # else:
                      #   output_file.write("[src_line " + str(instrumented_src_line_num) + " *** unpopular line *** ] " + src_line)
                      output_file.write(src_line)

            src_line_num += 1
            instrumented_src_line_num += 1
            is_if_single += 1
            is_consecutive_unpopular_expression += 1
          srcfile.close()
          print src_path + " done!"
          print src_path + ": " + str(num_total_inserted_lines_srcfile)
          output_file.close()
          if num_total_inserted_lines_srcfile == 0:
            os.remove(output_path)
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
