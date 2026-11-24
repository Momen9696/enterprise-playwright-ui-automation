"""Fixed demo accounts and seed items. These are fixtures, not real credentials."""

from demo_app.constants import PAGE_SIZE, PRIORITIES, STATUSES

USERS = (
    {
        "key": "admin",
        "email": "admin@demo.local",
        "name": "Avery Admin",
        "password": "AdminPass123!",
        "role": "admin",
    },
    {
        "key": "member",
        "email": "member@demo.local",
        "name": "Morgan Member",
        "password": "MemberPass123!",
        "role": "member",
    },
    {
        "key": "pager",
        "email": "pager@demo.local",
        "name": "Parker Pager",
        "password": "PagerPass123!",
        "role": "member",
    },
)

PAGER_ITEM_COUNT = 12


def pager_items() -> list[dict[str, str]]:
    """Twelve stable items used by search and pagination tests.

    Tests must not create, edit, or delete items owned by the pager account.
    """
    items: list[dict[str, str]] = []
    for number in range(1, PAGER_ITEM_COUNT + 1):
        items.append(
            {
                "title": f"Pager Item {number:02d}",
                "description": f"Seeded work item {number} for pagination and search.",
                "status": STATUSES[(number - 1) % len(STATUSES)],
                "priority": PRIORITIES[(number - 1) % len(PRIORITIES)],
            }
        )
    return items


def member_items() -> list[dict[str, str]]:
    return [
        {
            "title": "Member Seed Note A",
            "description": "Visible to the member account.",
            "status": "open",
            "priority": "medium",
        },
        {
            "title": "Member Seed Note B",
            "description": "A completed member note.",
            "status": "done",
            "priority": "low",
        },
    ]


def expected_pages(total: int, page_size: int = PAGE_SIZE) -> int:
    if total <= 0:
        return 1
    return (total + page_size - 1) // page_size
