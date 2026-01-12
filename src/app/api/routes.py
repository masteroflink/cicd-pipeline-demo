"""API routes for items and calculator endpoints."""

import uuid

from fastapi import APIRouter, HTTPException, status

from app.models.schemas import (
    CalculateRequest,
    CalculateResponse,
    ItemCreate,
    ItemResponse,
    Operation,
)
from app.services.calculator import add, divide, multiply, subtract

router = APIRouter(prefix="/api/v1", tags=["api"])

# In-memory storage for items
items_db: dict[str, ItemResponse] = {}


@router.get("/items", response_model=list[ItemResponse])
def get_items() -> list[ItemResponse]:
    """Get all items.

    Returns:
        List of all items in the database.
    """
    return list(items_db.values())


@router.post("/items", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(item: ItemCreate) -> ItemResponse:
    """Create a new item.

    Args:
        item: Item data to create.

    Returns:
        The created item with generated ID.
    """
    item_id = str(uuid.uuid4())
    item_response = ItemResponse(
        id=item_id,
        name=item.name,
        description=item.description,
    )
    items_db[item_id] = item_response
    return item_response


@router.get("/items/{item_id}", response_model=ItemResponse)
def get_item(item_id: str) -> ItemResponse:
    """Get a specific item by ID.

    Args:
        item_id: The unique identifier of the item.

    Returns:
        The item with the specified ID.

    Raises:
        HTTPException: If the item is not found.
    """
    if item_id not in items_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id '{item_id}' not found",
        )
    return items_db[item_id]


@router.post("/calculate", response_model=CalculateResponse)
def calculate(request: CalculateRequest) -> CalculateResponse:
    """Perform a calculation.

    Args:
        request: The calculation request with operands and operation.

    Returns:
        The calculation result.

    Raises:
        HTTPException: If division by zero is attempted.
    """
    operations = {
        Operation.ADD: add,
        Operation.SUBTRACT: subtract,
        Operation.MULTIPLY: multiply,
        Operation.DIVIDE: divide,
    }

    try:
        result = operations[request.operation](request.a, request.b)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from None

    return CalculateResponse(
        a=request.a,
        b=request.b,
        operation=request.operation.value,
        result=result,
    )
