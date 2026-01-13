"""API routes for items and calculator endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import Item
from app.models.schemas import (
    CalculateRequest,
    CalculateResponse,
    ItemCreate,
    ItemResponse,
    Operation,
)
from app.services.calculator import add, divide, multiply, subtract

router = APIRouter(prefix="/api/v1", tags=["api"])


@router.get("/items", response_model=list[ItemResponse])
async def get_items(db: AsyncSession = Depends(get_db)) -> list[ItemResponse]:
    """Get all items.

    Returns:
        List of all items in the database.
    """
    result = await db.execute(select(Item))
    items = result.scalars().all()
    return [
        ItemResponse(id=item.id, name=item.name, description=item.description)
        for item in items
    ]


@router.post("/items", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    item: ItemCreate, db: AsyncSession = Depends(get_db)
) -> ItemResponse:
    """Create a new item.

    Args:
        item: Item data to create.

    Returns:
        The created item with generated ID.
    """
    db_item = Item(name=item.name, description=item.description)
    db.add(db_item)
    await db.flush()
    await db.refresh(db_item)

    return ItemResponse(
        id=db_item.id,
        name=db_item.name,
        description=db_item.description,
    )


@router.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(item_id: str, db: AsyncSession = Depends(get_db)) -> ItemResponse:
    """Get a specific item by ID.

    Args:
        item_id: The unique identifier of the item.

    Returns:
        The item with the specified ID.

    Raises:
        HTTPException: If the item is not found.
    """
    result = await db.execute(select(Item).where(Item.id == item_id))
    item = result.scalar_one_or_none()

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id '{item_id}' not found",
        )

    return ItemResponse(id=item.id, name=item.name, description=item.description)


@router.post("/calculate", response_model=CalculateResponse)
async def calculate(request: CalculateRequest) -> CalculateResponse:
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
