import re

backup_path = r"d:\Agriculture project\.agents\sub_orch_backend_core\models_backup.md"
target_path = r"d:\Agriculture project\backend\app\models\models.py"

with open(backup_path, "r", encoding="utf-8") as f:
    content = f.read()

# Extract code from ```python ... ``` block
match = re.search(r"```python\n(.*?)\n```", content, re.DOTALL)
if not match:
    raise ValueError("Could not find python code block in backup!")

code = match.group(1)

# Now edit Farmer class
# We want to add security_question and security_question_answer columns
# Let's find:
#     loan_amount = Column(Float, default=0.0, nullable=True)
# And append:
#     security_question = Column(String, nullable=True)
#     security_question_answer = Column(String, nullable=True)
farmer_target = "    loan_amount = Column(Float, default=0.0, nullable=True)"
farmer_replacement = """    loan_amount = Column(Float, default=0.0, nullable=True)
    security_question = Column(String, nullable=True)
    security_question_answer = Column(String, nullable=True)"""

if farmer_target in code:
    code = code.replace(farmer_target, farmer_replacement, 1)
else:
    raise ValueError("Could not find Farmer target line in code")

# Now edit Buyer class
# Let's find in Buyer class:
#     created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
# Since there are multiple places with created_at, let's find the Buyer block:
buyer_target = """class Buyer(Base):
    __tablename__ = "buyers"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)
    phone_number = Column(String, default="Not Provided", nullable=False)
    address = Column(String, default="Not Provided", nullable=False)
    location = Column(String, default="Not Provided", nullable=False)
    suspended = Column(Boolean, default=False, nullable=False)
    status = Column(String, default="ACTIVE", nullable=False)
    status_change_reason = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)"""

buyer_replacement = buyer_target + """
    security_question = Column(String, nullable=True)
    security_question_answer = Column(String, nullable=True)"""

if buyer_target in code:
    code = code.replace(buyer_target, buyer_replacement, 1)
else:
    raise ValueError("Could not find Buyer target block in code")

with open(target_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Successfully restored and updated models.py!")
