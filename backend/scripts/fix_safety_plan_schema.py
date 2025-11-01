#!/usr/bin/env python3
"""
Fix SafetyPlanCreate schema to match database
"""

# Read the schemas
with open('app/schemas/crisis.py', 'r') as f:
    content = f.read()

# The database schema shows these are ARRAY fields, so the schema should use List
# Replace the SafetyPlanCreate class if it has wrong field types
old_safety_plan = '''class SafetyPlanCreate(BaseModel):
    plan_name: str
    warning_signs: List[str]
    internal_coping_strategies: List[str]
    external_coping_strategies: List[str]
    social_contacts: List[str]
    professional_contacts: List[str]
    environment_safety: str
    reasons_for_living: List[str]'''

new_safety_plan = '''class SafetyPlanCreate(BaseModel):
    plan_name: str
    warning_signs: Optional[List[str]] = None
    internal_coping_strategies: Optional[List[str]] = None
    external_coping_strategies: Optional[List[str]] = None
    social_contacts: Optional[List[str]] = None
    professional_contacts: Optional[List[str]] = None
    environment_safety: Optional[str] = None
    reasons_for_living: Optional[List[str]] = None'''

if old_safety_plan in content:
    content = content.replace(old_safety_plan, new_safety_plan)
    print("✅ Fixed SafetyPlanCreate schema")
else:
    print("⚠️ SafetyPlanCreate schema already fixed or has different structure")

# Write back
with open('app/schemas/crisis.py', 'w') as f:
    f.write(content)
