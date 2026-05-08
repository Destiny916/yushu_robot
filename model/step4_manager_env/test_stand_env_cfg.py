import unittest

import stand_env_cfg


class StandEnvCfgTests(unittest.TestCase):
    def test_defaults_match_project_runtime_rules(self):
        self.assertEqual(1, stand_env_cfg.DEFAULT_NUM_ENVS)
        self.assertEqual(0, stand_env_cfg.DEFAULT_MAX_STEPS)

    def test_robot_prim_path_uses_manager_scene_namespace(self):
        self.assertEqual("{ENV_REGEX_NS}/Robot", stand_env_cfg.ROBOT_PRIM_PATH)

    def test_required_observation_and_action_names_are_declared(self):
        self.assertEqual(
            ["base_ang_vel", "projected_gravity", "joint_pos_rel", "joint_vel_rel", "last_action"],
            stand_env_cfg.POLICY_OBSERVATION_TERMS,
        )
        self.assertEqual("joint_pos", stand_env_cfg.ACTION_TERM_NAME)
        self.assertEqual("reset_joints_by_offset", stand_env_cfg.RESET_JOINTS_TERM_NAME)

    def test_config_factory_and_robot_config_are_available(self):
        self.assertTrue(callable(stand_env_cfg.create_g1_stand_env_cfg))
        self.assertEqual("g1_local_cfg", stand_env_cfg.G1_LOCAL_CFG.__class__.__module__)


if __name__ == "__main__":
    unittest.main()
