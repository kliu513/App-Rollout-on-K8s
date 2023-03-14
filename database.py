import sqlite3
from entities import Cluster, Service, Application, Rollout, RolloutPlan

connection = sqlite3.connect("main.db")
cursor = connection.cursor()

# Cluster operations
def create_cluster_table():
    cursor.execute("""CREATE TABLE IF NOT EXISTS CLUSTERS (
        name text PRIMARY KEY,
        ring int,
        file text,
        timestamp text
    )""")

def insert_cluster(cluster: Cluster):
    with connection:
        cursor.execute("INSERT OR IGNORE INTO CLUSTERS VALUES (:name, :ring, :config, :timestamp)", 
        {"name": cluster.name, "ring": cluster.ring, "config": cluster.config, "timestamp": cluster.timestamp})

def get_cluster(cluster_name: str):
    with connection:
        cursor.execute("SELECT * FROM CLUSTERS WHERE name = ?", (cluster_name,))
    cluster_info = cursor.fetchone()
    return Cluster(*cluster_info)

def list_cluster(cluster_name: str):
    with connection:
        cursor.execute("SELECT ring FROM CLUSTERS WHERE name = ?", (cluster_name,))
    cluster_ring = cursor.fetchone()
    with connection:
        cursor.execute("SELECT * FROM CLUSTERS WHERE ring = ?", (*cluster_ring,))
    siblings = cursor.fetchall()
    results = []
    for sibling in siblings:
        results.append(Cluster(*sibling))
    return results

def delete_cluster(cluster_name: str):
    with connection:
        cursor.execute("SELECT * FROM CLUSTERS WHERE name = ?", (cluster_name,))
    deleted_cluster = cursor.fetchone()
    with connection:
        cursor.execute("DELETE FROM CLUSTERS WHERE name = ?", (cluster_name,))
    return Cluster(*deleted_cluster)

def update_cluster(cluster_name: str, cluster_ring: int):
    with connection:
        cursor.execute("UPDATE CLUSTERS SET ring = ? WHERE name = ?", (cluster_ring, cluster_name,))
    with connection:
        cursor.execute("SELECT * FROM CLUSTERS WHERE name = ?", (cluster_name,))
    updated_cluster = cursor.fetchone()
    return Cluster(*updated_cluster)

def list_all_clusters():
    with connection:
        cursor.execute("SELECT * FROM CLUSTERS")
    clusters = cursor.fetchall()
    results = []
    for cluster in clusters:
        results.append(Cluster(*cluster))
    return results

# Service operations
def create_service_table():
    cursor.execute("""CREATE TABLE IF NOT EXISTS SERVICES (
        application text,
        service text,
        repo text,
        version text,
        dependencies text,
        rollout_plan text,
        timestamp text,
        CONSTRAINT service_key PRIMARY KEY (application, service)
    )""")

def insert_service(service: Service):
    with connection:
        cursor.execute("INSERT OR IGNORE INTO SERVICES VALUES (:application, :service, :repo, :version, \
            :dependencies, :rollout_plan, :timestamp)", 
        {"application": service.application, "service": service.service, "repo": service.repo, \
            "version": service.version, "dependencies": service.dependencies, \
            "rollout_plan": service.rollout_plan, "timestamp": service.timestamp})

def update_service(app_name: str, service_name: str, service_deps: str):
    with connection:
        cursor.execute("UPDATE SERVICES SET dependencies = ? WHERE application = ? AND service = ?", \
            (service_deps, app_name, service_name,))
    with connection:
        cursor.execute("SELECT * FROM SERVICES WHERE application = ? AND service = ?", (app_name, service_name,))
    updated_service = cursor.fetchone()
    return Service(*updated_service)

def delete_service(app_name: str, service_name: str):
    with connection:
        cursor.execute("SELECT * FROM SERVICES WHERE application = ? AND service = ?", (app_name, service_name,))
    deleted_service = cursor.fetchone()
    with connection:
        cursor.execute("DELETE FROM SERVICES WHERE application = ? AND service = ?", (app_name, service_name,))
    return Service(*deleted_service)

def get_service(app_name: str, service_name: str):
    with connection:
        cursor.execute("SELECT * FROM SERVICES WHERE application = ? AND service = ?", (app_name, service_name,))
    service_info = cursor.fetchone()
    return Service(*service_info)

def list_all_services():
    with connection:
        cursor.execute("SELECT * FROM SERVICES")
    services = cursor.fetchall()
    results = []
    for service in services:
        results.append(Service(*service))
    return results

# Application operations
def create_application_table():
    cursor.execute("""CREATE TABLE IF NOT EXISTS APPLICATIONS (
        name text PRIMARY KEY,
        timestamp text
    )""")

def insert_application(app: Application):
    with connection:
        cursor.execute("INSERT OR IGNORE INTO APPLICATIONS VALUES (:name, :timestamp)", 
        {"name": app.name, "timestamp": app.timestamp})

def delete_application(name: str):
    with connection:
        cursor.execute("SELECT * FROM APPLICATIONS WHERE name = ?", (name,))
    deleted_application = cursor.fetchone()
    with connection:
        cursor.execute("DELETE FROM APPLICATIONS WHERE name = ?", (name,))
        cursor.execute("DELETE FROM SERVICES WHERE application = ?", (name,))
    return Application(*deleted_application)

def update_rollout_plan(app_name: str, service_name: str, new_version: str):
    with connection:
        cursor.execute("UPDATE SERVICES SET rollout_plan = ? WHERE application = ? AND service = ?", \
            (new_version, app_name, service_name,))
    with connection:
        cursor.execute("SELECT * FROM SERVICES WHERE application = ? AND service = ?", (app_name, service_name,))
    updated_service = cursor.fetchone()
    return Service(*updated_service)

def get_application(name: str):
    with connection:
        cursor.execute("SELECT * FROM SERVICES WHERE application = ?", (name,))
    results = cursor.fetchall()
    services = []
    for res in results:
        services.append(Service(*res))
    with connection:
        cursor.execute("SELECT * FROM APPLICATIONS WHERE name = ?", (name,))
    result = cursor.fetchone()
    application = Application(*result)
    application.services = services
    return application

def list_all_applications():
    with connection:
        cursor.execute("SELECT * FROM APPLICATIONS")
    apps = cursor.fetchall()
    results = []
    for app in apps:
        results.append(Application(*app))
    return results

# Rollout operations
def create_rollout_table():
    cursor.execute("""CREATE TABLE IF NOT EXISTS ROLLOUTS (
        application text,
        status int,
        guid text PRIMARY KEY,
        timestamp text,
        rollout_plans text
    )""")

def insert_rollout(rollout: Rollout):
    with connection:
        cursor.execute("SELECT * FROM ROLLOUTS WHERE application = ? AND status = 1", (rollout.application,))
    if len(cursor.fetchall()) > 0:
        print("Insertion failed: an application can only have one running rollout")
        return False
    with connection:
        cursor.execute("SELECT service, rollout_plan FROM SERVICES WHERE application = ? AND rollout_plan IS NOT NULL", \
                       (rollout.application,))
    results = cursor.fetchall()
    rollout_plans = [repr(RolloutPlan(*result)) for result in results]
    with connection:
        cursor.execute("INSERT OR IGNORE INTO ROLLOUTS VALUES (:application, :status, :guid, :timestamp, :rollout_plans)", 
        {"application": rollout.application,"status": rollout.status, "guid": rollout.guid, \
         "timestamp": rollout.timestamp, "rollout_plans": ", ".join(rollout_plans)})
    return True

def finish_rollout(application: str):
    update_rollout_status(application, 2)
    with connection:
        cursor.execute("SELECT * FROM SERVICES WHERE application = ?", (application,))
    results = cursor.fetchall()
    services = [Service(*result) for result in results]
    with connection:
        for service in services:
            cursor.execute("UPDATE SERVICES SET version = ? WHERE service = ? AND rollout_plan IS NOT NULL", \
                           (service.rollout_plan, service.service,))
    with connection:
        for service in services:
            cursor.execute("UPDATE SERVICES SET rollout_plan = NULL WHERE service = ?", (service.service,))

def get_rollout(application: str):
    with connection:
        cursor.execute("SELECT * FROM ROLLOUTS WHERE application = ? AND status = 1", (application,))
    result = cursor.fetchone()
    return Rollout(*result)

def list_all_rollouts():
    with connection:
        cursor.execute("SELECT * FROM ROLLOUTS")
    results = cursor.fetchall()
    return [Rollout(*result) for result in results]

def update_rollout_status(application: str, status=0):
    with connection:
        cursor.execute("UPDATE ROLLOUTS SET status = ? WHERE application = ? AND status = 1", \
                       (status, application,))

create_cluster_table()
create_service_table() 
create_application_table()
create_rollout_table()
