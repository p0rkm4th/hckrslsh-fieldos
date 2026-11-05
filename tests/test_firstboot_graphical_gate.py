import configparser
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class FirstbootGraphicalGateTests(unittest.TestCase):
    def test_firstboot_is_a_required_predecessor_of_graphical_target(self):
        unit = configparser.ConfigParser(interpolation=None)
        unit.read(ROOT / "installer/provisioning/fieldos-firstboot.service")
        self.assertEqual(
            set(unit.get("Unit", "Before").split()),
            {"display-manager.service", "graphical.target"},
        )
        self.assertEqual(
            set(unit.get("Install", "RequiredBy").split()),
            {"display-manager.service", "graphical.target"},
        )
        self.assertFalse(unit.has_option("Install", "WantedBy"))
        self.assertFalse(unit.has_option("Unit", "ConditionPathExists"))

    def test_customer_autoinstall_installs_and_enables_the_gated_unit(self):
        user_data = (ROOT / "installer/autoinstall/user-data").read_text()
        self.assertIn(
            "cp /target/opt/fieldos/installer/provisioning/fieldos-firstboot.service "
            "/target/etc/systemd/system/fieldos-firstboot.service",
            user_data,
        )
        self.assertIn(
            "curtin in-target --target=/target -- systemctl enable fieldos-firstboot.service",
            user_data,
        )


if __name__ == "__main__":
    unittest.main()
