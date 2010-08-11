import unittest

from ots.server.model.testrun import Testrun 
from ots.server.model.tests.system.mock_taskrunner import MockTaskRunnerResults

from ots.server.results.api import TestrunResult

class TestModel(unittest.TestCase):

    def test_ots_model_results(self):
        mock_task_runner = MockTaskRunnerResults()
        run_test = mock_task_runner.run
        testrun = Testrun(run_test)
        ret_val = testrun.run()
        self.assertEquals(2, len(testrun.results)) 
        self.assertEquals("test_1", testrun.results[0].name())
        self.assertEquals("test_2", testrun.results[1].name())
        self.assertEquals(TestrunResult.FAIL, ret_val)

    def test_ots_model_global_timeout(self):
        pass
        
if __name__ == "__main__":
    unittest.main()
