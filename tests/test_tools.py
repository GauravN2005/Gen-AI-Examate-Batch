import unittest

from app.tools import sip_rupee_cost_averaging


class SipToolTests(unittest.TestCase):
    def test_nav_based_calculation(self) -> None:
        result = sip_rupee_cost_averaging(6000, [60, 50, 40, 60])
        self.assertEqual(result["total_invested"], 24000)
        self.assertEqual(result["total_units"], 470)
        self.assertAlmostEqual(result["average_cost_per_unit"], 24000 / 470)
        self.assertEqual(result["final_value"], 28200)
        self.assertEqual(result["gain_or_loss"], 4200)
        self.assertEqual(
            [row["units_bought"] for row in result["monthly_breakdown"]],
            [100, 120, 150, 100],
        )

    def test_assumed_return_with_step_up(self) -> None:
        result = sip_rupee_cost_averaging(
            2000,
            annual_return_percent=10,
            years=2,
            yearly_step_up_percent=5,
        )
        self.assertEqual(result["mode"], "assumed_return_projection")
        self.assertEqual(result["total_invested"], 49200)
        self.assertTrue(result["illustrative"])
        self.assertEqual(result["contribution_timing"], "end of each month")
        self.assertEqual(len(result["monthly_breakdown"]), 24)

    def test_invalid_inputs(self) -> None:
        with self.assertRaises(ValueError):
            sip_rupee_cost_averaging(0, [10])
        with self.assertRaises(ValueError):
            sip_rupee_cost_averaging(1000, [])
        with self.assertRaises(ValueError):
            sip_rupee_cost_averaging(1000, [10, 0])
        with self.assertRaises(ValueError):
            sip_rupee_cost_averaging(
                1000, annual_return_percent=-100, years=1
            )


if __name__ == "__main__":
    unittest.main()
