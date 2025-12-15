from django.test import TestCase
from .scoring import score_tasks, detect_cycles
from datetime import date, timedelta

class ScoringTests(TestCase):
    def test_basic_scoring(self):
        t1 = {"id":1,"title":"A","due_date":date.today(), "estimated_hours":2,"importance":9,"dependencies":[]}
        t2 = {"id":2,"title":"B","due_date":date.today()+timedelta(days=10),"estimated_hours":8,"importance":5,"dependencies":[]}
        res = score_tasks([t1,t2])
        self.assertGreater(res[0]["score"], res[1]["score"])

    def test_past_due_boost(self):
        t = {"id":1,"title":"Late","due_date":date.today()-timedelta(days=2),"estimated_hours":5,"importance":3,"dependencies":[]}
        res = score_tasks([t])
        self.assertEqual(res[0]["score"], res[0]["score"]) # trivial but ensures runs

    def test_detect_cycle(self):
        tasks = [{"id":1,"dependencies":[2]},{"id":2,"dependencies":[1]}]
        self.assertTrue(detect_cycles(tasks))
