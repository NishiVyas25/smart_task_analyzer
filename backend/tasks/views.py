from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import TaskSerializer
from .scoring import score_tasks, detect_cycles
from datetime import datetime

class AnalyzeTasks(APIView):
    def post(self, request):
        data = request.data
        if not isinstance(data, list):
            return Response({"error":"expected a list of tasks"}, status=400)
        # minimal validation
        try:
            tasks = []
            for t in data:
                ser = TaskSerializer(data=t)
                ser.is_valid(raise_exception=True)
                tt = ser.validated_data
                # parse due_date into date if string
                if tt.get("due_date"):
                    if isinstance(tt["due_date"], str):
                        tt["due_date"] = datetime.strptime(tt["due_date"], "%Y-%m-%d").date()
                tasks.append(tt)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

        # detect circular dependencies
        if detect_cycles(tasks):
            # return warning field: you can also return partial result
            return Response({"error": "circular dependency detected. Please fix dependencies."}, status=400)

        # calculate scores
        strategy = request.query_params.get("strategy", "smart")
        results = score_tasks(tasks, strategy=strategy)
        return Response(results)

class SuggestTasks(APIView):
    def post(self, request):
        data = request.data

        if not isinstance(data, list):
            return Response(
                {"error": "Expected a list of tasks"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            tasks = []
            for t in data:
                ser = TaskSerializer(data=t)
                ser.is_valid(raise_exception=True)
                tt = ser.validated_data

                if tt.get("due_date"):
                    tt["due_date"] = datetime.strptime(
                        str(tt["due_date"]), "%Y-%m-%d"
                    ).date()

                tasks.append(tt)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

        if detect_cycles(tasks):
            return Response(
                {"error": "Circular dependency detected"},
                status=400
            )

        results = score_tasks(tasks)
        top3 = results[:3]

        for t in top3:
            t["why"] = (
                f"High priority because urgency={t['explanation']['urgency']}, "
                f"importance={t['explanation']['importance']}, "
                f"low effort={t['explanation']['effort']}"
            )

        return Response(top3)
