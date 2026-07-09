# Database Design

This document explains the data model behind Mealdoo, the reasoning behind key schema decisions, and the trade-offs considered along the way.

The schema is defined in [`schema.dbml`](./schema.dbml) using DBML syntax and can be visualised at [dbdiagram.io](https://dbdiagram.io).

---

## Overview

Mealdoo's data model is built around three concerns:

1. **Multi-user households** — Family members share inventory and meal plans while maintaining individual accounts.
2. **A dual-source content model** — Both system-provided and user-defined items and recipes coexist in the same tables.
3. **Batch-level inventory tracking** — Groceries are tracked per purchase batch to support FIFO expiry management.

The schema contains 10 tables, 5 enums, and 15 foreign key relationships. 

---

## Core Concepts

### Households as tenants

A **household** represents a group of people who share pantry inventory, recipes, and meal plans. This is the primary tenant boundary — most tables carry a `household_id` to scope data.

Users and households have a **many-to-many** relationship via `household_members`:

- A user can belong to multiple households (e.g., living with roommates, plus a household with parents).
- A household has multiple members with roles (`owner`, `member`).

This structure supports realistic scenarios: users leaving one household to join another without losing their account, or households persisting after their creator leaves.

### Dual-source content: system + user

Both `items` (pantry ingredients) and `recipes` use a `nullable household_id` pattern:

- `household_id IS NULL` → system-provided content, visible to all households
- `household_id IS NOT NULL` → household-specific custom content

A query for "everything this household can use" looks like:

```sql
SELECT * FROM items 
WHERE household_id IS NULL OR household_id = :current_household_id
```

This avoids maintaining parallel tables for system and user content. The same pattern is common in multi-tenant SaaS products where system templates coexist with tenant customisations.

### Batch tracking for inventory

`inventory_entries` records each purchase as a separate row, not an aggregated stock count. Two purchases of tomatoes on different days create two rows, each with its own `expiry_date` and remaining `quantity`.

This supports:

- **FIFO expiry management** — prioritise older batches when planning meals.
- **Traceability** — link each batch back to the receipt it came from via `receipt_id`.
- **Accurate expiry warnings** — one batch expiring soon doesn't shadow a fresher batch of the same item.

---

## Entity Relationship Diagram

See [`schema.dbml`](./schema.dbml)

**Tables:**

| Table | Purpose |
|-------|---------|
| `users` | Account information (auth handled by Supabase Auth) |
| `households` | Tenant boundary for shared data |
| `household_members` | Many-to-many join between users and households |
| `items` | Global catalogue of ingredients (system + user) |
| `recipes` | Recipes with metadata (system + user) |
| `recipe_items` | Ingredients required per recipe with quantities |
| `receipts` | Uploaded receipts and their OCR output |
| `inventory_entries` | Per-batch pantry records |
| `shopping_list_items` | Household shopping list |
| `meal_plans` | Scheduled meals per date and meal type |

---

## Design Decisions

### Foreign key delete strategies

Every foreign key explicitly specifies an `ON DELETE` behaviour. Three strategies are used:

**CASCADE — Records with no independent meaning**

Applied to join tables and composition relationships:

- `household_members` → both foreign keys (a membership without a user or household is meaningless)
- `recipe_items.recipe_id` (ingredients belong to their recipe)
- `items.household_id`, `recipes.household_id`, `receipts.household_id`, `inventory_entries.household_id`, `shopping_list_items.household_id`, `meal_plans.household_id` (household-owned content disappears with the household)
- `shopping_list_items.item_id` (shopping list entries are ephemeral working state, not history)

**RESTRICT — Referenced records must remain intact**

Applied where deletion would corrupt an existing recipe or historical record:

- `recipe_items.item_id` — deleting an item would leave recipes with missing ingredients
- `inventory_entries.item_id` — inventory history should not lose its item reference

The application layer is responsible for handling the "you can't delete this because it's used elsewhere" case.

**SET NULL — Attribution cleared but content preserved**

Applied to `created_by` and `uploaded_by` fields, and to `meal_plans.recipe_id` and `inventory_entries.receipt_id`:

- `items.created_by`, `recipes.created_by`, `meal_plans.created_by`, `receipts.uploaded_by`, `shopping_list_items.added_by` — when a user deletes their account, their contributions to shared household content remain visible; ownership is cleared.
- `meal_plans.recipe_id` — a planned meal preserves its date, meal type, and servings even if the linked recipe is deleted.
- `inventory_entries.receipt_id` — an inventory batch remains valid even after its source receipt is removed.

### Dual unit fields on `recipe_items` and `items`

Both `items.default_unit` and `recipe_items.unit` exist. This is intentional redundancy:

- `items.default_unit` — how the item is typically purchased (tomatoes by the piece, soy sauce by the bottle).
- `recipe_items.unit` — how the item is used in a specific recipe (tomatoes in grams, soy sauce in tablespoons).

A future unit-conversion service will handle "the recipe needs 50g of tomato, the pantry has 3 tomatoes" reconciliation.

---

## What's Not Modelled Yet

Deliberately out of scope for the initial schema:

- **Supermarket specials data** — will be added when the recommendation feature is designed. Likely a separate `store_specials` table joining to `items` by name/category.
- **Multi-list shopping** — the current model assumes one active shopping list per household. Extending to named lists would require introducing a `shopping_lists` parent table.

---

## Future Migrations to Anticipate

Decisions likely to require schema changes as the product evolves:

- **Vector embeddings for item recognition** — a `pgvector` column on `items` for CLIP embeddings, once the photo recognition pipeline is built.
- **Recipe images** — a separate `recipe_images` table if recipes support multiple photos and step-by-step images.
- **Meal plan grouping** — if users request "save this week's plan as a template", a `meal_plan_templates` table will be introduced.

## Implementation Notes

### Enum Type Sharing Across Tables

Some enum types (`item_unit`) are referenced by multiple tables. When defining these in SQLAlchemy models, only the first model definition should let SQLAlchemy create the enum type in the database; subsequent references must use `create_type=False` to prevent duplicate-creation errors.

In migration files that reference existing enum types across migrations, `postgresql.ENUM` (from `sqlalchemy.dialects`) is preferred over the generic `sa.Enum` because it strictly respects the `create_type=False` parameter.

### On-Delete Coherence with Nullability

Foreign keys with `ON DELETE SET NULL` behavior must be declared as nullable in the model definition. Otherwise, the delete operation will fail at runtime due to conflicting NOT NULL constraint. Example: `meal_plans.recipe_id` uses SET NULL, so it must be `Mapped[UUID | None]`.

### Enum Cleanup in Downgrade

Alembic's autogenerate creates enum types in `upgrade()` but doesn't 
automatically drop them in `downgrade()`. Each migration that creates new enum types must manually add `sa.Enum(name='xxx').drop(op.get_bind())` statements in `downgrade()`, placed after all `drop_table` operations. Enum types that are only *referenced* (not created) by a migration must NOT be dropped in that migration's downgrade.