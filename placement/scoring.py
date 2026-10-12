BAND_WEIGHT={'A1':1,'A2':2,'B1':3}


def objective_score(items, answers):
    possible = sum(BAND_WEIGHT[x['band']] for x in items)
    got = sum(
        BAND_WEIGHT[x['band']]
        for x in items
        if str(answers.get(x['id'], '')) == str(x['answer'])
    )
    return round(100 * got / possible, 1) if possible else 0

def classify(scores):
    
    overall=round(sum(scores.values())/len(scores),1)
    productive=min(scores.get('writing',0),scores.get('speaking',0))
    receptive=min(scores.get('reading',0),scores.get('listening',0))
    
    if overall >= 70 and productive >= 55 and receptive >= 60 and scores["grammar_vocab"] >= 60:
        level = "B1"
        start = 120
    elif overall >= 50 and productive >= 35 and receptive >= 45 and scores["grammar_vocab"] >= 45:
        level = "A2"
        start = 64
    elif overall >= 25:
        level = "A1"
        start = 29
    else:
        level = "A0"
        start = 1

    strengths=[k for k,v in scores.items() if v>=65]
    weaknesses=[k for k,v in scores.items() if v<45]
    
    spread=max(scores.values()) - min(scores.values())
    confidence=.9 if spread < 30 else .7
    
    return {'level':level,
            'start_day':start,
            'overall':overall,
            'scores':scores,
            'strengths':strengths,
            'weaknesses':weaknesses,
            'confidence':confidence}



# from collections import defaultdict
# from math import isfinite
# from statistics import mean


# LEVELS = ("A1", "A2", "B1")
# SKILLS = ("reading", "listening", "writing", "speaking")

# START_DAY = {
#     "Pre-A1": 1,
#     "A1": 29,
#     "A2": 64,
#     "B1": 120,
# }

# WRITING_WEIGHTS = {
#     "task_fulfilment": 30,
#     "organisation": 20,
#     "vocabulary": 20,
#     "grammar": 20,
#     "written_conventions": 10,
# }

# SPEAKING_WEIGHTS = {
#     "task_fulfilment": 25,
#     "interaction": 20,
#     "fluency_coherence": 20,
#     "vocabulary": 15,
#     "grammar": 10,
#     "intelligibility": 10,
# }

# MIN_TASKS = 2
# TARGET_SCORE = 75
# OBJECTIVE_TASK_FLOOR = 60
# REQUIRED_CRITERION_SCORE = 3


# def validate_number(value, minimum, maximum, name):
#     """Validate a finite numeric score within the specified range."""
#     if (
#         isinstance(value, bool)
#         or not isinstance(value, (int, float))
#         or not isfinite(value)
#         or not minimum <= value <= maximum
#     ):
#         raise ValueError(
#             f"{name} must be a finite number between "
#             f"{minimum} and {maximum}."
#         )
#     return float(value)


# def objective_score(items, answers):
#     """
#     Score objective items separately by CEFR band and task.

#     Each item must contain:
#         id, band, task_id, answer

#     Returns:
#         {"A1": [task_percentage, ...], "A2": [...], "B1": [...]}

#     Missing answers count as incorrect. Matching is exact after
#     converting to strings and removing surrounding whitespace.
#     """
#     totals = defaultdict(lambda: {"correct": 0, "possible": 0})
#     seen_ids = set()

#     for item in items:
#         band = item["band"]
#         item_id = item["id"]
#         task_id = item["task_id"]

#         if band not in LEVELS:
#             raise ValueError(f"Unsupported band: {band}")

#         if item_id in seen_ids:
#             raise ValueError(f"Duplicate item ID: {item_id}")
#         seen_ids.add(item_id)

#         if item["answer"] is None:
#             raise ValueError(f"Missing answer key for item: {item_id}")

#         result = totals[(band, task_id)]
#         result["possible"] += 1

#         if (
#             item_id in answers
#             and str(answers[item_id]).strip()
#             == str(item["answer"]).strip()
#         ):
#             result["correct"] += 1

#     scores = {band: [] for band in LEVELS}

#     for (band, task_id), result in totals.items():
#         # Keep full precision for placement decisions.
#         percentage = 100 * result["correct"] / result["possible"]
#         scores[band].append(percentage)

#     return scores


# def rubric_score(criteria, skill):
#     """
#     Calculate a writing/speaking task score from 0–4 ratings.

#     All criteria are required. Missing ratings represent missing
#     evidence and must not silently become zero.
#     """
#     if skill == "writing":
#         weights = WRITING_WEIGHTS
#     elif skill == "speaking":
#         weights = SPEAKING_WEIGHTS
#     else:
#         raise ValueError("Rubric scoring supports writing or speaking.")

#     missing = set(weights) - set(criteria)
#     extra = set(criteria) - set(weights)

#     if missing or extra:
#         raise ValueError(
#             f"{skill}: missing criteria={sorted(missing)}, "
#             f"unexpected criteria={sorted(extra)}"
#         )

#     ratings = {
#         name: validate_number(criteria[name], 0, 4, name)
#         for name in weights
#     }

#     score = sum(
#         ratings[name] / 4 * weight
#         for name, weight in weights.items()
#     )

#     required = ["task_fulfilment"]
#     if skill == "speaking":
#         required.append("interaction")

#     meets_target = (
#         score >= TARGET_SCORE
#         and all(
#             ratings[name] >= REQUIRED_CRITERION_SCORE
#             for name in required
#         )
#     )

#     return {
#         "score": score,
#         "criteria": ratings,
#         "meets_target": meets_target,
#     }


# def assess_skill(skill, band_tasks):
#     """Assess each band and return the highest demonstrated level."""
#     unknown_bands = set(band_tasks) - set(LEVELS)
#     if unknown_bands:
#         raise ValueError(f"Unsupported bands: {sorted(unknown_bands)}")

#     evidence = {}

#     for band in LEVELS:
#         tasks = band_tasks.get(band, [])

#         if skill in ("reading", "listening"):
#             task_scores = [
#                 validate_number(value, 0, 100, f"{skill}/{band}")
#                 for value in tasks
#             ]

#             enough_evidence = len(task_scores) >= MIN_TASKS
#             meets_target = (
#                 enough_evidence
#                 and mean(task_scores) >= TARGET_SCORE
#                 and min(task_scores) >= OBJECTIVE_TASK_FLOOR
#             )

#         else:
#             results = [rubric_score(task, skill) for task in tasks]
#             task_scores = [result["score"] for result in results]

#             enough_evidence = len(results) >= MIN_TASKS
#             meets_target = (
#                 enough_evidence
#                 and all(result["meets_target"] for result in results)
#             )

#         evidence[band] = {
#             "task_count": len(tasks),
#             "task_scores": [round(value, 1) for value in task_scores],
#             "average": (
#                 round(mean(task_scores), 1) if task_scores else None
#             ),
#             "status": (
#                 "insufficient_evidence"
#                 if not enough_evidence
#                 else "meets_target"
#                 if meets_target
#                 else "below_target"
#             ),
#         }

#     demonstrated = [
#         band
#         for band in LEVELS
#         if evidence[band]["status"] == "meets_target"
#     ]

#     if demonstrated:
#         level = demonstrated[-1]
#     elif evidence["A1"]["status"] == "below_target":
#         # Routing label, not a positive assessment of Pre-A1 ability.
#         level = "Pre-A1"
#     else:
#         level = None

#     return {"level": level, "evidence": evidence}


# def classify(scores):
#     """
#     Produce provisional placement from level-specific task evidence.

#     Expected structure:
#         reading/listening: {band: [task percentages]}
#         writing/speaking:  {band: [criterion dictionaries]}
#         grammar_vocab:    optional diagnostic percentage
#     """
#     missing = set(SKILLS) - set(scores)
#     if missing:
#         raise ValueError(f"Missing skills: {sorted(missing)}")

#     assessments = {
#         skill: assess_skill(skill, scores[skill])
#         for skill in SKILLS
#     }

#     skill_levels = {
#         skill: assessment["level"]
#         for skill, assessment in assessments.items()
#     }

#     rank = {"Pre-A1": 0, "A1": 1, "A2": 2, "B1": 3}
#     complete = all(level is not None for level in skill_levels.values())

#     if complete:
#         level = min(skill_levels.values(), key=rank.get)
#         highest = max(rank[value] for value in skill_levels.values())
#         lowest = min(rank[value] for value in skill_levels.values())

#         strengths = [
#             skill for skill, value in skill_levels.items()
#             if rank[value] == highest
#         ] if highest > lowest else []

#         focus_skills = [
#             skill for skill, value in skill_levels.items()
#             if rank[value] == lowest
#         ]
#     else:
#         level = None
#         strengths = []
#         focus_skills = [
#             skill for skill, value in skill_levels.items()
#             if value is None
#         ]

#     diagnostic = scores.get("grammar_vocab")
#     if diagnostic is not None:
#         diagnostic = validate_number(
#             diagnostic, 0, 100, "grammar_vocab"
#         )

#     return {
#         "level": level,
#         "start_day": START_DAY.get(level),
#         "skill_levels": skill_levels,
#         "assessments": assessments,
#         "strengths": strengths,
#         "recommended_focus": focus_skills,
#         "grammar_vocab": diagnostic,
#         "placement_status": (
#             "provisional" if complete else "insufficient_evidence"
#         ),
#         "confidence": None,
#     }