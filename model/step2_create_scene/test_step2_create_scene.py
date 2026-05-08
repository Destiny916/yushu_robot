import unittest

import step2_create_scene as step2


class Step2CreateSceneTests(unittest.TestCase):
    def test_default_run_uses_one_robot_and_infinite_steps(self):
        self.assertEqual(1, step2.DEFAULT_NUM_ENVS)
        self.assertEqual(0, step2.DEFAULT_MAX_STEPS)

    def test_robot_uses_interactive_scene_namespace(self):
        self.assertEqual("{ENV_REGEX_NS}/Robot", step2.ROBOT_PRIM_PATH)

    def test_default_usd_path_uses_global_generated_usd(self):
        usd_path = step2.get_robot_usd_path()

        self.assertEqual("generatedUSD", usd_path.parent.name)
        self.assertEqual("model", usd_path.parents[1].name)
        self.assertEqual("g1_29dof_mode_16.usd", usd_path.name)

    def test_scene_cfg_factory_is_available(self):
        self.assertTrue(callable(step2.create_g1_scene_cfg_class))

    def test_step2_uses_step3_local_robot_cfg(self):
        self.assertEqual("g1_local_cfg", step2.G1_LOCAL_CFG.__class__.__module__)


if __name__ == "__main__":
    unittest.main()
