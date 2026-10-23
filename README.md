# KAVA

KAVA helps people put together a wildfire insurance claim. You upload your
photos, receipts and reports, it checks the claim against a set of 47 rules an
insurer would care about, keeps improving the claim until it scores well, and
then gives you a ready-to-send claim package.

Frontend is live at https://kava-xi.vercel.app (backend on Render).

## How it works

The app is a four-step wizard.

1. **Upload documents.** Drop in damage photos, receipts, the fire department
   report, contractor estimates and so on. Claude reads each file and pulls out
   the useful details (amounts, dates, what the damage looks like). There's also
   a receipt sync step that pulls purchase receipts from retailers. Right now it
   reads sample data from `test_claims/receipts.json` instead of a live API.
2. **Create the claim packet.** Fill in the claimant, policy number, property
   address, incident date and amount, and the backend bundles everything into a
   claim packet and saves it.
3. **Validation loop.** The packet is scored against the 47 rules, grouped into
   completeness, damage assessment, documentation quality and fraud indicators.
   Each round goes a level deeper (basic screening, then a re-check with the
   receipt data, then a forensic pass, then a final expert review). Between
   rounds the backend adds synced receipts and re-reads low-confidence documents.
   It stops once the claim hits 80% or after four rounds.
4. **Final outputs.** You get a zip with a cover letter, proof of loss
   statement, damage photos, itemized loss inventory, receipts, the validation
   report and the original documents. The result is also signed with an ECDSA
   key so it can be checked later through `/api/verify-proof/{id}`, and the
   claim gets a trust badge based on its score (gold at 90%+, silver at 80%+,
   bronze at 60%+).

Claims are stored in SQLite.

## Tech stack

- Frontend: Next.js, React, TypeScript, Tailwind CSS
- Backend: Python, FastAPI, SQLAlchemy
- AI: Claude (claude-sonnet-4) for document reading and claim evaluation
- PDFs: ReportLab
- Hosting: Vercel (frontend), Render (backend)

## Running it locally

You'll need Python 3, Node.js and a Claude API key.

1. Copy `.env.example` to `.env` in the project root and add your
   `CLAUDE_API_KEY`.

2. Set up the backend:

   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Install the frontend:

   ```bash
   cd frontend
   npm install
   ```

4. From the project root, start both:

   ```bash
   ./start.sh
   ```

   The frontend runs on http://localhost:3001 and the backend on
   http://localhost:8000. Use `./status.sh` to check them and `./stop.sh` to
   shut them down.

## Sample data

`test_realistic_claim/` has a full set of documents for a made-up kitchen fire
claim (photo, receipts, policy, fire department report, contractor estimate) that
you can upload to try the whole flow. `test_claims/` has more sample documents
plus the receipt data used by the sync step.

## License

MIT. Built at HackMIT 2025.
