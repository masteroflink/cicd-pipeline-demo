"""Tests for the API routes.

TDD: These tests are written BEFORE the implementation.
"""

from fastapi.testclient import TestClient


class TestItemsAPI:
    """Tests for the /api/v1/items endpoints."""

    def test_get_items_returns_list(self, client: TestClient) -> None:
        """Test that GET /api/v1/items returns a list."""
        response = client.get("/api/v1/items")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_post_items_creates_item(self, client: TestClient) -> None:
        """Test that POST /api/v1/items creates and returns an item."""
        item_data = {"name": "Test Item", "description": "A test item"}
        response = client.post("/api/v1/items", json=item_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Item"
        assert data["description"] == "A test item"
        assert "id" in data

    def test_post_items_generates_unique_id(self, client: TestClient) -> None:
        """Test that POST /api/v1/items generates unique IDs."""
        item1 = client.post(
            "/api/v1/items", json={"name": "Item 1", "description": "First"}
        ).json()
        item2 = client.post(
            "/api/v1/items", json={"name": "Item 2", "description": "Second"}
        ).json()
        assert item1["id"] != item2["id"]

    def test_get_item_by_id_returns_item(self, client: TestClient) -> None:
        """Test that GET /api/v1/items/{id} returns the specific item."""
        # Create an item first
        create_response = client.post(
            "/api/v1/items", json={"name": "Specific Item", "description": "For lookup"}
        )
        created_item = create_response.json()
        item_id = created_item["id"]

        # Get the item by ID
        response = client.get(f"/api/v1/items/{item_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == item_id
        assert data["name"] == "Specific Item"
        assert data["description"] == "For lookup"

    def test_get_item_by_id_returns_404_for_nonexistent(
        self, client: TestClient
    ) -> None:
        """Test that GET /api/v1/items/{id} returns 404 for non-existent ID."""
        response = client.get("/api/v1/items/nonexistent-id-12345")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_get_items_returns_created_items(self, client: TestClient) -> None:
        """Test that GET /api/v1/items returns all created items."""
        # Create some items
        client.post("/api/v1/items", json={"name": "Item A", "description": "First"})
        client.post("/api/v1/items", json={"name": "Item B", "description": "Second"})

        # Get all items
        response = client.get("/api/v1/items")
        assert response.status_code == 200
        data = response.json()
        # Should contain at least the 2 items we just created
        # (may contain more from other tests due to in-memory storage)
        assert len(data) >= 2
        names = [item["name"] for item in data]
        assert "Item A" in names
        assert "Item B" in names

    def test_post_items_validates_required_fields(self, client: TestClient) -> None:
        """Test that POST /api/v1/items validates required fields."""
        # Missing name field
        response = client.post("/api/v1/items", json={"description": "No name"})
        assert response.status_code == 422

        # Missing description field
        response = client.post("/api/v1/items", json={"name": "No description"})
        assert response.status_code == 422

        # Empty body
        response = client.post("/api/v1/items", json={})
        assert response.status_code == 422


class TestCalculateAPI:
    """Tests for the /api/v1/calculate endpoint."""

    def test_calculate_add(self, client: TestClient) -> None:
        """Test POST /api/v1/calculate with add operation."""
        response = client.post(
            "/api/v1/calculate", json={"a": 5, "b": 3, "operation": "add"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == 8
        assert data["operation"] == "add"

    def test_calculate_subtract(self, client: TestClient) -> None:
        """Test POST /api/v1/calculate with subtract operation."""
        response = client.post(
            "/api/v1/calculate", json={"a": 10, "b": 4, "operation": "subtract"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == 6
        assert data["operation"] == "subtract"

    def test_calculate_multiply(self, client: TestClient) -> None:
        """Test POST /api/v1/calculate with multiply operation."""
        response = client.post(
            "/api/v1/calculate", json={"a": 6, "b": 7, "operation": "multiply"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == 42
        assert data["operation"] == "multiply"

    def test_calculate_divide(self, client: TestClient) -> None:
        """Test POST /api/v1/calculate with divide operation."""
        response = client.post(
            "/api/v1/calculate", json={"a": 20, "b": 4, "operation": "divide"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == 5.0
        assert data["operation"] == "divide"

    def test_calculate_divide_by_zero_returns_400(self, client: TestClient) -> None:
        """Test POST /api/v1/calculate divide by zero returns 400."""
        response = client.post(
            "/api/v1/calculate", json={"a": 10, "b": 0, "operation": "divide"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

    def test_calculate_invalid_operation(self, client: TestClient) -> None:
        """Test POST /api/v1/calculate with invalid operation returns 422."""
        response = client.post(
            "/api/v1/calculate", json={"a": 5, "b": 3, "operation": "invalid"}
        )
        assert response.status_code == 422

    def test_calculate_with_floats(self, client: TestClient) -> None:
        """Test POST /api/v1/calculate works with float values."""
        response = client.post(
            "/api/v1/calculate", json={"a": 2.5, "b": 3.5, "operation": "add"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == 6.0

    def test_calculate_response_includes_inputs(self, client: TestClient) -> None:
        """Test POST /api/v1/calculate response includes input values."""
        response = client.post(
            "/api/v1/calculate", json={"a": 5, "b": 3, "operation": "add"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["a"] == 5
        assert data["b"] == 3
