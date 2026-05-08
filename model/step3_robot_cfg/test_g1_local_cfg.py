import unittest

import g1_local_cfg


class G1LocalCfgTests(unittest.TestCase):
    def test_default_cfg_uses_global_generated_usd(self):
        usd_path = g1_local_cfg.get_robot_usd_path()

        self.assertEqual(g1_local_cfg.DEFAULT_PRIM_PATH, g1_local_cfg.G1_LOCAL_CFG.prim_path)
        self.assertEqual("generatedUSD", usd_path.parent.name)
        self.assertEqual("model", usd_path.parents[1].name)
        self.assertEqual("g1_29dof_mode_16.usd", usd_path.name)

    def test_actuator_groups_are_reusable_and_complete_for_29dof_body(self):
        groups = g1_local_cfg.ACTUATOR_GROUPS

        self.assertEqual(["legs", "feet", "waist", "arms"], list(groups.keys()))
        self.assertIn(".*_knee_joint", groups["legs"])
        self.assertIn(".*_ankle_roll_joint", groups["feet"])
        self.assertIn("waist_.*_joint", groups["waist"])
        self.assertIn(".*_wrist_.*_joint", groups["arms"])

    def test_factory_accepts_replacement_prim_path(self):
        self.assertTrue(callable(g1_local_cfg.make_g1_local_cfg))
        self.assertTrue(callable(g1_local_cfg.G1_LOCAL_CFG.replace))


if __name__ == "__main__":
    unittest.main()
