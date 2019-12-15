import sys
sys.path.insert(1, "functions")

from core import Core

test = Core()

test.activate_stage("liftoff!")

num_stages = 1

for stage in range(num_stages):
    test.stage_when_engine_empty()
