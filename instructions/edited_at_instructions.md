# Plan of Action to Add "edited_at" Timestamp for Messages

Below is a step-by-step plan to introduce a new column called "edited_at" in the messages table, update the backend endpoints that handle message edits, and adjust the frontend to use this new column instead of relying on "updated_at" for displaying edited messages.

---

## 1. Database Changes

- [ ] Create a new nullable column, `edited_at`, in the `messages` table
  - Defaults to `NULL`
  - Stores the timestamp when the message is edited

Example Alembic migration snippet:

[CODE START]
def upgrade():
    op.add_column('messages',
                  sa.Column('edited_at', sa.DateTime(timezone=True), nullable=True))
    # Additional logic if needed

def downgrade():
    op.drop_column('messages', 'edited_at')
[CODE END]

---

## 2. Model and Schema Updates

- [x] Update the SQLAlchemy `Message` model to include the `edited_at` column.
- [x] Update any relevant Pydantic schemas (e.g., the `Message` schema) to include `edited_at`.

Example model update snippet:

[CODE START]
class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True)
    content = Column(String, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    edited_at = Column(DateTime(timezone=True), nullable=True)  # Newly added column
    # ... other fields
[CODE END]

---

## 3. Edit Message Endpoint Changes

- [x] In the message edit endpoint (typically `PUT /channels/{channel_id}/messages/{message_id}`):
  - Update the `edited_at` field with the current timestamp (e.g., `datetime.utcnow()`) whenever a user edits a message.
  - Keep `updated_at` as is (it can still be auto-updated or database-managed).

Example endpoint logic snippet:

[CODE START]
@router.put("/channels/{channel_id}/messages/{message_id}")
async def edit_message(channel_id: int, message_id: int, payload: EditMessageSchema, db: Session = Depends(...)):
    message = get_message_by_id(db, message_id)
    # ... validation checks
    message.content = payload.content
    message.edited_at = datetime.utcnow()  # Update edited_at
    db.commit()
    db.refresh(message)
    return message
[CODE END]

---

## 4. WebSocket Event Adjustments

- [x] Ensure the updated WebSocket event payload for message edits includes the new `edited_at` value:
  - If the event was previously sending `updated_at`, now it should also send (or replace with) `edited_at`.
  - Compare the value of `edited_at`; if it's not `NULL`, the client can display the edited indicator.

Example WebSocket payload snippet:

[CODE START]
{
  "type": "message_update",
  "channel_id": 789,
  "message": {
    "id": 123,
    "content": "Edited content",
    "edited_at": "2024-01-07T12:30:00Z",
    ...
  }
}
[CODE END]

---

## 5. Frontend Adjustments

- [x] Identify the existing usage of `updated_at` in the frontend:
  - Likely within the `ChatMessage` component (or a similarly named file/component).
- [x] Replace references to `updated_at` with `edited_at` to determine if a message was edited:
  - If `edited_at` is `null`, do not display the "(edited)" indicator.
  - If `edited_at` is not `null`, display the edited time label or icon.

Example frontend usage snippet (TypeScript/React):

[CODE START]
function ChatMessage({ message }: ChatMessageProps) {
  const { content, created_at, edited_at } = message;

  return (
    <div>
      <p>{content}</p>
      <span>Sent at: {new Date(created_at).toLocaleTimeString()}</span>
      {edited_at && (
        <span> (edited at {new Date(edited_at).toLocaleTimeString()})</span>
      )}
    </div>
  );
}
[CODE END]

---

## 6. Testing

- [ ] Verify the database migration runs without errors and the `edited_at` column is added.
- [ ] Test the edit message endpoint to confirm:
  - `edited_at` is properly set when editing a message.
  - `updated_at` remains unaffected for visual "last updated" behaviors if needed.
- [ ] Check the WebSocket events to ensure `edited_at` is appropriately included in the edited message payload.
- [ ] Confirm the frontend properly shows or hides the "edited" label based on `edited_at`.

---

## 7. Additional Considerations

- [x] Decide how to handle existing messages without an `edited_at` column (these will be `NULL` by default).
- [x] Determine if `updated_at` should remain purely database-managed, or if you want to keep it synced with `edited_at`.
- [x] Update any relevant documentation (API docs, schemas, or developer notes) regarding this new field.

---

### Summary

By introducing an `edited_at` column, we can distinguish between general row updates (`updated_at`) and specific message edits (`edited_at`). The frontend will rely on `edited_at` to determine whether to display an edited-time indicator. WebSocket events will include `edited_at` to propagate this information in real time.