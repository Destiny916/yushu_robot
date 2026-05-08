import unittest
from pathlib import Path

import step1_load_articulation as step1


class Step1LoadArticulationTests(unittest.TestCase):
    def test_default_usd_path_uses_global_generated_usd(self):
        usd_path = step1.get_robot_usd_path()

        self.assertEqual("generatedUSD", usd_path.parent.name)
        self.assertEqual("model", usd_path.parents[1].name)
        self.assertEqual("g1_29dof_mode_16.usd", usd_path.name)

    def test_scene_origins_match_requested_env_count(self):
        origins = step1.make_scene_origins(num_envs=3, spacing=1.25)

        self.assertEqual([(0.0, 0.0, 0.0), (1.25, 0.0, 0.0), (2.5, 0.0, 0.0)], origins)

    def test_default_run_uses_one_robot_and_infinite_steps(self):
        self.assertEqual(1, step1.DEFAULT_NUM_ENVS)
        self.assertEqual(0, step1.DEFAULT_MAX_STEPS)

    def test_build_robot_cfg_factory_accepts_custom_prim_path(self):
        factory = getattr(step1, "build_g1_articulation_cfg")

        self.assertTrue(callable(factory))
        self.assertEqual(Path(__file__).resolve().parent, Path(step1.__file__).resolve().parent)


if __name__ == "__main__":
    unittest.main()
