# Memory Workflow

## Capture

- Detect stable information in the current conversation.
- Ask before saving anything ambiguous or sensitive.
- Convert long dialogue into compact memory items.

## Recall

- Start with the current task.
- Pull the smallest set of memories that change the answer.
- Prefer recent, confirmed, and directly relevant items.

## Update

- Apply confirmed corrections immediately.
- Replace outdated preferences or decisions with a superseding entry.
- Keep a short session summary at the end of important work.

## Forget

- Remove items that are clearly wrong, sensitive, or explicitly deleted by the user.
- If history matters, mark the item deleted or superseded rather than erasing context silently.

## Safety

- Do not store secrets, tokens, or credentials.
- Do not infer personal attributes from weak signals.
- Do not turn one-off tasks into permanent memory.
