import unittest
from tempfile import TemporaryDirectory
from pathlib import Path

from robot_asset import (
    find_missing_meshes,
    get_default_urdf_path,
    get_default_usd_path,
    get_isaaclab_source_paths,
    list_mesh_references,
)


class RobotAssetTests(unittest.TestCase):
    def test_default_urdf_references_existing_meshes(self):
        urdf_path = get_default_urdf_path()

        mesh_refs = list_mesh_references(urdf_path)
        missing = find_missing_meshes(urdf_path)

        self.assertEqual(59, len(mesh_refs))
        self.assertEqual(35, len(set(mesh_refs)))
        self.assertEqual([], missing)

    def test_default_usd_stays_inside_this_workflow_folder(self):
        usd_path = get_default_usd_path()

        self.assertEqual("build_robot_model", usd_path.parents[1].name)
        self.assertEqual("generated", usd_path.parent.name)

    def test_missing_mesh_detection_uses_urdf_relative_paths(self):
        with TemporaryDirectory() as temp_dir:
            urdf_path = Path(temp_dir) / "missing_mesh.urdf"
            urdf_path.write_text(
                """<robot name="fixture">
  <link name="base">
    <visual>
      <geometry>
        <mesh filename="meshes/not_present.STL"/>
      </geometry>
    </visual>
  </link>
</robot>
""",
                encoding="utf-8",
            )

            self.assertEqual(["meshes/not_present.STL"], find_missing_meshes(urdf_path))

    def test_isaaclab_source_paths_include_core_package(self):
        source_paths = get_isaaclab_source_paths()

        self.assertIn("isaaclab", {path.name for path in source_paths})
        self.assertTrue(any((path / "isaaclab").is_dir() for path in source_paths))


if __name__ == "__main__":
    unittest.main()
