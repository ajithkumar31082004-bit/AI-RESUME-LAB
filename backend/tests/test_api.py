"""
AI RESUME LAB — Integration and Unit Tests for REST API Endpoints
"""
import unittest
import json
import os
import sys

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from config import TestingConfig
from models.database import db


class TestApiEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app(TestingConfig)
        cls.client = cls.app.test_client()

    def setUp(self):
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_health_check(self):
        """Test the health check endpoint."""
        res = self.client.get("/health")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "ok")

    def test_auth_and_dashboard_flow(self):
        """Test registration, login, and dashboard summary."""
        # Register
        reg_res = self.client.post("/api/auth/register", json={
            "name": "Jane Cloud",
            "email": "jane@example.com",
            "password": "Password123!"
        })
        self.assertEqual(reg_res.status_code, 201)
        token = reg_res.get_json()["token"]

        headers = {"Authorization": f"Bearer {token}"}

        # Dashboard summary
        dash_res = self.client.get("/api/dashboard/summary", headers=headers)
        self.assertEqual(dash_res.status_code, 200)
        dash_data = dash_res.get_json()
        self.assertIn("ats_score", dash_data)
        self.assertIn("score_history", dash_data)

        # Add application
        app_res = self.client.post("/api/dashboard/applications", headers=headers, json={
            "company": "Amazon",
            "job_title": "Cloud Architect",
            "status": "applied",
            "notes": "Referral from teammate"
        })
        self.assertEqual(app_res.status_code, 201)

    def test_analyze_text(self):
        """Test resume text analysis and ATS scoring."""
        sample_resume = """
        Jane Doe
        jane.doe@example.com | 555-123-4567 | linkedin.com/in/janedoe | github.com/janedoe

        Summary
        Experienced Cloud Engineer with 5+ years specializing in AWS, Kubernetes, and automated CI/CD pipelines.

        Skills
        Python, AWS, EC2, S3, Docker, Kubernetes, Terraform, Linux, Git, SQL, REST APIs, CI/CD, Prometheus

        Work Experience
        Senior Cloud Engineer — TechCorp (2021 - Present)
        • Architected and deployed microservices on AWS EKS, reducing infrastructure cost by 25%.
        • Automated CI/CD pipelines with GitHub Actions, slashing deployment time by 40%.
        • Managed Terraform infrastructure modules for 50+ cloud resources.

        Education
        B.S. in Computer Science — University of Tech
        """

        res = self.client.post("/api/resume/analyze-text", json={
            "resume_text": sample_resume,
            "job_description": "Looking for a Cloud Engineer with AWS, Docker, Kubernetes, Terraform, Python."
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertGreaterEqual(data["ats_score"], 60)
        self.assertIsNotNone(data["job_match"])
        self.assertGreater(len(data["strengths"]), 0)
        self.assertGreater(len(data["matching_skills"]), 0)

    def test_skills_gap_and_learning_path(self):
        """Test skill gap analysis and role roadmap."""
        gap_res = self.client.post("/api/skills/gap", json={
            "skills": ["Python", "AWS", "Docker", "Git"],
            "target_role": "cloud_engineer"
        })
        self.assertEqual(gap_res.status_code, 200)
        data = gap_res.get_json()
        self.assertIn("match_score", data)
        self.assertIn("matching_skills", data)
        self.assertIn("missing_skills", data)

        path_res = self.client.get("/api/skills/learning-path?role=cloud_engineer")
        self.assertEqual(path_res.status_code, 200)
        path_data = path_res.get_json()
        self.assertIn("steps", path_data)

    def test_interview_evaluator(self):
        """Test interview question retrieval and answer evaluation."""
        q_res = self.client.post("/api/interview/questions", json={
            "role": "Cloud Engineer",
            "level": "mid"
        })
        self.assertEqual(q_res.status_code, 200)
        questions = q_res.get_json()["questions"]
        self.assertIn("technical", questions)
        self.assertIn("behavioral", questions)

        ans_res = self.client.post("/api/interview/answer", json={
            "answer": "In my previous role, I had a production incident where latency spiked by 300%. I used CloudWatch and Prometheus to isolate a memory leak in a pod, rolled back the deployment, and reduced downtime by 45%.",
            "session_id": 1
        })
        self.assertEqual(ans_res.status_code, 200)
        eval_data = ans_res.get_json()
        self.assertGreaterEqual(eval_data["score"], 60)
        self.assertTrue(eval_data["has_metrics"])

    def test_ai_content_generators(self):
        """Test summary enhancer, experience rewriter, and headline generator."""
        sum_res = self.client.post("/api/ai/improve-summary", json={
            "summary": "I am a cloud engineer with 4 years experience building servers.",
            "job_title": "Senior Cloud Engineer"
        })
        self.assertEqual(sum_res.status_code, 200)
        self.assertIn("improved_summary", sum_res.get_json())

        exp_res = self.client.post("/api/ai/rewrite-experience", json={
            "experience": "Handled deployments with Docker and improved server speeds."
        })
        self.assertEqual(exp_res.status_code, 200)
        self.assertIn("bullets", exp_res.get_json())


if __name__ == "__main__":
    unittest.main()
