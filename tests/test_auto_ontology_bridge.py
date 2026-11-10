"""
Unit Test for Auto-Ontology Bridge Module
"""

import unittest
from miner.auto_ontology_bridge import AutoOntologyBridge

class TestAutoOntologyBridge(unittest.TestCase):
    def test_ddl_generation(self):
        ddl = AutoOntologyBridge.get_ddl_schema()
        self.assertIn("CREATE TABLE IF NOT EXISTS dim_equipment", ddl)
        self.assertIn("CREATE TABLE IF NOT EXISTS fact_defect_incident", ddl)
        self.assertIn("CREATE TABLE IF NOT EXISTS fact_root_cause_action", ddl)

    def test_terms_payload_builder(self):
        sample_terms = [
            {
                "id": "term_ak",
                "name": "Air Knife (显影风刀)",
                "description": "Developer CDA drying knife",
                "synonyms": ["AK", "风刀", "Air Knife"]
            }
        ]
        payload = AutoOntologyBridge.build_terms_payload(sample_terms)
        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]["id"], "term_ak")
        self.assertTrue(payload[0]["name_certified"])
        self.assertIn("风刀", payload[0]["synonyms"])

    def test_transform_incidents_to_relational_rows(self):
        incidents = [
            {
                "equipment_id": "PHT200",
                "equipment_name": "Track Act 12 #200",
                "layer_id": "PLN",
                "defect_code": "DEV_AK_MURA",
                "defect_name_zh": "显影风刀条纹白条",
                "impact_yield_loss_pct": 10.0,
                "scrap_sheet_count": 120,
                "detect_station": "MAC_ANN",
                "root_cause_action": {
                    "root_cause_physical": "Developer air knife flow rate deficiency",
                    "target_unit": "DEV_AK",
                    "param_name": "air_flow_rate",
                    "param_unit": "L/min",
                    "param_before": "1200",
                    "param_after": "1650",
                    "countermeasure_summary": "Increase AK flow to 1650 L/min",
                    "verification_status": "Released_PCCB",
                    "report_doc_name": "report.ppt"
                }
            }
        ]
        tables = AutoOntologyBridge.transform_incidents_to_relational_rows(incidents)
        self.assertEqual(len(tables["dim_equipment"]), 1)
        self.assertEqual(tables["dim_equipment"][0]["equipment_id"], "PHT200")
        self.assertEqual(len(tables["dim_process_layer"]), 1)
        self.assertEqual(tables["dim_process_layer"][0]["layer_id"], "PLN")
        self.assertEqual(len(tables["fact_defect_incident"]), 1)
        self.assertEqual(tables["fact_defect_incident"][0]["impact_yield_loss_pct"], 10.0)
        self.assertEqual(len(tables["fact_root_cause_action"]), 1)
        self.assertEqual(tables["fact_root_cause_action"][0]["param_after"], "1650")

    def test_mcp_config_generation(self):
        cfg = AutoOntologyBridge.generate_mcp_config("http://192.168.101.101:3000")
        self.assertIn("mcpServers", cfg)
        self.assertIn("auto-ontology", cfg["mcpServers"])
        self.assertEqual(cfg["mcpServers"]["auto-ontology"]["env"]["AUTO_ONTOLOGY_API_URL"], "http://192.168.101.101:3000")

    def test_model_interchange_document_generation(self):
        doc = AutoOntologyBridge.generate_model_interchange_document(database_name="test_fab_db")
        self.assertIn("data_layer", doc)
        self.assertIn("semantic_layer", doc)
        self.assertIn("databases", doc["data_layer"])
        self.assertEqual(len(doc["data_layer"]["databases"][0]["schemas"][0]["tables"]), 5)
        self.assertEqual(len(doc["semantic_layer"]["terms"]), 3)
        self.assertEqual(len(doc["semantic_layer"]["sql_attributes"]["manual"]), 2)

        yaml_str = AutoOntologyBridge.export_auto_ontology_yaml(database_name="test_fab_db")
        self.assertIn("data_layer:", yaml_str)
        self.assertIn("semantic_layer:", yaml_str)
        self.assertIn("dim_equipment", yaml_str)

if __name__ == "__main__":
    unittest.main()
