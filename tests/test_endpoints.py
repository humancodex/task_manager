import pytest
from fastapi.testclient import TestClient


def test_create_task(client: TestClient):
    response = client.post(
        "/api/tasks",
        json={
            "title": "Test Task",
            "description": "Test Description",
            "status": "pending",
            "priority": "high"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert "id" in data


def test_get_task(client: TestClient):
    create_response = client.post(
        "/api/tasks",
        json={"title": "Test Task"}
    )
    task_id = create_response.json()["id"]
    
    response = client.get(f"/api/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["id"] == task_id


def test_get_nonexistent_task(client: TestClient):
    response = client.get("/api/tasks/550e8400-e29b-41d4-a716-446655440000")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]["message"].lower()


def test_list_tasks_with_filtering(client: TestClient):
    response = client.get("/api/tasks?status=pending&priority=high")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data


def test_list_tasks_with_invalid_status(client: TestClient):
    """Test that invalid status values return proper error"""
    response = client.get("/api/tasks?status=invalid_status")
    assert response.status_code == 422
    data = response.json()
    assert "error" in data["detail"]
    assert "Invalid status value" in data["detail"]["error"]
    assert "valid_values" in data["detail"]
    assert "pending" in data["detail"]["valid_values"]
    assert "in_progress" in data["detail"]["valid_values"]
    assert "completed" in data["detail"]["valid_values"]


def test_list_tasks_with_invalid_priority(client: TestClient):
    """Test that invalid priority values return proper error"""
    response = client.get("/api/tasks?priority=invalid_priority")
    assert response.status_code == 422
    data = response.json()
    assert "error" in data["detail"]
    assert "Invalid priority value" in data["detail"]["error"]
    assert "valid_values" in data["detail"]
    assert "low" in data["detail"]["valid_values"]
    assert "medium" in data["detail"]["valid_values"]
    assert "high" in data["detail"]["valid_values"]


def test_update_task(client: TestClient):
    create_response = client.post(
        "/api/tasks",
        json={"title": "Original Title"}
    )
    task_id = create_response.json()["id"]
    
    response = client.put(
        f"/api/tasks/{task_id}",
        json={"title": "Updated Title"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"


def test_delete_task(client: TestClient):
    create_response = client.post(
        "/api/tasks",
        json={"title": "To Delete"}
    )
    task_id = create_response.json()["id"]
    
    response = client.delete(f"/api/tasks/{task_id}")
    assert response.status_code == 204
    
    get_response = client.get(f"/api/tasks/{task_id}")
    assert get_response.status_code == 404


def test_health_check(client: TestClient):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "version" in data
    assert "database" in data


def test_root_endpoint_structure(client: TestClient):
    """Test root endpoint returns expected structure"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    
    # Check required fields are present
    assert "message" in data
    assert "suggestion" in data
    assert "api_info" in data
    assert "available_endpoints" in data
    assert "task_count" in data
    assert "environment" in data
    
    # Check api_info structure
    api_info = data["api_info"]
    assert "version" in api_info
    assert "base_url" in api_info
    assert "documentation" in api_info
    assert "health_check" in api_info
    
    # Check available_endpoints structure
    endpoints = data["available_endpoints"]
    assert "tasks" in endpoints
    assert "health" in endpoints
    
    # Check task count is a number
    assert isinstance(data["task_count"], int)
    assert data["task_count"] >= 0


def test_root_endpoint_task_behavior(client: TestClient):
    """Test root endpoint behavior changes based on task count"""
    # Get initial state
    initial_response = client.get("/")
    initial_count = initial_response.json()["task_count"]
    
    # Create a test task
    create_response = client.post(
        "/api/tasks",
        json={
            "title": "Test Task for Root",
            "description": "Test Description", 
            "status": "pending",
            "priority": "medium"
        }
    )
    assert create_response.status_code == 201
    
    # Check task count increased
    after_create_response = client.get("/")
    after_create_data = after_create_response.json()
    assert after_create_data["task_count"] == initial_count + 1
    
    # Message should contain task count
    assert "task" in after_create_data["message"].lower()
    
    # Delete the task
    task_id = create_response.json()["id"]
    delete_response = client.delete(f"/api/tasks/{task_id}")
    assert delete_response.status_code == 204
    
    # Check task count decreased
    after_delete_response = client.get("/")
    after_delete_data = after_delete_response.json()
    assert after_delete_data["task_count"] == initial_count