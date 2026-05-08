import unittest

import sensors_cfg


class SensorsCfgTests(unittest.TestCase):
    def test_defaults_match_project_runtime_rules(self):
        self.assertEqual(1, sensors_cfg.DEFAULT_NUM_ENVS)
        self.assertEqual(0, sensors_cfg.DEFAULT_MAX_STEPS)

    def test_contact_sensor_targets_ankle_roll_links(self):
        self.assertEqual("contact_forces", sensors_cfg.CONTACT_SENSOR_NAME)
        self.assertEqual("{ENV_REGEX_NS}/Robot/.*ankle_roll_link", sensors_cfg.CONTACT_SENSOR_PRIM_PATH)
        self.assertEqual(6, sensors_cfg.CONTACT_SENSOR_HISTORY_LENGTH)

    def test_sensor_env_factory_is_available(self):
        self.assertTrue(callable(sensors_cfg.create_g1_sensor_env_cfg))


if __name__ == "__main__":
    unittest.main()
