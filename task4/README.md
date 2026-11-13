# Task 4 — Quest, clue inventory, timeline and quiz

Task 4 is imported and routed by the project's Scene Manager in `main.py`.

## Integrated Pác Bó 1941 flow

1. Choose **Hang Pác Bó** on the map and press **Enter** to investigate.
2. Complete the location's evidence challenges to collect its field clues.
3. Press **D**. `main.py` routes Pác Bó to the Task 4 scene, where its cited clue
   cards are displayed in the inventory.
4. Drag the four clue cards from inventory into the causal slots; press
   **Enter** to verify. Incorrect order shows a contradiction and can be retried.
5. Answer the three A-D review questions with **1-4** or mouse. Each correct
   answer adds 30 knowledge points. A completed attempt marks the quest done.
6. The finished Pác Bó payload is written to `data/task4_pacbo_progress.json`.

## Modules

- `quest_manager.py`: existing game-wide unlock/progress manager used by map and
  the original location quiz flow.
- `quest_system.py`: reusable `QuestStateMachine`, source-validated `Clue`,
  `ClueInventory`, `DeductionTimelineBoard`, `TimelineScene`, `QuizSystem`, and
  FastAPI-ready JSON serialization.
- `main.py`: owns the Task 4 scene state and routes keyboard/mouse input to it.

The module-level demo can be run with:

```powershell
python -m task4.quest_system
```

If earlier project tasks are not ready, start the standalone interactive demo
instead. It opens its own Pygame window, uses one quiz question, and does not
require login, MySQL, or the main game's location unlocks:

```powershell
python -m task4.demo_scene
```

Press Enter to start, drag the four sample clues into the timeline slots, press
Enter to verify, then answer the single question with 1-4 or the mouse. Wrong
answers can be retried. A successful run writes `data/task4_demo_result.json`.

## Persistence

The integrated sample currently writes the Task 4 schema as local JSON. The
existing MySQL `task4_quest_progress` table only stores clue IDs and attempts;
connecting the full JSON payload to FastAPI or extending the SQL schema is a
separate backend integration step.