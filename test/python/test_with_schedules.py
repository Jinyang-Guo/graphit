#!/usr/local/bin/python

import unittest
import subprocess
import os
import shutil
import sys

use_parallel = False

class TestGraphitCompiler(unittest.TestCase):
    first_time_setup = True

    #NOTE: currently the tests can only work within the build/bin directory
    @classmethod
    def setUpClass(cls):
        build_dir = "../../build"
        if not os.path.isdir(build_dir):
            print "build the binaries"
            #shutil.rmtree("../../build_dir")
            os.mkdir(build_dir)
            os.chdir(build_dir)
            subprocess.call(["cmake", ".."])
            subprocess.call(["make"])
            os.chdir('./bin')
        else:
            # working directory is in the bin folder
            os.chdir(build_dir)
            os.chdir('./bin')

        cwd = os.getcwd()

        cls.root_test_input_dir = "../test/input/"
        cls.cpp_compiler = "g++"
        cls.compile_flags = "-std=c++11"
        cls.include_path = "../src/runtime_lib"
        cls.output_file_name = "test.cpp"
        cls.executable_file_name = "test.o"


    def setUp(self):
        self.clean_up()

        #def tearDown(self):
        #self.clean_up()

    def clean_up(self):
        #clean up previously generated files
        if os.path.isfile(self.output_file_name):
            os.remove(self.output_file_name)
        if os.path.isfile(self.executable_file_name):
            os.remove(self.executable_file_name)

    def basic_compile_test(self, input_file_name):
        input_with_schedule_path = '../../test/input_with_schedules/'
        print os.getcwd()
        compile_cmd = "python graphitc.py -f " + input_with_schedule_path + input_file_name + " -o test.cpp"
        print compile_cmd
        subprocess.check_call(compile_cmd, shell=True)
        cpp_compile_cmd = "g++ -g -std=c++11 -I ../../src/runtime_lib/  test.cpp -o test.o"

        if use_parallel:
            print "using icpc for parallel compilation"
            cpp_compile_cmd = "icpc -g -std=c++11 -I ../../src/runtime_lib/ -DCILK test.cpp -o test.o"

        subprocess.check_call(cpp_compile_cmd, shell=True)

    def basic_compile_exec_test(self, input_file_name):
        input_with_schedule_path = '../../test/input_with_schedules/'
        print os.getcwd()
        compile_cmd = "python graphitc.py -f " + input_with_schedule_path + input_file_name + " -o test.cpp"
        print compile_cmd
        subprocess.check_call(compile_cmd, shell=True)
        subprocess.check_call("g++ -g -std=c++11 -I ../../src/runtime_lib/  test.cpp "  " -o test.o", shell=True)
        os.chdir("..")
        subprocess.check_call("bin/test.o")
        os.chdir("bin")


        # actual test cases

    def bfs_verified_test(self, input_file_name):
        self.basic_compile_test(input_file_name)
        os.chdir("..");
        cmd = "./bin/test.o" + " > verifier_input"
        subprocess.call(cmd, shell=True)

        # invoke the BFS verifier
        proc = subprocess.Popen("./bin/bfs_verifier -f ../test/graphs/4.el -t verifier_input -r 8", stdout=subprocess.PIPE, shell=True)
        test_flag = False
        for line in iter(proc.stdout.readline,''):
            if line.rstrip().find("SUCCESSFUL") != -1:
                test_flag = True
                break;
        self.assertEqual(test_flag, True)
        os.chdir("bin")


    def cc_verified_test(self, input_file_name):
        self.basic_compile_test(input_file_name)
        # proc = subprocess.Popen(["./"+ self.executable_file_name], stdout=subprocess.PIPE)
        os.chdir("..")
        cmd = "./bin/test.o" + " > verifier_input"
        subprocess.call(cmd, shell=True)

        # invoke the BFS verifier
        proc = subprocess.Popen("./bin/cc_verifier -f ../test/graphs/4.el -t verifier_input", stdout=subprocess.PIPE, shell=True)
        test_flag = False
        for line in iter(proc.stdout.readline,''):
            if line.rstrip().find("SUCCESSFUL") != -1:
                test_flag = True
                break;
        self.assertEqual(test_flag, True)
        os.chdir("bin")

    def sssp_verified_test(self, input_file_name):
        self.basic_compile_test(input_file_name)
        # proc = subprocess.Popen(["./"+ self.executable_file_name], stdout=subprocess.PIPE)
        os.chdir("..");
        cmd = "./bin/test.o" + " > verifier_input"
        subprocess.call(cmd, shell=True)

        # invoke the BFS verifier
        proc = subprocess.Popen("./bin/sssp_verifier -f ../test/graphs/4.wel -t verifier_input -r 0", stdout=subprocess.PIPE, shell=True)
        test_flag = False
        for line in iter(proc.stdout.readline,''):
            if line.rstrip().find("SUCCESSFUL") != -1:
                test_flag = True
                break;
        self.assertEqual(test_flag, True)
        os.chdir("bin")

    def pr_verified_test(self, input_file_name):
        self.basic_compile_test(input_file_name)
        proc = subprocess.Popen("./"+ self.executable_file_name + " ../../test/graphs/test.el", shell=True, stdout=subprocess.PIPE)
        #check the value printed to stdout is as expected
        output = proc.stdout.readline()
        print "output: " + output.strip()
        self.assertEqual(float(output.strip()), 0.00289518)


    def cf_verified_test(self, input_file_name):
        self.basic_compile_test(input_file_name)
        proc = subprocess.Popen("./"+ self.executable_file_name + " ../../test/graphs/test_cf.wel", shell=True, stdout=subprocess.PIPE)
        #check the value printed to stdout is as expected
        output = proc.stdout.readline()
        print "output: " + output.strip()
        self.assertEqual(float(output.strip()), 7.49039)

    def test_simple_splitting(self):
        self.basic_compile_test("simple_loop_index_split.gt")

    def test_pagerank_AoS(self):
        self.basic_compile_test("simple_pagerank_with_AoS.gt")

    def test_eigenvector_pagerank_fusion(self):
        self.basic_compile_test("eigenvector_pr_fusion.gt")

    def test_bfs_push_parallel_cas_verified(self):
        self.bfs_verified_test("bfs_push_parallel_cas.gt")

    def test_bfs_hybrid_dense_parallel_cas_verified(self):
        self.bfs_verified_test("bfs_hybrid_dense_parallel_cas.gt")

    def test_bfs_push_parallel_cas_verified(self):
        self.bfs_verified_test("bfs_push_parallel_cas.gt")

    def test_bfs_pull_parallel_verified(self):
        self.bfs_verified_test("bfs_pull_parallel.gt")

    def test_bfs_push_sliding_queue_parallel_cas_verified(self):
        self.bfs_verified_test("bfs_push_sliding_queue_parallel_cas.gt")

    def test_cc_hybrid_dense_parallel_cas_verified(self):
        self.cc_verified_test("cc_hybrid_dense_parallel_cas.gt")

    def test_cc_push_parallel_cas_verified(self):
        self.cc_verified_test("cc_push_parallel_cas.gt")

    def test_cc_pull_parallel_verified(self):
        self.cc_verified_test("cc_pull_parallel.gt")

    def test_sssp_push_parallel_cas_verified(self):
        self.sssp_verified_test("sssp_push_parallel_cas.gt")

    def test_sssp_hybrid_denseforward_parallel_cas_verified(self):
        self.sssp_verified_test("sssp_hybrid_denseforward_parallel_cas.gt")

    def test_sssp_hybrid_dense_parallel_cas_verified(self):
        self.sssp_verified_test("sssp_hybrid_dense_parallel_cas.gt")

    def test_sssp_pull_parallel_verified(self):
        self.sssp_verified_test("sssp_pull_parallel.gt")

    def test_pagerank_parallel_pull_expect(self):
        self.pr_verified_test("pagerank_pull_parallel.gt")

    def test_pagerank_parallel_push_expect(self):
        self.pr_verified_test("pagerank_push_parallel.gt")

    def test_cf_parallel_expect(self):
        self.cf_verified_test("cf_pull_parallel.gt")

if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == "parallel":
        use_parallel = True
        print "using parallel"
        del sys.argv[1]

    unittest.main()
    # used for enabling a specific test

    # suite = unittest.TestSuite()
    # suite.addTest(TestGraphitCompiler('test_cf_parallel_expect'))
    # unittest.TextTestRunner(verbosity=2).run(suite)
