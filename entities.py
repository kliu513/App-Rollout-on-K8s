import datetime
import uuid

class Cluster:
    def __init__(self, name, ring, config_filename, timestamp=None):
        self.name = name
        self.ring = ring
        self.config = config_filename
        self.timestamp = timestamp if timestamp is not None else datetime.datetime.now().isoformat()
    
    def __repr__(self) -> str:
        return f"({self.name}, {self.ring}, {self.config}, {self.timestamp})"

class Service:
    def __init__(self, application, service, repo, version, dependencies, rollout_plan=None, timestamp=None):
        self.application = application
        self.service = service
        self.repo = repo
        self.version = version
        self.dependencies = dependencies
        self.rollout_plan = rollout_plan
        self.timestamp = timestamp if timestamp is not None else datetime.datetime.now().isoformat()
    
    def __repr__(self) -> str:
        return f"({self.application}, {self.service}, {self.repo}, {self.version}, {self.dependencies}, \
            {self.rollout_plan}, {self.timestamp})"

class Application:
    def __init__(self, name, timestamp=None, services=[]):
        self.name = name
        self.timestamp = timestamp if timestamp is not None else datetime.datetime.now().isoformat()
        self.services = services
    
    def __repr__(self) -> str:
        return f"({self.name}, {self.timestamp})"

class Rollout:
    def __init__(self, application, status=1, guid=None, timestamp=None, rollout_plans=None):
        self.application = application
        self.status = status  # 0: cancelled, 1: running, 2: finished
        self.guid = guid if guid is not None else uuid.uuid4().hex
        self.timestamp = timestamp if timestamp is not None else datetime.datetime.now().isoformat()
        self.rollout_plans = rollout_plans
    
    def __repr__(self) -> str:
        return f"({self.guid}, {self.application}, {self.status}, {self.timestamp})"
    
class RolloutPlan:
    def __init__(self, service, rollout_plan):
        self.service = service
        self.rollout_plan = rollout_plan
    
    def __repr__(self) -> str:
        return f"({self.service}, {self.rollout_plan})"
